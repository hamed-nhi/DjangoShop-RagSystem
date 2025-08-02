from datetime import datetime
# from pyexpat.errors import messages
from django.shortcuts import render,get_object_or_404,redirect
from django.views import View
from .shop_card import ShopCart
from apps.products.models import Product
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.accounts.models import Customer
from .models import Order,OrderDetails,PaymentType
from  .forms import OrderForm
from django.core.exceptions import ObjectDoesNotExist
from apps.discounts.forms import CouponForm
from apps.discounts.models import Coupon
from django.db.models import Q
from django.contrib import messages
#-------------------------------------------------------------------------------------------------------

# class ShopCartView(View):
#     def get(self,request,*args,**kwargs):
#         shop_cart=ShopCart(request)
#         return render (request,"orders_app/shop_cart.html",{"shop_cart":shop_cart})


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
# ==========================================================================================


class ShopCartView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "orders_app/shop_cart.html")

def show_shop_cart(request):
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
    
    return render(request, "orders_app/partials/show_shop_cart.html", context)

#-------------------------------------------------------------------------------------------------------

def add_to_shop_cart(request):
    product_id = request.GET.get('product_id')
    qty = request.GET.get('qty')
    shop_cart = ShopCart(request)
    product = get_object_or_404(Product, id=product_id)
    shop_cart.add_to_shop_cart(product, qty)
    return HttpResponse(shop_cart.count)

#-------------------------------------------------------------------------------------------------------


def delete_from_shop_cart(request):
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        shop_cart = ShopCart(request)
        shop_cart.delete_from_shop_cart(product)
        return show_shop_cart(request)
    return HttpResponse(status=400)

#-------------------------------------------------------------------------------------------------------

def update_shop_cart(request):
    if request.method == "POST":
        product_id_list = request.POST.getlist('product_id_list[]')
        qty_list = request.POST.getlist('qty_list[]')
        shop_cart = ShopCart(request)
        shop_cart.update(product_id_list, qty_list)
        return show_shop_cart(request)
    return HttpResponse(status=400)

#-------------------------------------------------------------------------------------------------------

def status_of_shop_cart(request):
    shop_cart = ShopCart(request)
    return HttpResponse(shop_cart.count)

#-------------------------------------------------------------------------------------------------------

class CreateOrderView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            customer = Customer.objects.get(user=request.user)
            
        # except Customer.DoesNotExist:
        except ObjectDoesNotExist:

            customer = Customer.objects.create(user=request.user)

        order = Order.objects.create(customer=customer,payment_type=get_object_or_404(PaymentType,id=1))
        shop_cart = ShopCart(request)

        for item in shop_cart:
            OrderDetails.objects.create(
                order=order,
                product=item['product'],
                price=item['price'],
                qty=item['qty']
            )

        return redirect('orders:checkout_order', order.id)




