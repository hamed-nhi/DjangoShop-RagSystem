from django.urls import path
from . import views



app_name="account" # that namespace we describe in Main url > we should use it here 
urlpatterns = [
    # path('',views.index,name=""),
    path('register/',views.RegisterUserView.as_view(),name="register"),
    path('verify/',views.VerifyResgiterCodeView.as_view(),name="verify"),
    path('login/',views.LoginUserView.as_view(),name="login"),
    path('logout/',views.LogoutUserView.as_view(),name="logout"),
    path('userpanel/',views.UserPanelView.as_view(),name="userpanel"),
    

]
