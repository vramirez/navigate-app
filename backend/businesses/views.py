from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.decorators import action
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