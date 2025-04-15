from django.db import models
from django.contrib.auth.models import AbstractUser,PermissionsMixin,BaseUserManager,UserManager
from django.utils import timezone 




#for managing the users
class CustomUserManager(BaseUserManager):

    def create_user(self,mobile_number, email="",name="",family="",active_code=None,gender=None,password=None):
        if not mobile_number:
            raise ValueError("شماره موبایل را وراد کنید ")
        #مدلی میسازیم که فقط فیلد های معمولی رو ذخیره کنیم و فیلد هایی مثل پسوورد رو نمیگیریم تا مستقیم وارد دیتا بیس نشن چون میخوایم هش گذاری کنیم
        user = self.model(
            mobile_number=mobile_number,
            email=self.normalize_email(email),
            name=name,
            family=family,
            active_code=active_code,
            gender=gender,

        )
        #برای هش کردن پسوورد
        user.set_password(password)
        user.save(using=self._db)
        return user

##### دوتا نکته مهم  1




# 1- هر وقت میخواهی پسورد ذخیره کنی از setpassword  استفاده کن


# 2- هر وقت میخواهی از ایمیل استفاده کنی از normalize_email  استفاده کن




# email="",name="",family="" اگه کاربر عادی صدا بازنه اینو خالی میفرسته ولی سوپر یوزر باشه باید پر بشه 
#چرا چون میخواهیم فرم هایی که جلوی کاربر گذاشته میشه زیاد شلوغ نباشه
  
  
    def create_superuser(self,mobile_number, email,name,family,password=None,active_code=None,gender=None):
        user= self.create_user(

            mobile_number=mobile_number,
            email=email,
            name=name,
            family=family,
            active_code=active_code,
            gender=gender,
            password=password,
        )
        user.is_active=True
        user.is_admin=True
        user.save(using=self._db)
        return user

# self یک اشاره‌گر (pointer) به خود شیء است.
# از طریق self می‌توانیم به متغیرها و توابع داخل شیء دسترسی پیدا کنیم.




# برای این که بتوانیم ارث بری کنیم باید در پارامتر های کلا یا  تابع استفاده شود 
class CustomUser(AbstractUser, PermissionsMixin):
    first_name = None
    last_name = None
    username = None  # Remove the username field #Its not in mehdi abbasi code
    mobile_number=models.CharField(max_length=11,unique=True)
    email=models.EmailField(max_length=100,blank=False)
    name = models.CharField(max_length=100,blank=True)
    family= models.CharField(max_length=100,blank=True)
    GENDER_CHOICES=(('True','مرد'),('False','زن'))
    gender= models.CharField(max_length=50,choices=GENDER_CHOICES,default=True,null=True,blank=True)
    register_date= models.DateField(default=timezone.now)
    is_active=models.BooleanField(default=False)
    active_code = models.CharField(max_length=100,null=True,blank=True)
    is_admin = models.BooleanField(default=False)


    FIRSTNAME_FIELD='name'
    USERNAME_FIELD = 'mobile_number'
    REQUIRED_FIELDS = ['email','name','family']

    objects =CustomUserManager()

    def __str__(self):
        return self.name +" "+self.family
    


    #این دو تابع برای اینه که ما هیچ محدودیتی از نظر سطح دسترسی نداریم
    def has_perms(self, perm_list, obj=None):
        """
        Return True if the user has each of the specified permissions. If
        object is passed, check if the user has all required perms for it.
        """
        return True
    
    def has_module_perms(self, app_label):
        """
        Return True if the user has any permissions in the given app label.
        Use similar logic as has_perm(), above.
        """
        return True
    # ادمین بودن و نبودن رو چک میکنه 
    @property
    def is_staff(self):
        return self.is_admin