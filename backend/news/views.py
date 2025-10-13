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
        queryset = NewsArticle.objects.select_related('source')

        # Filter parameters
        city = self.request.query_params.get('city')
        primary_city = self.request.query_params.get('primary_city')  # ML extracted city
        event_type = self.request.query_params.get('event_type')  # Legacy field
        event_type_detected = self.request.query_params.get('event_type_detected')  # ML field
        is_processed = self.request.query_params.get('is_processed')
        days_ago = self.request.query_params.get('days_ago')
        min_relevance = self.request.query_params.get('min_relevance')  # Legacy field
        business_suitability_score__gte = self.request.query_params.get('business_suitability_score__gte')  # ML field
        features_extracted = self.request.query_params.get('features_extracted')
        event_scale = self.request.query_params.get('event_scale')

        # Temporal filtering (Phase 3 - task-11)
        exclude_past_events = self.request.query_params.get('exclude_past_events')
        event_start_date_gte = self.request.query_params.get('event_start_date_gte')
        event_start_date_lte = self.request.query_params.get('event_start_date_lte')

        # Geographic filtering (Phase 3 - task-11)
        source_country = self.request.query_params.get('source_country')

        # City filtering (legacy - source city or event location)
        if city:
            queryset = queryset.filter(
                Q(source__city=city) | Q(event_location__icontains=city)
            )

        # ML-extracted city filtering (Phase 3 - task-4)
        if primary_city:
            queryset = queryset.filter(primary_city=primary_city)

        # Event type filtering
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        if event_type_detected:
            queryset = queryset.filter(event_type_detected=event_type_detected)

        # ML features
        if features_extracted is not None:
            queryset = queryset.filter(features_extracted=features_extracted.lower() == 'true')
        if event_scale:
            queryset = queryset.filter(event_scale=event_scale)

        # Processing status
        if is_processed is not None:
            queryset = queryset.filter(is_processed=is_processed.lower() == 'true')

        # Date filtering (published date)
        if days_ago:
            try:
                date_threshold = timezone.now() - timedelta(days=int(days_ago))
                queryset = queryset.filter(published_date__gte=date_threshold)
            except ValueError:
                pass

        # Temporal filtering (event date) - task-11
        # Exclude past events (but keep articles without event dates)
        if exclude_past_events and exclude_past_events.lower() == 'true':
            queryset = queryset.filter(
                Q(event_start_datetime__gte=timezone.now()) | Q(event_start_datetime__isnull=True)
            )

        # Event date range filtering
        if event_start_date_gte:
            try:
                queryset = queryset.filter(event_start_datetime__gte=event_start_date_gte)
            except ValueError:
                pass
        if event_start_date_lte:
            try:
                queryset = queryset.filter(event_start_datetime__lte=event_start_date_lte)
            except ValueError:
                pass

        # Geographic filtering by source country - task-11
        if source_country:
            queryset = queryset.filter(source__country=source_country)

        # Relevance/suitability scores
        if min_relevance:
            try:
                queryset = queryset.filter(business_relevance_score__gte=float(min_relevance))
            except ValueError:
                pass
        if business_suitability_score__gte:
            try:
                queryset = queryset.filter(business_suitability_score__gte=float(business_suitability_score__gte))
            except ValueError:
                pass

        return queryset.order_by('-published_date')
    
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
        articles = self.get_queryset().filter(business_relevance_score__gt=0.7)[:20]
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