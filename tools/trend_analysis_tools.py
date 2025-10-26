"""
Trend Analysis Tools with Backup Rules

Fixes:
1. Stopwords removal (ko/en)
2. Lower thresholds for clustering
3. Backup rule: generate 3-5 trends from top n-grams/NER if clustering fails
"""

import re
from collections import Counter
from typing import List, Dict, Any, Tuple
from datetime import datetime


# Stopwords (Korean + English)
STOPWORDS_KO = {
    '을', '를', '이', '가', '은', '는', '에', '의', '와', '과', '도', '로', '으로',
    '에서', '에게', '한', '하는', '하다', '있다', '없다', '되다', '이다', '아니다',
    '그', '저', '이', '것', '수', '등', '및', '또', '또는', '그리고', '하지만'
}

STOPWORDS_EN = {
    'the', 'and', 'that', 'this', 'with', 'for', 'are', 'from', 'has',
    'have', 'had', 'will', 'would', 'could', 'should', 'may', 'can',
    'is', 'was', 'were', 'been', 'be', 'being', 'to', 'of', 'in', 'on',
    'at', 'by', 'as', 'it', 'its', 'an', 'a', 'or', 'but', 'if', 'than',
    'more', 'most', 'very', 'such', 'so', 'just', 'only', 'also', 'too',
    'then', 'than', 'when', 'where', 'what', 'which', 'who', 'how', 'why'
}


