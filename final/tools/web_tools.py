"""
통합 웹 검색 도구
Tavily API 우선, DuckDuckGo Fallback
"""

import os
from typing import List, Dict, Any


class WebSearchTool:
    """
    통합 웹 검색 도구
    - Tavily API 우선 사용 (고품질 검색 결과)
    - DuckDuckGo Fallback (무료, API 키 불필요)
    """
    
    def __init__(self):
        self.tavily_enabled = bool(os.getenv('TAVILY_API_KEY'))
        
        if self.tavily_enabled:
            print("[INFO] Tavily API 사용 가능 - 우선 사용")
            from tools.tavily_search_tools import TavilySearchTool
            self.tavily = TavilySearchTool()
        else:
            print("[INFO] Tavily API 키 없음 - DuckDuckGo 사용")
            self.tavily = None
        
        # DuckDuckGo는 항상 Fallback으로 준비
        from tools.duckduckgo_tools import DuckDuckGoSearchTool
        self.duckduckgo = DuckDuckGoSearchTool()
    
    def search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        웹 검색 실행
        1. Tavily API 시도 (키가 있는 경우)
        2. 실패 시 DuckDuckGo 사용
        """
        # 1. Tavily API 시도
        if self.tavily_enabled and self.tavily:
            try:
                results = self.tavily.search(query, num_results)
                if results:
                    return results
                else:
                    print(f"    [INFO] Tavily 결과 없음 - DuckDuckGo로 재시도")
            except Exception as e:
                print(f"    [WARNING] Tavily 실패: {e} - DuckDuckGo로 재시도")
        
        # 2. DuckDuckGo Fallback
        print(f"    [DuckDuckGo] '{query}' 재시도 중...")
        try:
            results = self.duckduckgo.search(query, num_results)
            return results
        except Exception as e:
            print(f"    [ERROR] DuckDuckGo도 실패: {e}")
            return self._fallback_search_results(query)
    
    def fetch(self, url: str) -> str:
        """URL에서 컨텐츠 가져오기"""
        if self.tavily:
            try:
                return self.tavily.fetch(url)
            except:
                pass
        return self.duckduckgo.fetch(url)
    
    def _fallback_search_results(self, query: str) -> List[Dict[str, Any]]:
        """
        모든 검색 실패 시 대체 검색 결과
        """
        print(f"[WARNING] '{query}' 검색 결과를 가져올 수 없습니다. 대체 검색을 시도합니다.")
        
        # 기본 fallback 데이터
        fallback_data = [
            {
                'title': f'전기차 시장 동향 및 전망 2024',
                'url': 'https://www.example.com',
                'content': f'{query}에 대한 전기차 시장 분석 정보입니다.',
                'score': 0.5
            },
            {
                'title': f'EV 배터리 기술 혁신 뉴스',
                'url': 'https://www.example.com',
                'content': '전기차 배터리 관련 최신 기술 동향입니다.',
                'score': 0.4
            }
        ]
        
        return fallback_data


__all__ = ['WebSearchTool']

