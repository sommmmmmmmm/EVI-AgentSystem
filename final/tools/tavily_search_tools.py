"""
Tavily API를 사용한 웹 검색 도구
고품질 검색 결과 제공 (유료 플랜 권장)
"""

import os
import requests
import time
from typing import List, Dict, Any, Optional
from tools.cache_manager import CacheManager


class TavilySearchTool:
    """
    Tavily API를 사용한 웹 검색 도구
    - 고품질 검색 결과
    - AI에 최적화된 컨텐츠
    - 빠른 응답 속도
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('TAVILY_API_KEY')
        self.base_url = "https://api.tavily.com/search"
        self.cache_manager = CacheManager()
        self.session = requests.Session()
        
        if not self.api_key:
            print("[WARNING] Tavily API 키가 설정되지 않았습니다.")
            print("   .env 파일에 TAVILY_API_KEY를 추가하세요.")
        else:
            print(f"[OK] Tavily API 키 설정됨: {self.api_key[:8]}...")
    
    def search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        Tavily API를 사용한 웹 검색
        
        Args:
            query: 검색 쿼리
            num_results: 결과 개수 (최대 10)
        
        Returns:
            검색 결과 리스트
        """
        if not self.api_key:
            print(f"[ERROR] Tavily API 키가 없습니다: '{query}'")
            return []
        
        # 1. 캐시에서 결과 조회
        cache_key = f"tavily_{query}_{num_results}"
        cached_result = self.cache_manager.get_cached_result(cache_key, num_results)
        if cached_result is not None:
            print(f"    [CACHE] Tavily '{query}' 캐시에서 {len(cached_result)}개 결과 조회")
            return cached_result
        
        try:
            print(f"    [Tavily] '{query}' 검색 중...")
            
            # Tavily API 호출
            payload = {
                "api_key": self.api_key,
                "query": query,
                "search_depth": "advanced",  # basic or advanced
                "max_results": min(num_results, 10),
                "include_answer": False,
                "include_raw_content": False,
                "include_images": False
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            response = self.session.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            # 상태 코드 확인
            if response.status_code == 200:
                data = response.json()
                results = self._parse_tavily_results(data)
                
                print(f"    [OK] Tavily '{query}' 검색 완료: {len(results)}개 결과")
                
                # 2. 결과를 캐시에 저장
                self.cache_manager.set_cached_result(cache_key, num_results, results)
                
                # API 요청 간격 (유료 플랜은 더 많은 요청 가능)
                time.sleep(0.5)
                return results
                
            elif response.status_code == 429:
                print(f"    [ERROR] Tavily API 제한 초과 (429): 너무 많은 요청")
                return []
                
            elif response.status_code == 401:
                print(f"    [ERROR] Tavily API 인증 실패 (401): API 키를 확인하세요")
                return []
                
            elif response.status_code == 432:
                print(f"    [ERROR] Tavily API 오류 (432): {response.text[:200]}")
                return []
                
            else:
                print(f"    [ERROR] Tavily API 오류: {response.status_code} - {response.text[:200]}")
                return []
                
        except requests.exceptions.Timeout:
            print(f"    [ERROR] Tavily API 타임아웃: '{query}'")
            return []
            
        except requests.exceptions.RequestException as e:
            print(f"    [ERROR] Tavily API 요청 실패: {e}")
            return []
            
        except Exception as e:
            print(f"    [ERROR] Tavily 검색 오류: {e}")
            return []
    
    def _parse_tavily_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Tavily API 응답을 파싱하여 표준 형식으로 변환
        """
        results = []
        
        # Tavily는 results 배열로 결과 반환
        for idx, item in enumerate(data.get('results', [])):
            results.append({
                'title': item.get('title', ''),
                'url': item.get('url', ''),
                'content': item.get('content', ''),
                'score': item.get('score', 0.95 - (idx * 0.05)),
                'published_date': item.get('published_date', '')
            })
        
        return results
    
    def fetch(self, url: str) -> str:
        """
        URL에서 컨텐츠 가져오기
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"[FAIL] URL 가져오기 실패 {url}: {e}")
            return ""

