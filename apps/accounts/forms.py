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