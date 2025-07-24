import math
from django.db import models
from email.mime import image
from django.utils import timezone
from utils import FileUpload
# from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
# from django.core.urlresolvers import reverse 
from django.urls import reverse



def upload_brand_image(instance,filename):
    return f'images/brand/{filename}'


class Brand(models.Model):
    brand_title = models.CharField(max_length=100, verbose_name='نام برند')
    file_upload = FileUpload('images','brand')
    image_name=models.ImageField(upload_to=file_upload.upload_to,verbose_name='تصویر برند کالا')
    slug = models.SlugField(max_length=200,null=True)

    def __str__(self):
        return self.brand_title
    
    class Meta:
        verbose_name = 'برند'
        verbose_name_plural='برند ها'

#---------------------------------------------------------------------------


def upload_product_group_image(instance,filename):
    return f'images/product_group/{filename}'

class ProductGroup(models.Model):
    group_title = models.CharField(max_length=100, verbose_name="عنوان گروه کالا")
    file_upload = FileUpload('images','product_group')
    image_name=models.ImageField(upload_to=file_upload.upload_to,verbose_name='تصویر گروه کالا')
    description = models.TextField(blank=True,null=True,verbose_name='توضیحات گروه کالا')
    is_active=models.BooleanField(default=True,blank=True,verbose_name='وضعیت فعال/غیرفعال')
    group_parent=models.ForeignKey('ProductGroup',on_delete=models.CASCADE,verbose_name='والد گروه کالا',  blank=True, null=True, related_name="groups")                              
    slug = models.SlugField(max_length=200,null=True)
    register_date=models.DateTimeField(auto_now_add=True,verbose_name="تاریخ درج")
    published_date = models.DateTimeField(default=timezone.now,verbose_name='تاریخ انتشار')
    update_date=models.DateTimeField(auto_now=True,verbose_name='تاریخ آخرین بروز رسانی')


    def __str__(self):
        return self.group_title

    class Meta:
        verbose_name= 'گروه کالا'
        verbose_name_plural='گروه های کالا'
        
        
        
#--------------------------------------------------------------
class Feature(models.Model):
    feature_name = models.CharField (max_length=200,verbose_name='نام ویژگی')
    product_group =models.ManyToManyField(ProductGroup,verbose_name='گروه کالا',related_name='features_of_groups')
    
    def __str__(self):
        return self.feature_name
    
    
    class Meta:
        verbose_name='ویژگی'
        verbose_name_plural = 'ویژگی ها'
        
