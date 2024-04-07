from django.contrib.auth import views
from django.urls import path, include

from main.views import index
from main.views_api import PingManager


urlpatterns = [
    path('', index, name='index'),
    path('login/', views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('api/', include([
        path('ping/<str:ip>/', PingManager.as_view()),
    ])),
]
