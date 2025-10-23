"""
API 사용량 모니터링 도구
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Any

class APIMonitor:
    """API 사용량 모니터링"""
    
    def __init__(self):
        self.request_count = 0
        self.start_time = datetime.now()
        self.request_history = []
        self.rate_limits = {
            'tavily': {'requests_per_minute': 10, 'requests_per_hour': 100},
            'openai': {'requests_per_minute': 60, 'requests_per_hour': 1000},
            'dart': {'requests_per_minute': 30, 'requests_per_hour': 1000}
        }
    
    def log_request(self, api_name: str, query: str = "") -> None:
        """API 요청 로그 기록"""
        self.request_count += 1
        self.request_history.append({
            'timestamp': datetime.now(),
            'api_name': api_name,
            'query': query[:50] + "..." if len(query) > 50 else query
        })
        
        print(f"    [API] {api_name} 요청 #{self.request_count}: {query[:30]}...")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """사용량 통계 반환"""
        now = datetime.now()
        runtime = now - self.start_time
        
        # 최근 1시간 요청 수
        one_hour_ago = now - timedelta(hours=1)
        recent_requests = [r for r in self.request_history if r['timestamp'] > one_hour_ago]
        
        # 최근 1분 요청 수
        one_minute_ago = now - timedelta(minutes=1)
        minute_requests = [r for r in self.request_history if r['timestamp'] > one_minute_ago]
        
        return {
            'total_requests': self.request_count,
            'runtime_minutes': runtime.total_seconds() / 60,
            'requests_per_hour': len(recent_requests),
            'requests_per_minute': len(minute_requests),
            'start_time': self.start_time.isoformat(),
            'current_time': now.isoformat()
        }
    
    def check_rate_limit(self, api_name: str) -> bool:
        """API 요청 한도 확인"""
        if api_name not in self.rate_limits:
            return True
        
        limits = self.rate_limits[api_name]
        now = datetime.now()
        
        # 1분간 요청 수 확인
        one_minute_ago = now - timedelta(minutes=1)
        minute_requests = [r for r in self.request_history 
                          if r['timestamp'] > one_minute_ago and r['api_name'] == api_name]
        
        if len(minute_requests) >= limits['requests_per_minute']:
            print(f"    [WARNING] {api_name} 1분 요청 한도 초과: {len(minute_requests)}/{limits['requests_per_minute']}")
            return False
        
        # 1시간 요청 수 확인
        one_hour_ago = now - timedelta(hours=1)
        hour_requests = [r for r in self.request_history 
                        if r['timestamp'] > one_hour_ago and r['api_name'] == api_name]
        
        if len(hour_requests) >= limits['requests_per_hour']:
            print(f"    [WARNING] {api_name} 1시간 요청 한도 초과: {len(hour_requests)}/{limits['requests_per_hour']}")
            return False
        
        return True
    
    def get_wait_time(self, api_name: str) -> int:
        """대기 시간 계산 (초)"""
        if api_name not in self.rate_limits:
            return 1
        
        limits = self.rate_limits[api_name]
        now = datetime.now()
        
        # 1분간 요청 수 확인
        one_minute_ago = now - timedelta(minutes=1)
        minute_requests = [r for r in self.request_history 
                          if r['timestamp'] > one_minute_ago and r['api_name'] == api_name]
        
        if len(minute_requests) >= limits['requests_per_minute']:
            # 가장 오래된 요청까지의 남은 시간
            oldest_request = min(minute_requests, key=lambda x: x['timestamp'])
            wait_seconds = 60 - (now - oldest_request['timestamp']).total_seconds()
            return max(int(wait_seconds), 1)
        
        return 1
    
    def print_summary(self) -> None:
        """사용량 요약 출력"""
        stats = self.get_usage_stats()
        
        print("\n" + "="*50)
        print("📊 API 사용량 요약")
        print("="*50)
        print(f"총 요청 수: {stats['total_requests']}")
        print(f"실행 시간: {stats['runtime_minutes']:.1f}분")
        print(f"시간당 요청: {stats['requests_per_hour']}")
        print(f"분당 요청: {stats['requests_per_minute']}")
        print("="*50)
