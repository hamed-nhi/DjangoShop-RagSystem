
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve 

urlpatterns = [
    path('admin/',admin.site.urls),
    path('',include("apps.main.urls", namespace='main')),
    path('accounts/',include("apps.accounts.urls",namespace="accounts")),
    path('products/',include("apps.products.urls",namespace="products")),
    path('orders/',include("apps.orders.urls",namespace="orders")),
    path('discounts/',include("apps.discounts.urls",namespace="discounts")),
    path('warehouses/',include("apps.warehouses.urls",namespace="warehouses")),
    path('csf/',include("apps.c_s_f.urls",namespace="csf")),
    path('ckeditor/',include("ckeditor_uploader.urls")),
    path('search/',include("apps.search.urls",namespace="search")),
    
    

    

]

#  ] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    # در حالت توسعه، از روش استاندارد جنگو استفاده کن
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # در حالت پروداکشن (یا تست با DEBUG=False)، از این مسیر برای سرو کردن فایل مدیا استفاده کن
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]

handler400 = 'apps.main.views.handler400'
handler403 = 'apps.main.views.handler403'
handler404 = 'apps.main.views.handler404'
handler500 = 'apps.main.views.handler500'
