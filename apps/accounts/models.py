from django.db import models
from django.contrib.auth.models import AbstractUser,PermissionsMixin,BaseUserManager,UserManager
from django.utils import timezone 
from utils import FileUpload

class CustomUserManager(BaseUserManager):
    def create_user(self,mobile_number, email="",name="",family="",active_code=None,gender=None,password=None):
        if not mobile_number:
            raise ValueError("شماره موبایل را وراد کنید ")
        user = self.model(
            mobile_number=mobile_number,
            email=self.normalize_email(email),
            name=name,
            family=family,
            active_code=active_code,
            gender=gender,

        )
        user.set_password(password)
        user.save(using=self._db)
        return user


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
        user.is_superuser=True
        user.save(using=self._db)
        return user
# -------------------------------------------------------------------------------

class CustomUser(AbstractUser, PermissionsMixin):
    first_name = None
    last_name = None 
    username = None  
    mobile_number=models.CharField(max_length=11,unique=True, verbose_name='شماره موبایل')
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
    
    
    @property
    def is_staff(self):
        return self.is_admin
    
# -------------------------------------------------------------------------------

class Customer(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE,primary_key=True)
    phone_number = models.CharField(max_length=11,null=True,blank=True)
    address=models.TextField(null=True,blank=True)
    file_upload = FileUpload('images','customer')
    image_name= models.ImageField(upload_to=file_upload.upload_to,null=True,blank=True,verbose_name='تصویر ')
    
    def __str_(self):
        return f"{self.user}"