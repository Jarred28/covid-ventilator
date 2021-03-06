from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('home/', views.home, name='home'),
    path('ventilators/', views.VentilatorList.as_view(), name='ventilator-list'),
    path('order/requested', views.RequestedOrders.as_view(), name='requested-order'),
    path('order/supplied', views.SuppliedOrders.as_view(), name='supplied-order'),
    path('ventilators/approve/<batchid>/', views.approve_ventilators, name='ventilator-approve'),
    path('ventilators/<int:pk>/', views.VentilatorDetail.as_view(), name='ventilator-detail'),
    path('accounts/request_credentials/', views.RequestCredentials.as_view(), name='request-credentials'),
    path('call_back_reserve/<int:order_id>/', views.call_back_reserve, name='call-back-reserve'),
    path('order/request_reserve/<int:order_id>/', views.request_reserve, name='request-reserve'),
    path('deny_reserve/<int:order_id>/', views.deny_reserve, name='deny-reserve'),
    path('deploy_reserve/<int:order_id>/', views.deploy_reserve, name='deploy-reserve'),
    path('system/dashboard/', views.Dashboard.as_view(), name='sys-dashboard'),
    path('system/settings/', views.SystemSettings.as_view(), name='sys-settings'),
    path('system/demand/', views.SystemDemand.as_view(), name='sys-demand'),
    path('system/supply/', views.SystemSupply.as_view(), name='sys-supply'),
    path('system/source-reserve/', views.SystemSourceReserve.as_view(), name='sys-source-reserve'),
    path('system/destination-reserve/', views.SystemDestinationReserve.as_view(), name='sys-destination-reserve'),
    path('hospitals/', views.HospitalCEO.as_view(), name='ceo-dashboard'),
    path('hospitals/approve/<batchid>/', views.HospitalCEOApprove.as_view(), name='ceo-approve'),
    path('hospitals/offer/<batchid>/', views.HospitalCEOSharedOffer.as_view(), name='ceo-sharedoffer'),
    path('reset_db/', views.reset_db, name='reset-db')
]

urlpatterns = format_suffix_patterns(urlpatterns)
