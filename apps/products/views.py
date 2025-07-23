# from django.shortcuts import render,get_object_or_404
# from .models import Product,ProductGroup
# from django.db.models import Q,Count
# from django.views import View


# def get_root_group():
#     return ProductGroup.objects.filter(Q(is_active=True)& Q(group_parent=None)) # سرگروه هارو برمیکردونه

# def get_cheap_products(request,*args,**kwargs):
#     products= Product.objects.filter(is_active=True).order_by('price')[:4]
#     product_groups=  get_root_group()
    
#     context= {
#     'products': products,
#     'product_groups': product_groups  # جمع! نه مفرد!
#     }
#     return render(request,"product_app/partials/cheap_products.html",context)

# def get_last_products(request,*args,**kwargs):
#     products= Product.objects.filter(is_active=True).order_by('-published_date')[:4]
#     product_groups= get_root_group()
    
#     context= {
#     'products': products,
#     'product_groups': product_groups  # جمع! نه مفرد!
#     }
#     return render(request,"product_app/partials/last_products.html",context)

# def get_popular_product_groups(request,*args,**kwargs):
#     product_groups=ProductGroup.objects.filter(Q(is_active=True)).annotate(count=Count('products_of_groups')).order_by('-count')[:3]
#     context={
#         'product_groups':product_groups
#     }
#     return render(request,"product_app/partials/popular_product_groups.html",context)

# #Details of Products
# class ProductDeatailView(View):
#     def get(self,request,slug):
#         product=get_object_or_404(Product,slug=slug)
#         if product.is_active:
#             return render(request,"product_app/product_detail.html",{'product':product})
 
 
# #این رو باید بگونه ای تغییر بدیم که لپتاپ ها مشابه تو اون رنج قیمت نشون داده بشن        
# #محصولات مرتبط
# def get_related_products(request,*args, **kwargs):
#     current_product=get_object_or_404(Product,slug=kwargs['slug'])
#     related_products=[]
#     for group in current_product.product_group.all():
#         related_products.extend(Product.objects.filter(Q(is_active=True) & Q(product_group=group) & ~Q(id=current_product.id))[:5]) 
#     return render(request,"product_app/partials/related_products.html",{'related_products':related_products})
    
# # این رو باید بگونه تغییر بدیم که گروه تبدیل به برند بشه   
# #لیست  کلیه گروه های محصولات 
# class ProductGroupsView(View):
#     def get(self,request):
#         product_groups=ProductGroup.objects.filter(Q(is_active=True)).annotate(count=Count('products_of_groups')).order_by('-count')
#         return render (request,"product_app/product_groups.html",{'product_groups':product_groups})
    
    
    
    
# # این رو باید بگونه تغییر بدیم که گروه تبدیل به برند بشه       
# #لیست  محصولات هر گروه محصولات
# class ProductsByGroupView(View):
#     def get(self,request,*args, **kwargs):
#         current_group=get_object_or_404(ProductGroup,slug=kwargs['slug'])
#         products = Product.objects.filter(Q(is_active=True) & Q(product_group=current_group))
#         return render (request,"product_app/products.html",{'products':products,'current_group':current_group })
    
    
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from .models import FeatureValue, Product, ProductGroup, Brand
from django.db.models import Q, Count
from django.views import View

#====================================================
# دیکشنری‌های ترجمه برای مشخصات فنی محصول
#====================================================
FEATURE_NAME_TRANSLATIONS = {
    'Rating': 'امتیاز',
    'processor_brand': 'برند پردازنده',
    'processor_tier': 'سری پردازنده',
    'num_cores': 'تعداد هسته',
    'num_threads': 'تعداد رشته',
    'ram_memory': 'حافظه رم (گیگابایت)',
    'primary_storage_type': 'نوع حافظه اصلی',
    'primary_storage_capacity': 'ظرفیت حافظه اصلی (گیگابایت)',
    'secondary_storage_type': 'نوع حافظه دوم',
    'secondary_storage_capacity': 'ظرفیت حافظه دوم',
    'gpu_brand': 'برند گرافیک',
    'gpu_type': 'نوع گرافیک',
    'is_touch_screen': 'صفحه نمایش لمسی',
    'display_size': 'اندازه صفحه (اینچ)',
    'resolution_width': 'عرض تصویر (پیکسل)',
    'resolution_height': 'ارتفاع تصویر (پیکسل)',
    'OS': 'سیستم عامل',
    'year_of_warranty': 'سال گارانتی',
    'category': 'کاربری',
}

