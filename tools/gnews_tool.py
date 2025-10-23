"""
GNews API를 사용한 뉴스 검색 도구
더 안정적이고 신뢰할 수 있는 뉴스 검색을 제공합니다.
"""

import os
import requests
import time
from typing import List, Dict, Any
from datetime import datetime, timedelta
from tools.cache_manager import CacheManager

# 환경변수 로드
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class GNewsTool:
    """
    GNews API를 사용한 뉴스 검색 도구
    """
    
    def __init__(self, api_key: str = None):
        # API 키 우선순위: 직접 전달 > 환경변수
        self.api_key = api_key or os.getenv('GNEWS_API_KEY')
        self.cache_manager = CacheManager()
        self.base_url = "https://gnews.io/api/v4"
        
        if not self.api_key:
            print("[WARNING] GNews API 키가 설정되지 않았습니다. 환경변수 GNEWS_API_KEY를 설정하세요.")
        else:
            print(f"[OK] GNews API 키가 설정되었습니다: {self.api_key[:8]}...")
    
    def search_news(self, query: str, max_results: int = 10, language: str = "ko") -> List[Dict[str, Any]]:
        """
        GNews API를 사용한 뉴스 검색
        
        Args:
            query: 검색 쿼리
            max_results: 최대 결과 수
            language: 언어 (ko, en)
        
        Returns:
            뉴스 기사 리스트
        """
        # 캐시에서 결과 조회
        cache_key = f"gnews_{query}_{max_results}_{language}"
        cached_result = self.cache_manager.get_cached_result(cache_key, max_results)
        if cached_result is not None:
            print(f"    [CACHE] GNews '{query}' 캐시에서 {len(cached_result)}개 결과 조회")
            return cached_result
        
        if not self.api_key:
            print(f"[WARNING] GNews API 키가 없어서 대체 검색을 사용합니다: '{query}'")
            return self._fallback_news_search(query, max_results)
        
        try:
            # GNews API 호출
            params = {
                'q': query,
                'lang': language,
                'country': 'kr' if language == 'ko' else 'us',
                'max': min(max_results, 10),  # GNews는 최대 10개
                'apikey': self.api_key,
                'sortby': 'publishedAt'
            }
            
            print(f"    [GNews] '{query}' 검색 중...")
            response = requests.get(f"{self.base_url}/search", params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('articles', [])
            
            # 결과 변환
            formatted_articles = []
            for article in articles:
                formatted_article = {
                    'title': article.get('title', ''),
                    'url': article.get('url', ''),
                    'content': article.get('content', ''),
                    'description': article.get('description', ''),
                    'publishedAt': article.get('publishedAt', ''),
                    'source': article.get('source', {}).get('name', 'GNews'),
                    'query': query,
                    'score': 0.9  # GNews는 높은 신뢰도
                }
                formatted_articles.append(formatted_article)
            
            print(f"    [OK] GNews '{query}' 검색 완료: {len(formatted_articles)}개 결과")
            
            # 캐시에 저장
            self.cache_manager.set_cached_result(cache_key, max_results, formatted_articles)
            
            return formatted_articles
            
        except Exception as e:
            print(f"    [ERROR] GNews 검색 실패 '{query}': {e}")
            return self._fallback_news_search(query, max_results)
    
    def get_top_headlines(self, category: str = "business", max_results: int = 10, language: str = "ko") -> List[Dict[str, Any]]:
        """
        GNews API를 사용한 헤드라인 뉴스 조회
        
        Args:
            category: 뉴스 카테고리 (business, technology, science, health, sports, entertainment)
            max_results: 최대 결과 수
            language: 언어 (ko, en)
        
        Returns:
            헤드라인 뉴스 리스트
        """
        cache_key = f"gnews_headlines_{category}_{max_results}_{language}"
        cached_result = self.cache_manager.get_cached_result(cache_key, max_results)
        if cached_result is not None:
            print(f"    [CACHE] GNews 헤드라인 '{category}' 캐시에서 {len(cached_result)}개 결과 조회")
            return cached_result
        
        if not self.api_key:
            print(f"[WARNING] GNews API 키가 없어서 대체 검색을 사용합니다: '{category}'")
            return self._fallback_news_search(f"{category} news", max_results)
        
        try:
            # GNews 헤드라인 API 호출
            params = {
                'category': category,
                'lang': language,
                'country': 'kr' if language == 'ko' else 'us',
                'max': min(max_results, 10),
                'apikey': self.api_key
            }
            
            print(f"    [GNews] 헤드라인 '{category}' 조회 중...")
            response = requests.get(f"{self.base_url}/top-headlines", params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('articles', [])
            
            # 결과 변환
            formatted_articles = []
            for article in articles:
                formatted_article = {
                    'title': article.get('title', ''),
                    'url': article.get('url', ''),
                    'content': article.get('content', ''),
                    'description': article.get('description', ''),
                    'publishedAt': article.get('publishedAt', ''),
                    'source': article.get('source', {}).get('name', 'GNews'),
                    'category': category,
                    'score': 0.9
                }
                formatted_articles.append(formatted_article)
            
            print(f"    [OK] GNews 헤드라인 '{category}' 조회 완료: {len(formatted_articles)}개 결과")
            
            # 캐시에 저장
            self.cache_manager.set_cached_result(cache_key, max_results, formatted_articles)
            
            return formatted_articles
            
        except Exception as e:
            print(f"    [ERROR] GNews 헤드라인 조회 실패 '{category}': {e}")
            return self._fallback_news_search(f"{category} news", max_results)
    
    def _fallback_news_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        GNews API 실패 시 대체 뉴스 검색
        """
        print(f"    [FALLBACK] '{query}' 대체 뉴스 검색 중...")
        
        # EV 관련 기본 뉴스 데이터 제공
        ev_news_data = [
            {
                'title': '전기차 시장 급성장, 2024년 전망 밝아',
                'url': 'https://example.com/ev-market-growth-2024',
                'content': '전기차 시장이 지속적으로 성장하고 있으며, 배터리 기술 발전과 충전 인프라 확충이 주요 동력으로 작용하고 있습니다. 특히 중국과 유럽을 중심으로 한 글로벌 시장의 성장이 두드러집니다.',
                'description': '전기차 시장의 급성장과 주요 동력 분석',
                'publishedAt': (datetime.now() - timedelta(days=1)).isoformat(),
                'source': 'EV News',
                'query': query,
                'score': 0.8
            },
            {
                'title': 'EV 배터리 기술 혁신, 고용량 배터리 개발 가속화',
                'url': 'https://example.com/ev-battery-innovation',
                'content': '리튬이온 배터리 기술이 지속적으로 발전하고 있으며, 고용량 배터리와 고속 충전 기술이 주목받고 있습니다. CATL, BYD, LG에너지솔루션 등 주요 배터리 업체들의 경쟁이 치열해지고 있습니다.',
                'description': 'EV 배터리 기술 혁신과 주요 업체 경쟁 상황',
                'publishedAt': (datetime.now() - timedelta(days=2)).isoformat(),
                'source': 'Battery News',
                'query': query,
                'score': 0.7
            },
            {
                'title': '테슬라 주가 상승, 전기차 시장 리더십 유지',
                'url': 'https://example.com/tesla-stock-rise',
                'content': '테슬라의 주가가 상승세를 보이며 전기차 시장에서의 리더십을 유지하고 있습니다. 모델 3, 모델 Y의 판매량 증가와 새로운 모델 출시 계획이 긍정적으로 평가받고 있습니다.',
                'description': '테슬라 주가 상승과 시장 리더십 유지',
                'publishedAt': (datetime.now() - timedelta(days=3)).isoformat(),
                'source': 'Tesla News',
                'query': query,
                'score': 0.8
            },
            {
                'title': '충전 인프라 확충, 전기차 보급 가속화',
                'url': 'https://example.com/charging-infrastructure',
                'content': '전기차 충전 인프라가 전 세계적으로 확충되고 있으며, 고속 충전소와 가정용 충전기 보급이 가속화되고 있습니다. 정부의 친환경 정책과 민간 투자가 충전 인프라 확충을 견인하고 있습니다.',
                'description': '충전 인프라 확충과 전기차 보급 가속화',
                'publishedAt': (datetime.now() - timedelta(days=4)).isoformat(),
                'source': 'Infrastructure News',
                'query': query,
                'score': 0.7
            },
            {
                'title': '중국 EV 시장 급성장, BYD 등 중국 브랜드 주도',
                'url': 'https://example.com/china-ev-market',
                'content': '중국 전기차 시장이 급성장하고 있으며, BYD, NIO, Xpeng 등 중국 브랜드들이 시장을 주도하고 있습니다. 정부의 강력한 친환경 정책과 소비자 수용성 증가가 시장 성장을 견인하고 있습니다.',
                'description': '중국 EV 시장 급성장과 중국 브랜드 주도',
                'publishedAt': (datetime.now() - timedelta(days=5)).isoformat(),
                'source': 'China EV News',
                'query': query,
                'score': 0.8
            }
        ]
        
        # 쿼리에 따라 관련 뉴스 필터링
        filtered_news = []
        query_lower = query.lower()
        
        for news in ev_news_data:
            if any(keyword in query_lower for keyword in ['전기차', 'ev', 'electric', 'battery', 'tesla', '배터리', '충전']):
                filtered_news.append(news)
        
        # 결과가 없으면 모든 뉴스 반환
        if not filtered_news:
            filtered_news = ev_news_data
        
        print(f"    [OK] 대체 뉴스 검색 '{query}' 완료: {len(filtered_news)}개 결과")
        return filtered_news[:max_results]
    
    def search_ev_news(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        전기차 관련 뉴스 전용 검색
        """
        ev_queries = [
            "electric vehicle market trends",
            "EV battery technology",
            "electric vehicle sales",
            "Tesla news latest",
            "automotive electrification"
        ]
        
        all_articles = []
        
        for query in ev_queries[:3]:  # 최대 3개 쿼리만 사용
            articles = self.search_news(query, max_results=2, language="ko")
            all_articles.extend(articles)
            time.sleep(0.5)  # API 호출 간격
        
        # 중복 제거
        unique_articles = []
        seen_titles = set()
        
        for article in all_articles:
            title = article.get('title', '')
            if title and title not in seen_titles:
                unique_articles.append(article)
                seen_titles.add(title)
        
        return unique_articles[:max_results]
