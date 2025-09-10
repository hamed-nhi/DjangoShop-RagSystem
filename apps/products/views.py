from collections import defaultdict
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.db.models import Q, Count, Min, Max
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from .compare import CompareProduct
from .filters import ProductFilter
from .models import FeatureValue, Product, ProductGroup, Brand, Feature

# Import the dictionaries from your new central file
from .translations import FEATURE_NAME_TRANSLATIONS, FEATURE_VALUE_TRANSLATIONS

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
            # --- Preparing translated specifications ---
            translated_specs = []
            for spec in product.product_features.all():
                # Now using the imported dictionaries
                translated_name = FEATURE_NAME_TRANSLATIONS.get(spec.feature.feature_name, spec.feature.feature_name)
                translated_value = FEATURE_VALUE_TRANSLATIONS.get(spec.value, spec.value)
                translated_specs.append({'name': translated_name, 'value': translated_value})

            comment_count = product.comments_product.filter(is_active=True).count()

            context = {
                'product': product,
                'specifications': translated_specs,
                'comment_count': comment_count,
            }
            return render(request, "product_app/product_detail.html", context)

#----------------------------------------------------------------------------------------------
# Related products based on price range
def get_related_products(request, *args, **kwargs):
    current_product = get_object_or_404(Product, slug=kwargs['slug'])
    
    price_margin = current_product.price * 0.10
    min_price = current_product.price - price_margin
    max_price = current_product.price + price_margin
    
    related_products = Product.objects.filter(
        Q(is_active=True) & 
        Q(price__gte=min_price) & 
        Q(price__lte=max_price) &
        ~Q(id=current_product.id)
    ).order_by('?')[:5]

    return render(request, "product_app/partials/related_products.html", {'related_products': related_products})

#----------------------------------------------------------------------------------------------
# List of all product groups
class ProductGroupsView(View):
    def get(self, request):
        product_groups = ProductGroup.objects.filter(is_active=True)\
            .annotate(count=Count('products_of_groups'))\
            .order_by('-count')
        return render(request, "product_app/product_groups.html", {'product_groups': product_groups})

#----------------------------------------------------------------------------------------------
# Products by group view
class ProductsGroupsView(View):
    def get(self, request, *args, **kwargs):
        current_group = get_object_or_404(ProductGroup, slug=kwargs['slug'])
        products = Product.objects.filter(is_active=True, product_group=current_group)
        return render(request, "product_app/products.html", {'products': products, 'current_group': current_group})

#-----------------------------------------------------------------------------------------------
# Product groups for filter
def get_product_groups(request):
    product_groups=ProductGroup.objects.annotate(count=Count('products_of_groups'))\
        .filter(Q(is_active=True) & ~Q(count=0))\
        .order_by('-count')
    return render(request,"product_app/partials/product_groups.html",{'product_groups':product_groups})
    
#-----------------------------------------------------------------------------------------------
# Brands for filter
def get_brands(request,*args,**kwargs):
    product_groups=get_object_or_404(ProductGroup,slug=kwargs['slug'])
    brand_list_id=product_groups.products_of_groups.filter(is_active=True,).values('brand_id')
    brands=Brand.objects.filter(pk__in=brand_list_id)\
        .annotate(count=Count('product_of_brands'))\
        .filter(~Q(count=0))\
        .order_by('-count')
    
    return render(request,"product_app/partials/brands.html",{'brands':brands})

#-----------------------------------------------------------------------------------------------
def get_feature_for_filter(request, *args, **kwargs):
    """
    This view prepares a list of features and their values for a specific product group,
    along with their Persian translations, and sends them to the template.
    """
    product_group = get_object_or_404(ProductGroup, slug=kwargs['slug'])
    feature_list = product_group.features_of_groups.all()
    
    translated_features = []
    for feature in feature_list:
        # Now using the imported dictionaries
        translated_name = FEATURE_NAME_TRANSLATIONS.get(feature.feature_name, feature.feature_name)
        
        values = feature.feature_values.all()
        if not values:
            continue

        translated_values = []
        for value in values:
            # Now using the imported dictionaries
            translated_title = FEATURE_VALUE_TRANSLATIONS.get(value.value_title, value.value_title)
            translated_values.append({
                'id': value.id,
                'translated_title': translated_title
            })
            
        translated_features.append({
            'id': feature.id,
            'translated_name': translated_name,
            'values': translated_values
        })

    context = {
        'translated_features': translated_features
    }
    return render(request, "product_app/partials/features_filter.html", context)

