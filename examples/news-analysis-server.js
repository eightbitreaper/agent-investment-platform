/**
 * News Analysis MCP Server for the Agent Investment Platform.
 *
 * This server provides financial news aggregation and sentiment analysis
 * through various news sources and social media monitoring.
 */

const { MCPServer } = require('./lib/mcp-base');
const axios = require('axios');
const Sentiment = require('sentiment');
const winston = require('winston');

class NewsAnalysisServer extends MCPServer {
    constructor() {
        super({
            name: 'news-analysis-server',
            version: '1.0.0',
            description: 'Financial news aggregation and sentiment analysis'
        });

        // Initialize sentiment analyzer
        this.sentiment = new Sentiment();

        // API keys
        this.newsApiKey = process.env.NEWS_API_KEY;
        this.redditClientId = process.env.REDDIT_CLIENT_ID;
        this.redditClientSecret = process.env.REDDIT_CLIENT_SECRET;

        // Rate limiting
        this.rateLimits = new Map();

        // Setup logging
        this.logger = winston.createLogger({
            level: 'info',
            format: winston.format.combine(
                winston.format.timestamp(),
                winston.format.errors({ stack: true }),
                winston.format.json()
            ),
            transports: [
                new winston.transports.Console(),
                new winston.transports.File({ filename: 'logs/news-analysis-server.log' })
            ]
        });

        this.registerCapabilities();
    }

    registerCapabilities() {
        // News search tool
        this.registerTool({
            name: 'search_financial_news',
            description: 'Search for financial news articles related to specific stocks or topics',
            inputSchema: {
                type: 'object',
                properties: {
                    query: {
                        type: 'string',
                        description: 'Search query (stock symbol, company name, or topic)'
                    },
                    sources: {
                        type: 'array',
                        description: 'News sources to search',
                        items: {
                            type: 'string',
                            enum: ['newsapi', 'reddit', 'yahoo', 'all']
                        },
                        default: ['all']
                    },
                    limit: {
                        type: 'integer',
                        description: 'Maximum number of articles to return',
                        minimum: 1,
                        maximum: 50,
                        default: 10
                    },
                    language: {
                        type: 'string',
                        description: 'Language for news articles',
                        enum: ['en', 'es', 'fr', 'de'],
                        default: 'en'
                    },
                    from_date: {
                        type: 'string',
                        description: 'Start date for news search (YYYY-MM-DD)',
                        format: 'date'
                    },
                    to_date: {
                        type: 'string',
                        description: 'End date for news search (YYYY-MM-DD)',
                        format: 'date'
                    }
                },
                required: ['query']
            }
        }, this.handleSearchFinancialNews.bind(this));

        // Sentiment analysis tool
        this.registerTool({
            name: 'analyze_sentiment',
            description: 'Analyze sentiment of financial news articles or text',
            inputSchema: {
                type: 'object',
                properties: {
                    text: {
                        type: 'string',
                        description: 'Text to analyze for sentiment'
                    },
                    articles: {
                        type: 'array',
                        description: 'Array of articles to analyze',
                        items: {
                            type: 'object',
                            properties: {
                                title: { type: 'string' },
                                description: { type: 'string' },
                                content: { type: 'string' }
                            }
                        }
                    }
                },
                oneOf: [
                    { required: ['text'] },
                    { required: ['articles'] }
                ]
            }
        }, this.handleAnalyzeSentiment.bind(this));

        // Social media monitoring tool
        this.registerTool({
            name: 'monitor_social_media',
            description: 'Monitor social media discussions about stocks or financial topics',
            inputSchema: {
                type: 'object',
                properties: {
                    symbol: {
                        type: 'string',
                        description: 'Stock symbol to monitor',
                        pattern: '^[A-Z]{1,5}$'
                    },
                    platforms: {
                        type: 'array',
                        description: 'Social media platforms to monitor',
                        items: {
                            type: 'string',
                            enum: ['reddit', 'twitter']
                        },
                        default: ['reddit']
                    },
                    timeframe: {
                        type: 'string',
                        description: 'Timeframe for monitoring',
                        enum: ['1h', '24h', '7d', '30d'],
                        default: '24h'
                    },
                    sentiment_threshold: {
                        type: 'number',
                        description: 'Minimum sentiment score to include',
                        minimum: -1,
                        maximum: 1,
                        default: -1
                    }
                },
                required: ['symbol']
            }
        }, this.handleMonitorSocialMedia.bind(this));

        // Trend detection tool
        this.registerTool({
            name: 'detect_trends',
            description: 'Detect trending topics and sentiment patterns in financial news',
            inputSchema: {
                type: 'object',
                properties: {
                    category: {
                        type: 'string',
                        description: 'Financial category to analyze',
                        enum: ['stocks', 'crypto', 'bonds', 'commodities', 'general'],
                        default: 'stocks'
                    },
                    timeframe: {
                        type: 'string',
                        description: 'Timeframe for trend analysis',
                        enum: ['1h', '6h', '24h', '7d'],
                        default: '24h'
                    },
                    min_mentions: {
                        type: 'integer',
                        description: 'Minimum number of mentions to be considered trending',
                        minimum: 3,
                        default: 5
                    }
                }
            }
        }, this.handleDetectTrends.bind(this));

        // News summary tool
        this.registerTool({
            name: 'summarize_news',
            description: 'Generate summary of news articles with key insights',
            inputSchema: {
                type: 'object',
                properties: {
                    articles: {
                        type: 'array',
                        description: 'Articles to summarize',
                        items: {
                            type: 'object',
                            properties: {
                                title: { type: 'string' },
                                description: { type: 'string' },
                                content: { type: 'string' },
                                source: { type: 'string' },
                                published_at: { type: 'string' }
                            },
                            required: ['title', 'content']
                        },
                        minItems: 1,
                        maxItems: 20
                    },
                    summary_length: {
                        type: 'string',
                        description: 'Length of summary',
                        enum: ['short', 'medium', 'long'],
                        default: 'medium'
                    },
                    focus_areas: {
                        type: 'array',
                        description: 'Specific areas to focus on in summary',
                        items: {
                            type: 'string',
                            enum: ['market_impact', 'earnings', 'regulations', 'mergers', 'leadership']
                        }
                    }
                },
                required: ['articles']
            }
        }, this.handleSummarizeNews.bind(this));
    }

