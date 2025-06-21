from django.contrib import admin
from django.urls import path, include
from investapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('investapp.urls')),  # Your app routes
    path('invest/', views.invest, name='invest'),  # Custom investment endpoint
    path('withdraw/', views.withdraw, name='withdraw'),

]