#-----------------------------------------------------------------------------------------------
# For two dropdowns in admin panel
def get_filter_value_for_feature(request):
    if request.method =='GET':
        feature_id=request.GET["feature_id"]
        feature_value=FeatureValue.objects.filter(feature_id=feature_id)
        res={fv.value_title:fv.id for fv in feature_value}
    return JsonResponse(data=res,safe=False)

#-----------------------------------------------------------------------------------------------
class ProductByGroupsView(View):
    def get(self, request, *args, **kwargs):
        slug = kwargs["slug"]
        current_group = get_object_or_404(ProductGroup, slug=slug)

        products = Product.objects.filter(is_active=True, product_group=current_group)
        res_aggre = products.aggregate(min=Min('price'), max=Max('price'))

        price_filter = ProductFilter(request.GET, queryset=products)
        products = price_filter.qs

        brands_filter_ids = request.GET.getlist('brand')
        if brands_filter_ids:
            products = products.filter(brand__id__in=brands_filter_ids)

        features_filter_ids = request.GET.getlist('feature')
        selected_values = []
        if features_filter_ids:
            selected_values = FeatureValue.objects.filter(id__in=features_filter_ids).select_related('feature')
            
            grouped_values = defaultdict(list)
            for value in selected_values:
                grouped_values[value.feature_id].append(value.id)

            for feature_group_ids in grouped_values.values():
                products = products.filter(product_features__filter_value__id__in=feature_group_ids)
        
        products = products.distinct()

        sort_type = request.GET.get('sort_type', '0')
        if sort_type == '1':
            products = products.order_by('price')
        elif sort_type == '2':
            products = products.order_by('-price')

        paginator = Paginator(products, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        active_filters = []
        query_params = request.GET.copy()

        if brands_filter_ids:
            brands = Brand.objects.filter(id__in=brands_filter_ids)
            for brand in brands:
                query_params_copy = query_params.copy()
                query_params_copy.pop('brand', None)
                remove_url = f"?{query_params_copy.urlencode()}" if query_params_copy else request.path
                active_filters.append({
                    'type': 'برند',
                    'name': brand.brand_title,
                    'remove_url': remove_url
                })

        if features_filter_ids:
            for value in selected_values:
                query_params_copy = query_params.copy()
                current_features = query_params_copy.getlist('feature')
                if str(value.id) in current_features:
                    current_features.remove(str(value.id))
                query_params_copy.setlist('feature', current_features)
                
                remove_url = f"?{query_params_copy.urlencode()}" if query_params_copy else request.path
                active_filters.append({
                    'type': FEATURE_NAME_TRANSLATIONS.get(value.feature.feature_name, value.feature.feature_name),
                    'name': value.value_title,
                    'remove_url': remove_url
                })

        context = {
            'current_group': current_group,
            'page_obj': page_obj,
            'product_count': paginator.count,
            'filter': price_filter,
            'sort_type': sort_type,
            'group_slug': slug,
            'active_filters': active_filters,
            'res_aggre': res_aggre,
        }
        
        return render(request, "product_app/products.html", context)

#--------------------------------------------------------------------
# This is a context processor, it should be registered in settings.py
def navbar_context(request):
    high_rated_products = Product.objects.filter(
        is_active=True,
        product_features__feature_id=20,
        product_features__value__gte=60
    ).distinct()[:5]
    
    popular_brands = Brand.objects.annotate(
        product_count=Count('product_of_brands')
    ).order_by('-product_count')[:5]
    
    return {
        'high_rated_products': high_rated_products,
        'popular_brands': popular_brands
    }

#--------------------------------------------------------------------
# ********* Compare Products *********
#--------------------------------------------------------------------

def show_compare_list_view(request):
    compare_list_obj = CompareProduct(request)
    products = compare_list_obj.get_products()
    context = {'products': products}
    return render(request, 'product_app/compare_list.html', context)

# def compare_table_partial(request):
#     compare_list_obj = CompareProduct(request)
#     products = compare_list_obj.get_products()
#     features = Feature.objects.filter(productfeature__product__in=products).distinct()
#     context = {'products': products, 'features': features}
#     return render(request, "product_app/partials/compare_table.html", context)
def compare_table_partial(request):
    compare_list_obj = CompareProduct(request)
    products = compare_list_obj.get_products()
    
    features = Feature.objects.filter(
        productfeature__product__in=products
    ).exclude(
        feature_name='Rating' # Exclude 'Rating' feature
    ).distinct()

    context = {'products': products, 'features': features}
    return render(request, "product_app/partials/compare_table.html", context)

def status_of_compare_list(request):
    compare_list = CompareProduct(request)
    return HttpResponse(len(compare_list))

def add_to_compare_list(request):
    product_id = request.GET.get('productId')
    product_group_id = request.GET.get('productGroupId')
    if not product_id or not product_group_id:
        return JsonResponse({"status": "error", "message": "اطلاعات کامل ارسال نشده است."}, status=400)
    compare_list = CompareProduct(request)
    result = compare_list.add(product_id=product_id, product_group_id=product_group_id)
    return JsonResponse(result)

# def delete_from_compare_list(request):
#     product_id = request.GET.get('productId')
#     if product_id:
#         compare_list = CompareProduct(request)
#         compare_list.delete(product_id=product_id)
#     return compare_table_partial(request)
@require_http_methods(["POST"])
def delete_from_compare_list(request):
    """
    Handles POST requests from JavaScript to remove a product from the compare list.
    """
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')

        if product_id:
            compare_list = CompareProduct(request)
            compare_list.delete(product_id=str(product_id))
            return JsonResponse({'status': 'success', 'message': 'Product removed successfully.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Product ID not provided.'}, status=400)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)





