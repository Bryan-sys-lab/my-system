"""
Pydantic models for request/response validation
"""
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, UUID4, field_validator, ConfigDict
from datetime import datetime, timezone


class ProjectBase(BaseModel):
    """Base project model"""
    name: str = Field(..., min_length=1, max_length=255)


class ProjectCreate(ProjectBase):
    """Project creation model"""
    pass


class ProjectResponse(BaseModel):
    """Project response model"""
    id: str
    name: str
    created_at: Optional[datetime] = None
    item_count: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class ItemBase(BaseModel):
    """Base item model"""
    content: str = ""
    meta: Dict[str, Any] = Field(default_factory=dict)


class ItemCreate(ItemBase):
    """Item creation model"""
    project_id: str


class ItemResponse(BaseModel):
    """Item response model"""
    id: str
    project_id: str
    content: str
    meta: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WatcherBase(BaseModel):
    """Base watcher model"""
    type: str
    config: Dict[str, Any] = Field(default_factory=dict)
    interval_seconds: int = Field(default=3600, ge=60, le=86400)  # 1 min to 24 hours
    enabled: bool = True


class WatcherCreate(WatcherBase):
    """Watcher creation model"""
    pass


class WatcherResponse(BaseModel):
    """Watcher response model"""
    id: str
    type: str
    interval_seconds: int
    enabled: bool
    last_run_at: Optional[datetime] = None
    config: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class CollectionRequest(BaseModel):
    """Base collection request model"""
    project_id: str

    @field_validator('project_id')
    def project_id_non_empty(cls, v: str) -> str:
        if not v or (isinstance(v, str) and v.strip() == ""):
            raise ValueError("project_id must be a non-empty string")
        return v


class WebCollectionRequest(CollectionRequest):
    """Web collection request"""
    url: str = Field(..., description="URL to collect from")

    @field_validator('url')
    def url_non_empty(cls, v: str) -> str:
        if not v or (isinstance(v, str) and v.strip() == ""):
            raise ValueError("url must be a non-empty string")
        return v


class RSSCollectionRequest(CollectionRequest):
    """RSS collection request"""
    pack: str = Field(default="feeds/east_africa.yaml", description="RSS pack file path")


class RedditCollectionRequest(CollectionRequest):
    """Reddit collection request"""
    subreddit: str


class YouTubeCollectionRequest(CollectionRequest):
    """YouTube collection request"""
    channel_id: str


class WaybackCollectionRequest(CollectionRequest):
    """Wayback collection request"""
    url: str


class SocialCollectionRequest(CollectionRequest):
    """Base social media collection request"""
    limit: int = Field(default=25, ge=1, le=100)


class TwitterSearchRequest(SocialCollectionRequest):
    """Twitter search request"""
    q: str
    max_results: int = Field(default=25, ge=1, le=100)


class FacebookPageRequest(SocialCollectionRequest):
    """Facebook page request"""
    page_id: str


class InstagramUserRequest(SocialCollectionRequest):
    """Instagram user request"""
    ig_user_id: str


class TelegramChannelRequest(SocialCollectionRequest):
    """Telegram channel request"""
    chat_id: str
    limit: int = Field(default=50, ge=1, le=200)


class DiscordChannelRequest(SocialCollectionRequest):
    """Discord channel request"""
    channel_id: str
    limit: int = Field(default=50, ge=1, le=200)


class MastodonPublicRequest(SocialCollectionRequest):
    """Mastodon public request"""
    instance_url: str
    access_token: str = ""


class BlueskyActorRequest(SocialCollectionRequest):
    """Bluesky actor request"""
    handle: str


class TikTokUserRequest(SocialCollectionRequest):
    """TikTok user request"""
    username: str
    max_items: int = Field(default=20, ge=1, le=100)


class BatchRunRequest(BaseModel):
    """Batch run request"""
    project_id: str
    rss: List[str] = Field(default_factory=list)
    twitter_handles: List[str] = Field(default_factory=list)
    facebook_pages: List[str] = Field(default_factory=list)
    instagram_ids: List[str] = Field(default_factory=list)
    telegram_chats: List[str] = Field(default_factory=list)
    discord_channels: List[str] = Field(default_factory=list)
    mastodon_instances: List[str] = Field(default_factory=list)
    bluesky_handles: List[str] = Field(default_factory=list)
    tiktok_users: List[str] = Field(default_factory=list)
    reddit_subreddits: List[str] = Field(default_factory=list)
    deepweb: Optional[Dict[str, Any]] = None
    onion: Optional[Dict[str, Any]] = None
    nitter_instance: str = "https://nitter.net"