class TrendAnalyzer:
    """
    Trend analyzer with backup rules to prevent 0 trends
    """
    
    def __init__(self):
        self.min_cluster_size = 3  # Lowered from 10
        self.min_similarity = 0.6  # Lowered from 0.8
        self.min_trends = 3  # Guarantee at least 3 trends
        
    def detect_language(self, text: str) -> str:
        """Detect if text is Korean or English"""
        korean_chars = len(re.findall(r'[ㄱ-ㅎㅏ-ㅣ가-힣]', text))
        total_chars = len(re.sub(r'\s', '', text))
        
        if total_chars == 0:
            return 'en'
        
        ratio = korean_chars / total_chars
        return 'ko' if ratio > 0.3 else 'en'
    
    def remove_stopwords(self, words: List[str], language: str = 'en') -> List[str]:
        """Remove stopwords based on language"""
        stopwords = STOPWORDS_KO if language == 'ko' else STOPWORDS_EN
        
        cleaned = []
        for word in words:
            word_lower = word.lower()
            # Skip if stopword, too short, or all digits
            if (word_lower not in stopwords and 
                len(word) >= 2 and 
                not word.isdigit()):
                cleaned.append(word)
        
        return cleaned
    
    def extract_keywords(
        self, 
        news_articles: List[Dict[str, Any]],
        top_n: int = 20
    ) -> Dict[str, List[Tuple[str, int]]]:
        """
        Extract keywords with stopwords removed
        
        Args:
            news_articles: List of news article dicts
            top_n: Number of top keywords per category
            
        Returns:
            Dict of category -> [(keyword, count), ...]
        """
        categories = {
            'companies': Counter(),
            'tech': Counter(),
            'market': Counter(),
            'investment': Counter()
        }
        
        for article in news_articles:
            title = article.get('title', '')
            content = article.get('content', '')
            text = f"{title} {content}"
            
            # Detect language
            lang = self.detect_language(text)
            
            # Extract words
            words = re.findall(r'\b[A-Za-z가-힣]{2,}\b', text)
            
            # Remove stopwords
            words = self.remove_stopwords(words, language=lang)
            
            # Categorize (simplified logic)
            for word in words:
                word_lower = word.lower()
                
                # Company names (capitalized or known patterns)
                if word[0].isupper() or any(term in word_lower for term in ['motor', 'auto', 'energy']):
                    categories['companies'][word] += 1
                
                # Tech keywords
                elif any(term in word_lower for term in ['battery', 'chip', 'software', 'tech', '배터리', '칩', '소프트웨어']):
                    categories['tech'][word] += 1
                
                # Market keywords
                elif any(term in word_lower for term in ['market', 'price', 'growth', 'sales', '시장', '가격', '성장', '판매']):
                    categories['market'][word] += 1
                
                # Investment keywords
                elif any(term in word_lower for term in ['invest', 'stock', 'fund', 'revenue', '투자', '주식', '펀드', '수익']):
                    categories['investment'][word] += 1
                
                # Default to tech
                else:
                    categories['tech'][word] += 1
        
        # Return top N per category
        result = {}
        for category, counter in categories.items():
            result[category] = counter.most_common(top_n)
        
        return result
    
    def extract_trends_from_keywords(
        self,
        keywords: Dict[str, List[Tuple[str, int]]],
        min_trends: int = 3,
        news_articles: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Backup rule: Generate trends from top keywords
        
        Args:
            keywords: Dict from extract_keywords()
            min_trends: Minimum trends to generate
            news_articles: News articles for impact calculation
            
        Returns:
            List of trend dicts with impact scores
        """
        trends = []
        
        # Combine all top keywords across categories
        all_keywords = []
        for category, kw_list in keywords.items():
            for keyword, count in kw_list[:5]:  # Top 5 per category
                all_keywords.append({
                    'keyword': keyword,
                    'count': count,
                    'category': category
                })
        
        # Sort by count
        all_keywords.sort(key=lambda x: x['count'], reverse=True)
        
        # Generate trends from top keywords
        seen = set()
        for kw_data in all_keywords:
            if len(trends) >= min_trends * 2:  # Get extra candidates
                break
            
            keyword = kw_data['keyword']
            if keyword.lower() in seen:
                continue
            
            seen.add(keyword.lower())
            
            # 🆕 의미있는 트렌드 이름 생성
            trend_name = self._generate_trend_name(keyword, kw_data['category'])
            
            # 🆕 Impact Score 계산
            impact_score = 0.0
            if news_articles:
                impact_score = self._calculate_impact_score([keyword], news_articles)
            
            trends.append({
                'title': trend_name,
                'description': f"{keyword} 관련 시장 동향 및 발전 방향",
                'keywords': [keyword],
                'relevance_score': min(kw_data['count'] / 10, 1.0),
                'impact_score': impact_score,  # 🆕 Impact Score 추가
                'source': 'keyword_extraction',
                'category': kw_data['category']
            })
        
        # Return top N by relevance
        trends.sort(key=lambda x: x['relevance_score'], reverse=True)
        return trends[:min_trends]
    
    def _generate_trend_name(self, keyword: str, category: str) -> str:
        """
        Generate meaningful trend name from keyword
        
        Args:
            keyword: Main keyword
            category: Category (companies, tech, market, investment)
            
        Returns:
            Meaningful trend name
        """
        # Category-based templates
        templates = {
            'companies': [
                f"{keyword} 시장 확대",
                f"{keyword} 성장 전략",
                f"{keyword} 글로벌 확장"
            ],
            'tech': [
                f"{keyword} 기술 혁신",
                f"{keyword} 개발 가속화",
                f"{keyword} 기술 발전"
            ],
            'market': [
                f"{keyword} 시장 동향",
                f"{keyword} 수요 증가",
                f"{keyword} 시장 성장"
            ],
            'investment': [
                f"{keyword} 투자 확대",
                f"{keyword} 자금 조달",
                f"{keyword} 투자 유치"
            ]
        }
        
        # Get template for category
        category_templates = templates.get(category, [f"{keyword} 관련 동향"])
        
        # Simple selection (can be enhanced with LLM)
        return category_templates[0]
    
    def _calculate_impact_score(self, keywords: List[str], news_articles: List[Dict[str, Any]]) -> float:
        """
        Calculate impact score based on news frequency and recency
        
        Args:
            keywords: List of keywords
            news_articles: News articles
            
        Returns:
            Impact score (0.0-1.0)
        """
        if not news_articles:
            return 0.0
        
        from datetime import datetime, timedelta
        
        total_articles = len(news_articles)
        mention_count = 0
        recent_mentions = 0  # Last 3 days
        
        try:
            cutoff = datetime.now() - timedelta(days=3)
        except:
            cutoff = None
        
        for article in news_articles:
            content = f"{article.get('title', '')} {article.get('content', '')}".lower()
            
            # Check if any keyword is mentioned
            if any(kw.lower() in content for kw in keywords):
                mention_count += 1
                
                # Check recency
                if cutoff:
                    pub_date = article.get('published_date')
                    if pub_date:
                        try:
                            if isinstance(pub_date, str):
                                # Parse ISO format
                                pub_date = pub_date.replace('Z', '+00:00')
                                article_date = datetime.fromisoformat(pub_date)
                            else:
                                article_date = pub_date
                            
                            if article_date > cutoff:
                                recent_mentions += 1
                        except:
                            pass
        
        if total_articles == 0 or mention_count == 0:
            return 0.5  # Default score when no mentions
        
        # 1. Frequency score (0.0-0.5): How often mentioned relative to total articles
        frequency_ratio = mention_count / total_articles
        frequency_score = min(frequency_ratio * 1.5, 0.5)  # Scale up to 0.5 max
        
        # 2. Recency score (0.0-0.3): How many recent mentions
        recency_ratio = recent_mentions / mention_count if mention_count > 0 else 0
        recency_score = recency_ratio * 0.3
        
        # 3. Mention intensity (0.0-0.2): More mentions = higher impact
        intensity_score = min(mention_count / 10.0, 1.0) * 0.2  # Normalize to 10 mentions
        
        # Total impact score (0.0-1.0)
        impact_score = frequency_score + recency_score + intensity_score
        
        return round(min(impact_score, 1.0), 2)
    
    def extract_n_grams(
        self,
        news_articles: List[Dict[str, Any]],
        n: int = 2,
        top_k: int = 10
    ) -> List[Tuple[str, int]]:
        """
        Extract top n-grams (2-grams, 3-grams) from news
        
        Args:
            news_articles: List of news articles
            n: N-gram size (2 or 3)
            top_k: Number of top n-grams
            
        Returns:
            List of (n-gram, count)
        """
        ngram_counter = Counter()
        
        for article in news_articles:
            title = article.get('title', '')
            content = article.get('content', '')
            text = f"{title} {content}"
            
            # Detect language
            lang = self.detect_language(text)
            
            # Extract words
            words = re.findall(r'\b[A-Za-z가-힣]{2,}\b', text)
            words = self.remove_stopwords(words, language=lang)
            
            # Generate n-grams
            for i in range(len(words) - n + 1):
                ngram = ' '.join(words[i:i+n])
                ngram_counter[ngram] += 1
        
        return ngram_counter.most_common(top_k)
    
    def analyze_trends_with_fallback(
        self,
        news_articles: List[Dict[str, Any]],
        clustering_result: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Main trend analysis with fallback
        
        Args:
            news_articles: List of news articles
            clustering_result: Result from clustering (may be empty)
            
        Returns:
            List of trends (guaranteed min_trends)
        """
        print(f"\n   [TREND] Analyzing {len(news_articles)} news articles...")
        
        # Step 1: Try clustering result
        if clustering_result and len(clustering_result) >= self.min_trends:
            print(f"   [TREND] ✓ Found {len(clustering_result)} trends from clustering")
            return clustering_result
        
        print(f"   [TREND] ⚠ Clustering produced {len(clustering_result) if clustering_result else 0} trends")
        print(f"   [TREND] Applying backup rules...")
        
        # Step 2: Extract keywords
        keywords = self.extract_keywords(news_articles, top_n=20)
        
        # Log keyword stats
        for category, kw_list in keywords.items():
            if kw_list:
                top_3 = ', '.join([kw for kw, _ in kw_list[:3]])
                print(f"   [TREND]   {category}: {top_3}")
        
        # Step 3: Generate trends from keywords (with news for impact calculation)
        keyword_trends = self.extract_trends_from_keywords(
            keywords, 
            min_trends=self.min_trends,
            news_articles=news_articles  # 🆕 Pass news for impact score
        )
        
        # Step 4: Add n-gram trends if still not enough
        if len(keyword_trends) < self.min_trends:
            print(f"   [TREND] Adding n-gram trends...")
            
            bigrams = self.extract_n_grams(news_articles, n=2, top_k=5)
            for phrase, count in bigrams:
                if len(keyword_trends) >= self.min_trends:
                    break
                
                keyword_trends.append({
                    'title': f"{phrase.title()} Trend",
                    'description': f"Emerging trend: {phrase}",
                    'keywords': phrase.split(),
                    'relevance_score': min(count / 10, 1.0),
                    'source': 'n_gram_extraction',
                    'category': 'market'
                })
        
        print(f"   [TREND] ✓ Generated {len(keyword_trends)} trends via backup rules")
        
        return keyword_trends


def test_trend_analyzer():
    """Test the trend analyzer"""
    
    print("="*70)
    print("Trend Analyzer Test")
    print("="*70)
    
    # Sample news
    news = [
        {
            'title': 'Tesla and Ford Announce Battery Partnership',
            'content': 'Electric vehicle makers Tesla and Ford are developing new battery technology...'
        },
        {
            'title': 'LG Energy Solution Expands Production',
            'content': 'LG Energy Solution announced plans to expand battery production capacity...'
        },
        {
            'title': '현대차, 전기차 배터리 기술 혁신',
            'content': '현대자동차가 새로운 배터리 기술을 개발하여 전기차 시장에서 경쟁력을 강화...'
        }
    ]
    
    analyzer = TrendAnalyzer()
    
    # Test 1: Keywords
    print("\n[Test 1] Keyword Extraction")
    keywords = analyzer.extract_keywords(news, top_n=5)
    for category, kw_list in keywords.items():
        if kw_list:
            print(f"  {category}: {[kw for kw, _ in kw_list]}")
    
    # Test 2: Trends with fallback
    print("\n[Test 2] Trend Generation (Fallback)")
    trends = analyzer.analyze_trends_with_fallback(news, clustering_result=[])
    for i, trend in enumerate(trends, 1):
        print(f"  {i}. {trend['title']} (score: {trend['relevance_score']:.2f})")
    
    # Test 3: Language detection
    print("\n[Test 3] Language Detection")
    print(f"  English: {analyzer.detect_language('Tesla announces new battery')}")
    print(f"  Korean: {analyzer.detect_language('현대차 전기차 배터리')}")
    
    print("\n" + "="*70)
    print("✓ All tests completed!")
    print("="*70)


if __name__ == "__main__":
    test_trend_analyzer()


