from django.urls import path
from . import views



app_name="account" # that namespace we describe in Main url > we should use it here 
urlpatterns = [
    # path('',views.index,name=""),
    path('register/',views.RegisterUserView.as_view(),name="register"),
    path('verify/',views.VerifyResgiterCodeView.as_view(),name="verify"),
    
]
