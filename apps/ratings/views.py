"""
Views for ratings and reviews with anonymous display.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Rating, Review
from .serializers import (
    AnonymousRatingSerializer, AnonymousReviewSerializer,
    MyRatingSerializer, MyReviewSerializer, SubmitRatingSerializer
)
from apps.accounts.models import StylistProfile
from apps.salons.models import Salon
from apps.accounts.permissions import IsCustomer


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsCustomer])
def submit_rating(request):
    """
    Submit rating and optional review for completed appointment.
    
    POST /ratings/api/submit/
    Body: {
        appointment_id: int,
        rating: int (1-5),
        review_text: string (optional)
    }
    """
    serializer = SubmitRatingSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        result = serializer.save()
        
        return Response({
            'message': 'امتیاز و نظر شما ثبت شد. از شما متشکریم!',
            'rating_id': result['rating'].id,
            'review_id': result['review'].id if result['review'] else None
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def stylist_ratings(request, stylist_id):
    """
    Get anonymous ratings for a stylist.
    
    GET /ratings/api/stylist/<id>/ratings/
    """
    stylist = get_object_or_404(StylistProfile, id=stylist_id)
    ratings = Rating.objects.filter(stylist=stylist).order_by('-created_at')
    
    serializer = AnonymousRatingSerializer(ratings, many=True)
    
    # Calculate average
    if ratings.exists():
        avg_rating = sum(r.rating for r in ratings) / len(ratings)
    else:
        avg_rating = 0
    
    return Response({
        'stylist_id': stylist_id,
        'stylist_name': stylist.full_name,
        'average_rating': round(avg_rating, 2),
        'total_ratings': ratings.count(),
        'ratings': serializer.data
    })


@api_view(['GET'])
def stylist_reviews(request, stylist_id):
    """
    Get anonymous reviews for a stylist.
    
    GET /ratings/api/stylist/<id>/reviews/
    """
    stylist = get_object_or_404(StylistProfile, id=stylist_id)
    reviews = Review.objects.filter(
        stylist=stylist,
        is_approved=True
    ).order_by('-created_at')
    
    serializer = AnonymousReviewSerializer(reviews, many=True)
    
    return Response({
        'stylist_id': stylist_id,
        'stylist_name': stylist.full_name,
        'total_reviews': reviews.count(),
        'reviews': serializer.data
    })


@api_view(['GET'])
def salon_reviews(request, salon_id):
    """
    Get all anonymous reviews for a salon (from all its stylists).
    
    GET /ratings/api/salon/<id>/reviews/
    """
    salon = get_object_or_404(Salon, id=salon_id)
    
    # Get all reviews for stylists in this salon
    reviews = Review.objects.filter(
        stylist__salon=salon,
        is_approved=True
    ).order_by('-created_at')
    
    serializer = AnonymousReviewSerializer(reviews, many=True)
    
    return Response({
        'salon_id': salon_id,
        'salon_name': salon.name,
        'average_rating': float(salon.average_rating),
        'total_ratings': salon.total_ratings,
        'total_reviews': reviews.count(),
        'reviews': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsCustomer])
def my_reviews(request):
    """
    Get current customer's own ratings and reviews.
    
    GET /ratings/api/my-reviews/
    """
    customer = request.user.customer_profile
    
    ratings = Rating.objects.filter(customer=customer).order_by('-created_at')
    reviews = Review.objects.filter(customer=customer).order_by('-created_at')
    
    ratings_serializer = MyRatingSerializer(ratings, many=True)
    reviews_serializer = MyReviewSerializer(reviews, many=True)
    
    return Response({
        'ratings_count': ratings.count(),
        'reviews_count': reviews.count(),
        'ratings': ratings_serializer.data,
        'reviews': reviews_serializer.data
    })