class AllProductGroupsView(View):
    def get(self, request):
        return redirect('products:products_of_group', slug='laptop') 

def get_best_selling_products(request, *args, **kwargs):
    products = Product.objects.filter(is_active=True).order_by('-base_rating')[:4] 
    # featured_product = Product.objects.filter(is_active=True, category__name='لپ تاپ').first()  # یا هر شرط دیگری

    context = {
        'title': 'پرفروش ترین ها', # This title will still be used in the template
        'products': products,
        # 'featured_product': featured_product,

    }
    return render(request, "product_app/partials/best_selling_products.html", context)

# from collections import defaultdict
# from django.core.paginator import Paginator
# from django.http import HttpResponse, JsonResponse
# from django.shortcuts import render, get_object_or_404, redirect

# from apps.products.compare import CompareProduct
# from .filters import ProductFilter
# from .models import FeatureValue, Product, ProductGroup, Brand, Feature
# from django.db.models import Q, Count,Min,Max
# from django.views import View

# FEATURE_NAME_TRANSLATIONS = {
#     'Rating': 'امتیاز',
#     'processor_brand': 'برند پردازنده',
#     'processor_tier': 'سری پردازنده',
#     'num_cores': 'تعداد هسته',
#     'num_threads': 'تعداد رشته',
#     'ram_memory': 'حافظه رم (گیگابایت)',
#     'primary_storage_type': 'نوع حافظه اصلی',
#     'primary_storage_capacity': 'ظرفیت حافظه اصلی (گیگابایت)',
#     'secondary_storage_type': 'نوع حافظه دوم',
#     'secondary_storage_capacity': 'ظرفیت حافظه دوم',
#     'gpu_brand': 'برند گرافیک',
#     'gpu_type': 'نوع گرافیک',
#     'is_touch_screen': 'صفحه نمایش لمسی',
#     'display_size': 'اندازه صفحه (اینچ)',
#     'resolution_width': 'عرض تصویر (پیکسل)',
#     'resolution_height': 'ارتفاع تصویر (پیکسل)',
#     'OS': 'سیستم عامل',
#     'year_of_warranty': 'سال گارانتی',
#     'category': 'کاربری',
    
# }

# FEATURE_VALUE_TRANSLATIONS = {
#     'intel': 'اینتل', 'amd': 'ای‌ام‌دی', 'apple': 'اپل', 'nvidia': 'انویدیا',
#     'integrated': 'یکپارچه', 'dedicated': 'مجزا',
#     'False': 'خیر', 'True': 'بله',
#     'ssd': 'SSD', 'hdd': 'HDD', 'no secondary storage': 'ندارد',
#     'windows': 'ویندوز', 'mac': 'مک', 'dos': 'داس', 'other': 'سایر',
#     'ubuntu': 'اوبونتو', 'mainstream': 'عمومی', 'gaming': 'گیمینگ',
#     'premium': 'حرفه‌ای', 'budget': 'اقتصادی','android':'اندروید',
#     'chrome':'کروم',
# }
# #====================================================

