# apps/ai_assistant/views.py (نسخه نهایی و اصلاح شده)

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.http import require_http_methods
import json
import time
import logging
from .models import Conversation, ChatMessage
from .services.agent_core import run_agent_stream 
from langchain_core.messages import HumanMessage, AIMessage

# تنظیم لاگر
logger = logging.getLogger(__name__)
from apps.products.models import Product
import json

# +++ ویوی جدید برای API +++
@login_required
@require_http_methods(["POST"])
def get_product_details_api(request):
    """
    یک API داخلی برای دریافت اطلاعات تکمیلی محصولات (لینک و تصویر)
    بر اساس لیستی از شناسه‌ها.
    """
    try:
        data = json.loads(request.body)
        product_ids = data.get('ids', [])

        if not isinstance(product_ids, list):
            return JsonResponse({'error': 'ورودی باید یک لیست از شناسه‌ها باشد.'}, status=400)

        # حذف شناسه‌های تکراری و اطمینان از عددی بودن آنها
        unique_ids = set(int(pid) for pid in product_ids)
        
        products = Product.objects.filter(id__in=unique_ids)
        
        response_data = {}
        for product in products:
            response_data[str(product.id)] = {
                'url': product.get_absolute_url(),
                'image_url': product.image_name.url if product.image_name else '',
                'name': product.product_name,
                'price': f"{product.price:,} تومان" # فرمت شده برای نمایش
            }
            
        return JsonResponse(response_data)

    except (json.JSONDecodeError, TypeError, ValueError):
        return JsonResponse({'error': 'داده‌های ارسالی نامعتبر است.'}, status=400)
    except Exception as e:
        logger.error(f"Error in get_product_details_api: {e}")
        return JsonResponse({'error': 'خطای داخلی سرور'}, status=500)



def is_widget_request(request):
    """تشخیص درخواست ویجت"""
    return (request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 
            request.GET.get('widget') == 'true' or
            request.headers.get('X-Widget-Mode') == 'true')

@login_required
def get_or_create_conversation(request, conversation_id=None, widget_mode=False):
    """
    ایجاد یا بازیابی مکالمه با منطق اصلاح شده و صحیح
    """
    # حالت ۱: درخواست برای یک مکالمه با شناسه مشخص (از ویجت یا صفحه کامل)
    if conversation_id:
        try:
            conversation = Conversation.objects.get(id=conversation_id, user=request.user)
            
            # اگر از ویجت به صفحه کامل می‌آییم، مکالمه را "ارتقا" می‌دهیم
            if not widget_mode and conversation.is_widget:
                conversation.is_widget = False
                if 'چت سریع' in conversation.title:
                    conversation.title = conversation.title.replace('چت سریع', 'مکالمه')
                conversation.save()
            
            # اگر در صفحه کامل هستیم، شناسه را در سشن ذخیره می‌کنیم
            if not widget_mode:
                request.session['active_conversation_id'] = str(conversation.id)

            return conversation
        except Conversation.DoesNotExist:
            # اگر شناسه نامعتبر بود، به حالت ایجاد مکالمه جدید می‌رویم
            if not widget_mode and 'active_conversation_id' in request.session:
                del request.session['active_conversation_id']
            return new_conversation(request, widget_mode)

    # حالت ۲: صفحه کامل چت بدون شناسه خاص (بررسی سشن برای آخرین مکالمه)
    if not widget_mode:
        active_conversation_id = request.session.get('active_conversation_id')
        if active_conversation_id:
            try:
                return Conversation.objects.get(id=active_conversation_id, user=request.user, is_widget=False)
            except Conversation.DoesNotExist:
                del request.session['active_conversation_id']
    
    # حالت ۳: اولین بازدید از ویجت یا صفحه کامل (ایجاد مکالمه کاملا جدید)
    return new_conversation(request, widget_mode)


def new_conversation(request, widget_mode=False):
    """ایجاد یک مکالمه جدید"""
    conversation = Conversation.objects.create(
        user=request.user,
        is_widget=widget_mode,
        title='چت سریع' if widget_mode else 'مکالمه جدید'
    )
    
    if not widget_mode:
        request.session['active_conversation_id'] = str(conversation.id)
    
    return conversation

