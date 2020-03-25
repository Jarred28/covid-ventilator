from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

urlpatterns = [
    path('', LoginView.as_view()),
    path('ventilators/', views.ventilator_list),
    path('ventilators/<int:pk>/', views.ventilator_detail),
]