# def get_root_group():
#     return ProductGroup.objects.filter(Q(is_active=True) & Q(group_parent=None))

# def get_cheap_products(request, *args, **kwargs):
#     products = Product.objects.filter(is_active=True).order_by('price')[:4]
#     product_groups = get_root_group()
#     context = {
#         'products': products,
#         'product_groups': product_groups
#     }
#     return render(request, "product_app/partials/cheap_products.html", context)

# def get_last_products(request, *args, **kwargs):
#     products = Product.objects.filter(is_active=True).order_by('-published_date')[:4]
#     product_groups = get_root_group()
#     context = {
#         'products': products,
#         'product_groups': product_groups
#     }
#     return render(request, "product_app/partials/last_products.html", context)

# def get_popular_product_groups(request, *args, **kwargs):
#     product_groups = ProductGroup.objects.filter(is_active=True).annotate(count=Count('products_of_groups')).order_by('-count')[:3]
#     context = {
#         'product_groups': product_groups
#     }
#     return render(request, "product_app/partials/popular_product_groups.html", context)

# # Details of Products
# class ProductDeatailView(View):
#     def get(self, request, slug):
#         product = get_object_or_404(Product, slug=slug)
#         if product.is_active:
#             # --- آماده‌سازی مشخصات ترجمه شده ---
#             translated_specs = []
#             for spec in product.product_features.all():
#                 translated_name = FEATURE_NAME_TRANSLATIONS.get(spec.feature.feature_name, spec.feature.feature_name)
#                 translated_value = FEATURE_VALUE_TRANSLATIONS.get(spec.value, spec.value)
#                 translated_specs.append({'name': translated_name, 'value': translated_value})

#             comment_count = product.comments_product.filter(is_active=True).count()

#             context = {
#                 'product': product,
#                 'specifications': translated_specs,
#                 'comment_count': comment_count,
#             }
#             return render(request, "product_app/product_detail.html", context)
# #----------------------------------------------------------------------------------------------
# # محصولات مرتبط بر اساس بازه قیمتی
# def get_related_products(request, *args, **kwargs):
#     current_product = get_object_or_404(Product, slug=kwargs['slug'])
    
#     # تعریف بازه قیمتی ( 10% بالاتر و پایین‌تر)
#     price_margin = current_product.price * 0.10
#     min_price = current_product.price - price_margin
#     max_price = current_product.price + price_margin
    
#     related_products = Product.objects.filter(
#         Q(is_active=True) & 
#         Q(price__gte=min_price) & 
#         Q(price__lte=max_price) &
#         ~Q(id=current_product.id) # خود محصول فعلی را حذف کن
#     ).order_by('?')[:5] # مرتب‌سازی تصادفی برای تنوع

#     return render(request, "product_app/partials/related_products.html", {'related_products': related_products})
# #----------------------------------------------------------------------------------------------

# #----------------------------------------------------------------------------------------------
# # لیست کلیه گروه های محصولات
# class ProductGroupsView(View):
#     def get(self, request):
#         product_groups = ProductGroup.objects.filter(is_active=True)\
#             .annotate(count=Count('products_of_groups'))\
#             .order_by('-count')
#         return render(request, "product_app/product_groups.html", {'product_groups': product_groups})
# #----------------------------------------------------------------------------------------------
# #changed def ProductsByGroupView
# class ProductsGroupsView(View):
#     def get(self, request, *args, **kwargs):
#         current_group = get_object_or_404(ProductGroup, slug=kwargs['slug'])
#         products = Product.objects.filter(is_active=True, product_group=current_group)
#         return render(request, "product_app/products.html", {'products': products, 'current_group': current_group})

# #-----------------------------------------------------------------------------------------------
# # لیست گروه محصولات برای فیلتر
# def get_product_groups(request):
#     product_groups=ProductGroup.objects.annotate(count=Count('products_of_groups'))\
#                                        .filter(Q(is_active=True) & ~Q(count=0))\
#                                        .order_by('-count')
#     return render(request,"product_app/partials/product_groups.html",{'product_groups':product_groups})
    
