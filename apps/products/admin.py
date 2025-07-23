from django.contrib import admin
from .models import Brand, FeatureValue,ProductGroup,Product,ProductFeature,Feature,ProductGallary
from django.db.models.aggregates import Count
from django.http import HttpResponse
from django.core import serializers
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter, ChoiceDropdownFilter
from django.db.models import Q
from django.contrib.admin import SimpleListFilter
from admin_decorators import (short_description, order_field, )
#----------------------------------------------------------------
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('brand_title','slug',)
    list_filter = ('brand_title',)
    search_fields = ('brand_title',)
    ordering = ('brand_title',)
#----------------------------------------------------------------
#====================================================================
# اکشن نویسی برای ProductGroup
def de_active_product_group(modeladmin,request,queryset):
    res=queryset.update(is_active=False)    
    message=f'تعداد گروه{res} کالا غیر فعال شد'
    modeladmin.message_user(request,message)

def active_product_group(modeladmin,request,queryset):
    res=queryset.update(is_active=True)    
    message=f' تعداد گروه{res} کالا  فعال شد'
    modeladmin.message_user(request,message)
    
def export_json(modeladmin,request,queryset):
    response = HttpResponse(content_type='application/json')
    serializers.serialize("json",queryset, stream=response)
    return response    
#====================================================================
#----------------------------------------------------------------
class ProductGroupInstanceInlineAdmin(admin.TabularInline):
    model=ProductGroup
    extra=1
    # زمانی میتونیم این کار رو انجام بدیم که کلیدخارجی وجود داشته باشه
#----------------------------------------------------------------
#یک فیلتر خاص برای خودمان برای پنل ادمین طراحی میکنیم که از پیش فرض های خود جنگو که همان فیلتر باکس سمت راست  استفاده نکنیم
#در واقع میخواهیم والد ها را بیاوریم و ان ها فقط نشان داده شوند 
class GroupFilter(SimpleListFilter):
    title='گروه محصولات'
    #حparameter_name در واقع همانی است که در url میاید
    parameter_name='group'
    #تابع جسجتو که خودمان دوباره نویسی کردیم
    def lookups(self, request, model_admin):
        sub_groups=ProductGroup.objects.filter(~Q(group_parent=None))
        groups= set([item.group_parent for item in sub_groups])
        return [(item.id, item.group_title) for item in groups] # خروجی در واقع انهایی که فرزند سطح اخر نیستند به ما برگردانده میشود 
      
    # به مقادیر انها اساره میکنه
    def queryset(self, request, queryset):
        if self.value() != None:
            return queryset.filter(Q(group_parent =self.value()))
        return queryset




#----------------------------------------------------------------
@admin.register(ProductGroup)
class ProductGroupAdmin(admin.ModelAdmin):
    list_display = ('group_title', 'is_active', 'parent_title', 'slug', 'register_date', 'update_date','count_sub_group','count_product_of_group')  # Changed 'group_parent' to 'parent_title'
    # list_filter = ('group_title', ('group_parent',DropdownFilter),)
    #استفاده از فیلتر سفارسی مه خودمان  ساختیم
    list_filter = (GroupFilter,'is_active',)
    search_fields = ('group_title',)
    ordering = ('group_parent', 'group_title',)
    actions =[de_active_product_group,active_product_group,export_json, ]
    inlines = [ProductGroupInstanceInlineAdmin]
    list_editable =['is_active']
    #--------------
    #َAdded From Gpt 
    def parent_title(self, obj):
        return obj.group_parent.group_title if obj.group_parent else 'گروه اصلی '  # Display 'No Parent' if group_parent is None
    parent_title.short_description = 'والد گروه کالا'  # Set the column header in Persian
    #--------------
    
    def get_queryset(self, *args, **kwargs):
        qs= super(ProductGroupAdmin,self).get_queryset(*args, **kwargs)
        # یک ستون اضافه کردیم
        qs= qs.annotate(sub_group=Count('groups')) # We use related name of group_parent of ProductGroup model
        qs =qs.annotate(product_of_group = Count('products_of_groups'))
        return qs
    
    
    @short_description('تعداد زیرگروه ها') 
    @order_field('sub_group') #مرتب سازی 
    def count_sub_group(self,obj):
        return obj.sub_group
    
    @short_description('تعداد کالا های گروه') 
    @order_field('product_of_group') #مرتب سازی 
     
    def count_product_of_group(self,obj):
        return obj.product_of_group
    
    
    
    
    count_sub_group.short_description='تعداد زیر گروه ها'       
    de_active_product_group.short_description='غیرفعال کردن گروه های انتخاب شده'
    active_product_group.short_description='فعال کردن گروه های انتخاب شده'
    export_json.short_description='خروجی json از گروه های انتخاب شده'
