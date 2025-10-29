from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Business, BusinessKeywords, AdminUser
from .serializers import BusinessSerializer, BusinessKeywordsSerializer, AdminUserSerializer


class BusinessViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing businesses
    """
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    
    def get_queryset(self):
        queryset = Business.objects.all()
        city = self.request.query_params.get('city')
        business_type = self.request.query_params.get('type')
        
        if city:
            queryset = queryset.filter(city=city)
        if business_type:
            queryset = queryset.filter(business_type=business_type)
            
        return queryset
    
    @action(detail=True, methods=['get'])
    def recommendations(self, request, pk=None):
        """Get recommendations for a specific business"""
        business = self.get_object()
        recommendations = business.recommendations.all()
        from recommendations.serializers import RecommendationSerializer
        serializer = RecommendationSerializer(recommendations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def keywords(self, request, pk=None):
        """Get keywords for a specific business"""
        business = self.get_object()
        keywords = business.keywords.all()
        serializer = BusinessKeywordsSerializer(keywords, many=True)
        return Response(serializer.data)


class BusinessKeywordsListCreateView(generics.ListCreateAPIView):
    """
    List and create business keywords
    """
    serializer_class = BusinessKeywordsSerializer
    
    def get_queryset(self):
        business_id = self.request.query_params.get('business_id')
        if business_id:
            return BusinessKeywords.objects.filter(business_id=business_id)
        return BusinessKeywords.objects.all()


class AdminUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing admin users
    """
    queryset = AdminUser.objects.all()
    serializer_class = AdminUserSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Get authenticated user's profile including their business

    Returns:
        {
            'user': { 'id', 'username', 'email' },
            'business': { 'id', 'name', 'business_type', 'business_type_details', ... },
            'business_type_code': 'pub'  # Quick access to type code
        }
    """
    user = request.user

    # Get user's business (assuming one business per user for now)
    try:
        business = Business.objects.select_related('business_type').get(
            owner=user,
            is_active=True
        )
        business_data = BusinessSerializer(business).data
        business_type_code = business.business_type.code
    except Business.DoesNotExist:
        business_data = None
        business_type_code = None

    return Response({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        },
        'business': business_data,
        'business_type_code': business_type_code
    })