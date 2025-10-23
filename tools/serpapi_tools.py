"""
SerpAPI 기반 웹 검색 도구 (무료 할당량)
Tavily API 대체용
"""

import os
import requests
import time
from typing import List, Dict, Any
from tools.cache_manager import CacheManager


class SerpAPISearchTool:
    """
    SerpAPI 기반 웹 검색 도구
    무료 할당량: 월 100회 검색
    """
    
    def __init__(self):
        self.api_key = os.getenv('SERPAPI_API_KEY')
        self.base_url = "https://serpapi.com/search"
        self.cache_manager = CacheManager()
        self.session = requests.Session()
    
    def search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        SerpAPI를 사용한 웹 검색
        
        Args:
            query: 검색 쿼리
            num_results: 결과 개수
        
        Returns:
            검색 결과 리스트
        """
        if not self.api_key:
            print(f"[WARNING] SerpAPI 키가 설정되지 않았습니다. Google 검색으로 대체합니다.")
            return self._google_search_fallback(query, num_results)
        
        # 1. 캐시에서 결과 조회
        cached_result = self.cache_manager.get_cached_result(query, num_results)
        if cached_result is not None:
            return cached_result
        
        try:
            params = {
                'q': query,
                'api_key': self.api_key,
                'engine': 'google',
                'num': min(num_results, 10),
                'gl': 'us',  # 미국 기준
                'hl': 'en'   # 영어
            }
            
            response = self.session.get(self.base_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                results = self._parse_serpapi_results(data, num_results)
                
                print(f"    SerpAPI '{query}' 검색 완료: {len(results)}개 결과")
                
                # 2. 결과를 캐시에 저장
                self.cache_manager.set_cached_result(query, num_results, results)
                
                # API 요청 간격 추가 (1초 대기)
                time.sleep(1)
                return results
                
            else:
                print(f"[FAIL] SerpAPI 오류: {response.status_code} - {response.text}")
                return self._google_search_fallback(query, num_results)
                
        except Exception as e:
            print(f"[FAIL] SerpAPI 검색 오류: {e}")
            return self._google_search_fallback(query, num_results)
    
    def _parse_serpapi_results(self, data: Dict[str, Any], num_results: int) -> List[Dict[str, Any]]:
        """
        SerpAPI 응답을 파싱하여 표준 형식으로 변환
        """
        results = []
        
        # Organic Results (일반 검색 결과)
        organic_results = data.get('organic_results', [])
        for result in organic_results[:num_results]:
            results.append({
                'title': result.get('title', ''),
                'url': result.get('link', ''),
                'content': result.get('snippet', ''),
                'score': 1.0 - (len(results) * 0.1)  # 순위에 따른 점수
            })
        
        # Answer Box (답변 박스)
        answer_box = data.get('answer_box')
        if answer_box and len(results) < num_results:
            results.insert(0, {
                'title': answer_box.get('title', ''),
                'url': answer_box.get('link', ''),
                'content': answer_box.get('answer', answer_box.get('snippet', '')),
                'score': 1.0
            })
        
        # Knowledge Graph
        knowledge_graph = data.get('knowledge_graph')
        if knowledge_graph and len(results) < num_results:
            results.insert(0, {
                'title': knowledge_graph.get('title', ''),
                'url': knowledge_graph.get('website', ''),
                'content': knowledge_graph.get('description', ''),
                'score': 0.9
            })
        
        return results[:num_results]
    
    def _google_search_fallback(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """
        Google Custom Search API를 사용한 보완 검색
        """
        try:
            api_key = os.getenv('GOOGLE_API_KEY')
            search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
            
            if not api_key or not search_engine_id:
                print(f"[WARNING] Google API 키가 설정되지 않았습니다.")
                return self._fallback_search_results(query)
            
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
                        'score': 0.8
                    })
                
                print(f"    Google Custom Search '{query}' 검색 완료: {len(results)}개 결과")
                return results
                
        except Exception as e:
            print(f"[WARNING] Google 보완 검색 실패: {e}")
        
        return self._fallback_search_results(query)
    
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
    SerpAPISearchTool을 사용
    """
    
    def __init__(self):
        self.serpapi = SerpAPISearchTool()
    
    def search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """기존 인터페이스와 호환"""
        return self.serpapi.search(query, num_results)
    
    def fetch(self, url: str) -> str:
        """기존 인터페이스와 호환"""
        return self.serpapi.fetch(url)
