# apps/ai_assistant/apps.py

# class AiAssistantConfig(AppConfig):
#     default_auto_field = "django.db.models.BigAutoField"
#     name = "apps.ai_assistant"
from django.apps import AppConfig
import os
from django.apps import AppConfig

class AiAssistantConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ai_assistant'

    def ready(self):
        """
        This method is called when the Django application is ready.
        We load our heavy models here. By removing the 'RUN_MAIN' check,
        we ensure the models are always loaded in the active process.
        """
        from .services import global_services
        from .services.retriever import HybridRetriever
        
        # We only instantiate if it hasn't been done already
        # to prevent issues if ready() is called multiple times.
        if global_services.hybrid_retriever is None:
            global_services.hybrid_retriever = HybridRetriever()
