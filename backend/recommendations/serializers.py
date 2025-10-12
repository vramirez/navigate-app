from rest_framework import serializers
from .models import Recommendation, RecommendationFeedback, RecommendationTemplate


class RecommendationSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(source='business.name', read_only=True)
    content_type_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Recommendation
        fields = [
            'id', 'business', 'business_name', 'content_type', 'object_id',
            'content_type_name', 'title', 'description', 'category',
            'action_type', 'priority', 'confidence_score', 'impact_score',
            'effort_score', 'recommended_start_date', 'recommended_end_date',
            'estimated_duration_hours', 'reasoning', 'resources_needed',
            'expected_outcomes', 'is_viewed', 'is_accepted', 'is_implemented',
            'user_feedback', 'user_rating', 'expires_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_content_type_name(self, obj):
        if obj.content_type:
            return obj.content_type.model
        return None


class RecommendationFeedbackSerializer(serializers.ModelSerializer):
    recommendation_title = serializers.CharField(source='recommendation.title', read_only=True)
    
    class Meta:
        model = RecommendationFeedback
        fields = [
            'id', 'recommendation', 'recommendation_title', 'rating',
            'usefulness_score', 'implementation_difficulty', 'actual_impact',
            'comments', 'is_implemented', 'implementation_date', 'created_at'
        ]
        read_only_fields = ['created_at']


class RecommendationTemplateSerializer(serializers.ModelSerializer):
    usage_count = serializers.SerializerMethodField()
    
    class Meta:
        model = RecommendationTemplate
        fields = [
            'id', 'title', 'description_template', 'category', 'action_type',
            'default_priority', 'trigger_keywords', 'business_types',
            'cities', 'is_active', 'usage_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'usage_count']
    
    def get_usage_count(self, obj):
        # This would require a proper relationship or counter field in production
        return 0