from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('invest/', views.invest, name='invest'),
    path('deposit/<int:inv_id>/', views.deposit, name='deposit'),  # 👈 add this
    path('confirm/<int:inv_id>/', views.confirm_deposit, name='confirm_deposit')

]