FEATURE_VALUE_TRANSLATIONS = {
    'intel': 'اینتل', 'amd': 'ای‌ام‌دی', 'apple': 'اپل', 'nvidia': 'انویدیا',
    'integrated': 'یکپارچه', 'dedicated': 'مجزا',
    'False': 'خیر', 'True': 'بله',
    'ssd': 'SSD', 'hdd': 'HDD', 'no secondary storage': 'ندارد',
    'windows': 'ویندوز', 'mac': 'مک', 'dos': 'داس', 'other': 'سایر',
    'ubuntu': 'اوبونتو', 'mainstream': 'عمومی', 'gaming': 'گیمینگ',
    'premium': 'حرفه‌ای', 'budget': 'اقتصادی',
}
#====================================================

def get_root_group():
    return ProductGroup.objects.filter(Q(is_active=True) & Q(group_parent=None))

def get_cheap_products(request, *args, **kwargs):
    products = Product.objects.filter(is_active=True).order_by('price')[:4]
    product_groups = get_root_group()
    context = {
        'products': products,
        'product_groups': product_groups
    }
    return render(request, "product_app/partials/cheap_products.html", context)

def get_last_products(request, *args, **kwargs):
    products = Product.objects.filter(is_active=True).order_by('-published_date')[:4]
    product_groups = get_root_group()
    context = {
        'products': products,
        'product_groups': product_groups
    }
    return render(request, "product_app/partials/last_products.html", context)

def get_popular_product_groups(request, *args, **kwargs):
    product_groups = ProductGroup.objects.filter(is_active=True).annotate(count=Count('products_of_groups')).order_by('-count')[:3]
    context = {
        'product_groups': product_groups
    }
    return render(request, "product_app/partials/popular_product_groups.html", context)

# Details of Products
class ProductDeatailView(View):
    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        if product.is_active:
            # --- آماده‌سازی مشخصات ترجمه شده ---
            translated_specs = []
            for spec in product.product_features.all():
                translated_name = FEATURE_NAME_TRANSLATIONS.get(spec.feature.feature_name, spec.feature.feature_name)
                translated_value = FEATURE_VALUE_TRANSLATIONS.get(spec.value, spec.value)
                translated_specs.append({'name': translated_name, 'value': translated_value})
            
            context = {
                'product': product,
                'specifications': translated_specs,
            }
            return render(request, "product_app/product_detail.html", context)

# محصولات مرتبط بر اساس بازه قیمتی
def get_related_products(request, *args, **kwargs):
    current_product = get_object_or_404(Product, slug=kwargs['slug'])
    
    # تعریف بازه قیمتی (مثلا 20% بالاتر و پایین‌تر)
    price_margin = current_product.price * 0.20
    min_price = current_product.price - price_margin
    max_price = current_product.price + price_margin
    
    related_products = Product.objects.filter(
        Q(is_active=True) & 
        Q(price__gte=min_price) & 
        Q(price__lte=max_price) &
        ~Q(id=current_product.id) # خود محصول فعلی را حذف کن
    ).order_by('?')[:5] # مرتب‌سازی تصادفی برای تنوع

    return render(request, "product_app/partials/related_products.html", {'related_products': related_products})

#==== ویوهای مربوط به گروه محصولات (بدون تغییر) ====
class ProductGroupsView(View):
    def get(self, request):
        product_groups = ProductGroup.objects.filter(is_active=True).annotate(count=Count('products_of_groups')).order_by('-count')
        return render(request, "product_app/product_groups.html", {'product_groups': product_groups})

class ProductsByGroupView(View):
    def get(self, request, *args, **kwargs):
        current_group = get_object_or_404(ProductGroup, slug=kwargs['slug'])
        products = Product.objects.filter(is_active=True, product_group=current_group)
        return render(request, "product_app/products.html", {'products': products, 'current_group': current_group})

#==== ویوهای جدید برای برندها ====
class BrandListView(View):
    def get(self, request):
        # شمردن تعداد محصولات هر برند و مرتب‌سازی بر اساس آن
        brands = Brand.objects.annotate(product_count=Count('brands')).order_by('-product_count')
        return render(request, "product_app/brand_list.html", {'brands': brands})

class ProductsByBrandView(View):
    def get(self, request, *args, **kwargs):
        current_brand = get_object_or_404(Brand, slug=kwargs['slug'])
        products = Product.objects.filter(is_active=True, brand=current_brand)
        return render(request, "product_app/products_by_brand.html", {'products': products, 'current_brand': current_brand})
    
    
    
#------------------------------------------------------------
#two dropdown in adminpanel
def get_filter_value_for_feature(request):
    if request.method == 'GET':
        feature_id = request.GET["feature_id"]
        feature_values=FeatureValue.objects.filter(feature_id=feature_id)
        res = {fv.value_title:fv.id for fv in feature_values}
        print(100*"@")
        print(res)
        print(100*"@")
        return JsonResponse(data=res , safe=False)

        