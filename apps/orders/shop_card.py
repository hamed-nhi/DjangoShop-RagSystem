# products/services.py (assuming this is your shop_card.py file)
from apps.products.models import Product
import copy

class ShopCart:
    def __init__(self, request):
        self.session = request.session
        temp = self.session.get('shop_cart')
        if not temp:
            temp = self.session['shop_cart'] = {}
        self.shop_cart = temp

        # --- FIX START: Ensure 'final_price' for existing items when initializing cart ---
        # This loop will go through all items currently in the session cart
        # and ensure they have 'final_price' and update it if necessary.
        for product_id_str, item_data in self.shop_cart.items():
            try:
                product_obj = Product.objects.get(id=int(product_id_str))
                # Update final_price for existing items (important if discounts change)
                item_data['final_price'] = int(round(product_obj.get_price_by_discount()))
                # Also ensure 'price' is present if you use it for original price
                if 'price' not in item_data:
                    item_data['price'] = str(product_obj.price) 
            except Product.DoesNotExist:
                # If a product in the cart no longer exists in DB, remove it from cart
                del self.shop_cart[product_id_str]
            except (ValueError, TypeError):
                # Handle cases where product_id_str isn't an int or price isn't convertible
                del self.shop_cart[product_id_str]
        self.save() # Save changes back to session after cleanup/update
        # --- FIX END ---

        self.count = len(self.shop_cart.keys())

    def add_to_shop_cart(self, product, qty):
        product_id = str(product.id)
        # Ensure 'final_price' is always set/updated when adding or incrementing
        self.shop_cart.setdefault(product_id, {
            "qty": 0,
            "price": str(product.price), # Ensure original price is stored as string too
        })
        # Always update final_price in case discounts change
        self.shop_cart[product_id]["final_price"] = int(round(product.get_price_by_discount()))
        
        self.shop_cart[product_id]["qty"] += int(qty)
        self.count = len(self.shop_cart.keys())
        self.save()

    def delete_from_shop_cart(self, product):
        product_id = str(product.id)
        if product_id in self.shop_cart: # Add check to avoid KeyError if product not in cart
            del self.shop_cart[product_id]
            self.save()

    # =====================================================================

    def update(self, product_id_list, qty_list):
        for product_id, qty in zip(product_id_list, qty_list):
            if product_id in self.shop_cart:
                try:
                    # Update quantity
                    self.shop_cart[product_id]['qty'] = int(qty)
                    # Also ensure final_price is updated if product details might change
                    product_obj = Product.objects.get(id=int(product_id))
                    self.shop_cart[product_id]['final_price'] = int(round(product_obj.get_price_by_discount()))
                    self.shop_cart[product_id]['price'] = str(product_obj.price) # Update original price too
                except (ValueError, TypeError, Product.DoesNotExist):
                    # If quantity is not valid, or product no longer exists, remove it
                    if product_id in self.shop_cart:
                        del self.shop_cart[product_id]
        self.save()

    # =====================================================================
    def save(self):
        self.session.modified = True

    def __iter__(self):
        list_ids = self.shop_cart.keys()
        products = Product.objects.filter(id__in=list_ids)
        
        # Create a mapping of product ID to product object for efficient lookup
        products_map = {str(p.id): p for p in products}

        temp = copy.deepcopy(self.shop_cart)
        
        for product_id_str, item in temp.items():
            if product_id_str in products_map:
                product_obj = products_map[product_id_str]
                item["product"] = product_obj
                # Ensure final_price is up-to-date and cast to float/int if needed
                item["final_price"] = int(round(product_obj.get_price_by_discount())) 
                # Also make sure 'price' is a number if you use it for calculation
                item["price"] = float(product_obj.price) # Convert to float for calculation if needed

                # Calculate total price for this item
                item["total_price"] = item["final_price"] * item["qty"] 
                yield item
            else:
                # If product no longer exists, you might want to remove it from the cart
                # Or just skip it for this iteration. For clean-up, better remove.
                # It's good that you clean up in __init__ as well.
                pass 
                
    def calc_total_price(self):
        sum_price = 0 
        for item_id_str, item_data in self.shop_cart.items(): # Iterate over self.shop_cart values
            try:
                # Ensure final_price is treated as a number
                final_price = float(item_data['final_price']) # Use float for more precision
                quantity = int(item_data['qty'])
                sum_price += final_price * quantity
            except KeyError:
                print(f"Error: 'final_price' key missing for item {item_id_str}. Data: {item_data}")
                # Log this, or consider removing the problematic item from the cart
            except (ValueError, TypeError):
                print(f"Error: Price or Quantity not a number for item {item_id_str}. Data: {item_data}")
                # Log this, or consider removing the problematic item
        return sum_price

