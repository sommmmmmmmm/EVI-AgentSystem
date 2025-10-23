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
    
    def search_news(self, query: str, max_results: int = 10, language: str = "en") -> List[Dict[str, Any]]:
        """
        GNews API를 사용한 뉴스 검색 (기본 영문 검색)

        Args:
            query: 검색 쿼리
            max_results: 최대 결과 수
            language: 언어 (en 권장, ko 사용 시 제한적)

        Returns:
            뉴스 기사 리스트 (실패 시 빈 리스트)
        """
        # 캐시에서 결과 조회
        cache_key = f"gnews_{query}_{max_results}_{language}"
        cached_result = self.cache_manager.get_cached_result(cache_key, max_results)
        if cached_result is not None:
            print(f"    [CACHE] GNews '{query}' 캐시에서 {len(cached_result)}개 결과 조회")
            return cached_result

        if not self.api_key:
            print(f"[ERROR] GNews API 키가 없습니다. 뉴스를 검색할 수 없습니다: '{query}'")
            return []

        try:
            # GNews API 호출 (영문 우선)
            params = {
                'q': query,
                'lang': language,
                'country': 'us',  # 영문 검색을 위해 US로 고정
                'max': min(max_results, 10),  # GNews는 최대 10개
                'apikey': self.api_key,
                'sortby': 'publishedAt'
            }

            print(f"    [GNews] '{query}' 검색 중 (lang={language}, country=us)...")
            response = requests.get(f"{self.base_url}/search", params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            articles = data.get('articles', [])

            if not articles:
                print(f"    [WARNING] GNews '{query}' 검색 결과 없음")
                return []

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
            print(f"    [INFO] 진짜 데이터를 찾을 수 없습니다. 더미 데이터를 사용하지 않습니다.")
            return []
    
    def get_top_headlines(self, category: str = "business", max_results: int = 10, language: str = "en") -> List[Dict[str, Any]]:
        """
        GNews API를 사용한 헤드라인 뉴스 조회 (기본 영문 검색)

        Args:
            category: 뉴스 카테고리 (business, technology, science, health, sports, entertainment)
            max_results: 최대 결과 수
            language: 언어 (en 권장)

        Returns:
            헤드라인 뉴스 리스트 (실패 시 빈 리스트)
        """
        cache_key = f"gnews_headlines_{category}_{max_results}_{language}"
        cached_result = self.cache_manager.get_cached_result(cache_key, max_results)
        if cached_result is not None:
            print(f"    [CACHE] GNews 헤드라인 '{category}' 캐시에서 {len(cached_result)}개 결과 조회")
            return cached_result
        
        if not self.api_key:
            print(f"[ERROR] GNews API 키가 없습니다. 헤드라인을 조회할 수 없습니다: '{category}'")
            return []

        try:
            # GNews 헤드라인 API 호출 (영문 우선)
            params = {
                'category': category,
                'lang': language,
                'country': 'us',  # 영문 검색을 위해 US로 고정
                'max': min(max_results, 10),
                'apikey': self.api_key
            }

            print(f"    [GNews] 헤드라인 '{category}' 조회 중 (lang={language}, country=us)...")
            response = requests.get(f"{self.base_url}/top-headlines", params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            articles = data.get('articles', [])

            if not articles:
                print(f"    [WARNING] GNews 헤드라인 '{category}' 검색 결과 없음")
                return []

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
            print(f"    [INFO] 진짜 데이터를 찾을 수 없습니다. 더미 데이터를 사용하지 않습니다.")
            return []
    
    # Removed _fallback_news_search - no longer using dummy data

    def search_ev_news(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        전기차 관련 뉴스 전용 검색 (영문 쿼리 사용)
        """
        ev_queries = [
            "electric vehicle market trends",
            "EV battery technology news",
            "electric vehicle sales statistics",
            "Tesla stock news",
            "automotive electrification 2024"
        ]

        all_articles = []

        for query in ev_queries[:5]:  # 최대 5개 영문 쿼리 사용
            articles = self.search_news(query, max_results=2, language="en")
            if articles:  # 실제 데이터가 있을 때만 추가
                all_articles.extend(articles)
            time.sleep(0.5)  # API 호출 간격

        if not all_articles:
            print(f"    [WARNING] EV 뉴스를 찾을 수 없습니다. 네트워크 또는 API 문제를 확인하세요.")
            return []

        # 중복 제거
        unique_articles = []
        seen_titles = set()

        for article in all_articles:
            title = article.get('title', '')
            if title and title not in seen_titles:
                unique_articles.append(article)
                seen_titles.add(title)

        print(f"    [OK] 총 {len(unique_articles)}개의 고유한 EV 뉴스 수집")
        return unique_articles[:max_results]
