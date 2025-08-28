# apps/ai_assistant/services/__init__.py

import sys
import os
from .retriever import HybridRetriever

# نام اسکریپتی که در حال اجراست را پیدا می‌کنیم
script_name = os.path.basename(sys.argv[0])

# بررسی می‌کنیم که آیا سرور در حال اجراست
is_running_server = any(arg in ['runserver', 'gunicorn', 'uwsgi'] for arg in sys.argv)

# بررسی می‌کنیم که آیا اسکریپت تست ما در حال اجراست
is_running_test_script = (script_name == 'test_retriever.py')

# اگر یکی از دو شرط بالا برقرار بود، مدل‌ها را بارگذاری کن
if is_running_server or is_running_test_script:
    # این آبجکت فقط یک بار ساخته شده و در حافظه باقی می‌ماند
    hybrid_retriever = HybridRetriever()
else:
    hybrid_retriever = None