# # کدهایی که نیاز به دیتا بیس ندارد بهتره در این فایل مجزا نوشته بشه
# #Services
# from apps.products.models import Product
# import copy

# class ShopCart:
#     def __init__(self,request):
#         self.session=request.session
#         temp=self.session.get('shop_cart')
#         if not temp:
#             temp=self.session['shop_cart']={}
#         self.shop_cart=temp
#         self.count=len(self.shop_cart.keys())
 

#     # def add_to_shop_cart(self,product,qty):
#     #     product_id=str(product.id)
#     #     if product_id not in self.shop_cart:
#     #         self.shop_cart[product_id]={"qty":0,"price":product.price,"final_price":product.get_price_by_discount(),}
#     #     self.shop_cart[product_id]["qty"]+=int(qty)
#     #     self.count=len(self.shop_cart.keys())
#     #     self.save()
#     def add_to_shop_cart(self,product,qty):
#         product_id=str(product.id)
#         if product_id not in self.shop_cart:
#             self.shop_cart[product_id]={"qty":0,"price":product.price,"final_price":int(round(product.get_price_by_discount())),} 
#         self.shop_cart[product_id]["qty"]+=int(qty)
#         self.count=len(self.shop_cart.keys())
#         self.save()


#     def delete_from_shop_cart(self,product):
#         product_id=str(product.id)
#         del self.shop_cart[product_id]
#         self.save()

# # =====================================================================

    
#     def update(self, product_id_list, qty_list):
#     # استفاده از zip خواناتر و بهتر است
#         for product_id, qty in zip(product_id_list, qty_list):
#             if product_id in self.shop_cart:
#                 # بهتر است یک بررسی برای اطمینان از عددی بودن مقدار انجام شود
#                 try:
#                     self.shop_cart[product_id]['qty'] = int(qty)
#                 except (ValueError, TypeError):
#                     # اگر مقدار تعداد، عدد نبود، آن را نادیده بگیر
#                     pass
#         # save() فقط یک بار در انتها فراخوانی می‌شود
#         self.save()       
                
#     # def update(self,product_id_list,qty_list):
#     #     i=0
#     #     for product_id in product_id_list:
#     #         self.shop_cart[product_id]['qty']=int(qty_list[i])
#     #         i+=1
#     #     self.save()
        
        
#     # def update(self, product_id_list, qty_list):
#     #     for i, product_id in enumerate(product_id_list):
#     #         if product_id in self.shop_cart and i < len(qty_list):  # Check if product exists in cart
#     #             self.shop_cart[product_id]['qty'] = int(qty_list[i])
#     #     self.save()

# # =====================================================================
#     def save(self):
#         self.session.modified=True

        
        
#     # def __iter__(self):
#     #     list_ids=self.shop_cart.keys()
#     #     products=Product.objects.filter(id__in=list_ids)
#     #     temp=self.shop_cart.copy()
#     #     for product in products:
#     #         temp[str(product.id)]["product"]=product

#     #     for item in temp.values():
#     #         item["total_price"]=item["price"]*item["qty"]
#     #         yield item         


#     # def __iter__(self):
#     #     list_ids = self.shop_cart.keys()
#     #     products = Product.objects.filter(id__in=list_ids)
        
#     #     # 2. از copy.deepcopy به جای .copy() استفاده کنید
#     #     temp = copy.deepcopy(self.shop_cart)
        
#     #     for product in products:
#     #         # اکنون این تغییر فقط روی دیکشنری temp اعمال می‌شود و سشن اصلی امن است
#     #         temp[str(product.id)]["product"] = product

#     #     for item in temp.values():
#     #         item["total_price"] =int(item["final_price"])  * item["qty"]
#     #         yield item
            
#     def __iter__(self):
#         list_ids = self.shop_cart.keys()
#         products = Product.objects.filter(id__in=list_ids)
        
#         temp = copy.deepcopy(self.shop_cart)
        
#         for product in products:
#             temp[str(product.id)]["product"] = product

#         for item in temp.values():
#             item["total_price"] = int(item["final_price"]) * item["qty"] 
#             yield item
            
#     # def calc_total_price(self):
#     #     sum=0
#     #     for item in self.shop_cart.values():
#     #         sum+=int(item['final_price']) * item['qty']
#     #     return sum
    
#     def calc_total_price(self):
#         sum_price = 0 
#         for item in self.shop_cart.values():
#             sum_price += int(item['final_price']) * item['qty']
#         return sum_price
    