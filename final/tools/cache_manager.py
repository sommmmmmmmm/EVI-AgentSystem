"""
API 요청 결과 캐싱 시스템
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class CacheManager:
    """API 요청 결과 캐싱 관리자"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.cache_duration = 86400  # 24시간 캐시 (86400초)
        
        # 캐시 디렉토리 생성
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def _get_cache_key(self, query: str, num_results: int) -> str:
        """캐시 키 생성"""
        import hashlib
        key_string = f"{query}_{num_results}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cache_file_path(self, cache_key: str) -> str:
        """캐시 파일 경로 반환"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get_cached_result(self, query: str, num_results: int) -> Optional[Dict[str, Any]]:
        """캐시된 결과 조회"""
        try:
            cache_key = self._get_cache_key(query, num_results)
            cache_file = self._get_cache_file_path(cache_key)
            
            if not os.path.exists(cache_file):
                return None
            
            # 캐시 파일 읽기
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 캐시 만료 확인
            cache_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cache_time > timedelta(seconds=self.cache_duration):
                os.remove(cache_file)  # 만료된 캐시 삭제
                return None
            
            print(f"    [CACHE] '{query}' 캐시에서 조회")
            return cache_data['result']
            
        except Exception as e:
            print(f"    [WARNING] 캐시 조회 실패: {e}")
            return None
    
    def set_cached_result(self, query: str, num_results: int, result: Dict[str, Any]) -> None:
        """결과를 캐시에 저장"""
        try:
            cache_key = self._get_cache_key(query, num_results)
            cache_file = self._get_cache_file_path(cache_key)
            
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'query': query,
                'num_results': num_results,
                'result': result
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            print(f"    [CACHE] '{query}' 결과 캐시에 저장")
            
        except Exception as e:
            print(f"    [WARNING] 캐시 저장 실패: {e}")
    
    def clear_expired_cache(self) -> None:
        """만료된 캐시 정리"""
        try:
            if not os.path.exists(self.cache_dir):
                return
            
            current_time = datetime.now()
            removed_count = 0
            
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            cache_data = json.load(f)
                        
                        cache_time = datetime.fromisoformat(cache_data['timestamp'])
                        if current_time - cache_time > timedelta(seconds=self.cache_duration):
                            os.remove(file_path)
                            removed_count += 1
                            
                    except Exception:
                        # 손상된 캐시 파일 삭제
                        os.remove(file_path)
                        removed_count += 1
            
            if removed_count > 0:
                print(f"    [CACHE] {removed_count}개 만료된 캐시 파일 정리")
                
        except Exception as e:
            print(f"    [WARNING] 캐시 정리 실패: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """캐시 통계 정보"""
        try:
            if not os.path.exists(self.cache_dir):
                return {'total_files': 0, 'total_size': 0}
            
            total_files = 0
            total_size = 0
            
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    total_files += 1
                    total_size += os.path.getsize(file_path)
            
            return {
                'total_files': total_files,
                'total_size': total_size,
                'cache_dir': self.cache_dir
            }
            
        except Exception as e:
            print(f"    [WARNING] 캐시 통계 조회 실패: {e}")
            return {'total_files': 0, 'total_size': 0}