#-------------------------------------------------------------------------------------------------------
class CheckoutOrderView(LoginRequiredMixin,View):
    def get(self, request, order_id):
        user =request.user
        customer = get_object_or_404(Customer,user=user)
        shop_cart=ShopCart(request)
        order = get_object_or_404(Order,id=order_id)

        VAT_RATE = 0.09
        DELIVERY_FEE = 100000
        FREE_SHIPPING_THRESHOLD = 50000000
        NUDGE_RANGE = 10000000   
        total_price = shop_cart.calc_total_price()
        tax = int(total_price * VAT_RATE)
        delivery = DELIVERY_FEE
        amount_for_free_shipping = None

        if total_price >= FREE_SHIPPING_THRESHOLD:
            delivery = 0
        elif (FREE_SHIPPING_THRESHOLD - total_price) <= NUDGE_RANGE:
            amount_for_free_shipping = FREE_SHIPPING_THRESHOLD - total_price

       
        grand_total_before_discount = total_price + tax + delivery
        

        discount_percentage_applied = 0
        discount_amount_applied = 0

        if order.discount > 0:
            discount_percentage_applied = order.discount
            discount_amount_applied = int(grand_total_before_discount * order.discount / 100)
            grand_total = grand_total_before_discount - discount_amount_applied
       
            grand_total = int(grand_total) 
        else:
            grand_total = grand_total_before_discount 

        data={
            'name':user.name,
            'family':user.family,
            'email':user.email,
            'phone_number': customer.phone_number or user.mobile_number,
            'address':customer.address,
            'description':order.description,
        }

        form_coupon = CouponForm()
        form = OrderForm(initial=data)

        context = {
        "shop_cart": shop_cart,
        "total_price": total_price,
        "tax": tax,
        "delivery": delivery,
        "grand_total": grand_total,
        "amount_for_free_shipping": amount_for_free_shipping,
        "form":form,
        "form_coupon": form_coupon,
        'order':order,
        "discount_percentage_applied": discount_percentage_applied,
        "discount_amount_applied": discount_amount_applied,
        "grand_total_before_discount": grand_total_before_discount, 
        }

        return render(request, 'orders_app/checkout.html',context)


    def post(self, request, order_id):
        form = OrderForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            try:
                order = Order.objects.get(id=order_id)
                order.description = cd['description']
                order.payment_type = PaymentType.objects.get(id=cd['payment_type'])
                order.save()

                user = request.user
                user.name = cd['name']
                user.family = cd['family']
                user.email = cd['email']
                user.save()

                customer = Customer.objects.get(user=user)
                customer.phone_number = cd['phone_number']
                customer.address = cd['address']    
                customer.save()

                
                # پیام موفقیت‌آمیز بهبود یافته با user.name و user.family
                # messages.success(request, f"آقای/خانم {user.name} {user.family} عزیز، سفارش شما با شماره پیگیری {order.id} با موفقیت ثبت و نهایی شد. ✅ از خرید شما متشکریم!")
                return redirect('orders:checkout_order', order_id=order.id)
            
            except ObjectDoesNotExist:
                messages.error(request, "خطا در پردازش سفارش. اطلاعات مورد نیاز (مانند نوع پرداخت یا سفارش) یافت نشد. ❌")
            except Exception as e:
                messages.error(request, f"خطای سیستمی در هنگام ثبت سفارش رخ داد: {e} ⛔")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"خطا در فیلد '{form.fields[field].label}': {error} ⚠️")
            messages.error(request, "لطفاً اطلاعات وارد شده را بررسی کنید. برخی از فیلدها صحیح نیستند. 📝")

        return redirect('orders:checkout_order', order_id=order.id)



    # def post(self, request, order_id):
    #     form = OrderForm(request.POST)
    #     if form.is_valid():
    #         cd = form.cleaned_data

    #         try:
    #             order = Order.objects.get(id=order_id)
    #             order.description = cd['description']
    #             order.payment_type = PaymentType.objects.get(id=cd['payment_type'])
    #             order.save()

    #             user = request.user
    #             user.name = cd['name']
    #             user.family = cd['family']
    #             user.email = cd['email']
    #             user.save()

    #             customer= Customer.objects.get(user=user)
    #             customer.phone_number = cd['phone_number']
    #             customer.address = cd['address']    
    #             customer.save()

    #             messages.success(request, "سفارش شما با موفقیت ثبت شد.")
    #             return redirect('orders:order_detail', order_id=order.id)
            

    #         except ObjectDoesNotExist:
    #             messages.error(request, "خطا در ثبت سفارش. لطفاً دوباره تلاش کنید.")
    #     return redirect('orders:checkout_order', order_id=order.id)

#--------------------------------------------------------------------------------------------
# class CheckoutOrderView(LoginRequiredMixin,View):
#     def get(self, request, order_id):
#         user =request.user
#         customer = get_object_or_404(Customer,user=user)
#         shop_cart=ShopCart(request)
#         order = get_object_or_404(Order,id=order_id)

#         VAT_RATE = 0.09
#         DELIVERY_FEE = 100000
#         FREE_SHIPPING_THRESHOLD = 50000000
#         NUDGE_RANGE = 10000000   
#         total_price = shop_cart.calc_total_price()
#         tax = int(total_price * VAT_RATE)
#         delivery = DELIVERY_FEE
#         amount_for_free_shipping = None

