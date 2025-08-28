# apps/ai_assistant/views.py (نسخه نهایی)

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import json
from langchain_core.messages import HumanMessage, AIMessage
import time
from .services.agent_core import run_agent_stream
from .models import Conversation, ChatMessage

@login_required
def get_or_create_conversation(request, conversation_id=None):
    if conversation_id:
        try:
            conversation = Conversation.objects.get(id=conversation_id, user=request.user)
            request.session['active_conversation_id'] = str(conversation.id)
            return conversation
        except Conversation.DoesNotExist:
            return new_chat_view(request, is_redirect=False)

    active_conversation_id = request.session.get('active_conversation_id')
    if active_conversation_id:
        try:
            conversation = Conversation.objects.get(id=active_conversation_id, user=request.user)
            return conversation
        except Conversation.DoesNotExist:
            del request.session['active_conversation_id']
    
    conversation = Conversation.objects.create(user=request.user)
    request.session['active_conversation_id'] = str(conversation.id)
    return conversation

@login_required
def chat_view(request, conversation_id=None):
    """
    Main chat view, upgraded with performance timing for the full request lifecycle.
    """
    conversation = get_or_create_conversation(request, conversation_id)

    if request.method == 'POST':
        # Record the absolute start time of the request
        request_start_time = time.perf_counter()
        
        try:
            body = json.loads(request.body.decode('utf-8'))
            user_message = body.get('message', '').strip()

            if not user_message:
                return JsonResponse({'error': 'Message cannot be empty.'}, status=400)

            def stream_and_save_response():
                chat_history_objects = conversation.messages.order_by('timestamp').all()
                chat_history_for_agent = []
                for msg in chat_history_objects:
                    if msg.sender == 'user':
                        chat_history_for_agent.append(HumanMessage(content=msg.content))
                    else:
                        chat_history_for_agent.append(AIMessage(content=msg.content))
                
                full_response = []
                first_chunk_received = False
                
                # --- Call the agent and start streaming ---
                agent_start_time = time.perf_counter()
                print("\n--- Invoking Agent ---")
                for chunk in run_agent_stream(user_message, chat_history_for_agent, request):
                    if not first_chunk_received:
                        first_chunk_time = time.perf_counter()
                        print(f">>> [TIMER] Agent 'Thinking Time' (Time to First Token): {first_chunk_time - agent_start_time:.4f} seconds.")
                        first_chunk_received = True
                    
                    full_response.append(chunk)
                    yield chunk
                
                stream_end_time = time.perf_counter()
                if first_chunk_received:
                     print(f">>> [TIMER] Full Response Streaming Duration: {stream_end_time - first_chunk_time:.4f} seconds.")

                # --- DB Save ---
                save_start_time = time.perf_counter()
                final_text = "".join(full_response)
                ChatMessage.objects.create(conversation=conversation, sender='user', content=user_message)
                ChatMessage.objects.create(conversation=conversation, sender='assistant', content=final_text)
                if conversation.messages.count() <= 2 and len(user_message) > 5:
                    conversation.title = user_message[:50]
                    conversation.save()
                save_end_time = time.perf_counter()
                print(f">>> [TIMER] DB Save Duration: {save_end_time - save_start_time:.4f} seconds.")

                # --- Total Time Calculation ---
                total_time = time.perf_counter() - request_start_time
                print(f"\n>>> [TIMER] TOTAL REQUEST-TO-RESPONSE DURATION: {total_time:.4f} seconds. <<<\n")

            return StreamingHttpResponse(stream_and_save_response(), content_type="text/plain")

        except Exception as e:
            print(f"!!! FATAL ERROR in chat_view (streaming): {str(e)}")
            return StreamingHttpResponse("An unexpected error occurred on the server.", status=500, content_type="text/plain")
    
    user_conversations = Conversation.objects.filter(user=request.user).order_by('-created_at')
    current_chat_messages = conversation.messages.order_by('timestamp').all()
    context = {
        'user_conversations': user_conversations,
        'active_conversation_id': str(conversation.id),
        'current_chat_messages': current_chat_messages
    }
    return render(request, 'ai_assistant/chat.html', context)


@login_required
def new_chat_view(request, is_redirect=True):
    if 'active_conversation_id' in request.session:
        del request.session['active_conversation_id']
    if is_redirect:
        return redirect(reverse('ai_assistant:chat_view'))
    else:
        return get_or_create_conversation(request)