class CrawlRequest(BaseModel):
    """Crawl request"""
    project_id: str
    seeds: List[str]
    allow_domains: List[str] = Field(default_factory=list)
    max_pages: int = Field(default=100, ge=1, le=1000)


class OnionCrawlRequest(CrawlRequest):
    """Onion crawl request"""
    allow_onion: bool = False
    max_pages: int = Field(default=50, ge=1, le=500)


class EnrichYOLORequest(BaseModel):
    """YOLO enrichment request"""
    project_id: str
    image_paths: List[str]
    model_name: str = "yolov8n.pt"


class CLIPIndexRequest(BaseModel):
    """CLIP index request"""
    namespace: str
    image_paths: List[str]


class CLIPSearchRequest(BaseModel):
    """CLIP search request"""
    namespace: str
    queries: List[str]
    k: int = Field(default=5, ge=1, le=100)


class LabelStudioProjectRequest(BaseModel):
    """Label Studio project creation request"""
    title: str
    description: str = ""
    label_config: str
    project_type: str = "text"


class LabelStudioTaskRequest(BaseModel):
    """Label Studio task creation request"""
    tasks: List[Dict[str, Any]]


class AnnotationSubmitRequest(BaseModel):
    """Annotation submission request"""
    task_id: int
    result: List[Dict[str, Any]]
    project_id: int


class AdvancedSearchRequest(BaseModel):
    """Advanced search request"""
    query: str = ""
    platforms: List[str] = Field(default_factory=list)
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    location: Optional[Dict[str, Any]] = None
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class ExportRequest(BaseModel):
    """Export request"""
    format: str = Field(default="json", pattern="^(json|csv)$")
    project_id: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    platform: Optional[str] = None
    limit: int = Field(default=10000, ge=1, le=50000)


class AnalyticsRequest(BaseModel):
    """Analytics request"""
    days: int = Field(default=30, ge=1, le=365)


class AIInsightsRequest(BaseModel):
    """AI insights request"""
    days: int = Field(default=7, ge=1, le=90)


class AIAnalyzeReportRequest(BaseModel):
    """AI report analysis request"""
    data_type: str = "comprehensive"
    time_range: Optional[Dict[str, Any]] = None
    focus_areas: Optional[List[str]] = None
    analysis_depth: str = "detailed"


class AIGenerateNarrativeRequest(BaseModel):
    """AI narrative generation request"""
    analysis_data: Dict[str, Any]
    style: str = "professional"
    audience: str = "executive"
    length: str = "comprehensive"


class AIGenerateInsightsRequest(BaseModel):
    """AI insights generation request"""
    data_context: Dict[str, Any]
    insight_types: List[str] = Field(default=["trends", "anomalies", "predictions"])
    confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)


class AISummarizeContentRequest(BaseModel):
    """AI content summarization request"""
    content_items: List[Dict[str, Any]]
    summary_type: str = "executive"
    max_length: int = Field(default=500, ge=100, le=5000)
    include_key_points: bool = True


class AIEnhancedWatcherRequest(BaseModel):
    """AI enhanced watcher request"""
    name: str
    keywords: List[str]
    platforms: List[str] = Field(default_factory=list)
    ai_features: Optional[Dict[str, Any]] = None


class ReportGenerateRequest(BaseModel):
    """Report generation request"""
    report_type: str = "comprehensive"
    format: str = "markdown"
    time_range: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    include_ai_insights: bool = True


class ScheduleReportRequest(BaseModel):
    """Schedule report request"""
    name: str
    schedule: str  # cron format
    report_config: Dict[str, Any]
    recipients: List[str] = Field(default_factory=list)


class AnomalyDetectionRequest(BaseModel):
    """Anomaly detection request"""
    days: int = Field(default=7, ge=1, le=90)
    threshold: float = Field(default=2.0, ge=1.0, le=5.0)


class PredictionRequest(BaseModel):
    """Prediction request"""
    days_ahead: int = Field(default=7, ge=1, le=90)


class SentimentTrendsRequest(BaseModel):
    """Sentiment trends request"""
    days: int = Field(default=7, ge=1, le=90)


class TopicClustersRequest(BaseModel):
    """Topic clusters request"""
    days: int = Field(default=7, ge=1, le=90)
    num_clusters: int = Field(default=5, ge=2, le=20)


