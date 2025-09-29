from rest_framework import serializers
from .models import NewsSource, NewsArticle, SocialMediaPost, ManualNewsEntry, CrawlHistory


class NewsSourceSerializer(serializers.ModelSerializer):
    articles_count = serializers.SerializerMethodField()
    crawler_status = serializers.SerializerMethodField()
    last_crawl = serializers.SerializerMethodField()

    class Meta:
        model = NewsSource
        fields = [
            'id', 'name', 'source_type', 'country', 'website_url', 'rss_url',
            'crawler_url', 'rss_discovered', 'discovered_rss_url',
            'manual_crawl_enabled', 'crawl_sections',
            'reliability_score', 'is_active', 'last_fetched', 'created_at',
            'articles_count', 'crawler_status', 'last_crawl'
        ]
        read_only_fields = ['created_at', 'rss_discovered', 'discovered_rss_url', 'last_fetched']

    def get_articles_count(self, obj):
        return obj.articles.count()

    def get_crawler_status(self, obj):
        """Get crawler configuration status"""
        status = {
            'configured': bool(obj.crawler_url),
            'rss_available': obj.rss_discovered and bool(obj.discovered_rss_url),
            'manual_enabled': obj.manual_crawl_enabled and bool(obj.crawl_sections),
            'needs_setup': bool(obj.crawler_url) and not (obj.rss_discovered or obj.manual_crawl_enabled)
        }
        return status

    def get_last_crawl(self, obj):
        """Get information about the last crawl attempt"""
        last_crawl = obj.crawl_history.first()
        if last_crawl:
            return {
                'date': last_crawl.crawl_date,
                'status': last_crawl.status,
                'articles_found': last_crawl.articles_found,
                'articles_saved': last_crawl.articles_saved
            }
        return None


class NewsArticleSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)
    source_country = serializers.CharField(source='source.country', read_only=True)

    class Meta:
        model = NewsArticle
        fields = [
            'id', 'source', 'source_name', 'source_country', 'title', 'content', 'url',
            'author', 'published_date', 'section', 'crawl_section', 'event_type', 'event_date',
            'event_location', 'business_relevance_score', 'extracted_keywords',
            'entities', 'sentiment_score', 'is_processed', 'processing_error', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


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


class CrawlHistorySerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)
    duration_seconds = serializers.SerializerMethodField()

    class Meta:
        model = CrawlHistory
        fields = [
            'id', 'source', 'source_name', 'crawl_date', 'status', 'crawl_type',
            'articles_found', 'articles_saved', 'error_message', 'crawl_duration',
            'duration_seconds'
        ]
        read_only_fields = ['crawl_date', 'crawl_duration']

    def get_duration_seconds(self, obj):
        if obj.crawl_duration:
            return obj.crawl_duration.total_seconds()
        return None


class ManualNewsEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ManualNewsEntry
        fields = [
            'id', 'title', 'content', 'event_type', 'event_date',
            'location', 'source_notes', 'entered_by', 'created_at'
        ]
        read_only_fields = ['created_at']