    async handleSearchFinancialNews(params) {
        const { query, sources = ['all'], limit = 10, language = 'en', from_date, to_date } = params;

        try {
            const results = [];
            const searchSources = sources.includes('all') ? ['newsapi', 'reddit'] : sources;

            // Search NewsAPI
            if (searchSources.includes('newsapi') && this.newsApiKey) {
                const newsApiResults = await this.searchNewsAPI(query, limit, language, from_date, to_date);
                results.push(...newsApiResults);
            }

            // Search Reddit
            if (searchSources.includes('reddit')) {
                const redditResults = await this.searchReddit(query, limit);
                results.push(...redditResults);
            }

            // Sort by relevance and published date
            results.sort((a, b) => {
                const dateA = new Date(a.published_at || 0);
                const dateB = new Date(b.published_at || 0);
                return dateB - dateA;
            });

            // Limit results
            const limitedResults = results.slice(0, limit);

            return {
                success: true,
                data: {
                    query,
                    articles: limitedResults,
                    total_found: results.length,
                    sources_searched: searchSources,
                    timestamp: new Date().toISOString()
                }
            };

        } catch (error) {
            this.logger.error('Error searching financial news:', error);
            throw new Error(`News search failed: ${error.message}`);
        }
    }

    async searchNewsAPI(query, limit, language, fromDate, toDate) {
        if (!this.newsApiKey) {
            return [];
        }

        try {
            const params = {
                q: query,
                language,
                sortBy: 'relevancy',
                pageSize: Math.min(limit, 100),
                apiKey: this.newsApiKey
            };

            if (fromDate) params.from = fromDate;
            if (toDate) params.to = toDate;

            const response = await axios.get('https://newsapi.org/v2/everything', { params });

            return response.data.articles.map(article => ({
                title: article.title,
                description: article.description,
                content: article.content,
                url: article.url,
                source: article.source.name,
                author: article.author,
                published_at: article.publishedAt,
                url_to_image: article.urlToImage
            }));

        } catch (error) {
            this.logger.error('NewsAPI search error:', error);
            return [];
        }
    }

