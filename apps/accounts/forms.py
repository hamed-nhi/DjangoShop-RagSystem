from django import forms
from django.forms import ModelForm, ValidationError
from .models import CustomUser
from django.contrib.auth.forms import ReadOnlyPasswordHashField
# for admin panel
class UserCreationForm(forms.ModelForm):
    password1=forms.CharField(label="Password",widget=forms.PasswordInput)
    password2=forms.CharField(label="Re-Password",widget=forms.PasswordInput)
   
   
    class Meta:
        model = CustomUser
        fields =['mobile_number','email','name','family','gender']
       

#-----------------------------------------------------------

    def clean_password2(self):
        pass1=self.cleaned_data['password1']
        pass2=self.cleaned_data['password2']
        if pass1 and pass2 and pass1 !=pass2:
            raise ValidationError('رمز عبور ها مغایرت دارند ')
        return pass2

#-----------------------------------------------------------

    def clean_mobile_number(self):
        mobile_number = self.cleaned_data.get('mobile_number')
        if CustomUser.objects.filter(mobile_number=mobile_number).exists():
            raise ValidationError("This mobile number is already in use.")
        return mobile_number
#-----------------------------------------------------------

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("This email is already in use.")
        return email

    # def save(self,commit=True):
    #     user = super().save(commit=False)
    #     user.set_password(self.changed_data['password1'])
    #     if commit:
    #         user.save()
    #     return user

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])  # Fixed typo here
        if commit:
            user.save()
        return user

#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(help_text='برای تغییر رمز روی این <a href="../password/">لینک </a> کلیک کنید',
)
    class Meta:
        model=CustomUser
        fields =['mobile_number','email','name','family','gender','is_active','is_admin','password']
# برای ثبت نام کاربران میباشد 

#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
class RegisterUserForm(ModelForm):
    password1=forms.CharField(label="رمز عبور",widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':' رمز عبور را وارد کنید'},))
    password2=forms.CharField(label="تکرار رمز عبور",widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':' تکرار رمز عبور را وارد کنید'},))
    class Meta:
        model=CustomUser
        #فقط این فیلد هارو نیاز داریم نیاز نیست همه شود بری بیاری
        # اگر این فیلد ست رو نذاریم همه اش رو میره میاره 
        fields=['mobile_number',] # i delete the password filed because its come with def (clean_password)
        widgets={
            'mobile_number':forms.TextInput(attrs={'class':'form-control','placeholder':'شماره موبایل را وارد کنید'},)
        }


#-----------------------------------------------------------
#         def clean_password2(self):
#             pass1=self.cleaned_data['password1']
#             pass2=self.cleaned_data['password2']
#             if pass1 and pass2 and pass1 !=pass2:
#                 raise ValidationError(' رمزهای عبور با هم مطابقت ندارند')
#             return pass2

# #-----------------------------------------------------------

#         def clean_mobile_number(self):
#             mobile_number = self.cleaned_data.get('mobile_number')
#             if CustomUser.objects.filter(mobile_number=mobile_number).exists():
#                 raise ValidationError("این شماره موبایل قبلاً ثبت‌نام شده است.")
#             return mobile_number
    def clean_password2(self):
        pass1 = self.cleaned_data.get('password1')
        pass2 = self.cleaned_data.get('password2')
        if pass1 and pass2 and pass1 != pass2:
            raise ValidationError('رمزهای عبور با هم مطابقت ندارند.')
        return pass2

    def clean_mobile_number(self):
        mobile_number = self.cleaned_data.get('mobile_number')
        # بررسی می‌کنیم که آیا شماره موبایل در دیتابیس وجود دارد
        if mobile_number and CustomUser.objects.filter(mobile_number=mobile_number).exists():
            # **پیام خطا را به فارسی تغییر می‌دهیم**
            raise ValidationError("این شماره موبایل قبلاً ثبت‌نام شده است.")
        return mobile_number

#-----------------------------------------------------------
class VerifyResgiterForm(forms.Form):
    active_code =forms.CharField(label="",
                                 error_messages={"required":"این فیلد نمیتواند خالی باشد"},
                                 widget=forms.TextInput(attrs={'class':'form-control','placeholder':' کد ارسال شده را وارد کنید'},)
       ) 
    
#-----------------------------------------------------------


class LoginUserForm(forms.Form):
    mobile_number=forms.CharField(label="شماره موبایل",
                                 error_messages={"required":"این فیلد نمیتواند خالی باشد"},
                                 widget=forms.TextInput(attrs={'class':'form-control','placeholder':'شماره موبایل را وارد کنید'},)
       )  
    password=forms.CharField(label="رمز عبور",
                                 error_messages={"required":"این فیلد نمیتواند خالی باشد"},
                                 widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'رمز عبور را وارد کنید'},)
       )  
    
