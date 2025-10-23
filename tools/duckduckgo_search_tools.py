"""
DuckDuckGo 무료 검색 API 도구
"""

import requests
import time
from typing import List, Dict, Any
from urllib.parse import quote_plus
import json

class DuckDuckGoSearchTool:
    """
    DuckDuckGo 무료 검색 API
    - 무료 사용
    - API 키 불필요
    - 제한: 분당 20-30개 요청
    """
    
    def __init__(self):
        self.base_url = "https://api.duckduckgo.com"
        self.search_url = "https://html.duckduckgo.com/html/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        DuckDuckGo 검색 실행
        
        Args:
            query: 검색 쿼리
            num_results: 결과 수
            
        Returns:
            검색 결과 리스트
        """
        try:
            print(f"    [DuckDuckGo] '{query}' 검색 중...")
            
            # DuckDuckGo Instant Answer API 사용
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = self._parse_instant_answer(data, query)
                
                # 결과가 부족하면 HTML 검색으로 보완
                if len(results) < num_results:
                    html_results = self._search_html(query, num_results - len(results))
                    results.extend(html_results)
                
                # 요청 수 제한
                time.sleep(2)  # 2초 대기
                
                print(f"    [OK] DuckDuckGo '{query}' 검색 완료: {len(results)}개 결과")
                return results[:num_results]
                
            else:
                print(f"    [FAIL] DuckDuckGo API: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"    [ERROR] DuckDuckGo 검색 실패: {e}")
            return []
    
    def _parse_instant_answer(self, data: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
        """Instant Answer 결과 파싱"""
        results = []
        
        # Abstract (요약)
        if data.get('Abstract'):
            results.append({
                'title': data.get('Heading', query),
                'url': data.get('AbstractURL', ''),
                'content': data.get('Abstract', ''),
                'score': 1.0
            })
        
        # Related Topics
        for topic in data.get('RelatedTopics', [])[:5]:
            if isinstance(topic, dict) and topic.get('Text'):
                results.append({
                    'title': topic.get('FirstURL', '').split('/')[-1] if topic.get('FirstURL') else query,
                    'url': topic.get('FirstURL', ''),
                    'content': topic.get('Text', ''),
                    'score': 0.8
                })
        
        return results
    
    def _search_html(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """HTML 검색으로 보완"""
        try:
            params = {
                'q': query,
                'kl': 'us-en'
            }
            
            response = requests.get(
                self.search_url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return self._parse_html_results(response.text, num_results)
            
        except Exception as e:
            print(f"    [WARNING] HTML 검색 실패: {e}")
        
        return []
    
    def _parse_html_results(self, html: str, num_results: int) -> List[Dict[str, Any]]:
        """HTML 결과 파싱"""
        results = []
        
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # 검색 결과 추출
            result_divs = soup.find_all('div', class_='result')
            
            for div in result_divs[:num_results]:
                title_elem = div.find('a', class_='result__a')
                snippet_elem = div.find('a', class_='result__snippet')
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')
                    content = snippet_elem.get_text(strip=True) if snippet_elem else ''
                    
                    results.append({
                        'title': title,
                        'url': url,
                        'content': content,
                        'score': 0.7
                    })
        
        except ImportError:
            print("    [WARNING] BeautifulSoup4가 설치되지 않음. pip install beautifulsoup4")
        except Exception as e:
            print(f"    [WARNING] HTML 파싱 실패: {e}")
        
        return results

# 사용 예시
if __name__ == "__main__":
    tool = DuckDuckGoSearchTool()
    results = tool.search("Tesla stock news 2024", 5)
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Content: {result['content'][:100]}...")
        print()
