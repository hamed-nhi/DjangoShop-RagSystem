
import random
import os
from uuid import uuid4
from kavenegar import KavenegarAPI, APIException, HTTPException
import requests


# ----------------------------------------------------------------------------------

def create_random_code(length=5):
    return ''.join(random.choices('0123456789', k=length))


# ----------------------------------------------------------------------------------

# def send_sms(receptor, message):
#     api_key = os.environ.get('KAVENEGAR_API_KEY')

#     if not api_key:
#         print("!!! KAVENEGAR API KEY not found in environment variables.")
#         return None

#     params = {
#         'sender': '2000660110',
#         'receptor': receptor,
#         'message': message,
#     }

#     print("--- Kavenegar Debug ---")
#     print(f"Attempting to send SMS with params: {params}")

#     try:
#         api = KavenegarAPI(api_key)
#         response = api.sms_send(params)
        
#         print(f"Kavenegar API Response: {response}")

#         if response and response[0]['status'] in [1, 2, 3, 4, 5, 6, 10, 11]:
#             print(">>> SMS sent successfully!")
#         else:
#             print(f">>> SMS FAILED! Status: {response[0]['status']}, Status Text: {response[0]['statustext']}")

#         print("-----------------------")
#         return response

#     except APIException as e: 
#         print(f"!!! KAVENEGAR API ERROR: {e}")
#         print("-----------------------")
#         return None
        
#     except HTTPException as e:
#         print(f"!!! KAVENEGAR HTTP ERROR (Connection Problem): {e}")
#         print("-----------------------")
#         return None

#     except Exception as e:
#         print(f"!!! UNKNOWN ERROR during SMS send: {e}")
#         print("-----------------------")
#         return None
    
    
    

# ----------------------------------------------------------------------------------
def send_sms(receptor, message):
   
    api_url = os.environ.get('MELIPAYAMAK_API_URL')
    sender_number = os.environ.get('MELIPAYAMAK_SENDER')

    if not api_url or not sender_number:
        print("!!! MELIPAYAMAK_API_URL or MELIPAYAMAK_SENDER not found in environment variables.")
        return None

    data = {
        'from': sender_number,
        'to': receptor,
        'text': message,
    }

    print("--- MeliPayamak Debug ---")
    print(f"Attempting to send SMS to: {receptor}")

    try:
   
        response = requests.post(api_url, json=data, timeout=10)

        response.raise_for_status()

        response_data = response.json()
        print(f"MeliPayamak API Response: {response_data}")

        if 'recId' in response_data and response_data['recId'] > 0:
            print(">>> SMS sent successfully to the operator!")
        else:
            error_status = response_data.get('status', 'Unknown error')
            print(f">>> SMS FAILED! Status: {error_status}")

        print("-------------------------")
        return response_data

    except requests.exceptions.HTTPError as e:
        print(f"!!! MELIPAYAMAK HTTP ERROR: {e}")
        print(f"Response Body: {e.response.text}")
        print("-------------------------")
        return None

    except requests.exceptions.RequestException as e:
        print(f"!!! MELIPAYAMAK CONNECTION ERROR: {e}")
        print("-------------------------")
        return None

    except Exception as e:
        print(f"!!! UNKNOWN ERROR during SMS send: {e}")
        print("-------------------------")
        return None

# ----------------------------------------------------------------------------------



class FileUpload:
    def __init__(self,dir,prefix):
        self.dir = dir
        self.prefix=prefix

    def upload_to(self,instance,filename):
        filename, ext = os.path.splitext(filename)
        return f'{self.dir}/{self.prefix}/{uuid4()}{ext}'


