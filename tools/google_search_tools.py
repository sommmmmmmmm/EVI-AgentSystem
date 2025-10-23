"""
Google Custom Search API 도구
- 무료 할당량: 일일 100개 요청
- API 키 필요
"""

import requests
import time
import os
from typing import List, Dict, Any

class GoogleSearchTool:
    """
    Google Custom Search API
    - 무료 할당량: 일일 100개 요청
    - 고품질 결과
    - API 키 필요
    """
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY', '')
        self.search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID', '')
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.daily_requests = 0
        self.max_daily_requests = 100
    
    def search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        Google Custom Search 실행
        
        Args:
            query: 검색 쿼리
            num_results: 결과 수
            
        Returns:
            검색 결과 리스트
        """
        if not self.api_key or not self.search_engine_id:
            print(f"    [ERROR] Google API 키 또는 Search Engine ID가 설정되지 않음")
            return []
        
        if self.daily_requests >= self.max_daily_requests:
            print(f"    [WARNING] 일일 요청 한도 초과: {self.daily_requests}/{self.max_daily_requests}")
            return []
        
        try:
            print(f"    [Google] '{query}' 검색 중...")
            
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': min(num_results, 10),  # Google은 최대 10개
                'start': 1
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = self._parse_results(data)
                self.daily_requests += 1
                
                print(f"    [OK] Google '{query}' 검색 완료: {len(results)}개 결과")
                return results
                
            else:
                print(f"    [FAIL] Google API: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"    [ERROR] Google 검색 실패: {e}")
            return []
    
    def _parse_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Google 검색 결과 파싱"""
        results = []
        
        for item in data.get('items', []):
            results.append({
                'title': item.get('title', ''),
                'url': item.get('link', ''),
                'content': item.get('snippet', ''),
                'score': 0.9  # Google은 높은 신뢰도
            })
        
        return results
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """사용량 통계"""
        return {
            'daily_requests': self.daily_requests,
            'max_daily_requests': self.max_daily_requests,
            'remaining_requests': self.max_daily_requests - self.daily_requests
        }

# 사용 예시
if __name__ == "__main__":
    tool = GoogleSearchTool()
    results = tool.search("Tesla stock news 2024", 5)
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Content: {result['content'][:100]}...")
        print()
