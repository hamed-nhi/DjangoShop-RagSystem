# کدهایی که نیاز به دیتا بیس ندارد بهتره در این فایل مجزا نوشته بشه
#Services
from apps.products.models import Product
import copy

class ShopCart:
    def __init__(self,request):
        self.session=request.session
        temp=self.session.get('shop_cart')
        if not temp:
            temp=self.session['shop_cart']={}
        self.shop_cart=temp
        self.count=len(self.shop_cart.keys())
 

    def add_to_shop_cart(self,product,qty):
        product_id=str(product.id)
        if product_id not in self.shop_cart:
            self.shop_cart[product_id]={"qty":0,"price":product.price}
        self.shop_cart[product_id]["qty"]+=int(qty)
        self.count=len(self.shop_cart.keys())
        self.save()


    def delete_from_shop_cart(self,product):
        product_id=str(product.id)
        del self.shop_cart[product_id]
        self.save()

# =====================================================================

    
    def update(self, product_id_list, qty_list):
    # استفاده از zip خواناتر و بهتر است
        for product_id, qty in zip(product_id_list, qty_list):
            if product_id in self.shop_cart:
                # بهتر است یک بررسی برای اطمینان از عددی بودن مقدار انجام شود
                try:
                    self.shop_cart[product_id]['qty'] = int(qty)
                except (ValueError, TypeError):
                    # اگر مقدار تعداد، عدد نبود، آن را نادیده بگیر
                    pass
        # save() فقط یک بار در انتها فراخوانی می‌شود
        self.save()       
                
    # def update(self,product_id_list,qty_list):
    #     i=0
    #     for product_id in product_id_list:
    #         self.shop_cart[product_id]['qty']=int(qty_list[i])
    #         i+=1
    #     self.save()
        
        
    # def update(self, product_id_list, qty_list):
    #     for i, product_id in enumerate(product_id_list):
    #         if product_id in self.shop_cart and i < len(qty_list):  # Check if product exists in cart
    #             self.shop_cart[product_id]['qty'] = int(qty_list[i])
    #     self.save()

# =====================================================================
    def save(self):
        self.session.modified=True

        
        
    # def __iter__(self):
    #     list_ids=self.shop_cart.keys()
    #     products=Product.objects.filter(id__in=list_ids)
    #     temp=self.shop_cart.copy()
    #     for product in products:
    #         temp[str(product.id)]["product"]=product

    #     for item in temp.values():
    #         item["total_price"]=item["price"]*item["qty"]
    #         yield item         


    def __iter__(self):
        list_ids = self.shop_cart.keys()
        products = Product.objects.filter(id__in=list_ids)
        
        # 2. از copy.deepcopy به جای .copy() استفاده کنید
        temp = copy.deepcopy(self.shop_cart)
        
        for product in products:
            # اکنون این تغییر فقط روی دیکشنری temp اعمال می‌شود و سشن اصلی امن است
            temp[str(product.id)]["product"] = product

        for item in temp.values():
            item["total_price"] = item["price"] * item["qty"]
            yield item
            
            
    def calc_total_price(self):
        sum=0
        for item in self.shop_cart.values():
            sum+=item['price'] * item['qty']
        return sum
    
    