from .models import Product

class CompareProduct:
    def __init__(self, request):
        """
        مقداردهی اولیه سبد مقایسه از سشن
        """
        self.session = request.session
        compare_data = self.session.get('compare')
        if not compare_data:
            # اگر سبد مقایسه وجود نداشت، یک دیکشنری خالی بساز
            compare_data = self.session['compare'] = {}
        self.compare = compare_data

    def add(self, product_id, product_group_id):
        """
        افزودن یک محصول به سبد مقایسه با بررسی گروه محصول
        """
        product_id_str = str(product_id)
        
        # اگر لیست مقایسه خالی است، محصول را مستقیماً اضافه کن
        if not self.compare:
            self.compare[product_id_str] = {'group_id': str(product_group_id)}
            self.save()
            return {"status": "success", "message": "کالا با موفقیت به لیست مقایسه اضافه شد."}

        # اگر لیست خالی نیست، بررسی کن گروه محصول آیتم جدید با آیتم‌های قبلی یکی باشد
        # گروه محصول اولین آیتم موجود در لیست را به عنوان معیار در نظر می‌گیریم
        existing_group_id = next(iter(self.compare.values()))['group_id']
        
        if str(product_group_id) != existing_group_id:
            return {"status": "error", "message": "فقط کالاهایی از یک گروه یکسان را می‌توان مقایسه کرد."}
        
        # اگر گروه محصول یکی بود، و محصول از قبل وجود نداشت، آن را اضافه کن
        if product_id_str not in self.compare:
            self.compare[product_id_str] = {'group_id': str(product_group_id)}
            self.save()
            return {"status": "success", "message": "کالا با موفقیت به لیست مقایسه اضافه شد."}
        else:
            return {"status": "info", "message": "این کالا از قبل در لیست مقایسه وجود دارد."}

    def delete(self, product_id):
        """
        حذف یک محصول از سبد مقایسه
        """
        product_id_str = str(product_id)
        if product_id_str in self.compare:
            del self.compare[product_id_str]
            self.save()

    def save(self):
        """
        ذخیره تغییرات در سشن
        """
        self.session.modified = True

    def clear(self):
        """
        پاک کردن کامل سبد مقایسه از سشن
        """
        if 'compare' in self.session:
            del self.session['compare']
            self.save()

    def __len__(self):
        """
        تعداد آیتم‌های موجود در سبد مقایسه را برمی‌گرداند
        """
        return len(self.compare)

    def get_products(self):
        """
        لیست اشیاء محصولات موجود در سبد مقایسه را از دیتابیس واکشی می‌کند
        """
        product_ids = self.compare.keys()
        return Product.objects.filter(id__in=product_ids)


# class CompareProduct:
#     def __init__(self, request):
#         self.session = request.session
#         compare_product= self.session.get('compare_product')
#         if not compare_product:
#             compare_product = self.session['compare_product'] = []
#         self.compare_product = compare_product
#         self.count = len(self.compare_product)

# #-------------------------------------------------------------------------------

# def __iter__(self):
#     compare_product = self.compare_product.copy()
#     for item in compare_product:
#         yield item

# #-------------------------------------------------------------------------------

# def add_to_compare_product(self, productid):
#     productid = int(productid)   
#     if productid not in self.compare_product:
#         self.compare_product.append(productid)
#     self.count = len(self.compare_product)
#     self.session.modified = True

# #-------------------------------------------------------------------------------

# def delete_from_compare_product(self, productid):
#     self.compare_product.remove(int(productid))
#     self.ssession.modified = True

# #-------------------------------------------------------------------------------
# def clear_compare(self):
#     del self.session['compare_product']
#     self.session.modified = True