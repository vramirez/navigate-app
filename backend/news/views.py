from rest_framework import viewsets, generics, filters
from rest_framework.decorators import action
from rest_framework.response import Response
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
    """
    queryset = NewsSource.objects.all()
    serializer_class = NewsSourceSerializer
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
    """
    queryset = NewsArticle.objects.all()
    serializer_class = NewsArticleSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content', 'extracted_keywords']
    
    def get_queryset(self):
        queryset = NewsArticle.objects.select_related('source')
        
        # Filter parameters
        city = self.request.query_params.get('city')
        event_type = self.request.query_params.get('event_type')
        is_processed = self.request.query_params.get('is_processed')
        days_ago = self.request.query_params.get('days_ago')
        min_relevance = self.request.query_params.get('min_relevance')
        
        if city:
            queryset = queryset.filter(
                Q(source__city=city) | Q(event_location__icontains=city)
            )
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        if is_processed is not None:
            queryset = queryset.filter(is_processed=is_processed.lower() == 'true')
        if days_ago:
            try:
                date_threshold = timezone.now() - timedelta(days=int(days_ago))
                queryset = queryset.filter(published_date__gte=date_threshold)
            except ValueError:
                pass
        if min_relevance:
            try:
                queryset = queryset.filter(business_relevance_score__gte=float(min_relevance))
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