    async searchReddit(query, limit) {
        try {
            // Search relevant financial subreddits
            const subreddits = ['investing', 'stocks', 'SecurityAnalysis', 'ValueInvesting'];
            const results = [];

            for (const subreddit of subreddits) {
                try {
                    const response = await axios.get(`https://www.reddit.com/r/${subreddit}/search.json`, {
                        params: {
                            q: query,
                            restrict_sr: 1,
                            sort: 'relevance',
                            limit: Math.ceil(limit / subreddits.length)
                        },
                        headers: {
                            'User-Agent': 'AgentInvestmentPlatform/1.0.0'
                        }
                    });

                    const posts = response.data.data.children.map(child => ({
                        title: child.data.title,
                        description: child.data.selftext,
                        content: child.data.selftext,
                        url: `https://reddit.com${child.data.permalink}`,
                        source: `Reddit - r/${subreddit}`,
                        author: child.data.author,
                        published_at: new Date(child.data.created_utc * 1000).toISOString(),
                        score: child.data.score,
                        num_comments: child.data.num_comments
                    }));

                    results.push(...posts);

                } catch (error) {
                    this.logger.warn(`Error searching r/${subreddit}:`, error.message);
                }
            }

            return results;

        } catch (error) {
            this.logger.error('Reddit search error:', error);
            return [];
        }
    }

    async handleAnalyzeSentiment(params) {
        const { text, articles } = params;

        try {
            let results = [];

            if (text) {
                const analysis = this.sentiment.analyze(text);
                results.push({
                    text: text.substring(0, 100) + '...',
                    sentiment: this.categorizeSentiment(analysis.score),
                    score: analysis.score,
                    comparative: analysis.comparative,
                    positive_words: analysis.positive,
                    negative_words: analysis.negative
                });
            }

            if (articles) {
                for (const article of articles) {
                    const textToAnalyze = `${article.title} ${article.description || ''} ${article.content || ''}`;
                    const analysis = this.sentiment.analyze(textToAnalyze);

                    results.push({
                        title: article.title,
                        sentiment: this.categorizeSentiment(analysis.score),
                        score: analysis.score,
                        comparative: analysis.comparative,
                        positive_words: analysis.positive,
                        negative_words: analysis.negative
                    });
                }
            }

            // Calculate overall sentiment
            const overallScore = results.reduce((sum, r) => sum + r.score, 0) / results.length;
            const overallSentiment = this.categorizeSentiment(overallScore);

            return {
                success: true,
                data: {
                    results,
                    overall_sentiment: overallSentiment,
                    overall_score: overallScore,
                    total_analyzed: results.length,
                    timestamp: new Date().toISOString()
                }
            };

        } catch (error) {
            this.logger.error('Error analyzing sentiment:', error);
            throw new Error(`Sentiment analysis failed: ${error.message}`);
        }
    }

    async handleMonitorSocialMedia(params) {
        const { symbol, platforms = ['reddit'], timeframe = '24h', sentiment_threshold = -1 } = params;

        try {
            const results = [];

            if (platforms.includes('reddit')) {
                const redditData = await this.monitorRedditDiscussions(symbol, timeframe, sentiment_threshold);
                results.push(...redditData);
            }

            // Calculate sentiment distribution
            const sentimentCounts = {
                positive: 0,
                neutral: 0,
                negative: 0
            };

            results.forEach(post => {
                sentimentCounts[post.sentiment]++;
            });

            const totalPosts = results.length;
            const sentimentDistribution = {
                positive: totalPosts > 0 ? (sentimentCounts.positive / totalPosts * 100).toFixed(1) : 0,
                neutral: totalPosts > 0 ? (sentimentCounts.neutral / totalPosts * 100).toFixed(1) : 0,
                negative: totalPosts > 0 ? (sentimentCounts.negative / totalPosts * 100).toFixed(1) : 0
            };

            return {
                success: true,
                data: {
                    symbol,
                    posts: results,
                    sentiment_distribution: sentimentDistribution,
                    total_mentions: totalPosts,
                    timeframe,
                    platforms,
                    timestamp: new Date().toISOString()
                }
            };

        } catch (error) {
            this.logger.error('Error monitoring social media:', error);
            throw new Error(`Social media monitoring failed: ${error.message}`);
        }
    }

