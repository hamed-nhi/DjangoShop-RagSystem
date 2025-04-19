from django.shortcuts import render ,redirect
from django.views import View
from .forms import RegisterUserForm,VerifyResgiterForm
from .models import CustomUser
import utils
from django.contrib import messages

class RegisterUserView(View):
    def get(self,request,*args,**kwargs):
        form = RegisterUserForm()
        return render(request,"accounts_app/register.html",{"form":form})
        #فرم رو میفرسته


    def post(self,request,*args,**kwargs):
        form =RegisterUserForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            active_code=utils.create_random_code(5)
        
            #دیتایی که کاربر وارد کرده از این طریق گرفته میشه 

            #پسووردی که میخواهی اینجا بگیری نیازی نیست اون رو هش کنی چرا کهدر خود فایل مدل اون رو هش کردیم
            # یعنی در فایل مدل  اومدیم قبل از ذخیره پسوورد اون رو هش میکنیم
            CustomUser.objects.create_user( #  برای ذخیره کردن  اطلاعاتی که کاربر درج کرده است
                mobile_number = data['mobile_number'],
                active_code=active_code,
                password= data['password1'],
            )
            utils.send_sms(data['mobile_number'],f'کد فعال سازی حساب شما {active_code} می باشد ')
            #یه سری اطلاعات را بصورت ارایه در سشن نگهداری میکنیم که در حین ثبت نام از انها استفاده کنیم
            request.ssesion['user_ssesion']={
                'active_code':str(active_code),
                'mobile_number':data['mobile_number']
            }
            messages.success(request,'اطلاعات شما ثبت شد و کد فعال سازی ارسال شد ','success')
            return redirect('accounts:verify')
        # if not valid 
        messages.error(request,'خطا در ثبت نام','error')


class VerifyResgiterCodeView():
    def get(self,request,*args, **kwargs):
        form = VerifyResgiterForm
        return render(request,"accounts_app/verify_register_code.html",{"form":form})
    
    def post(self,request,*args, **kwargs):
        form= VerifyResgiterForm(request.POST)
        if form.is_valid():
            data=form.cleaned_data
            #همان سشن که در حین ثبت نام ذخیره کردیم در این جا استفاده میکنیم
            user_ssesion=request.ssesion['user_ssesion']
            if data['active_code'] == user_ssesion['active_code']:
                #اگر اکتیو کد درست بودند انگاه میریم یوزر رو پیدا میکنیم
                user= CustomUser.objects.get(mobile_number=user_ssesion['mobile_number'])
                user.is_active =True
                user.save()
                messages.success(request,'ثبت نام با موفقیت انجام شد ','success')