# #-----------------------------------------------------------------------------------------------
# # لیست برندها برای فیلتر
# def get_brands(request,*args,**kwargs):
#     product_groups=get_object_or_404(ProductGroup,slug=kwargs['slug'])
#     brand_list_id=product_groups.products_of_groups.filter(is_active=True,).values('brand_id')
#     brands=Brand.objects.filter(pk__in=brand_list_id)\
#                         .annotate(count=Count('product_of_brands'))\
#                         .filter(~Q(count=0))\
#                         .order_by('-count')
    
#     return render(request,"product_app/partials/brands.html",{'brands':brands})
# #-----------------------------------------------------------------------------------------------

# def get_feature_for_filter(request, *args, **kwargs):
#     """
#     این ویو لیست ویژگی‌ها و مقادیر آن‌ها را برای یک گروه محصول خاص،
#     به همراه ترجمه فارسی آن‌ها آماده کرده و به تمپلیت ارسال می‌کند.
#     """
#     product_group = get_object_or_404(ProductGroup, slug=kwargs['slug'])
#     feature_list = product_group.features_of_groups.all()
    
#     translated_features = []
#     for feature in feature_list:
#         # ترجمه نام ویژگی (مانند 'processor_brand' به 'برند پردازنده')
#         translated_name = FEATURE_NAME_TRANSLATIONS.get(feature.feature_name, feature.feature_name)
        
#         values = feature.feature_values.all()
#         # اگر یک ویژگی هیچ مقداری نداشت، آن را در فیلترها نمایش نده
#         if not values:
#             continue

#         translated_values = []
#         for value in values:
#             # ترجمه مقدار ویژگی (مانند 'intel' به 'اینتل')
#             translated_title = FEATURE_VALUE_TRANSLATIONS.get(value.value_title, value.value_title)
#             translated_values.append({
#                 'id': value.id,
#                 'translated_title': translated_title
#             })
            
#         translated_features.append({
#             'id': feature.id,
#             'translated_name': translated_name,
#             'values': translated_values
#         })

#     context = {
#         'translated_features': translated_features
#     }
#     return render(request, "product_app/partials/features_filter.html", context)
# #-----------------------------------------------------------------------------------------------
# # two dropdown in adminpanel
# from django.http import JsonResponse
# def get_filter_value_for_feature(request):
#     if request.method =='GET':
#         feature_id=request.GET["feature_id"]
#         feature_value=FeatureValue.objects.filter(feature_id=feature_id)
#         res={fv.value_title:fv.id for fv in feature_value}
#     return JsonResponse(data=res,safe=False)
 
#  #-----------------------------------------------------------------------------------------------
 
 
# class ProductByGroupsView(View):
   
#     def get(self, request, *args, **kwargs):
#         slug = kwargs["slug"]
#         current_group = get_object_or_404(ProductGroup, slug=slug)

#         # ۱. کوئری‌ست اولیه
#         products = Product.objects.filter(is_active=True, product_group=current_group)
#         res_aggre = products.aggregate(min=Min('price'), max=Max('price'))

#         # ۲. فیلتر قیمت
#         price_filter = ProductFilter(request.GET, queryset=products)
#         products = price_filter.qs

#         # ۳. فیلتر برند
#         brands_filter_ids = request.GET.getlist('brand')
#         if brands_filter_ids:
#             products = products.filter(brand__id__in=brands_filter_ids)

#         # ۴. فیلتر ویژگی‌ها
#         features_filter_ids = request.GET.getlist('feature')
#         selected_values = [] # تعریف اولیه برای جلوگیری از خطا
#         if features_filter_ids:
#             selected_values = FeatureValue.objects.filter(id__in=features_filter_ids).select_related('feature')
            
#             grouped_values = defaultdict(list)
#             for value in selected_values:
#                 grouped_values[value.feature_id].append(value.id)

#             for feature_group_ids in grouped_values.values():
#                 products = products.filter(product_features__filter_value__id__in=feature_group_ids)
        
#         products = products.distinct()

#         # ۵. مرتب‌سازی
#         sort_type = request.GET.get('sort_type', '0')
#         if sort_type == '1':
#             products = products.order_by('price')
#         elif sort_type == '2':
#             products = products.order_by('-price')

#         # ۶. صفحه‌بندی
#         paginator = Paginator(products, 15)
#         page_number = request.GET.get('page')
#         page_obj = paginator.get_page(page_number)

#         # ۷. ساخت لیست فیلترهای فعال برای نمایش در قالب
#         active_filters = []
#         query_params = request.GET.copy()

