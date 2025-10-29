from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from .models import Business, BusinessKeywords, AdminUser, BusinessType, BusinessTypeKeyword
from .serializers import (
    BusinessSerializer, BusinessKeywordsSerializer, AdminUserSerializer,
    BusinessTypeSerializer, DetailedBusinessTypeSerializer
)
from .permissions import IsAdminOrReadOnly


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


class BusinessTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing business types.
    Public read access, admin-only write access.
    """
    queryset = BusinessType.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'code'  # Use code instead of pk for lookups

    def get_serializer_class(self):
        """Use detailed serializer for retrieve/list, basic for other operations"""
        if self.action in ['list', 'retrieve']:
            return DetailedBusinessTypeSerializer
        return BusinessTypeSerializer

    def get_queryset(self):
        """Annotate queryset with business and keyword counts"""
        queryset = BusinessType.objects.annotate(
            business_count=Count('businesses', distinct=True),
            keyword_count=Count('keywords', distinct=True)
        ).order_by('code')  # Add ordering to avoid pagination warning

        # Optional filter by is_active
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset

    @action(detail=True, methods=['get'])
    def keywords(self, request, code=None):
        """
        Get all keywords for a specific business type.
        GET /api/business-types/{code}/keywords/
        """
        business_type = self.get_object()
        keywords = BusinessTypeKeyword.objects.filter(
            business_type=business_type
        ).order_by('-weight', 'keyword')

        # Simple keyword serializer response
        data = [{
            'id': kw.id,
            'keyword': kw.keyword,
            'weight': kw.weight,
            'is_active': kw.is_active,
            'created_at': kw.created_at
        } for kw in keywords]

        return Response({
            'business_type': business_type.code,
            'total_keywords': len(data),
            'keywords': data
        })

    @action(detail=True, methods=['get'])
    def statistics(self, request, code=None):
        """
        Get relevance statistics for a specific business type.
        GET /api/business-types/{code}/statistics/

        Returns distribution of article relevance scores for this type.
        """
        business_type = self.get_object()

        from news.models import ArticleBusinessTypeRelevance

        # Get all relevance scores for this type
        relevance_scores = ArticleBusinessTypeRelevance.objects.filter(
            business_type=business_type
        ).values_list('relevance_score', flat=True)

        # Calculate statistics
        total_articles = len(relevance_scores)
        if total_articles == 0:
            return Response({
                'business_type': business_type.code,
                'total_articles': 0,
                'statistics': None
            })

        # Calculate distribution buckets
        scores_list = list(relevance_scores)
        avg_score = sum(scores_list) / total_articles
        high_relevance = len([s for s in scores_list if s >= 0.7])
        medium_relevance = len([s for s in scores_list if 0.4 <= s < 0.7])
        low_relevance = len([s for s in scores_list if s < 0.4])

        return Response({
            'business_type': business_type.code,
            'total_articles': total_articles,
            'statistics': {
                'average_score': round(avg_score, 3),
                'min_score': round(min(scores_list), 3),
                'max_score': round(max(scores_list), 3),
                'distribution': {
                    'high': {'count': high_relevance, 'percentage': round(high_relevance / total_articles * 100, 1)},
                    'medium': {'count': medium_relevance, 'percentage': round(medium_relevance / total_articles * 100, 1)},
                    'low': {'count': low_relevance, 'percentage': round(low_relevance / total_articles * 100, 1)},
                }
            }
        })