"""
간단한 웹 검색 도구 (requests-html 기반)
API 키 없이 작동하는 무료 검색 도구
"""

import os
import requests
import time
from typing import List, Dict, Any
from tools.cache_manager import CacheManager
from urllib.parse import quote_plus
import re


class SimpleSearchTool:
    """
    간단한 웹 검색 도구
    API 키 없이 작동하는 무료 검색
    """
    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        간단한 웹 검색 실행
        
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
            # 여러 검색 엔진을 순차적으로 시도
            results = []
            
            # 1. Google 검색 시도
            google_results = self._google_search(query, num_results)
            if google_results:
                results.extend(google_results)
            
            # 2. Bing 검색 시도 (결과가 부족한 경우)
            if len(results) < num_results:
                bing_results = self._bing_search(query, num_results - len(results))
                results.extend(bing_results)
            
            # 3. DuckDuckGo 검색 시도 (결과가 부족한 경우)
            if len(results) < num_results:
                ddg_results = self._duckduckgo_search(query, num_results - len(results))
                results.extend(ddg_results)
            
            if results:
                print(f"    간단 검색 '{query}' 완료: {len(results)}개 결과")
                
                # 2. 결과를 캐시에 저장
                self.cache_manager.set_cached_result(query, num_results, results)
                
                # 요청 간격 추가
                time.sleep(1)
                return results[:num_results]
            else:
                return self._fallback_search_results(query)
                
        except Exception as e:
            print(f"[FAIL] 간단 검색 오류: {e}")
            return self._fallback_search_results(query)
    
    def _google_search(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Google 검색 (HTML 파싱)"""
        try:
            # Google 검색 URL
            search_url = f"https://www.google.com/search?q={quote_plus(query)}&num={min(num_results, 10)}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            # 간단한 HTML 파싱으로 결과 추출
            results = self._parse_google_html(response.text, num_results)
            return results
            
        except Exception as e:
            print(f"[WARNING] Google 검색 실패: {e}")
            return []
    
    def _bing_search(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Bing 검색 (HTML 파싱)"""
        try:
            # Bing 검색 URL
            search_url = f"https://www.bing.com/search?q={quote_plus(query)}&count={min(num_results, 10)}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            # 간단한 HTML 파싱으로 결과 추출
            results = self._parse_bing_html(response.text, num_results)
            return results
            
        except Exception as e:
            print(f"[WARNING] Bing 검색 실패: {e}")
            return []
    
    def _duckduckgo_search(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """DuckDuckGo 검색 (HTML 파싱)"""
        try:
            # DuckDuckGo 검색 URL
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            # 간단한 HTML 파싱으로 결과 추출
            results = self._parse_duckduckgo_html(response.text, num_results)
            return results
            
        except Exception as e:
            print(f"[WARNING] DuckDuckGo 검색 실패: {e}")
            return []
    
    def _parse_google_html(self, html: str, num_results: int) -> List[Dict[str, Any]]:
        """Google HTML 파싱"""
        results = []
        
        # 간단한 정규식으로 결과 추출
        # Google의 결과 구조에 맞춰 파싱
        import re
        
        # 제목과 링크 추출
        title_pattern = r'<h3[^>]*><a[^>]*href="([^"]*)"[^>]*>([^<]*)</a></h3>'
        matches = re.findall(title_pattern, html)
        
        for i, (url, title) in enumerate(matches[:num_results]):
            if url.startswith('/url?q='):
                url = url.split('/url?q=')[1].split('&')[0]
            
            results.append({
                'title': title,
                'url': url,
                'content': f"Google 검색 결과: {title}",
                'score': 1.0 - (i * 0.1)
            })
        
        return results
    
    def _parse_bing_html(self, html: str, num_results: int) -> List[Dict[str, Any]]:
        """Bing HTML 파싱"""
        results = []
        
        # Bing의 결과 구조에 맞춰 파싱
        import re
        
        # 제목과 링크 추출
        title_pattern = r'<h2><a[^>]*href="([^"]*)"[^>]*>([^<]*)</a></h2>'
        matches = re.findall(title_pattern, html)
        
        for i, (url, title) in enumerate(matches[:num_results]):
            results.append({
                'title': title,
                'url': url,
                'content': f"Bing 검색 결과: {title}",
                'score': 0.9 - (i * 0.1)
            })
        
        return results
    
    def _parse_duckduckgo_html(self, html: str, num_results: int) -> List[Dict[str, Any]]:
        """DuckDuckGo HTML 파싱"""
        results = []
        
        # DuckDuckGo의 결과 구조에 맞춰 파싱
        import re
        
        # 제목과 링크 추출
        title_pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
        matches = re.findall(title_pattern, html)
        
        for i, (url, title) in enumerate(matches[:num_results]):
            results.append({
                'title': title,
                'url': url,
                'content': f"DuckDuckGo 검색 결과: {title}",
                'score': 0.8 - (i * 0.1)
            })
        
        return results
    
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
    SimpleSearchTool을 사용
    """
    
    def __init__(self):
        self.simple_search = SimpleSearchTool()
    
    def search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """기존 인터페이스와 호환"""
        return self.simple_search.search(query, num_results)
    
    def fetch(self, url: str) -> str:
        """기존 인터페이스와 호환"""
        return self.simple_search.fetch(url)
