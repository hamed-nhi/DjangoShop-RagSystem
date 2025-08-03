from django.contrib import admin

from apps.warehouses.models import WarehouseType,Warehouse

# Register your models here.
@admin.register(WarehouseType)
class WarehouseTypeAdmin(admin.ModelAdmin):
    list_display = ('warehouse_type_title',)
    search_fields = ('warehouse_type_title',)
    list_filter = ('warehouse_type_title',)
    ordering = ('warehouse_type_title',)
    list_per_page = 20


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('warehouse_type', 'product', 'qty', 'price', 'register_date')
    search_fields = ('warehouse_type__warehouse_type_title', 'product__title')
    list_filter = ('warehouse_type', 'product')
    ordering = ('-register_date',)
    list_per_page = 20


