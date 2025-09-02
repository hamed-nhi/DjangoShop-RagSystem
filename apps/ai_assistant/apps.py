# apps/ai_assistant/apps.py
from django.apps import AppConfig
import os

class AiAssistantConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ai_assistant'

    def ready(self):
        """
        این متد زمانی فراخوانی می‌شود که جنگو آماده است.
        ما مدل‌های سنگین را فقط زمانی بارگذاری می‌کنیم که سرور اصلی در حال اجرا باشد
        تا از بارگذاری غیرضروری در فرآیند Reloader جلوگیری کنیم.
        """
        # این شرط چک می‌کند که آیا کد در فرآیند اصلی سرور اجرا می‌شود یا خیر
        # در محیط پروداکشن (مانند Gunicorn) این متغیر وجود ندارد و کد همیشه اجرا می‌شود.
        if os.environ.get('RUN_MAIN') or os.environ.get("WERKZEUG_RUN_MAIN"):
            
            from .services import global_services
            from .services.retriever import HybridRetriever
            
            # این شرط از بارگذاری مجدد مدل‌ها در صورت فراخوانی چندباره ready() جلوگیری می‌کند.
            if global_services.hybrid_retriever is None:
                print("--- Loading AI models for the main server process... ---")
                global_services.hybrid_retriever = HybridRetriever()
                print("--- AI models loaded successfully. ---")






























# # class AiAssistantConfig(AppConfig):
# #     default_auto_field = "django.db.models.BigAutoField"
# #     name = "apps.ai_assistant"
# from django.apps import AppConfig
# import os
# from django.apps import AppConfig

# class AiAssistantConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'apps.ai_assistant'

#     def ready(self):
#         """
#         This method is called when the Django application is ready.
#         We load our heavy models here. By removing the 'RUN_MAIN' check,
#         we ensure the models are always loaded in the active process.
#         """
#         from .services import global_services
#         from .services.retriever import HybridRetriever
        
#         # We only instantiate if it hasn't been done already
#         # to prevent issues if ready() is called multiple times.
#         if global_services.hybrid_retriever is None:
#             global_services.hybrid_retriever = HybridRetriever()
