from rest_framework import serializers
from .models import Business, BusinessKeywords, AdminUser


class BusinessKeywordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessKeywords
        fields = ['id', 'business', 'keyword', 'weight', 'is_negative', 'created_at']


class BusinessSerializer(serializers.ModelSerializer):
    keywords = BusinessKeywordsSerializer(many=True, read_only=True)
    recommendations_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Business
        fields = [
            'id', 'owner', 'name', 'business_type', 'city', 'description',
            'address', 'phone', 'email', 'website', 'target_audience',
            'capacity', 'staff_count', 'email_notifications',
            'recommendation_frequency', 'created_at', 'updated_at',
            'keywords', 'recommendations_count'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_recommendations_count(self, obj):
        return obj.recommendations.count()


class AdminUserSerializer(serializers.ModelSerializer):
    user_details = serializers.SerializerMethodField()
    
    class Meta:
        model = AdminUser
        fields = [
            'id', 'user', 'user_details', 'can_manage_news_sources',
            'can_create_businesses', 'city_access', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_user_details(self, obj):
        return {
            'username': obj.user.username,
            'email': obj.user.email,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
        }