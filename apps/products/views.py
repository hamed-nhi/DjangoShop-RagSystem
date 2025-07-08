from django.shortcuts import render,get_object_or_404
from .models import Product,ProductGroup
from django.db.models import Q,Count
from django.views import View


def get_root_group():
    return ProductGroup.objects.filter(Q(is_active=True)& Q(group_parent=None)) # سرگروه هارو برمیکردونه

def get_cheap_products(request,*args,**kwargs):
    products= Product.objects.filter(is_active=True).order_by('price')[:4]
    product_groups=  get_root_group()
    
    context= {
    'products': products,
    'product_groups': product_groups  # جمع! نه مفرد!
    }
    return render(request,"product_app/partials/cheap_products.html",context)

def get_last_products(request,*args,**kwargs):
    products= Product.objects.filter(is_active=True).order_by('-published_date')[:4]
    product_groups= get_root_group()
    
    context= {
    'products': products,
    'product_groups': product_groups  # جمع! نه مفرد!
    }
    return render(request,"product_app/partials/last_products.html",context)

def get_popular_product_groups(request,*args,**kwargs):
    product_groups=ProductGroup.objects.filter(Q(is_active=True)).annotate(count=Count('products_of_groups')).order_by('-count')[:3]
    context={
        'product_groups':product_groups
    }
    return render(request,"product_app/partials/popular_product_groups.html",context)

#Details of Products
class ProductDeatailView(View):
    def get(self,request,slug):
        product=get_object_or_404(Product,slug=slug)
        if product.is_active:
            return render(request,"product_app/product_detail.html",{'product':product})
 
 
#این رو باید بگونه ای تغییر بدیم که لپتاپ ها مشابه تو اون رنج قیمت نشون داده بشن        
#محصولات مرتبط
def get_related_products(request,*args, **kwargs):
    current_product=get_object_or_404(Product,slug=kwargs['slug'])
    related_products=[]
    for group in current_product.product_group.all():
        related_products.extend(Product.objects.filter(Q(is_active=True) & Q(product_group=group) & ~Q(id=current_product.id))[:5]) 
    return render(request,"product_app/partials/related_products.html",{'related_products':related_products})
    
# این رو باید بگونه تغییر بدیم که گروه تبدیل به برند بشه   
#لیست  کلیه گروه های محصولات 
class ProductGroupsView(View):
    def get(self,request):
        product_groups=ProductGroup.objects.filter(Q(is_active=True)).annotate(count=Count('products_of_groups')).order_by('-count')
        return render (request,"product_app/product_groups.html",{'product_groups':product_groups})
    
    
    
    
# این رو باید بگونه تغییر بدیم که گروه تبدیل به برند بشه       
#لیست  محصولات هر گروه محصولات
class ProductsByGroupView(View):
    def get(self,request,*args, **kwargs):
        current_group=get_object_or_404(ProductGroup,slug=kwargs['slug'])
        products = Product.objects.filter(Q(is_active=True) & Q(product_group=current_group))
        return render (request,"product_app/products.html",{'products':products,'current_group':current_group })