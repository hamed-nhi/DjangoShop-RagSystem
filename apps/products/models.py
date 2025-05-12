from django.db import models
from email.mime import image
from django.utils import timezone
from utils import FileUpload
# from ...utils import FileUpload

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
    group_parent=models.ForeignKey('ProductGroup',
                                   on_delete=models.CASCADE,
                                   verbose_name='والد گروه کالا',
                                    blank=True,
                                    null=True,
                                    related_name="groups",
                                    )
    slug = models.SlugField(max_length=200,null=True)
    register_date=models.DateTimeField(auto_now_add=True,verbose_name="تاریخ درج")
    published_date = models.DateTimeField(default=timezone.now,verbose_name='تاریخ انتشار')
    update_date=models.DateTimeField(auto_now=True,verbose_name='تاریخ آخرین بروز رسانی')


    def __self__(self):
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
    description = models.TextField(blank=True,null=True, verbose_name='توضیحات کالا')
    file_upload = FileUpload('images','product')
    image_name=models.ImageField(upload_to=file_upload.upload_to,verbose_name='تصویر کالا')
    price =models.PositiveIntegerField(default=0,verbose_name='قیمت کالا')
    product_group=models.ManyToManyField(ProductGroup,verbose_name='گروه کالا',related_name='products_of_groups')
    brand= models.ForeignKey(Brand,verbose_name='برند کالا',on_delete=models.CASCADE,null=True,related_name='brands')
    is_active=models.BooleanField(default=True,blank=True,verbose_name='وضعیت فعال/غیرفعال')
    slug = models.SlugField(max_length=200,null=True)
    register_date=models.DateTimeField(auto_now_add=True,verbose_name="تاریخ درج")
    published_date = models.DateTimeField(default=timezone.now,verbose_name='تاریخ انتشار')
    update_date=models.DateTimeField(auto_now=True,verbose_name='تاریخ آخرین بروز رسانی')
    features = models.ManyToManyField(Feature,through='ProductFeature') # توضیحات در بالای مدل ProductFeature



    def __str__(self):
        return self.product_name
    
    
    class Meta:
        verbose_name='کالا'
        verbose_name_plural=' کالا ها'
    
#--------------------------------------------------------------

# جدول که از حاصل ارتباط چند به چند بوجود میاید بصورت اتوماتیک 
# ولی در اینجا خودمان دستی ایجاد میکنیم چون میخواهیم در ان چیزی دیگری هم اضافه کنم

# ولی یک مشکلی که داریم چون این جدول بصورت اتوماتیک ایجاد نشده بعدا شناخته نخواهد شد برای همین یک فیلد به مدل #
#product  اضافه میکنیم

class ProductFeature(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,verbose_name='کالا')
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE,verbose_name='ویژگی')
    value = models.CharField(max_length=200,verbose_name='مقدار ویژگی کالا')
        
    def __str__(self):
        return f"{self.product} - {self.feature} : {self.value}"
    
    class Meta:
        verbose_name='ویژگی محصول'
        verbose_name_plural='ویژگی های محصول'
    
    
#--------------------------------------------------------------


class ProductGallary(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE, verbose_name='کالا')
    file_upload = FileUpload('images','product_gallery')
    image_name=models.ImageField(upload_to=file_upload.upload_to,verbose_name='تصویر کالا')
    
    
    class Meta:
        verbose_name = 'تصویر'
        verbose_name_plural='تصاویر'