#--------------------------------------------------------------
        
        
class Product(models.Model):
    product_name = models.CharField(max_length=550,verbose_name='نام کالا')
    # description = models.TextField(blank=True,null=True, verbose_name='توضیحات کالا')
    # description = RichTextUploadingField(blank=True,null=True, verbose_name='توضیحات کالا', config_name='special')
    summery_description=models.TextField(default="",null=True,blank=True)
    description = RichTextUploadingField(blank=True,null=True, verbose_name='توضیحات کالا', config_name='default')
    file_upload = FileUpload('images','product')
    image_name=models.ImageField(upload_to=file_upload.upload_to,verbose_name='تصویر کالا')
    price =models.PositiveIntegerField(default=0,verbose_name='قیمت کالا')
    #related_name هر وقت به یک کلید خارجی می دهیم یعنی عملا این فیلد ریلیتد گروپ رو میبریم اضافه میکنیم به خود مدل 
    #یعنی وقتی prodcut group میاد به product وصل بشه --> (این فیلد هم بهشون اضافه میشه(به گروه که میخواهد وصل بشه به گروه دیگه اضافه میشه))
    product_group=models.ManyToManyField(ProductGroup,verbose_name='گروه کالا',related_name='products_of_groups')
    brand= models.ForeignKey(Brand,verbose_name='برند کالا',on_delete=models.CASCADE,null=True,related_name='product_of_brands')
    is_active=models.BooleanField(default=True,blank=True,verbose_name='وضعیت فعال/غیرفعال')
    slug = models.SlugField(max_length=200,null=True)
    register_date=models.DateTimeField(auto_now_add=True,verbose_name="تاریخ درج")
    published_date = models.DateTimeField(default=timezone.now,verbose_name='تاریخ انتشار')
    update_date=models.DateTimeField(auto_now=True,verbose_name='تاریخ آخرین بروز رسانی')
    features = models.ManyToManyField(Feature,through='ProductFeature') # توضیحات در بالای مدل ProductFeature



    def __str__(self):
        return self.product_name
    
    
    # @property
    # def charm_price(self):
    #     if self.price < 100000:
    #         return math.floor(self.price / 1000) * 1000
    #     return math.floor(self.price / 10000) * 10000
    @property
    def charm_price(self):
        if self.price < 100000:
            rounded_up = math.ceil(self.price / 10000) * 10000
            return rounded_up - 100
        else:
            rounded_up = math.ceil(self.price / 100000) * 100000
            return rounded_up - 1000
    
    #new Fun after setting Fetch Data{برای هر محصول یک ضفحه مجزا میخواهیم ست کنیم که نیاز داریم slug  رو اینجا یکاری باهاش بکنیم}
    #هر زمان مدلی بود که نیاز داشتید مدام به اون دسترسی پیدا کنید  توضیح میشه که همچین تابعی برایش بنویسم
    ###############################################
    def get_absolute_url(self):
        return reverse('products:product_details', kwargs={'slug': self.slug})
    
    
    
    ###############################################
    
    class Meta:
        verbose_name='کالا'
        verbose_name_plural=' کالا ها'
 
 
 
#------------------------------------------------
class FeatureValue(models.Model):
    value_title = models.CharField(max_length=200,verbose_name='عنوان مقدار')
    feature = models.ForeignKey(Feature,on_delete=models.CASCADE,blank=True,null=True,verbose_name='ویژگی ', related_name='feature_values')
    
    
    def __str__(self):
        return f"{self.id} {self.value_title}"
    
    class Meta:
        verbose_name="مقدار ویژگی"
        verbose_name_plural='مقادیر ویژگی ها'
     
#--------------------------------------------------------------
# جدول که از حاصل ارتباط چند به چند بوجود میاید بصورت اتوماتیک 
# ولی در اینجا خودمان دستی ایجاد میکنیم چون میخواهیم در ان چیزی دیگری هم اضافه کنم

# ولی یک مشکلی که داریم چون این جدول بصورت اتوماتیک ایجاد نشده بعدا شناخته نخواهد شد برای همین یک فیلد به مدل #
#product  اضافه میکنیم
class ProductFeature(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,verbose_name='کالا', related_name='product_features')
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE,verbose_name='ویژگی')
    value = models.CharField(max_length=200,verbose_name='مقدار ویژگی کالا')
    #Or give the  '+'
    # filter_value = models.ForeignKey(FeatureValue,null=True,blank=True,on_delete=models.CASCADE,verbose_name='مقدار ویژگی برای فیلتر', related_name='product_features')
    filter_value =  models.ForeignKey(FeatureValue,null=True,blank=True,on_delete=models.CASCADE,verbose_name='مقدار ویژگی فیلتر',related_name='filter_feature_value')

    def __str__(self):
        return f"{self.product} - {self.feature}: {self.value}"
    
    class Meta:
        verbose_name='ویژگی محصول'
        verbose_name_plural='ویژگی های محصول'
    
#--------------------------------------------------------------
class ProductGallary(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE, verbose_name='کالا', related_name='gallery_images')
    file_upload = FileUpload('images','product_gallery')
    image_name=models.ImageField(upload_to=file_upload.upload_to,verbose_name='تصویر کالا')
    
    class Meta:
        verbose_name = 'تصویر'
        verbose_name_plural='تصاویر'
        
#--------------------------------------------------------------
        
