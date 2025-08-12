from django.urls import path
from . import views



app_name="account"
urlpatterns = [
    path('register/',views.RegisterUserView.as_view(),name="register"),
    path('verify/',views.VerifyResgiterCodeView.as_view(),name="verify"),
    path('login/',views.LoginUserView.as_view(),name="login"),
    path('logout/',views.LogoutUserView.as_view(),name="logout"),
    # path('userpanel/',views.UserPanelView.as_view(),name="userpanel"),
    path('change_password/',views.ChangePasswordView.as_view(),name="change_password"),
    path('remember_password/',views.RememberPasswordView.as_view(),name="remember_password"),

    path('userpanel', views.UserPanelView.as_view(),name='userpanel'),
    path('update-profile', views.UpdateProfileView.as_view(),name='update-profile'),
    path('show_last_orders', views.show_last_orders,name='show_last_orders'),
    # path('show_user_payments', views.show_user_payments,name='show_user_payments'),


    


    

]