#         if total_price >= FREE_SHIPPING_THRESHOLD:
#             delivery = 0
#         elif (FREE_SHIPPING_THRESHOLD - total_price) <= NUDGE_RANGE:
#             amount_for_free_shipping = FREE_SHIPPING_THRESHOLD - total_price

#         grand_total = total_price + tax + delivery
    
#         if order.discount >0:
#             # grand_total = grand_total - (grand_total * order.discount / 100)
#             grand_total = int(grand_total - (grand_total * order.discount / 100))
            
#         data={
#             'name':user.name,
#             'family':user.family,
#             'email':user.email,
#             # 'phone_number':customer.phone_number,
#             'phone_number': customer.phone_number or user.mobile_number,
#             'address':customer.address,
#             'description':order.description,
#         }
#         # print("Customer:", customer.__dict__)
#         # print("User:", customer.user.__dict__)
#         # print("Order:", order.__dict__)


#         # form =OrderForm(data)
#         form_coupon = CouponForm()
#         form = OrderForm(initial=data)

#         context = {
#         "shop_cart": shop_cart,
#         "total_price": total_price,
#         "tax": tax,
#         "delivery": delivery,
#         "grand_total": grand_total,
#         "amount_for_free_shipping": amount_for_free_shipping,
#         "form":form,
#         "form_coupon": form_coupon,
#         'order':order,
#         }

#         return render(request, 'orders_app/checkout.html',context)
    
#-------------------------------------------------------------------------------------------------------



class ApllyCoupon(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        order_id = kwargs['order_id']
        coupon_form = CouponForm(request.POST)
        
        coupon_code = "" 
        if coupon_form.is_valid():
            cd = coupon_form.cleaned_data
            coupon_code = cd['coupon_code']

        coupon_qs = Coupon.objects.filter(
            Q(coupon_code=coupon_code) & 
            Q(is_active=True) & 
            Q(start_date__lte=datetime.now()) & 
            Q(end_date__gte=datetime.now())
        )

        discount = 0
        try:
            order = Order.objects.get(id=order_id)       
            if coupon_qs.exists(): 
                discount = coupon_qs.first().discount
                order.discount = discount
                order.save()
                messages.success(request, f"کد تخفیف '{coupon_code}' با موفقیت اعمال شد. شما {discount}% تخفیف روی سفارش شماره {order.id} دریافت کردید. 🎉")
            else:
                order.discount = 0 
                order.save()
                messages.error(request, f"کد تخفیف '{coupon_code}' نامعتبر است یا منقضی شده است. لطفاً کد را بررسی کنید. ⚠️")

        except ObjectDoesNotExist:
            messages.error(request, "سفارش مورد نظر برای اعمال تخفیف یافت نشد. 😕")
        
        return redirect('orders:checkout_order', order_id)


# class ApllyCoupon(LoginRequiredMixin, View):
#     def post(self, request, *args, **kwargs):
#         order_id = kwargs['order_id']
#         coupon_form = CouponForm(request.POST)
#         if coupon_form.is_valid():
#             cd= coupon_form.cleaned_data
#             coupon_code = cd['coupon_code']

#         coupon=Coupon.objects.filter(
#             Q(coupon_code=coupon_code) & 
#             Q(is_active=True) & 
#             Q(start_date__lte=datetime.now()) & 
#             Q(end_date__gte=datetime.now())
#         )

#         discount=0
#         try:
#             order = Order.objects.get(id=order_id)       
#             if coupon:
#                 discount = coupon[0].discount
#                 order.discount=discount
#                 order.save()
#                 messages.success(request, f"کد تخفیف {coupon_code} با موفقیت اعمال شد. شما {discount}% تخفیف دریافت کردید.")
#                 return redirect('orders:checkout_order', order_id)
#             else:
#                 order.discount=discount
#                 order.save()
#                 messages.error(request, "کد تخفیف نامعتبر است یا منقضی شده است.")
#                     # return redirect('orders:checkout_order', order_id)

#         except ObjectDoesNotExist:
#             messages.error(request, "سفارش یافت نشد.")
#         return redirect('orders:checkout_order', order_id)
