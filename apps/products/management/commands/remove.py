from apps.products.models import Feature, ProductFeature, Product

# مرحله ۱: پیدا کردن Feature مربوط به price
price_feature = Feature.objects.filter(feature_name__iexact='price').first()

if price_feature:
    # مرحله ۲: گرفتن همه ProductFeatureهایی که به price مربوط هستند
    price_features = ProductFeature.objects.filter(feature=price_feature)

    count = 0
    for pf in price_features:
        try:
            price_value = int(str(pf.value).replace(',', '').strip())
            pf.product.price = price_value
            pf.product.save()
            count += 1
        except ValueError:
            print(f"خطا در تبدیل قیمت: {pf.value}")
    
    print(f"✅ قیمت {count} محصول با موفقیت منتقل شد.")
else:
    print("❌ ویژگی 'price' پیدا نشد.")
