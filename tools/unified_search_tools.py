"""
통합 검색 도구 - 여러 API를 Fallback으로 사용
"""

import os
from typing import List, Dict, Any
from tools.duckduckgo_search_tools import DuckDuckGoSearchTool
from tools.google_search_tools import GoogleSearchTool
from tools.bing_search_tools import BingSearchTool

class UnifiedSearchTool:
    """
    통합 검색 도구
    - 여러 검색 API를 순차적으로 시도
    - Fallback 시스템으로 안정성 확보
    """
    
    def __init__(self):
        self.search_tools = []
        
        # 1. DuckDuckGo (무료, API 키 불필요)
        self.search_tools.append({
            'name': 'DuckDuckGo',
            'tool': DuckDuckGoSearchTool(),
            'priority': 1,
            'enabled': True
        })
        
        # 2. Google Custom Search (무료 할당량)
        if os.getenv('GOOGLE_API_KEY') and os.getenv('GOOGLE_SEARCH_ENGINE_ID'):
            self.search_tools.append({
                'name': 'Google',
                'tool': GoogleSearchTool(),
                'priority': 2,
                'enabled': True
            })
        
        # 3. Bing Search (무료 할당량)
        if os.getenv('BING_API_KEY'):
            self.search_tools.append({
                'name': 'Bing',
                'tool': BingSearchTool(),
                'priority': 3,
                'enabled': True
            })
        
        # 우선순위별 정렬
        self.search_tools.sort(key=lambda x: x['priority'])
        
        print(f"    [INFO] {len(self.search_tools)}개 검색 도구 로드됨")
        for tool_info in self.search_tools:
            print(f"    - {tool_info['name']} (우선순위: {tool_info['priority']})")
    
    def search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        통합 검색 실행
        
        Args:
            query: 검색 쿼리
            num_results: 결과 수
            
        Returns:
            검색 결과 리스트
        """
        for tool_info in self.search_tools:
            if not tool_info['enabled']:
                continue
            
            try:
                print(f"    [{tool_info['name']}] '{query}' 검색 시도...")
                results = tool_info['tool'].search(query, num_results)
                
                if results:
                    print(f"    [SUCCESS] {tool_info['name']}에서 {len(results)}개 결과 수집")
                    return results
                else:
                    print(f"    [SKIP] {tool_info['name']}에서 결과 없음, 다음 도구 시도")
                    
            except Exception as e:
                print(f"    [ERROR] {tool_info['name']} 검색 실패: {e}")
                print(f"    [FALLBACK] 다음 도구로 전환...")
                continue
        
        print(f"    [WARNING] 모든 검색 도구 실패, 빈 결과 반환")
        return []
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """전체 사용량 통계"""
        stats = {
            'total_tools': len(self.search_tools),
            'enabled_tools': len([t for t in self.search_tools if t['enabled']]),
            'tool_stats': {}
        }
        
        for tool_info in self.search_tools:
            if hasattr(tool_info['tool'], 'get_usage_stats'):
                stats['tool_stats'][tool_info['name']] = tool_info['tool'].get_usage_stats()
        
        return stats
    
    def disable_tool(self, tool_name: str) -> bool:
        """특정 도구 비활성화"""
        for tool_info in self.search_tools:
            if tool_info['name'] == tool_name:
                tool_info['enabled'] = False
                print(f"    [INFO] {tool_name} 도구 비활성화됨")
                return True
        return False
    
    def enable_tool(self, tool_name: str) -> bool:
        """특정 도구 활성화"""
        for tool_info in self.search_tools:
            if tool_info['name'] == tool_name:
                tool_info['enabled'] = True
                print(f"    [INFO] {tool_name} 도구 활성화됨")
                return True
        return False

# 사용 예시
if __name__ == "__main__":
    tool = UnifiedSearchTool()
    results = tool.search("Tesla stock news 2024", 5)
    
    print(f"\n총 {len(results)}개 결과 수집됨")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Content: {result['content'][:100]}...")
        print()
    
    # 사용량 통계
    stats = tool.get_usage_stats()
    print(f"\n사용량 통계: {stats}")
