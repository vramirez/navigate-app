from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Recommendation, RecommendationFeedback, RecommendationTemplate
from .serializers import (
    RecommendationSerializer, RecommendationFeedbackSerializer,
    RecommendationTemplateSerializer
)


class RecommendationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing recommendations
    """
    queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description', 'category']
    
    def get_queryset(self):
        queryset = Recommendation.objects.select_related('business', 'content_type')
        
        # Filter parameters
        business_id = self.request.query_params.get('business_id')
        category = self.request.query_params.get('category')
        priority = self.request.query_params.get('priority')
        status = self.request.query_params.get('status')
        is_archived = self.request.query_params.get('is_archived')
        min_confidence = self.request.query_params.get('min_confidence')
        
        if business_id:
            queryset = queryset.filter(business_id=business_id)
        if category:
            queryset = queryset.filter(category=category)
        if priority:
            queryset = queryset.filter(priority=priority)
        if status:
            queryset = queryset.filter(status=status)
        if is_archived is not None:
            queryset = queryset.filter(is_archived=is_archived.lower() == 'true')
        if min_confidence:
            try:
                queryset = queryset.filter(confidence_score__gte=float(min_confidence))
            except ValueError:
                pass
                
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def urgent(self, request):
        """Get urgent recommendations"""
        recommendations = self.get_queryset().filter(
            priority='urgent',
            status='pending',
            is_archived=False
        )
        serializer = self.get_serializer(recommendations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def high_impact(self, request):
        """Get high impact recommendations"""
        recommendations = self.get_queryset().filter(
            impact_score__gte=0.8,
            is_archived=False
        )
        serializer = self.get_serializer(recommendations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_business(self, request):
        """Get recommendations grouped by business"""
        business_id = request.query_params.get('business_id')
        if not business_id:
            return Response({'error': 'business_id parameter required'}, status=400)
            
        recommendations = self.get_queryset().filter(
            business_id=business_id,
            is_archived=False
        )
        serializer = self.get_serializer(recommendations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get recommendation statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'by_priority': queryset.values('priority').annotate(count=Count('id')),
            'by_status': queryset.values('status').annotate(count=Count('id')),
            'by_category': queryset.values('category').annotate(count=Count('id')),
            'avg_confidence': queryset.aggregate(avg_confidence=Avg('confidence_score')),
            'avg_impact': queryset.aggregate(avg_impact=Avg('impact_score')),
        }
        
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a recommendation as read"""
        recommendation = self.get_object()
        recommendation.is_read = True
        recommendation.save(update_fields=['is_read'])
        return Response({'status': 'marked as read'})
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a recommendation"""
        recommendation = self.get_object()
        recommendation.is_archived = True
        recommendation.save(update_fields=['is_archived'])
        return Response({'status': 'archived'})


class RecommendationFeedbackViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing recommendation feedback
    """
    queryset = RecommendationFeedback.objects.all()
    serializer_class = RecommendationFeedbackSerializer
    
    def get_queryset(self):
        queryset = RecommendationFeedback.objects.select_related('recommendation')
        
        recommendation_id = self.request.query_params.get('recommendation_id')
        min_rating = self.request.query_params.get('min_rating')
        is_implemented = self.request.query_params.get('is_implemented')
        
        if recommendation_id:
            queryset = queryset.filter(recommendation_id=recommendation_id)
        if min_rating:
            try:
                queryset = queryset.filter(rating__gte=int(min_rating))
            except ValueError:
                pass
        if is_implemented is not None:
            queryset = queryset.filter(is_implemented=is_implemented.lower() == 'true')
            
        return queryset.order_by('-created_at')


class RecommendationTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing recommendation templates
    """
    queryset = RecommendationTemplate.objects.all()
    serializer_class = RecommendationTemplateSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description_template', 'trigger_keywords']
    
    def get_queryset(self):
        queryset = RecommendationTemplate.objects.all()
        
        category = self.request.query_params.get('category')
        action_type = self.request.query_params.get('action_type')
        business_type = self.request.query_params.get('business_type')
        city = self.request.query_params.get('city')
        is_active = self.request.query_params.get('is_active')
        
        if category:
            queryset = queryset.filter(category=category)
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        if business_type:
            queryset = queryset.filter(business_types__icontains=business_type)
        if city:
            queryset = queryset.filter(cities__icontains=city)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        return queryset.order_by('-created_at')