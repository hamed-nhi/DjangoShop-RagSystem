from django.contrib import admin
from .models import Brand,ProductGroup
from django.db.models.aggregates import Count
from django.http import HttpResponse
from django.core import serializers
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter, ChoiceDropdownFilter

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
    message=f' تعداد {res} کالا غیر فعال شد'
    modeladmin.message_user(request,message)

def active_product_group(modeladmin,request,queryset):
    res=queryset.update(is_active=True)    
    message=f' تعداد {res} کالا  فعال شد'
    modeladmin.message_user(request,message)
    
def export_json(modeladmin,request,queryset):
    response = HttpResponse(content_type='application/json')
    serializers.serialize("json",queryset, stream=response)
    return response    
#====================================================================
#----------------------------------------------------------------
class ProductGroupInstanceInlineAdmin(admin.TabularInline):
    model=ProductGroup
    # زمانی میتونیم این کار رو انجام بدیم که کلیدخارجی وجود داشته باشه

# @admin.register(ProductGroup)
# class ProductGroupAdmin(admin.ModelAdmin):

#     list_display = ('group_title', 'is_active', 'parent_title', 'slug', 'register_date', 'update_date',)
#     list_display = ('group_title','is_active','group_parent','slug','register_date','update_date',)
#     list_filter = ('group_title','group_parent',)
#     search_fields = ('group_title',)
#     ordering = ('group_parent','group_title',)
#     inlines =[ProductGroupInstanceInlineAdmin]
    
#--------------------------------
@admin.register(ProductGroup)
class ProductGroupAdmin(admin.ModelAdmin):
    list_display = ('group_title', 'is_active', 'parent_title', 'slug', 'register_date', 'update_date','count_sub_group')  # Changed 'group_parent' to 'parent_title'
    list_filter = ('group_title', ('group_parent',DropdownFilter),)
    search_fields = ('group_title',)
    ordering = ('group_parent', 'group_title',)
    actions =[de_active_product_group,active_product_group,export_json, ]
    inlines = [ProductGroupInstanceInlineAdmin]
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
        return qs
        
    def count_sub_group(self,obj):
        return obj.sub_group
    
    count_sub_group.short_description='تعداد زیر گروه ها'       
    de_active_product_group.short_description='غیرفعال کردن گروه های انتخاب شده'
    active_product_group.short_description='فعال کردن گروه های انتخاب شده'
    export_json.short_description='خروجی json از گروه های انتخاب شده'
#----------------------------------------------------------------