class SearchImageRequest(BaseModel):
    """Search image request"""
    k: int = Field(default=12, ge=1, le=100)
    phash_hamming_max: int = Field(default=6, ge=0, le=64)
    clip_threshold: float = Field(default=0.25, ge=0.0, le=1.0)


class IndexImagesRequest(BaseModel):
    """Index images request"""
    image_paths: List[str]


class RunAllRequest(BaseModel):
    """Run all collectors request"""
    query: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=500)
    whitelist: Optional[Union[List[str], Dict[str, Any]]] = None


class RunAllStreamRequest(RunAllRequest):
    """Run all collectors stream request"""
    collector_timeout: float = Field(default=10.0, ge=1.0, le=300.0)
    collector_workers: int = Field(default=8, ge=1, le=32)
    collector_retries: int = Field(default=1, ge=0, le=5)
    use_processes: bool = False


class WebFallbackRequest(BaseModel):
    """Web fallback request"""
    url: str
    project_id: str
    wait_css: Optional[str] = None


class RedditMultiRequest(BaseModel):
    """Reddit multi request"""
    project_id: str
    subreddits: List[str]


class SearchSuggestionsRequest(BaseModel):
    """Search suggestions request"""
    q: str
    limit: int = Field(default=10, ge=1, le=50)


class PlatformAnalyticsRequest(BaseModel):
    """Platform analytics request"""
    pass


class TimeSeriesRequest(BaseModel):
    """Time series request"""
    days: int = Field(default=30, ge=1, le=365)
    group_by: str = Field(default="day", pattern="^(day|hour)$")


class ExportAnalyticsRequest(BaseModel):
    """Export analytics request"""
    format: str = Field(default="json", pattern="^(json|csv)$")
    days: int = Field(default=30, ge=1, le=365)


class DetailedTrendsRequest(BaseModel):
    """Detailed trends request"""
    query: Optional[str] = None
    platform: Optional[str] = None
    days: int = Field(default=30, ge=1, le=365)
    include_predictions: bool = True


class ExportAnnotationsRequest(BaseModel):
    """Export annotations request"""
    format: str = Field(default="json", pattern="^(json|csv)$")


class GetTasksRequest(BaseModel):
    """Get tasks request"""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=200)


class GetProjectTasksRequest(GetTasksRequest):
    """Get project tasks request"""
    project_id: int = Field(..., ge=1)


class ExportAnnotationsByProjectRequest(BaseModel):
    """Export annotations by project request"""
    project_id: int = Field(..., ge=1)
    format: str = Field(default="json", pattern="^(json|csv)$")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "ok"


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None