#-----------------------------------------------------------

class ChangePasswordForm(forms.Form):
    password1=forms.CharField(label="رمز عبور",
                                error_messages={"required":"این فیلد نمیتواند خالی باشد"},
                                widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'رمز عبور را وارد کنید'},)
       )
    password2=forms.CharField(label="تکرار رمز عبور",
                                error_messages={"required":"این فیلد نمیتواند خالی باشد"},
                                widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'تکرار رمز عبور را وارد کنید'},)
       )
    
    def clean_password2(self):
        pass1=self.cleaned_data['password1']
        pass2=self.cleaned_data['password2']
        if pass1 and pass2 and pass1 !=pass2:
            raise ValidationError('رمز عبور ها مغایرت دارند ')
        return pass2
    
#-----------------------------------------------------------

class RememberPasswordForm(forms.Form):
    mobile_number=forms.CharField(label="شماره موبایل ",
                                error_messages={"required":"این فیلد نمیتواند خالی باشد"},
                                widget=forms.TextInput(attrs={'class':'form-control','placeholder':' شماره موبایل خود را وارد کنید'},)
       )
#-----------------------------------------------------------


class UpdateProfileForm(forms.Form):
    mobile_number=forms.CharField(label="",
                                  widget=forms.TextInput(attrs={'class':'form-control','placeholder':'شماره تلفن را وارد کنید','readonly':'readonly'}))
    name=forms.CharField(label="",
                                error_messages={'required':'این فیلد نمیتواند خالی باشد'},
                                  widget=forms.TextInput(attrs={'class':'form-control','placeholder':'نام خود را وارد کنید'}))
    family=forms.CharField(label="",
                                error_messages={'required':'این فیلد نمیتواند خالی باشد'},
                                  widget=forms.TextInput(attrs={'class':'form-control','placeholder':'نام خانوادگی خود را وارد کنید'}))
    email=forms.CharField(label="",
                                error_messages={'required':'این فیلد نمیتواند خالی باشد'},
                                  widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'ایمیل خود را وارد کنید'}))
    phone_number=forms.CharField(label="",
                                error_messages={'required':'این فیلد نمیتواند خالی باشد'},
                                  widget=forms.TextInput(attrs={'class':'form-control','placeholder':'شماره تلفن را وارد کنید'}))                              
    address=forms.CharField(label="",
                                error_messages={'required':'این فیلد نمیتواند خالی باشد'},
                                  widget=forms.Textarea(attrs={'class':'form-control','placeholder':'آدرس خود را وارد کنید'}))
    
    image=forms.ImageField(required=False)
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            max_size = 5 * 1024 * 1024
            if image.size > max_size:
                raise ValidationError('حجم تصویر نباید بیشتر از 5 مگابایت باشد.')
            allowed_types = ['image/jpeg', 'image/png']
            if image.content_type not in allowed_types:
                raise ValidationError('فقط فایل‌های JPEG و PNG مجاز هستند.')
        return image