from django.urls import path
from webapp import views

urlpatterns = [
    path('ventilators/', views.ventilator_list),
    path('ventilators/<int:pk>/', views.ventilator_detail),
]