class PaginatedResponse(BaseModel):
    """Paginated response"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    has_more: bool


class CollectionResponse(BaseModel):
    """Collection response"""
    saved: List[str]
    count: int
    source: Optional[str] = None
    errors: Optional[List[Dict[str, Any]]] = None


class SearchResponse(BaseModel):
    """Search response"""
    query: str
    total: int
    results: List[Dict[str, Any]]
    pagination: Dict[str, Any]
    filters: Dict[str, Any]


class AnalyticsResponse(BaseModel):
    """Analytics response"""
    totalCollections: int
    activeProjects: int
    totalWatchers: int
    enabledWatchers: int
    recentCollections: int
    recentAlerts: int
    platformStats: Dict[str, Any]
    systemHealth: Dict[str, Any]
    dataSources: int


class TimeSeriesResponse(BaseModel):
    """Time series response"""
    collections: List[Dict[str, Any]]
    platformTrends: Dict[str, List[Dict[str, Any]]]
    alerts: List[Dict[str, Any]]
    period: Dict[str, Any]


class PlatformAnalyticsResponse(BaseModel):
    """Platform analytics response"""
    platformPerformance: Dict[str, Any]
    geographicDistribution: List[Dict[str, Any]]
    totalPlatforms: int


class AIInsightsResponse(BaseModel):
    """AI insights response"""
    trend_analysis: Dict[str, Any]
    anomaly_detection: List[Dict[str, Any]]
    sentiment_analysis: Dict[str, Any]
    topic_clustering: List[Dict[str, Any]]
    predictive_insights: List[Dict[str, Any]]
    engagement_patterns: Dict[str, Any]
    generated_at: str


class AINarrativeResponse(BaseModel):
    """AI narrative response"""
    narrative_id: str
    generated_at: str
    style: str
    audience: str
    length: str
    title: str
    executive_summary: str
    main_body: str
    conclusions: str
    recommendations: str
    confidence_score: float
    key_takeaways: List[str]


class AIInsightsGeneratedResponse(BaseModel):
    """AI insights generated response"""
    insights_id: str
    generated_at: str
    insight_types: List[str]
    confidence_threshold: float
    insights: List[Dict[str, Any]]
    confidence_scores: List[float]
    data_quality: Dict[str, Any]
    recommendations: List[str]


class AISummaryResponse(BaseModel):
    """AI summary response"""
    summary_id: str
    generated_at: str
    summary_type: str
    max_length: int
    total_items_processed: int
    summary: str
    key_points: Optional[List[str]] = None
    sentiment_overview: Dict[str, Any]
    content_categories: Dict[str, Any]
    confidence_score: float


class ReportResponse(BaseModel):
    """Report response"""
    report_id: str
    generated_at: str
    format: str
    content: Optional[str] = None
    metadata: Dict[str, Any]


class PredictionsResponse(BaseModel):
    """Predictions response"""
    predictions: List[Dict[str, Any]]
    confidence_level: str
    methodology: str
    historical_data_points: int


class AnomalyResponse(BaseModel):
    """Anomaly response"""
    anomalies: List[Dict[str, Any]]
    threshold: float
    analysis_period: Dict[str, Any]
    total_data_points: int


class SentimentTrendsResponse(BaseModel):
    """Sentiment trends response"""
    sentiment_trends: List[Dict[str, Any]]
    overall_sentiment: str
    sentiment_volatility: float
    key_insights: List[str]


class TopicClustersResponse(BaseModel):
    """Topic clusters response"""
    topics: List[Dict[str, Any]]
    clustering_method: str
    total_documents_analyzed: int
    generated_at: str


class ImageSearchResponse(BaseModel):
    """Image search response"""
    query: Dict[str, Any]
    exact_matches: List[Dict[str, Any]]
    near_duplicates: List[Dict[str, Any]]
    similar_matches: List[Dict[str, Any]]


class StreamResponse(BaseModel):
    """Stream response"""
    type: str
    module: Optional[str] = None
    ok: Optional[bool] = None
    records: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class MetricsResponse(BaseModel):
    """Metrics response"""
    total_requests: int
    active_connections: int
    response_time_avg: float
    error_rate: float


class WatcherRunResponse(BaseModel):
    """Watcher run response"""
    triggered_watchers: int
    successful_runs: int
    failed_runs: int
    next_run_times: List[str]


class BatchResponse(BaseModel):
    """Batch response"""
    saved: List[str]
    counts: Dict[str, int]


class CrawlResponse(BaseModel):
    """Crawl response"""
    count: int
    saved: List[str]


class EnrichResponse(BaseModel):
    """Enrichment response"""
    count: int
    saved: List[str]


class IndexResponse(BaseModel):
    """Index response"""
    indexed: int
    total_index_size: int
    namespace: Optional[str] = None


class CLIPSearchResponse(BaseModel):
    """CLIP search response"""
    namespace: str
    results: List[Dict[str, Any]]


class LabelStudioResponse(BaseModel):
    """Label Studio response"""
    id: Optional[int] = None
    title: Optional[str] = None
    projects: Optional[List[Dict[str, Any]]] = None
    created_tasks: Optional[int] = None
    tasks: Optional[List[Dict[str, Any]]] = None


class AnnotationResponse(BaseModel):
    """Annotation response"""
    id: int
    result: List[Dict[str, Any]]
    task: int
    project: int
    created_at: str
    updated_at: str


class ExportResponse(BaseModel):
    """Export response"""
    export_info: Dict[str, Any]
    items: Optional[List[Dict[str, Any]]] = None
    total_projects: Optional[int] = None
    projects: Optional[List[Dict[str, Any]]] = None


class SuggestionsResponse(BaseModel):
    """Suggestions response"""
    suggestions: List[str]
    query: str


class WatcherAIEnhancedResponse(BaseModel):
    """AI enhanced watcher response"""
    id: str
    name: str
    type: str
    config: Dict[str, Any]
    ai_capabilities: List[str]


class ScheduleResponse(BaseModel):
    """Schedule response"""
    message: str
    report_id: str
    next_run: str


class RunAllResponse(BaseModel):
    """Run all response"""
    ok: bool
    results: Optional[List[Dict[str, Any]]] = None


class WebFallbackResponse(BaseModel):
    """Web fallback response"""
    saved: str
    source: str