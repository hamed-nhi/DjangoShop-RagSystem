from django.db import models
from email.mime import image


from ...utils import FileUpload

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


    def __self__(self):
        return self.group_title

    class Meta:
        verbose_name= 'گروه کالا'
        verbose_name_plural='گروه های کالا'