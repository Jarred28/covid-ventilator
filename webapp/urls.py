from django.urls import path
from django.contrib.auth.views import LoginView
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('', LoginView.as_view()),
    path('home/', views.home, name='home'),
    path('ventilators/', views.VentilatorList.as_view(), name='ventilator-list'),
    path('ventilators/<int:pk>/', views.VentilatorDetail.as_view(), name='ventilator-detail'),
    path('accounts/request_credentials', views.RequestCredentials.as_view(), name='request-credentials'),
    path('system/', views.SystemSettings.as_view(), name='sys-settings'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
