from rest_framework import viewsets, generics, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import NewsSource, NewsArticle, SocialMediaPost, ManualNewsEntry
from .serializers import (
    NewsSourceSerializer, NewsArticleSerializer,
    SocialMediaPostSerializer, ManualNewsEntrySerializer
)


class NewsSourceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing news sources
    TODO Phase 4: Restore authentication requirement
    """
    queryset = NewsSource.objects.all()
    serializer_class = NewsSourceSerializer
    permission_classes = [AllowAny]  # Temporary for MVP - allows frontend testing
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'city']
    
    def get_queryset(self):
        queryset = NewsSource.objects.all()
        city = self.request.query_params.get('city')
        is_active = self.request.query_params.get('is_active')
        
        if city:
            queryset = queryset.filter(city=city)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        return queryset.order_by('-created_at')


class NewsArticleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing news articles
    TODO Phase 4: Restore authentication requirement
    """
    queryset = NewsArticle.objects.all()
    serializer_class = NewsArticleSerializer
    permission_classes = [AllowAny]  # Temporary for MVP - allows frontend testing
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content', 'extracted_keywords']
    
    def get_queryset(self):
        """
        Filter articles by business type relevance

        Query params:
            - business_type (required): Filter by business type code (pub, restaurant, etc.)
            - min_relevance (optional): Override default threshold for business type
            - exclude_past_events (optional, default true): Filter out events older than 7 days
        """
        from businesses.models import BusinessType
        from django.db.models import F

        # Get business_type parameter (required)
        business_type_code = self.request.query_params.get('business_type')

        if not business_type_code:
            # Return empty queryset if no business type specified
            return NewsArticle.objects.none()

        # Get BusinessType object to access thresholds
        try:
            business_type = BusinessType.objects.get(code=business_type_code, is_active=True)
        except BusinessType.DoesNotExist:
            return NewsArticle.objects.none()

        # Get min_relevance (use business type default if not provided)
        min_relevance = self.request.query_params.get('min_relevance')
        if min_relevance:
            min_relevance = float(min_relevance)
        else:
            min_relevance = business_type.min_relevance_threshold

        # Base queryset: articles with relevance scores for this business type
        queryset = NewsArticle.objects.filter(
            type_relevance_scores__business_type=business_type,
            type_relevance_scores__relevance_score__gte=min_relevance
        ).distinct()

        # Annotate with user's relevance score for sorting/display
        queryset = queryset.annotate(
            user_relevance=F('type_relevance_scores__relevance_score')
        )

        # Event date filter: only events within last 7 days OR upcoming events
        exclude_past = self.request.query_params.get('exclude_past_events', 'true')
        if exclude_past.lower() == 'true':
            seven_days_ago = timezone.now() - timedelta(days=7)
            queryset = queryset.filter(
                Q(event_start_datetime__gte=seven_days_ago) |
                Q(event_start_datetime__isnull=True)
            )

        # Order by relevance (highest first), then by published date
        queryset = queryset.order_by('-user_relevance', '-published_date')

        return queryset
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent articles from the last 7 days"""
        date_threshold = timezone.now() - timedelta(days=7)
        articles = self.get_queryset().filter(published_date__gte=date_threshold)[:20]
        serializer = self.get_serializer(articles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def high_relevance(self, request):
        """Get high relevance articles (score > 0.7)"""
        # TODO task-18.5: Replace with per-type relevance filtering
        articles = self.get_queryset()[:20]
        serializer = self.get_serializer(articles, many=True)
        return Response(serializer.data)


class SocialMediaPostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing social media posts
    """
    queryset = SocialMediaPost.objects.all()
    serializer_class = SocialMediaPostSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['content', 'author_username', 'extracted_keywords']
    
    def get_queryset(self):
        queryset = SocialMediaPost.objects.all()
        
        platform = self.request.query_params.get('platform')
        location = self.request.query_params.get('location')
        min_relevance = self.request.query_params.get('min_relevance')
        
        if platform:
            queryset = queryset.filter(platform=platform)
        if location:
            queryset = queryset.filter(location_tags__icontains=location)
        if min_relevance:
            try:
                queryset = queryset.filter(business_relevance_score__gte=float(min_relevance))
            except ValueError:
                pass
                
        return queryset.order_by('-published_date')


class ManualNewsEntryListCreateView(generics.ListCreateAPIView):
    """
    List and create manual news entries
    """
    queryset = ManualNewsEntry.objects.all()
    serializer_class = ManualNewsEntrySerializer
    
    def get_queryset(self):
        queryset = ManualNewsEntry.objects.all()
        city = self.request.query_params.get('city')
        event_type = self.request.query_params.get('event_type')
        
        if city:
            queryset = queryset.filter(city=city)
        if event_type:
            queryset = queryset.filter(event_type=event_type)
            
        return queryset.order_by('-created_at')