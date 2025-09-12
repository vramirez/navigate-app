from rest_framework import serializers
from .models import NewsSource, NewsArticle, SocialMediaPost, ManualNewsEntry


class NewsSourceSerializer(serializers.ModelSerializer):
    articles_count = serializers.SerializerMethodField()
    
    class Meta:
        model = NewsSource
        fields = [
            'id', 'name', 'source_type', 'city', 'website_url', 'rss_url',
            'reliability_score', 'is_active', 'created_at', 'updated_at',
            'articles_count'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_articles_count(self, obj):
        return obj.articles.count()


class NewsArticleSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)
    
    class Meta:
        model = NewsArticle
        fields = [
            'id', 'source', 'source_name', 'title', 'content', 'url',
            'published_date', 'section', 'event_type', 'event_date',
            'event_location', 'business_relevance_score', 'extracted_keywords',
            'sentiment_score', 'is_processed', 'processed_at', 'created_at'
        ]
        read_only_fields = ['created_at', 'processed_at']


class SocialMediaPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaPost
        fields = [
            'id', 'platform', 'post_id', 'author_username', 'content',
            'published_date', 'engagement_metrics', 'location_tags',
            'business_relevance_score', 'extracted_keywords',
            'sentiment_score', 'is_processed', 'processed_at', 'created_at'
        ]
        read_only_fields = ['created_at', 'processed_at']


class ManualNewsEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ManualNewsEntry
        fields = [
            'id', 'title', 'content', 'event_type', 'event_date',
            'event_location', 'city', 'created_by', 'created_at'
        ]
        read_only_fields = ['created_at']