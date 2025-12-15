from rest_framework import generics, permissions
from .models import Salon
from .serializers import SalonSerializer

class SalonListAPIView(generics.ListAPIView):
    """
    API endpoint to list approved salons.
    Supports filtering by gender for logged-in customers.
    """
    serializer_class = SalonSerializer
    permission_classes = [permissions.AllowAny] # Allow browsing without login (optional)

    def get_queryset(self):
        queryset = Salon.objects.approved()
        
        # Gender filtering if user is authenticated customer
        if self.request.user.is_authenticated and self.request.user.user_type == 'customer':
            try:
                gender = self.request.user.customer_profile.gender
                queryset = queryset.for_gender(gender)
            except AttributeError:
                pass
                
        return queryset

class SalonDetailAPIView(generics.RetrieveAPIView):
    """
    API endpoint for salon details.
    """
    queryset = Salon.objects.approved()
    serializer_class = SalonSerializer
    permission_classes = [permissions.AllowAny]
