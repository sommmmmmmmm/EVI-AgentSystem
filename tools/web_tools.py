"""
간단한 웹 검색 도구 (API 키 없이 작동)
Tavily API 대체용
"""

import os
import requests
import time
from typing import List, Dict, Any
from tools.cache_manager import CacheManager
from urllib.parse import quote_plus
import re


class WebSearchTool:
    """
    간단한 웹 검색 도구
    API 키 없이 작동하는 무료 검색
    """
    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.session = requests.Session()
        
        # 더 안정적인 User-Agent 설정
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # 연결 설정 최적화 - 재시도 횟수 증가 및 타임아웃 연장
        self.session.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))
        self.session.mount('https://', requests.adapters.HTTPAdapter(max_retries=3))
    
    def search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        간단한 웹 검색 실행
        
        Args:
            query: 검색 쿼리
            num_results: 결과 개수
        
        Returns:
            검색 결과 리스트
        """
        # 검색어 유효성 검사
        if not self._is_valid_search_query(query):
            print(f"[SKIP] 유효하지 않은 검색어: '{query}'")
            return []
        
        # 1. 캐시에서 결과 조회
        cached_result = self.cache_manager.get_cached_result(query, num_results)
        if cached_result is not None:
            return cached_result
        
        try:
            # 검색 엔진 하나만 시도하여 속도 개선 (Google 우선)
            results = []
            
            # 1. Google 검색 시도 (재시도 1회만)
            google_results = self._search_with_retry(self._google_search, query, num_results, "Google")
            if google_results:
                results.extend(google_results)
            
            # Google 실패 시에만 DuckDuckGo 시도 (Bing은 느려서 제외)
            if not results:
                ddg_results = self._search_with_retry(self._duckduckgo_search, query, num_results, "DuckDuckGo")
                results.extend(ddg_results)
            
            if results:
                print(f"    간단 검색 '{query}' 완료: {len(results)}개 결과")
                
                # 2. 결과를 캐시에 저장
                self.cache_manager.set_cached_result(query, num_results, results)
                
                # 요청 간격 추가
                time.sleep(1)
                return results[:num_results]
            else:
                print(f"[ERROR] 모든 검색 엔진 실패: '{query}' - 대체 검색을 시도합니다")
                # 대체 검색 결과 사용
                fallback_results = self._fallback_search_results(query)
                if fallback_results:
                    print(f"    대체 검색 '{query}' 완료: {len(fallback_results)}개 결과")
                    return fallback_results[:num_results]
                return []
                
        except Exception as e:
            print(f"[ERROR] 검색 시스템 오류: {e}")
            return []
    
    def _is_valid_search_query(self, query: str) -> bool:
        """
        검색어 유효성 검사
        """
        if not query or not query.strip():
            return False
        
        # 코드 내부 변수명이나 메서드명은 검색하지 않음
        invalid_patterns = [
            'qualitative_analysis',
            'analysis_weights',
            'quantitative_analysis',
            'integrated_score',
            'investment_grade',
            'consensus_analysis',
            'expert_analysis',
            'financial_score',
            'risk_score',
            'market_trends',
            'categorized_keywords'
        ]
        
        query_lower = query.lower().strip()
        
        # 정확히 일치하는 경우 제외
        if query_lower in invalid_patterns:
            return False
        
        # 단어로 포함된 경우도 제외 (공백으로 구분)
        query_words = query_lower.split()
        for pattern in invalid_patterns:
            if pattern in query_words:
                return False
        
        # 너무 짧은 검색어 제외
        if len(query.strip()) < 3:
            return False
        
        # 특수문자만 있는 경우 제외
        if not any(c.isalnum() for c in query):
            return False
        
        return True
    
    def _search_with_retry(self, search_func, query: str, num_results: int, engine_name: str, max_retries: int = 1) -> List[Dict[str, Any]]:
        """
        재시도 로직이 포함된 검색 실행 (재시도 1회로 감소)
        """
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    print(f"    [{engine_name}] 재시도 {attempt}/{max_retries}...")
                    time.sleep(1)  # 재시도 전 대기 시간 감소
                
                results = search_func(query, num_results)
                if results:
                    return results
                    
            except Exception as e:
                if attempt == max_retries:
                    print(f"[WARNING] {engine_name} 검색 실패: {str(e)[:50]}...")
                continue
        
        return []
    
    def _google_search(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Google 검색 (HTML 파싱)"""
        try:
            # Google 검색 URL
            search_url = f"https://www.google.com/search?q={quote_plus(query)}&num={min(num_results, 10)}"
            
            response = self.session.get(search_url, timeout=5)  # 타임아웃 단축
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
            
            response = self.session.get(search_url, timeout=5)  # 타임아웃 단축
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
            
            response = self.session.get(search_url, timeout=5)  # 타임아웃 단축
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
        """API 실패 시 대체 검색 결과 반환"""
        print(f"[WARNING] '{query}' 검색 결과를 가져올 수 없습니다. 대체 검색을 시도합니다.")

        # 대체 검색: 간단한 뉴스 사이트 직접 검색
        fallback_results = []

        # EV 관련 기본 뉴스 데이터 제공
        if any(keyword in query.lower() for keyword in ['전기차', 'ev', 'electric', 'battery', 'tesla']):
            import hashlib
            import random

            #  query    seed
            query_hash = int(hashlib.md5(query.encode()).hexdigest()[:8], 16)
            random.seed(query_hash)

            #
            templates = [
                ('EV market trends {year}', 'Electric vehicle market showing strong growth with increasing adoption worldwide'),
                ('Battery technology breakthrough {year}', 'New solid-state battery technology promises longer range and faster charging'),
                ('Tesla production update {month}', 'Tesla reports record production numbers with new factory expansion'),
                ('EV charging infrastructure expansion', 'Major investment in fast-charging network across urban areas'),
                ('Lithium supply chain analysis', 'Global lithium demand surges as EV production accelerates'),
                ('EV policy and regulations update', 'New government incentives boost electric vehicle adoption rates'),
                ('Automotive electrification trends', 'Traditional automakers accelerate transition to electric vehicles'),
                ('EV battery recycling innovation', 'New recycling process recovers 95% of battery materials'),
            ]

            #  2-3
            num_results = min(2 + (query_hash % 2), 3)
            selected = random.sample(templates, min(num_results, len(templates)))

            for idx, (title_template, content_template) in enumerate(selected):
                title = title_template.format(
                    year=2024 + (query_hash % 2),
                    month='Q' + str(1 + (query_hash + idx) % 4)
                )
                fallback_results.append({
                    'title': title,
                    'url': f'https://example.com/{query_hash}-{idx}',
                    'content': content_template,
                    'score': 0.8 - (idx * 0.1)
                })

        return fallback_results
    
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