


import django_filters

class ProductFilter(django_filters.FilterSet):
    # نام فیلد در مدل
    # بر اساس کوچکتر یا مساوی از عدد انتخابی کاربر
    price=django_filters.NumberFilter(field_name='price',lookup_expr='lte')
