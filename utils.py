from kavenegar import *
#فایل هایی که تقریبا همیشه مورد نیازمونه رو تو اینجا نگهداری میکنه
#  و هر جایی خواستیم ازشون استفاده کنیم از اینجا برمیداریم

# for 5 digit 10000 to 99999
def create_random_code(count):
    import random #چون جای دیگری مصرفی نداره همین جا استفاده ش کردیم
    count-=1
    return random.randint(10**count,10**(count+1)-1)


# ارسال اس ام اس رو پیاده میکنیم چون در امثر جا ها نیاز داریم بهتره اینجا بنویسم و بعدا در جای دیگری استفاده کنیم
 
def send_sms(mobile_number,message):
    try:   
        api = KavenegarAPI('746166595063714E6F4334744766466A69336D6372735952384C6254564E46326B764F6D384E646A6A33593D')
        params = { 'sender' : '2000660110', 'receptor': 'mobile_number', 'message' :'message' }
        response = api.sms_send(params)
        return response
    except APIException as error:
        print(f'error1:{error}')
    except HTTPException as error:
        print(f'error2:{error}')

