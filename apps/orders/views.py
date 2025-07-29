from django.shortcuts import render,get_object_or_404,redirect
from django.views import View
from .shop_card import ShopCart
from apps.products.models import Product
from django.http import HttpResponse


class ShopCartView(View):
    def get(self,request,*args,**kwargs):
        shop_cart=ShopCart(request)
        return render (request,"orders_app/shop_cart.html",{"shop_cart":shop_cart})


# ==========================================================================================
# def show_shop_cart(request):
#     shop_cart=ShopCart(request)
#     total_price= shop_cart.calc_total_price()
#     delivery=100000
#     if total_price >50000000:
#         delivery =0
#     tax=0.09*total_price
#     context={
#         "shop_cart":shop_cart,
#         "shop_cart_count":shop_cart.count,
#         "total_price":total_price,
#         "delivery":delivery,
#          "tax":tax,
#     }
#     return render (request,"orders_app/partials/show_shop_cart.html",context)

# def show_shop_cart(request):
#     # --- تعریف مقادیر پایه ---
#     # بهتر است این مقادیر در فایل settings.py تعریف شوند تا به راحتی قابل تغییر باشند
#     VAT_RATE = 0.09  # نرخ مالیات بر ارزش افزوده ۱۰٪
#     DELIVERY_FEE = 100000  # هزینه ارسال ثابت ۱۰۰ هزار تومان
#     FREE_SHIPPING_THRESHOLD = 50000000  # آستانه ارسال رایگان: ۵۰ میلیون تومان
#     # محدوده ای که در آن به کاربر پیشنهاد ارسال رایگان می دهیم (مثلا ۱۰ میلیون تومان پایین تر از آستانه)
#     NUDGE_RANGE = 10000000 

#     shop_cart = ShopCart(request)
#     total_price = shop_cart.calc_total_price()

#     # --- محاسبه مالیات ---
#     # مالیات بر اساس قیمت کل کالاها محاسبه می شود
#     tax = int(total_price * VAT_RATE)

#     # --- منطق هوشمند هزینه ارسال ---
#     delivery = DELIVERY_FEE
#     amount_for_free_shipping = None  # متغیری برای نمایش پیام تشویقی

#     if total_price >= FREE_SHIPPING_THRESHOLD:
#         delivery = 0  # ارسال رایگان می شود
#     # اگر کاربر در محدوده تشویقی بود
#     elif (FREE_SHIPPING_THRESHOLD - total_price) <= NUDGE_RANGE:
#         # محاسبه می کنیم چقدر دیگر باید خرید کند تا ارسال رایگان شود
#         amount_for_free_shipping = FREE_SHIPPING_THRESHOLD - total_price

#     # --- محاسبه مبلغ نهایی قابل پرداخت ---
#     grand_total = total_price + tax + delivery

#     context = {
#         "shop_cart": shop_cart,
#         "shop_cart_count": shop_cart.count,
#         "total_price": total_price,       # مبلغ کل کالاها
#         "tax": tax,                       # مبلغ مالیات
#         "delivery": delivery,             # هزینه ارسال نهایی
#         "grand_total": grand_total,       # مبلغ کل قابل پرداخت
#         "amount_for_free_shipping": amount_for_free_shipping, # مبلغ باقی مانده تا ارسال رایگان
#     }
#     return render(request, "orders_app/partials/show_shop_cart.html", context)

# ==========================================================================================



# def add_to_shop_cart(request):
#     product_id=request.GET.get('product_id')
#     qty=request.GET.get('qty')
#     shop_cart=ShopCart(request)
#     product=get_object_or_404(Product,id=product_id)
#     shop_cart.add_to_shop_cart(product,qty)
#     return HttpResponse(shop_cart.count)


# def delete_from_shop_cart(request):
#     product_id=request.GET.get('product_id')
#     product=get_object_or_404(Product,id=product_id)
#     shop_cart=ShopCart(request)
#     shop_cart.delete_from_shop_cart(product)
#     return redirect("orders:show_shop_cart")
    
# def update_shop_cart(request):
#     product_id_list=request.GET.getlist('product_id_list[]')
#     qty_list=request.GET.getlist('qty_list[]')
#     shop_cart=ShopCart(request)
#     shop_cart.update(product_id_list,qty_list)
#     return redirect("orders:show_shop_cart")
    
    
# def status_of_shop_cart(request):
#     shop_cart=ShopCart(request)
#     return HttpResponse(shop_cart.count)


# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

# views.py


# این ویو برای نمایش صفحه اصلی سبد خرید است و درست است
class ShopCartView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "orders_app/shop_cart.html")

# ======================= تغییر اصلی اینجاست =======================
# این ویو فقط و فقط مسئول رندر کردن محتوای سبد خرید است.
# چه در بارگذاری اولیه و چه در پاسخ به AJAX
def show_shop_cart(request):
    # --- تعریف مقادیر پایه ---
    VAT_RATE = 0.09
    DELIVERY_FEE = 100000
    FREE_SHIPPING_THRESHOLD = 50000000
    NUDGE_RANGE = 10000000

    shop_cart = ShopCart(request)
    total_price = shop_cart.calc_total_price()
    tax = int(total_price * VAT_RATE)
    delivery = DELIVERY_FEE
    amount_for_free_shipping = None

    if total_price >= FREE_SHIPPING_THRESHOLD:
        delivery = 0
    elif (FREE_SHIPPING_THRESHOLD - total_price) <= NUDGE_RANGE:
        amount_for_free_shipping = FREE_SHIPPING_THRESHOLD - total_price

    grand_total = total_price + tax + delivery

    context = {
        "shop_cart": shop_cart,
        "shop_cart_count": shop_cart.count,
        "total_price": total_price,
        "tax": tax,
        "delivery": delivery,
        "grand_total": grand_total,
        "amount_for_free_shipping": amount_for_free_shipping,
    }
    # این ویو باید همیشه تمپلیت partial را رندر کند
    return render(request, "orders_app/partials/show_shop_cart.html", context)
# ================================================================

# این ویو بدون تغییر است
def add_to_shop_cart(request):
    product_id = request.GET.get('product_id')
    qty = request.GET.get('qty')
    shop_cart = ShopCart(request)
    product = get_object_or_404(Product, id=product_id)
    shop_cart.add_to_shop_cart(product, qty)
    return HttpResponse(shop_cart.count)

# این ویوها اکنون به درستی کار خواهند کرد
def delete_from_shop_cart(request):
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        shop_cart = ShopCart(request)
        shop_cart.delete_from_shop_cart(product)
        # فراخوانی ویو اصلاح‌شده که فقط partial را برمی‌گرداند
        return show_shop_cart(request)
    return HttpResponse(status=400)

def update_shop_cart(request):
    if request.method == "POST":
        product_id_list = request.POST.getlist('product_id_list[]')
        qty_list = request.POST.getlist('qty_list[]')
        shop_cart = ShopCart(request)
        shop_cart.update(product_id_list, qty_list)
        # فراخوانی ویو اصلاح‌شده که فقط partial را برمی‌گرداند
        return show_shop_cart(request)
    return HttpResponse(status=400)

# این ویو بدون تغییر است
def status_of_shop_cart(request):
    shop_cart = ShopCart(request)
    return HttpResponse(shop_cart.count)