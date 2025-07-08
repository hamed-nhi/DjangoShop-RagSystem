from django.urls import path
from . import views



app_name="products" # that namespace we describe in Main url > we should use it here 
urlpatterns = [
    path('cheap_products/',views.get_cheap_products,name="cheap_products"),
    path('last_products/',views.get_last_products,name="last_products"),
    path('get_popular_product_groups/',views.get_popular_product_groups,name="get_popular_product_groups"),
    path('product_details/<slug:slug>/',views.ProductDeatailView.as_view(),name='product_details'),
    path('related_products/<slug:slug>/',views.get_related_products,name='related_products'),
    path('product_groups/',views.ProductGroupsView.as_view(),name='product_groups'),
    path('products_of_group/<slug:slug>/',views.ProductsByGroupView.as_view(),name='products_of_group'),


]

