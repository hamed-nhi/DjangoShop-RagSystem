from django.contrib import admin
from .models import Coupon, DiscountBasket, DiscountBasketDetails



@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):  
    list_display = ('coupon_code', 'start_date', 'end_date', 'discount', 'is_active')
    search_fields = ('coupon_code',)
    list_filter = ('is_active', 'start_date', 'end_date')
    ordering = ('-start_date',)


class DiscountBasketDetailsInline(admin.TabularInline):
    model = DiscountBasketDetails
    extra = 3
    # verbose_name = "جزئیات سبد تخفیف"
    # verbose_name_plural = "جزئیات سبدهای تخفیف"

@admin.register(DiscountBasket)
class DiscountBasketAdmin(admin.ModelAdmin):
    list_display = ('discount_title', 'start_date', 'end_date', 'discount', 'is_active')
    search_fields = ('discount_title',)
    list_filter = ('is_active', 'start_date', 'end_date')
    ordering = ('-start_date',)
    inlines = [DiscountBasketDetailsInline]


