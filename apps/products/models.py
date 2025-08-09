import math
from django.db import models
from django.db.models import Sum, Avg, Value, Count
from django.db.models.functions import Coalesce
from email.mime import image
from django.utils import timezone
from utils import FileUpload
from ckeditor_uploader.fields import RichTextUploadingField
from django.urls import reverse
from datetime import datetime
from middlewares.middlewares import RequestMiddleware
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from .translations import FEATURE_NAME_TRANSLATIONS 
#--------------------------------------------------------------



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
    def get_display_name(self):
        return FEATURE_NAME_TRANSLATIONS.get(self.feature_name, self.feature_name)
    
    class Meta:
        verbose_name='ویژگی'
        verbose_name_plural = 'ویژگی ها'
        
#--------------------------------------------------------------
        
        
class Product(models.Model):
    product_name = models.CharField(max_length=550,verbose_name='نام کالا')
    summery_description=models.TextField(default="",null=True,blank=True)
    description = RichTextUploadingField(blank=True,null=True, verbose_name='توضیحات کالا', config_name='default')
    file_upload = FileUpload('images','product')
    image_name=models.ImageField(upload_to=file_upload.upload_to,verbose_name='تصویر کالا')
    price =models.PositiveIntegerField(default=0,verbose_name='قیمت کالا')
    product_group=models.ManyToManyField(ProductGroup,verbose_name='گروه کالا',related_name='products_of_groups')
    brand= models.ForeignKey(Brand,verbose_name='برند کالا',on_delete=models.CASCADE,null=True,related_name='product_of_brands')
    is_active=models.BooleanField(default=True,blank=True,verbose_name='وضعیت فعال/غیرفعال')
    slug = models.SlugField(max_length=200,null=True)
    register_date=models.DateTimeField(auto_now_add=True,verbose_name="تاریخ درج")
    published_date = models.DateTimeField(default=timezone.now,verbose_name='تاریخ انتشار')
    update_date=models.DateTimeField(auto_now=True,verbose_name='تاریخ آخرین بروز رسانی')
    features = models.ManyToManyField(Feature,through='ProductFeature') 

    base_rating = models.DecimalField(
        max_digits=3, decimal_places=2, 
        default=0.0, 
        verbose_name='امتیاز پایه'
    )
    base_rating_weight = models.PositiveIntegerField(
        default=0, 
        verbose_name='وزن امتیاز پایه'
    )


    # +++  field for search optimization +++
    search_vector = SearchVectorField(null=True, blank=True)
    


    
    def __str__(self):
        return self.product_name
    
    def get_absolute_url(self):
        return reverse('products:product_details', kwargs={'slug': self.slug})

    def get_price_by_discount(self):
        list1=[]

        for i in self.discount_basket_details2.all():
            if (i.discount_basket.is_active==True and
                i.discount_basket.start_date <= datetime.now() and 
                datetime.now() <= i.discount_basket.end_date):
                list1.append(i.discount_basket.discount)

        discount=0
        if (len(list1)>0):
            discount=max(list1)
        return self.price-(self.price*discount/100)
                
                
    def get_number_in_warehouse(self):
        sum1=self.warehouse_products.filter(warehouse_type_id=1).aggregate(Sum('qty'))
        sum2=self.warehouse_products.filter(warehouse_type_id=2).aggregate(Sum('qty')) 
        input=0
        if sum1['qty__sum'] !=None:
            input=sum1['qty__sum']
        output=0
        if sum2['qty__sum']!=None:
            output = sum2['qty__sum']
        return input-output
    
    @property
    def charm_price(self):
        if self.price < 100000:
            rounded_up = math.ceil(self.price / 10000) * 10000
            return rounded_up - 100
        else:
            rounded_up = math.ceil(self.price / 100000) * 100000
            return rounded_up - 1000

    
    # class Meta:
    #     verbose_name='کالا'
    #     verbose_name_plural=' کالا ها'

    

    def get_user_score(self):
        request = RequestMiddleware(get_response=None)
        request= request.thread_local.current_request
        score =0
        user_score=self.scoring_product.filter(scoring_user=request.user)
        if user_score.count() > 0:
            score = user_score[0].score_value
        return score
        

    # def get_average_score(self):
    #     avgScore = self.scoring_product.all().aggregate(Avg('score_value'))['score_value__avg']
    #     if avgScore == None:
    #         return 0
    #     else:
    #         return avgScore
    def get_average_score(self):
        """
        Calculates the weighted average score for the product with exactly 2 decimal places.
        """
        # Get the sum and count of scores from your site's users
        user_scores_data = self.scoring_product.aggregate(
            total_score=Sum('score_value'),
            vote_count=Count('id')
        )
        
        user_total_score = user_scores_data['total_score'] or 0
        user_vote_count = user_scores_data['vote_count'] or 0

        # Get the base rating and weight from the model
        base_score = self.base_rating * self.base_rating_weight
        base_votes = self.base_rating_weight

        # Calculate the weighted total score and total votes
        total_score = base_score + user_total_score
        total_votes = base_votes + user_vote_count

        # Avoid division by zero if there are no ratings at all
        if total_votes == 0:
            return 0.00  # Explicitly return with 2 decimal places

        # Calculate the final weighted average and format to 2 decimal places
        weighted_average = total_score / total_votes
        return float("{0:.2f}".format(weighted_average)) 


    def get_user_favorite(self):
        request = RequestMiddleware(get_response=None)
        request = request.thread_local.current_request
        flag = self.favorite_product.filter(favorite_user=request.user).exists()
        return flag
    
    
    def getMainProductGroup(self):
        return self.product_group.all()[0].id

    def save(self, *args, **kwargs):
        # This part is crucial for future products
        super().save(*args, **kwargs) 
        vector = (
            SearchVector('product_name', weight='A', config='simple') +
            SearchVector(Coalesce('brand__brand_title', Value('')), weight='B', config='simple') +
            SearchVector(Coalesce('summery_description', Value('')), weight='C', config='simple')
        )
        Product.objects.filter(pk=self.pk).update(search_vector=vector)



    class Meta:
        verbose_name = 'کالا'
        verbose_name_plural = 'کالا ها'
        indexes = [
            GinIndex(fields=['search_vector']),
        ]
    


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
        