@login_required
def delete_chat_view(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    if request.method == 'POST':
        deleted_id = str(conversation.id)
        conversation.delete()
        if request.session.get('active_conversation_id') == deleted_id:
            del request.session['active_conversation_id']
        return redirect(reverse('ai_assistant:chat_view'))
    return redirect(request.META.get('HTTP_REFERER', reverse('ai_assistant:chat_view')))







# # apps/ai_assistant/views.py

# from django.shortcuts import render, redirect, get_object_or_404
# from django.http import JsonResponse, StreamingHttpResponse
# from django.contrib.auth.decorators import login_required
# from django.urls import reverse
# import json
# import time

# from apps.orders.shop_card import ShopCart
# from apps.products.models import Product

# from .services.rag_core import assistant_service
# from .models import Conversation, ChatMessage

# @login_required
# def get_or_create_conversation(request, conversation_id=None):
#     if conversation_id:
#         try:
#             conversation = Conversation.objects.get(id=conversation_id, user=request.user)
#             request.session['active_conversation_id'] = str(conversation.id)
#             print(f"--- Switched to conversation ID: {conversation_id} ---")
#             return conversation
#         except Conversation.DoesNotExist:
#             return new_chat_view(request, is_redirect=False)

#     active_conversation_id = request.session.get('active_conversation_id')
#     if active_conversation_id:
#         try:
#             conversation = Conversation.objects.get(id=active_conversation_id, user=request.user)
#             print(f"--- Continuing conversation ID: {active_conversation_id} ---")
#             return conversation
#         except Conversation.DoesNotExist:
#             del request.session['active_conversation_id']
    
#     conversation = Conversation.objects.create(user=request.user)
#     request.session['active_conversation_id'] = str(conversation.id)
#     print(f"--- Started new conversation ID: {conversation.id} ---")
#     return conversation

# @login_required
# def chat_view(request, conversation_id=None):
#     """
#     Main chat view, upgraded with performance timing for streaming responses.
#     """
#     conversation = get_or_create_conversation(request, conversation_id)

#     if request.method == 'POST':
#         try:
#             request_start_time = time.perf_counter()

#             body = json.loads(request.body.decode('utf-8'))
#             user_message = body.get('message', '').strip()

#             if not user_message:
#                 return JsonResponse({'error': 'Message cannot be empty.'}, status=400)

#             def stream_and_save_response():
#                 history_start_time = time.perf_counter()
#                 chat_history_objects = conversation.messages.order_by('timestamp').all()
#                 chat_history_for_agent = []
#                 user_msg_content = None
#                 for msg in chat_history_objects:
#                     if msg.sender == 'user':
#                         user_msg_content = msg.content
#                     elif msg.sender == 'assistant' and user_msg_content:
#                         chat_history_for_agent.append({'user': user_msg_content, 'assistant': msg.content})
#                         user_msg_content = None
#                 history_end_time = time.perf_counter()
#                 print(f"\n>>> History Prep took: {history_end_time - history_start_time:.4f} seconds.")

#                 full_response = []
#                 first_chunk_received = False
                
#                 stream_start_time = time.perf_counter()
#                 print(">>> Invoking agent stream...")

#                 for chunk in assistant_service.stream(user_message, chat_history_for_agent):
#                     if not first_chunk_received:
#                         first_chunk_time = time.perf_counter()
#                         print(f">>> LLM Time to First Token (Thinking Time) took: {first_chunk_time - stream_start_time:.4f} seconds.")
#                         first_chunk_received = True
                    
#                     full_response.append(chunk)
#                     yield chunk
                
#                 stream_end_time = time.perf_counter()
#                 if first_chunk_received:
#                     print(f">>> Full Response Streaming took: {stream_end_time - first_chunk_time:.4f} seconds.")

#                 save_start_time = time.perf_counter()
#                 final_text = "".join(full_response)
#                 ChatMessage.objects.create(conversation=conversation, sender='user', content=user_message)
#                 ChatMessage.objects.create(conversation=conversation, sender='assistant', content=final_text)

#                 if conversation.messages.count() <= 2 and len(user_message) > 5:
#                     conversation.title = user_message[:50]
#                     conversation.save()
                
#                 save_end_time = time.perf_counter()
#                 print(f">>> DB Save took: {save_end_time - save_start_time:.4f} seconds.")
                
#                 total_time = time.perf_counter() - request_start_time
#                 print(f">>> Total request-to-response time: {total_time:.4f} seconds.\n")

#             return StreamingHttpResponse(stream_and_save_response(), content_type="text/event-stream")

#         except Exception as e:
#             print(f"!!! FATAL ERROR in chat_view (streaming): {str(e)}")
#             return StreamingHttpResponse("An unexpected error occurred on the server.", status=500, content_type="text/plain")
    
#     user_conversations = Conversation.objects.filter(user=request.user).order_by('-created_at')
#     current_chat_messages = conversation.messages.order_by('timestamp').all()
#     context = {
#         'user_conversations': user_conversations,
#         'active_conversation_id': str(conversation.id),
#         'current_chat_messages': current_chat_messages
#     }
#     return render(request, 'ai_assistant/chat.html', context)

# @login_required
# def new_chat_view(request, is_redirect=True):
#     if 'active_conversation_id' in request.session:
#         del request.session['active_conversation_id']
#         print("--- Active conversation cleared. Starting a new one. ---")
#     if is_redirect:
#         return redirect(reverse('ai_assistant:chat_view'))
#     else:
#         return get_or_create_conversation(request)

# @login_required
# def delete_chat_view(request, conversation_id):
#     conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
#     if request.method == 'POST':
#         deleted_id = str(conversation.id)
#         conversation.delete()
#         if request.session.get('active_conversation_id') == deleted_id:
#             del request.session['active_conversation_id']
#         print(f"--- Conversation {deleted_id} deleted successfully. ---")
#         return redirect(reverse('ai_assistant:chat_view'))
#     return redirect(request.META.get('HTTP_REFERER', reverse('ai_assistant:chat_view')))