    async monitorRedditDiscussions(symbol, timeframe, sentimentThreshold) {
        const subreddits = ['wallstreetbets', 'investing', 'stocks', 'SecurityAnalysis'];
        const results = [];

        // Convert timeframe to Reddit time parameter
        const timeMap = {
            '1h': 'hour',
            '24h': 'day',
            '7d': 'week',
            '30d': 'month'
        };

        const redditTime = timeMap[timeframe] || 'day';

        for (const subreddit of subreddits) {
            try {
                const response = await axios.get(`https://www.reddit.com/r/${subreddit}/search.json`, {
                    params: {
                        q: symbol,
                        restrict_sr: 1,
                        sort: 'hot',
                        t: redditTime,
                        limit: 25
                    },
                    headers: {
                        'User-Agent': 'AgentInvestmentPlatform/1.0.0'
                    }
                });

                const posts = response.data.data.children.map(child => {
                    const textToAnalyze = `${child.data.title} ${child.data.selftext}`;
                    const analysis = this.sentiment.analyze(textToAnalyze);
                    const sentiment = this.categorizeSentiment(analysis.score);

                    return {
                        title: child.data.title,
                        content: child.data.selftext,
                        url: `https://reddit.com${child.data.permalink}`,
                        subreddit: subreddit,
                        author: child.data.author,
                        score: child.data.score,
                        num_comments: child.data.num_comments,
                        created_at: new Date(child.data.created_utc * 1000).toISOString(),
                        sentiment: sentiment,
                        sentiment_score: analysis.score
                    };
                });

                // Filter by sentiment threshold
                const filteredPosts = posts.filter(post => post.sentiment_score >= sentimentThreshold);
                results.push(...filteredPosts);

            } catch (error) {
                this.logger.warn(`Error monitoring r/${subreddit}:`, error.message);
            }
        }

        return results.sort((a, b) => b.score - a.score);
    }

    async handleDetectTrends(params) {
        const { category = 'stocks', timeframe = '24h', min_mentions = 5 } = params;

        try {
            // Get trending topics from various sources
            const trends = await this.detectTrendingTopics(category, timeframe, min_mentions);

            return {
                success: true,
                data: {
                    category,
                    timeframe,
                    trends,
                    total_trends: trends.length,
                    timestamp: new Date().toISOString()
                }
            };

        } catch (error) {
            this.logger.error('Error detecting trends:', error);
            throw new Error(`Trend detection failed: ${error.message}`);
        }
    }

    async detectTrendingTopics(category, timeframe, minMentions) {
        // Mock implementation - in production would analyze actual data
        const mockTrends = [
            {
                topic: 'AAPL earnings',
                mentions: 45,
                sentiment: 'positive',
                sentiment_score: 0.3,
                growth_rate: 25.5,
                related_symbols: ['AAPL']
            },
            {
                topic: 'Fed interest rates',
                mentions: 32,
                sentiment: 'neutral',
                sentiment_score: 0.1,
                growth_rate: 15.2,
                related_symbols: ['SPY', 'QQQ']
            },
            {
                topic: 'TSLA production',
                mentions: 28,
                sentiment: 'negative',
                sentiment_score: -0.2,
                growth_rate: -8.3,
                related_symbols: ['TSLA']
            }
        ];

        return mockTrends.filter(trend => trend.mentions >= minMentions);
    }

    async handleSummarizeNews(params) {
        const { articles, summary_length = 'medium', focus_areas = [] } = params;

        try {
            // Analyze articles for key themes and sentiment
            const keyThemes = this.extractKeyThemes(articles);
            const overallSentiment = this.calculateOverallSentiment(articles);

            // Generate summary based on length preference
            const summary = this.generateSummary(articles, summary_length, focus_areas, keyThemes);

            return {
                success: true,
                data: {
                    summary,
                    key_themes: keyThemes,
                    overall_sentiment: overallSentiment,
                    articles_analyzed: articles.length,
                    summary_length,
                    focus_areas,
                    timestamp: new Date().toISOString()
                }
            };

        } catch (error) {
            this.logger.error('Error summarizing news:', error);
            throw new Error(`News summarization failed: ${error.message}`);
        }
    }

