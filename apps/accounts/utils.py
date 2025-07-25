import random
import os  # <--- ۱. این خط را اضافه کنید

from kavenegar import KavenegarAPI, APIException, HTTPException

def create_random_code(length=5):
    """
    یک کد عددی تصادفی برای فعال‌سازی ایجاد می‌کند.
    """
    return ''.join(random.choices('0123456789', k=length))



def send_sms(receptor, message):
    """
    این تابع با استفاده از API کاوه‌نگار یک پیامک ارسال می‌کند
    و تمام جزئیات و خطاها را در ترمینال چاپ می‌کند.
    """
    # ۲. کلید API از فایل .env خوانده می‌شود
    api_key = os.environ.get('KAVENEGAR_API_KEY')

    # یک بررسی کوچک برای اطمینان از وجود کلید
    if not api_key:
        print("!!! KAVENEGAR API KEY not found in environment variables.")
        return None

    params = {
        'sender': '2000660110',
        'receptor': receptor,
        'message': message,
    }

    print("--- Kavenegar Debug ---")
    print(f"Attempting to send SMS with params: {params}")

    try:
        api = KavenegarAPI(api_key)
        response = api.sms_send(params)
        
        print(f"Kavenegar API Response: {response}")

        # ... (بقیه کد شما بدون تغییر باقی می‌ماند) ...
        if response and response[0]['status'] in [1, 2, 3, 4, 5, 6, 10, 11]:
            print(">>> SMS sent successfully!")
        else:
            print(f">>> SMS FAILED! Status: {response[0]['status']}, Status Text: {response[0]['statustext']}")

        print("-----------------------")
        return response

    except APIException as e: 
        print(f"!!! KAVENEGAR API ERROR: {e}")
        print("-----------------------")
        return None
        
    except HTTPException as e:
        print(f"!!! KAVENEGAR HTTP ERROR (Connection Problem): {e}")
        print("-----------------------")
        return None

    except Exception as e:
        print(f"!!! UNKNOWN ERROR during SMS send: {e}")
        print("-----------------------")
        return None
    
    
    
class FileUpload:
    def __init__(self,dir,prefix):
        self.dir = dir
        self.prefix=prefix

    def upload_to(self,instance,filename):
        filename, ext = os.path.splitext(filename)
        return f'{self.dir}/{self.prefix}/{uuid4()}{ext}'


