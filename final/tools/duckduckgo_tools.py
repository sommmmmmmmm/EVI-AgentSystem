"""
DuckDuckGo API 기반 웹 검색 도구 (무료)
Tavily API 대체용
"""

import os
import requests
import time
from typing import List, Dict, Any
from tools.cache_manager import CacheManager
import urllib.parse


class DuckDuckGoSearchTool:
    """
    DuckDuckGo API 기반 웹 검색 도구
    무료이며 API 키가 필요하지 않음
    """
    
    def __init__(self):
        self.base_url = "https://api.duckduckgo.com"
        self.cache_manager = CacheManager()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        DuckDuckGo API를 사용한 웹 검색
        
        Args:
            query: 검색 쿼리
            num_results: 결과 개수
        
        Returns:
            검색 결과 리스트
        """
        # 1. 캐시에서 결과 조회
        cached_result = self.cache_manager.get_cached_result(query, num_results)
        if cached_result is not None:
            return cached_result
        
        try:
            # DuckDuckGo Instant Answer API 사용
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = self.session.get(
                f"{self.base_url}/",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = self._parse_duckduckgo_results(data, query, num_results)
                
                print(f"    DuckDuckGo '{query}' 검색 완료: {len(results)}개 결과")
                
                # 2. 결과를 캐시에 저장
                self.cache_manager.set_cached_result(query, num_results, results)
                
                # API 요청 간격 추가 (1초 대기)
                time.sleep(1)
                return results
                
            else:
                print(f"[FAIL] DuckDuckGo API 오류: {response.status_code} - {response.text}")
                return self._fallback_search_results(query)
                
        except Exception as e:
            print(f"[FAIL] DuckDuckGo 검색 오류: {e}")
            return self._fallback_search_results(query)
    
    def _parse_duckduckgo_results(self, data: Dict[str, Any], query: str, num_results: int) -> List[Dict[str, Any]]:
        """
        DuckDuckGo API 응답을 파싱하여 표준 형식으로 변환
        """
        results = []
        
        # Abstract (요약 정보)
        if data.get('Abstract'):
            results.append({
                'title': data.get('Heading', query),
                'url': data.get('AbstractURL', ''),
                'content': data.get('Abstract', ''),
                'score': 1.0
            })
        
        # Related Topics (관련 주제)
        related_topics = data.get('RelatedTopics', [])
        for topic in related_topics[:num_results-1]:  # Abstract 제외하고 나머지
            if isinstance(topic, dict) and topic.get('Text'):
                results.append({
                    'title': topic.get('Text', '')[:100] + '...' if len(topic.get('Text', '')) > 100 else topic.get('Text', ''),
                    'url': topic.get('FirstURL', ''),
                    'content': topic.get('Text', ''),
                    'score': 0.8
                })
        
        # Results (웹 결과)
        web_results = data.get('Results', [])
        for result in web_results[:num_results-len(results)]:
            results.append({
                'title': result.get('Text', ''),
                'url': result.get('FirstURL', ''),
                'content': result.get('Text', ''),
                'score': 0.7
            })
        
        # 결과가 부족한 경우 Google Custom Search로 보완
        if len(results) < num_results:
            google_results = self._google_search_fallback(query, num_results - len(results))
            results.extend(google_results)
        
        return results[:num_results]
    
    def _google_search_fallback(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """
        Google Custom Search API를 사용한 보완 검색 (선택사항)
        """
        try:
            # Google Custom Search API 키가 있는 경우에만 사용
            api_key = os.getenv('GOOGLE_API_KEY')
            search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
            
            if not api_key or not search_engine_id:
                return []
            
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': api_key,
                'cx': search_engine_id,
                'q': query,
                'num': min(num_results, 10)
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get('items', []):
                    results.append({
                        'title': item.get('title', ''),
                        'url': item.get('link', ''),
                        'content': item.get('snippet', ''),
                        'score': 0.6
                    })
                
                return results
                
        except Exception as e:
            print(f"[WARNING] Google 보완 검색 실패: {e}")
        
        return []
    
    def _fallback_search_results(self, query: str) -> List[Dict[str, Any]]:
        """API 실패 시 빈 결과 반환"""
        print(f"[WARNING] '{query}' 검색 결과를 가져올 수 없습니다.")
        return []
    
    def fetch(self, url: str) -> str:
        """
        URL에서 콘텐츠 가져오기
        
        Args:
            url: 가져올 URL
        
        Returns:
            콘텐츠 (HTML 텍스트)
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"[FAIL] URL 가져오기 실패 {url}: {e}")
            return ""


class WebSearchTool:
    """
    기존 WebSearchTool과 호환성을 위한 래퍼 클래스
    DuckDuckGoSearchTool을 사용
    """
    
    def __init__(self):
        self.duckduckgo = DuckDuckGoSearchTool()
    
    def search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """기존 인터페이스와 호환"""
        return self.duckduckgo.search(query, num_results)
    
    def fetch(self, url: str) -> str:
        """기존 인터페이스와 호환"""
        return self.duckduckgo.fetch(url)