    extractKeyThemes(articles) {
        // Simple keyword extraction
        const allText = articles.map(a => `${a.title} ${a.description || ''} ${a.content || ''}`).join(' ');
        const words = allText.toLowerCase().match(/\b\w+\b/g) || [];

        // Count word frequency
        const wordCount = {};
        words.forEach(word => {
            if (word.length > 3) { // Ignore short words
                wordCount[word] = (wordCount[word] || 0) + 1;
            }
        });

        // Get top themes
        const themes = Object.entries(wordCount)
            .sort(([, a], [, b]) => b - a)
            .slice(0, 10)
            .map(([word, count]) => ({ theme: word, mentions: count }));

        return themes;
    }

    calculateOverallSentiment(articles) {
        let totalScore = 0;
        let validAnalyses = 0;

        for (const article of articles) {
            const textToAnalyze = `${article.title} ${article.description || ''} ${article.content || ''}`;
            const analysis = this.sentiment.analyze(textToAnalyze);

            if (textToAnalyze.length > 10) {
                totalScore += analysis.score;
                validAnalyses++;
            }
        }

        const averageScore = validAnalyses > 0 ? totalScore / validAnalyses : 0;

        return {
            sentiment: this.categorizeSentiment(averageScore),
            score: averageScore,
            confidence: Math.min(validAnalyses / 10, 1) // Higher confidence with more articles
        };
    }

    generateSummary(articles, length, focusAreas, keyThemes) {
        const lengthMap = {
            short: 150,
            medium: 300,
            long: 500
        };

        const maxLength = lengthMap[length] || 300;

        // Combine key information from articles
        const summaryPoints = [];

        // Add theme-based summary
        if (keyThemes.length > 0) {
            summaryPoints.push(`Key topics include: ${keyThemes.slice(0, 3).map(t => t.theme).join(', ')}.`);
        }

        // Add focus area insights
        focusAreas.forEach(area => {
            const relevantArticles = articles.filter(a =>
                a.title.toLowerCase().includes(area.replace('_', ' ')) ||
                (a.description && a.description.toLowerCase().includes(area.replace('_', ' ')))
            );

            if (relevantArticles.length > 0) {
                summaryPoints.push(`${area.replace('_', ' ')} related news: ${relevantArticles.length} articles found.`);
            }
        });

        // Combine articles' descriptions for summary
        const descriptions = articles
            .filter(a => a.description)
            .map(a => a.description)
            .slice(0, 5)
            .join(' ');

        let summary = summaryPoints.join(' ') + ' ' + descriptions;

        // Truncate to max length
        if (summary.length > maxLength) {
            summary = summary.substring(0, maxLength - 3) + '...';
        }

        return summary;
    }

    categorizeSentiment(score) {
        if (score > 0.1) return 'positive';
        if (score < -0.1) return 'negative';
        return 'neutral';
    }

    async healthCheck() {
        const status = {
            status: 'healthy',
            timestamp: new Date().toISOString(),
            version: this.version,
            api_keys: {
                news_api: !!this.newsApiKey,
                reddit_client: !!this.redditClientId
            },
            capabilities: [
                'news_search',
                'sentiment_analysis',
                'social_media_monitoring',
                'trend_detection'
            ]
        };

        // Test API connectivity
        if (this.newsApiKey) {
            try {
                await axios.get('https://newsapi.org/v2/top-headlines', {
                    params: { country: 'us', category: 'business', pageSize: 1, apiKey: this.newsApiKey }
                });
                status.api_connectivity = { news_api: 'healthy' };
            } catch (error) {
                status.api_connectivity = { news_api: `error: ${error.message}` };
                status.status = 'degraded';
            }
        }

        return status;
    }
}

// Main entry point
async function main() {
    const server = new NewsAnalysisServer();
    await server.run();
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = NewsAnalysisServer;
