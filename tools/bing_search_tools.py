"""
Bing Search API 도구
- 무료 할당량: 월 1,000개 요청
- API 키 필요
"""

import requests
import time
import os
from typing import List, Dict, Any

class BingSearchTool:
    """
    Bing Search API
    - 무료 할당량: 월 1,000개 요청
    - 고품질 결과
    - API 키 필요
    """
    
    def __init__(self):
        self.api_key = os.getenv('BING_API_KEY', '')
        self.base_url = "https://api.bing.microsoft.com/v7.0/search"
        self.monthly_requests = 0
        self.max_monthly_requests = 1000
    
    def search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        Bing Search 실행
        
        Args:
            query: 검색 쿼리
            num_results: 결과 수
            
        Returns:
            검색 결과 리스트
        """
        if not self.api_key:
            print(f"    [ERROR] Bing API 키가 설정되지 않음")
            return []
        
        if self.monthly_requests >= self.max_monthly_requests:
            print(f"    [WARNING] 월간 요청 한도 초과: {self.monthly_requests}/{self.max_monthly_requests}")
            return []
        
        try:
            print(f"    [Bing] '{query}' 검색 중...")
            
            headers = {
                'Ocp-Apim-Subscription-Key': self.api_key
            }
            
            params = {
                'q': query,
                'count': min(num_results, 50),  # Bing은 최대 50개
                'offset': 0,
                'mkt': 'en-US',
                'safesearch': 'Moderate'
            }
            
            response = requests.get(
                self.base_url,
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = self._parse_results(data)
                self.monthly_requests += 1
                
                print(f"    [OK] Bing '{query}' 검색 완료: {len(results)}개 결과")
                return results
                
            else:
                print(f"    [FAIL] Bing API: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"    [ERROR] Bing 검색 실패: {e}")
            return []
    
    def _parse_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Bing 검색 결과 파싱"""
        results = []
        
        for item in data.get('webPages', {}).get('value', []):
            results.append({
                'title': item.get('name', ''),
                'url': item.get('url', ''),
                'content': item.get('snippet', ''),
                'score': 0.85  # Bing은 높은 신뢰도
            })
        
        return results
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """사용량 통계"""
        return {
            'monthly_requests': self.monthly_requests,
            'max_monthly_requests': self.max_monthly_requests,
            'remaining_requests': self.max_monthly_requests - self.monthly_requests
        }

# 사용 예시
if __name__ == "__main__":
    tool = BingSearchTool()
    results = tool.search("Tesla stock news 2024", 5)
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Content: {result['content'][:100]}...")
        print()
