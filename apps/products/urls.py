from django.urls import path
from . import views



app_name="products" # that namespace we describe in Main url > we should use it here 
urlpatterns = [
    path('cheap_products/',views.get_cheap_products,name="cheap_products"),
    path('last_products/',views.get_last_products,name="last_products"),
    path('get_popular_product_groups/',views.get_popular_product_groups,name="get_popular_product_groups"),
    path('product_details/<slug:slug>/',views.ProductDeatailView.as_view(),name='product_details'),
    path('related_products/<slug:slug>/',views.get_related_products,name='related_products'),

    path('product_groups/',views.ProductsGroupsView.as_view(),name='product_groups'),
    path('products_of_group/<slug:slug>/',views.ProductByGroupsView.as_view(),name='products_of_group'),
    path('ajax_admin/',views.get_filter_value_for_feature,name='filter_value_for_feature'),
    path('products_groups_partials',views.get_product_groups,name='products_groups_partials'),
    path('brands_partials/<slug:slug>/',views.get_brands,name='brands_partials'),
    path('feature_partials/<slug:slug>/',views.get_feature_for_filter,name='feature_partials'),
    path('compare/', views.show_compare_list_view, name='show_compare_list'),

    # URL for the PARTIAL table. Change the name here.
    path('compare-table/', views.compare_table_partial, name='compare_table'), # Changed from 'compare_table_partial'
    
    # URLs for the AJAX functions
    path('add_to_compare_list/', views.add_to_compare_list, name='add_to_compare_list'),
    # path('delete_from_compare_list/', views.delete_from_compare_list, name='delete_from_compare_list'),
    # path('delete_from_compare_list/', views.delete_from_compare_list, name='remove_from_compare'),
    path('delete_from_compare_list/', views.delete_from_compare_list, name='remove_from_compare'),

    path('status_of_compare_list/', views.status_of_compare_list, name='status_of_compare_list'),
    path('all_product_groups/', views.AllProductGroupsView.as_view(), name='all_product_groups'), 
    path('best_selling_products/', views.get_best_selling_products, name='best_selling_products'),


]