@login_required
@require_http_methods(["GET", "POST"])
def chat_view(request, conversation_id=None):
    """
    ویوی اصلی چت با پشتیبانی از حالت کامل و ویجت
    """
    widget_mode = is_widget_request(request)
    conversation = get_or_create_conversation(request, conversation_id, widget_mode)

    if request.method == 'POST':
        return handle_chat_message(request, conversation) # widget_mode is implicit
    
    return handle_chat_get_request(request, conversation, widget_mode)

def handle_chat_message(request, conversation):
    """پردازش پیام چت"""
    request_start_time = time.perf_counter()
    
    try:
        body = json.loads(request.body.decode('utf-8'))
        user_message = body.get('message', '').strip()

        if not user_message:
            return JsonResponse({'error': 'پیام نمی‌تواند خالی باشد.'}, status=400)

        def stream_and_save_response():
            nonlocal user_message, conversation, request_start_time
            
            chat_history = prepare_chat_history(conversation)
            full_response = []
            
            try:
                for chunk in run_agent_stream(user_message, chat_history, request):
                    full_response.append(chunk)
                    yield chunk
                
                save_messages(conversation, user_message, full_response)
                
            except Exception as e:
                logger.error(f"Error in streaming: {str(e)}")
                yield "خطا در پردازش درخواست. لطفاً دوباره تلاش کنید."
                raise

        return StreamingHttpResponse(
            stream_and_save_response(), 
            content_type="text/plain; charset=utf-8"
        )

    except json.JSONDecodeError:
        return JsonResponse({'error': 'داده‌های نامعتبر'}, status=400)
    except Exception as e:
        logger.error(f"Error in handle_chat_message: {str(e)}")
        return JsonResponse({'error': 'خطای سرور داخلی'}, status=500)

def prepare_chat_history(conversation):
    """آماده‌سازی تاریخچه چت برای ایجنت"""
    # .messages.all() از related_name در مدل استفاده می‌کند
    chat_history_objects = conversation.messages.order_by('timestamp').all()
    
    chat_history_for_agent = []
    for msg in chat_history_objects:
        if msg.sender == 'user':
            chat_history_for_agent.append(HumanMessage(content=msg.content))
        else:
            chat_history_for_agent.append(AIMessage(content=msg.content))
    
    return chat_history_for_agent

def save_messages(conversation, user_message, full_response):
    """ذخیره پیام‌ها در دیتابیس"""
    final_text = "".join(full_response)
    
    ChatMessage.objects.create(
        conversation=conversation, 
        sender='user', 
        content=user_message
    )
    
    ChatMessage.objects.create(
        conversation=conversation, 
        sender='assistant', 
        content=final_text
    )
    
    # .messages.count() از related_name در مدل استفاده می‌کند
    if conversation.messages.count() <= 2 and len(user_message) > 5:
        if not conversation.title or conversation.title in ['چت سریع', 'مکالمه جدید']:
             conversation.title = user_message[:50]
             conversation.save()

def handle_chat_get_request(request, conversation, widget_mode):
    """پردازش درخواست GET"""
    if widget_mode:
        return JsonResponse({
            'status': 'widget_mode',
            'conversation_id': str(conversation.id)
        })
    
    user_conversations = Conversation.objects.filter(
        user=request.user, 
        is_widget=False
    ).order_by('-created_at')
    
    current_chat_messages = conversation.messages.order_by('timestamp').all()
    
    context = {
        'user_conversations': user_conversations,
        'active_conversation_id': str(conversation.id),
        'current_chat_messages': current_chat_messages,
    }
    
    return render(request, 'ai_assistant/chat.html', context)

@login_required
@require_http_methods(["POST"])
def new_chat_view(request):
    """ایجاد مکالمه جدید برای صفحه کامل"""
    if 'active_conversation_id' in request.session:
        del request.session['active_conversation_id']
    
    conversation = new_conversation(request, widget_mode=False)
    
    return redirect(reverse('ai_assistant:chat_view_conversation', args=[conversation.id]))

@login_required
@require_http_methods(["POST"])
def delete_chat_view(request, conversation_id):
    """حذف مکالمه"""
    conversation = get_object_or_404(
        Conversation, 
        id=conversation_id, 
        user=request.user
    )
    
    deleted_id = str(conversation.id)
    conversation.delete()
    
    if request.session.get('active_conversation_id') == deleted_id:
        del request.session['active_conversation_id']
    
    return redirect(reverse('ai_assistant:chat_view'))