#         if brands_filter_ids:
#             brands = Brand.objects.filter(id__in=brands_filter_ids)
#             for brand in brands:
#                 query_params_copy = query_params.copy()
#                 # برای برند که چندتایی نیست، pop کافیست
#                 query_params_copy.pop('brand', None)
#                 remove_url = f"?{query_params_copy.urlencode()}" if query_params_copy else request.path
#                 active_filters.append({
#                     'type': 'برند',
#                     'name': brand.brand_title,
#                     'remove_url': remove_url
#                 })

#         if features_filter_ids:
#             for value in selected_values: # حالا selected_values به درستی در دسترس است
#                 query_params_copy = query_params.copy()
#                 current_features = query_params_copy.getlist('feature')
#                 if str(value.id) in current_features:
#                     current_features.remove(str(value.id))
#                 query_params_copy.setlist('feature', current_features)
                
#                 remove_url = f"?{query_params_copy.urlencode()}" if query_params_copy else request.path
#                 active_filters.append({
#                     'type': FEATURE_NAME_TRANSLATIONS.get(value.feature.feature_name, value.feature.feature_name),
#                     'name': value.value_title,
#                     'remove_url': remove_url
#                 })

#         # ۸. ساخت نهایی context (فقط یک بار)
#         context = {
#             'current_group': current_group,
#             'page_obj': page_obj,
#             'product_count': paginator.count,
#             'filter': price_filter,
#             'sort_type': sort_type,
#             'group_slug': slug,
#             'active_filters': active_filters,
#             'res_aggre': res_aggre,
#         }
        
#         # ۹. رندر کردن قالب (فقط یک بار)
#         return render(request, "product_app/products.html", context)






# #--------------------------------------------------------------------
# def navbar_context(request):
#     # دریافت محصولات با امتیاز 90+
#     high_rated_products = Product.objects.filter(
#         is_active=True,
#         product_features__feature_id=20,  # ID ویژگی Rating
#         product_features__value__gte=60   # امتیاز 90 به بالا
#     ).distinct()[:5]  # فقط 5 محصول برتر
    
#     # دریافت برندهای محبوب
#     popular_brands = Brand.objects.annotate(
#         product_count=Count('product_of_brands')
#     ).order_by('-product_count')[:5]
    
#     return {
#         'high_rated_products': high_rated_products,
#         'popular_brands': popular_brands
#     }


# #--------------------------------------------------------------------
# # ********* Compare Products *********






# class ShowCompareListView(View):
#     def get(self, request, *args, **kwargs):
#         compare_list=CompareProduct(request)
#         context={
#             'compare_list': compare_list,
#             # 'count': compare_list.count,
#         }
#         return render(request, "product_app/compare_list.html", context)
    
# def show_compare_list_view(request):
#     compare_list_obj = CompareProduct(request)
#     products = compare_list_obj.get_products()  # Correctly gets the list of product objects
    
#     context = {
#         'products': products
#     }
#     return render(request, 'product_app/compare_list.html', context)

# # This view is ONLY for the partial table (for AJAX and includes)
# def compare_table_partial(request):
#     compare_list_obj = CompareProduct(request)
#     products = compare_list_obj.get_products()

#     # Get all unique features for the products in the list
#     # The change is right here: 'product_features' is now 'productfeature'
#     features = Feature.objects.filter(productfeature__product__in=products).distinct()

#     context = {
#         'products': products,
#         'features': features,
#     }
#     return render(request, "product_app/partials/compare_table.html", context)

# # This view is for getting the item count for the header icon
# def status_of_compare_list(request):
#     compare_list = CompareProduct(request)
#     return HttpResponse(len(compare_list))

# # This view adds an item to the list
# def add_to_compare_list(request):
#     product_id = request.GET.get('productId')
#     product_group_id = request.GET.get('productGroupId')

#     if not product_id or not product_group_id:
#         return JsonResponse({"status": "error", "message": "اطلاعات کامل ارسال نشده است."}, status=400)

#     compare_list = CompareProduct(request)
#     result = compare_list.add(product_id=product_id, product_group_id=product_group_id)
#     return JsonResponse(result)

# # This view deletes an item and returns the updated table for AJAX
# def delete_from_compare_list(request):
#     product_id = request.GET.get('productId')
#     if product_id:
#         compare_list = CompareProduct(request)
#         compare_list.delete(product_id=product_id)
    
#     # After deleting, re-render the partial table and return it
#     return compare_table_partial(request)

