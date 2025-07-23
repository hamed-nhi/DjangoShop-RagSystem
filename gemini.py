from google.genai import types, Client

# تنظیم کلاینت برای استفاده از API گپ جی‌پی‌تی
client = Client(
    api_key='sk-oU6njwnq6PDQEGYEByAkNxKWC3ZxMGdKly48dqKsOthdyPBU',
    http_options=types.HttpOptions(base_url='https://api.gapgpt.app/')
)

# استفاده از مدل
response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents='can you assist me to buy Vivobook 15 A1504VA-NJ539 or Vivobook X1504VA-NJ816 i want ir for programing and network busines can you compare these?'
)

print(response.text)
