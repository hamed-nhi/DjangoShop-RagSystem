from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.products.models import Product


# ----------------------------------------------------------------------------------------------
class Coupon(models.Model):
    coupon_code= models.CharField(max_length=100, unique=True,verbose_name="کد تخفیف")
    start_date = models.DateTimeField(verbose_name="تاریخ شروع")
    end_date = models.DateTimeField(verbose_name="تاریخ پایان")
    discount = models.IntegerField(verbose_name="درصد تخفیف", validators=[MinValueValidator(0), MaxValueValidator(100)])
    is_active = models.BooleanField(default=False, verbose_name=",وضعیت فعال بودن کد تخفیف")

    
    class Meta:
        verbose_name = "کد تخفیف"
        verbose_name_plural = "کدهای تخفیف"

    def __str__(self):
        return self.coupon_code
# ----------------------------------------------------------------------------------------------


class DiscountBasket(models.Model):
    discount_title= models.CharField(max_length=100, verbose_name="عنوان تخفیف سبد خرید")

    start_date = models.DateTimeField(verbose_name="تاریخ شروع")
    end_date = models.DateTimeField(verbose_name="تاریخ پایان")
    discount = models.IntegerField(verbose_name="درصد تخفیف", validators=[MinValueValidator(0), MaxValueValidator(100)])
    is_active = models.BooleanField(default=False, verbose_name=",وضعیت فعال بودن کد تخفیف")

    
    class Meta:
        verbose_name = "سبد تخفیف"
        verbose_name_plural = "سبدهای تخفیف"

    def __str__(self):
        return self.discount_title
# ----------------------------------------------------------------------------------------------
    
class DiscountBasketDetails(models.Model):
    discount_basket = models.ForeignKey(DiscountBasket, on_delete=models.CASCADE, verbose_name="سبد تخفیف",related_name="discount_basket_details1")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="محصول",related_name="discount_basket_details2")

    class Meta:
        verbose_name = "جزئیات سبد تخفیف"
        verbose_name_plural = "جزئیات سبدهای تخفیف"

    def __str__(self):
        return f"{self.discount_basket} - {self.product}"
    
# ----------------------------------------------------------------------------------------------
