from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_routes, name='search_routes'),

    # Route Details
    path('route/<int:route_id>/', views.route_details, name='route_details'),

    # Reviews
    path('route/<int:route_id>/add_review/', views.add_review, name='add_review'),

    # Stage Details
    path('stage/<int:stage_id>/', views.stage_details, name='stage_details'),

    # Payments
    path('route/<int:route_id>/mpesa/', views.mpesa_pay, name='mpesa_pay'),
    path('route/<int:route_id>/cash/', views.cash_pay, name='cash_pay'),
]