# ai_assistant/urls.py

from django.urls import path
from . import views

# This is used to namespace the URLs of this app
app_name = 'ai_assistant'

urlpatterns = [
    # This maps the URL '/chat/' to our chat_view function
    path('chat/', views.chat_view, name='chat_view'),
    path('chat/<uuid:conversation_id>/', views.chat_view, name='chat_view_conversation'),
    path('new-chat/', views.new_chat_view, name='new_chat_view'),
    path('delete-chat/<uuid:conversation_id>/', views.delete_chat_view, name='delete_chat_view'),
    path('api/get_product_details/', views.get_product_details_api, name='get_product_details_api'),
    path('ai-compare/', views.ai_compare_view, name='ai_compare_view'),


]   