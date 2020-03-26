from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from webapp import views

urlpatterns = [
    path('', views.api_root),
    path('ventilators/', views.VentilatorList.as_view(), name='ventilator-list'),
    path('ventilators/<int:pk>/', views.VentilatorDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
