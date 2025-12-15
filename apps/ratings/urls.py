"""URL configuration for ratings app."""
from django.urls import path
from . import views

app_name = 'ratings'

urlpatterns = [
    # API endpoints
    path('api/submit/', views.submit_rating, name='api_submit'),
    path('api/stylist/<int:stylist_id>/ratings/', views.stylist_ratings, name='api_stylist_ratings'),
    path('api/stylist/<int:stylist_id>/reviews/', views.stylist_reviews, name='api_stylist_reviews'),
    path('api/salon/<int:salon_id>/reviews/', views.salon_reviews, name='api_salon_reviews'),
    path('api/my-reviews/', views.my_reviews, name='api_my_reviews'),
]
