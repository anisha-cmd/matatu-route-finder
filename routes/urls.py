from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_routes, name='search_routes'),
    path('route/<int:route_id>/', views.route_details, name='route_details'),
    path('stage/<int:stage_id>/', views.stage_details, name='stage_details'),
    path('route/<int:route_id>/reviews/', views.ad_review, name='ad_review'),
    path('route/<int:route_id>/add_review/', views.add_review, name='add_review'),
    path('route/<int:route_id>/mpesa/', views.mpesa_pay, name='mpesa_pay'),
]


