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

        grand_total = total_price + tax + delivery
    
        
        data={
            'name':user.name,
            'family':user.family,
            'email':user.email,
            # 'phone_number':customer.phone_number,
            'phone_number': customer.phone_number or user.mobile_number,
            'address':customer.address,
            'description':order.description,
        }
        # print("Customer:", customer.__dict__)
        # print("User:", customer.user.__dict__)
        # print("Order:", order.__dict__)


        # form =OrderForm(data)
        form = OrderForm(initial=data)
        context = {
        "shop_cart": shop_cart,
        "total_price": total_price,
        "tax": tax,
        "delivery": delivery,
        "grand_total": grand_total,
        "amount_for_free_shipping": amount_for_free_shipping,
        "form":form,
        }
        return render(request, 'orders_app/checkout.html',context)