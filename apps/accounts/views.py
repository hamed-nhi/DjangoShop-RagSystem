from django.shortcuts import render ,redirect
from django.views import View
from .forms import RegisterUserForm,VerifyResgiterForm,LoginUserForm
from .models import CustomUser
import utils
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.mixins import LoginRequiredMixin




class RegisterUserView(View):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('main:index')
        return super().dispatch(request, *args, **kwargs)
    
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
            # utils.send_sms(data['mobile_number'],f'کد فعال سازی حساب شما {active_code')
            utils.send_sms(data['mobile_number'],f'کد فعال سازی حساب شما {active_code} می باشد ')
            #یه سری اطلاعات را بصورت ارایه در سشن نگهداری میکنیم که در حین ثبت نام از انها استفاده کنیم
            request.session['user_session']={
                'active_code':str(active_code),
                'mobile_number':data['mobile_number']
            }
            messages.success(request,'اطلاعات شما ثبت شد و کد فعال سازی ارسال شد ','success')
            return redirect('accounts:verify')
        # if not valid 
        messages.error(request,'خطا در ثبت نام','danger')
        return render(request, "accounts_app/register.html", {"form": form})

class VerifyResgiterCodeView(View):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('main:index')
        return super().dispatch(request, *args, **kwargs)
    

    def get(self,request,*args, **kwargs):
        form = VerifyResgiterForm
        return render(request,"accounts_app/verify_register_code.html",{"form":form})
    
    def post(self,request,*args, **kwargs):
        form= VerifyResgiterForm(request.POST)
        if form.is_valid():
            data=form.cleaned_data
            #همان سشن که در حین ثبت نام ذخیره کردیم در این جا استفاده میکنیم
            user_session=request.session['user_session']
            if data['active_code'] == user_session['active_code']:
                #اگر اکتیو کد درست بودند انگاه میریم یوزر رو پیدا میکنیم
                user= CustomUser.objects.get(mobile_number=user_session['mobile_number'])
                user.is_active =True
                user.active_code=utils.create_random_code(5)
                user.save()
                messages.success(request,'ثبت نام با موفقیت انجام شد ','success')
                return redirect('main:index')
            else:
                messages.error(request,'کد فعال سازی ارد شده اشتباه است','danger')
                return render(request,"accounts_app/verify_register_code.html",{"form":form})
        messages.error(request,'اطلاعات وارد شده نادرست است','danger')
        return render(request,'accounts_app/verify_register_code.html',{"form":form})


#||||||||||||||||||||||||||||||||||||||||||||||||||||||


class LoginUserView(View):
    url_temp_name = "accounts_app/login.html"

    #وقتی وارد شدی هر چقدر هم بخوای بری صفحه ورود دیگه برات نمیاره - کار این تابع همینه
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('main:index')
        return super().dispatch(request, *args, **kwargs)
#----------------------------------------------------------------------------------------------------
    def get(self,request,*args,**kwargs):
        form = LoginUserForm()
        return render(request,self.url_temp_name,{"form":form})
        #فرم رو میفرسته
#----------------------------------------------------------------------------------------------------
    def post(self,request,*args,**kwargs):
        form=LoginUserForm(request.POST) # پست یعنی اون چیزی که به سمت سرور ارسال شده 
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(username=data['mobile_number'],password=data['password'])
            if user is not None: #یعنی اگر کاربری وجود داشت 
                db_user = CustomUser.objects.get(mobile_number=data['mobile_number'])
                # if db_user.is_active==True:
                if db_user.is_admin==False:
                    messages.success(request,'ورود با موفقیت انجام شد ','success')   
                    login(request,user)
                    # حال از اون صحه ای که اومده به صفحه لاگین میخواهیم برش گردونیم
                    next_url = request.GET.get('next')
                    if next_url is not None:
                        #   یعنی از یک صفحه دیگری از سایت امده به بخش ورود
                        return redirect(next_url)
                    else:
                        return redirect('main:index')

                else:
                    messages.error(request,'کاربر ادمین نمیتواند از اینجا وارد شود','warning')   
                    return render(request,self.url_temp_name,{"form":form})
            else:
                messages.error(request,'اطلاعات وارد شده نادرست می باشد','danger')   
                return render(request,self.url_temp_name,{"form":form})
        else:
            messages.error(request,'اطلاعات وارد شده نامعتبر است','danger')   
            return render(request,self.url_temp_name,{"form":form})
#----------------------------------------------------------------------------------------------------



#|||||||||||||||||||||||||||||||||||||||||||||\
class LogoutUserView(View):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('main:index')
        return super().dispatch(request, *args, **kwargs)
    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect('main:index')
        #فرم رو میفرسته



#|||||||||||||||||||||||||||||||||||||||||||||\
class UserPanelView(LoginRequiredMixin,View):
    url_temp_name = "accounts_app/userpanel.html"
    def get(self,request,*args, **kwargs):
        return render(request,self.url_temp_name)