#----------------------------------------------------------------
# اکشن نویسی برای Product
def de_active_product(modeladmin,request,queryset):
    res=queryset.update(is_active=False)    
    message=f' تعداد {res} کالا غیر فعال شد'
    modeladmin.message_user(request,message)

def active_product(modeladmin,request,queryset):
    res=queryset.update(is_active=True)    
    message=f' تعداد {res} کالا  فعال شد'
    modeladmin.message_user(request,message)
    
#=========================================================
class ProductFeatureInline(admin.TabularInline):
        model = ProductFeature
        extra= 22
        
        class Media:
            css ={
                'all':('css/admin_style.css',)
            }
            js= (
                'https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js',
                'js/admin_script.js',
            )
#=========================================================
class ProductGallaryInline(admin.TabularInline):
    model = ProductGallary
    extra=3
#=========================================================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name','display_product_groups','price','brand','is_active','update_date','slug', )
    list_filter = (('brand__brand_title',DropdownFilter),('product_group__group_title',DropdownFilter),)
    search_fields = ('product_name',)   
    ordering = ('update_date','product_name',)
    actions =[de_active_product,active_product]
    inlines=[ProductFeatureInline,ProductGallaryInline ]
    list_editable =['is_active']

    de_active_product.short_description='غیرفعال کردن  کالاهای انتخاب شده'
    active_product.short_description='فعال کردن  کالاهای انتخاب شده'
    
    def display_product_groups(self,obj):
        return ', '.join([group.group_title for group in obj.product_group.all()]) #تمام گروه هایی که کالای مد نظر داره 
   
    display_product_groups.short_description='گروه های کالا'
    

    #این تابع وجود دارد و ما اون رو دوباره نویسی کردیم برای خودمان 
    def formfield_for_manytomany(self,db_field,request,**kwargs):
        if db_field.name == 'product_group':
            kwargs["queryset"]=ProductGroup.objects.filter(~Q(group_parent=None)) #عملا ما نمیخواهیم گروه های اصلی در باکس برگردانده شوند 
        return super().formfield_for_manytomany(db_field ,request, **kwargs)
    
    fieldsets = (
        ('اطلاعات محصول', {
            "fields": (
                'product_name',
                'image_name',
                'price',
                ('product_group','brand','is_active',),
                'summery_description',
                'description',
                'slug')}),
        ('تاریخ و زمان', {'fields':(
            ('published_date',),
        )})
               
    )
    
#--------------------------------------------------------------
class FeatureValueInLine(admin.TabularInline):
    model=FeatureValue
    extra=3
    
    
@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display=('feature_name','display_groups','display_feature_values')
    list_filter=('feature_name',)
    search_fields=('feature_name',)
    ordering=['feature_name',]
    inlines=[FeatureValueInLine,]
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "product_group":
            kwargs["queryset"] = ProductGroup.objects.filter(~Q(group_parent=None))
        return super().formfield_for_manytomany(db_field, request, **kwargs)
    
    def display_groups(self,obj):
        return ', '.join([group.group_title for group in obj.product_group.all()])
    
    
    def display_feature_values(self,obj):
        return ', '.join([feature_value.value_title for feature_value in obj.feature_values.all()])
    
    display_groups.short_description='گروه های دارای این ویژگی'
    display_feature_values.short_description='مقادیر ممکن برای این وِیژگی'
    
    
#--------------------------------------------------------------
@admin.register(FeatureValue)
class FeatureValueAdmin(admin.ModelAdmin):
    list_display=('value_title','feature',  )
    
    fieldsets = (
        (None, {
            "fields": (
                'feature',
                'value_title',
            ),
        }),
    )
    