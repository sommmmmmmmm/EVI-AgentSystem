"""
DART Tagger Tool
Purpose: Extract company names, match DART corp_codes, and tag disclosures.
"""

from typing import List, Dict, Any, Set
import re
from datetime import datetime


class DARTTagger:
    """
    DART 공시 데이터 태깅 및 기업 매칭 도구
    """
    
    # 한국 전기차 관련 주요 기업 리스트
    KOREAN_EV_COMPANIES = {
        # 배터리
        'LG에너지솔루션': ['LG에너지솔루션', 'LG Energy Solution', 'LGES'],
        '삼성SDI': ['삼성SDI', 'Samsung SDI'],
        'SK온': ['SK온', 'SK On', 'SK이노베이션', 'SKinnovation'],
        '포스코케미칼': ['포스코케미칼', 'POSCO Chemical'],
        'LG화학': ['LG화학', 'LG Chem', 'LG Chemical'],
        
        # 완성차
        '현대자동차': ['현대자동차', '현대차', 'Hyundai Motor', 'Hyundai'],
        '기아': ['기아', 'Kia', 'Kia Motors'],
        
        # 부품/소재
        '에코프로비엠': ['에코프로비엠', 'EcoPro BM'],
        '에코프로': ['에코프로', 'EcoPro'],
        'LG전자': ['LG전자', 'LG Electronics'],
        '삼성전자': ['삼성전자', 'Samsung Electronics'],
        '엘앤에프': ['엘앤에프', 'L&F'],
        '천보': ['천보', 'CheonBo'],
        '코스모신소재': ['코스모신소재', 'Cosmo AM&T'],
        '후성': ['후성', 'Foosung'],
        '솔루스첨단소재': ['솔루스첨단소재', 'Solus Advanced Materials'],
        
        # 충전 인프라
        '에버온': ['에버온', 'EverON'],
        '대영채비': ['대영채비', 'Daeyoung Chaevi'],
        '파워로직스': ['파워로직스', 'Powerlogics'],
    }
    
    # 공시 유형별 중요도
    DISCLOSURE_IMPORTANCE = {
        # 높은 중요도
        'high': [
            '사업보고서', '분기보고서', '반기보고서',
            '매출액또는손익구조30%(대규모법인은15%)이상변경',
            '주요사항보고서', '투자판단관련주요경영사항',
            '최대주주등소유주식변동신고서',
            '유상증자결정', '전환사채권발행결정',
        ],
        # 중간 중요도
        'medium': [
            '주주총회소집공고', '결산실적공시',
            '매출액또는손익구조', '영업(잠정)실적',
            '타법인주식및출자증권양도결정',
        ],
        # 낮은 중요도
        'low': [
            '기타시장안내', '조회공시',
            '기타경영사항(자율공시)',
        ]
    }
    
    # EV 관련 키워드
    EV_KEYWORDS = [
        '전기차', '전기자동차', 'EV', 'electric vehicle',
        '배터리', 'battery', '이차전지', '2차전지',
        '양극재', '음극재', '분리막', '전해액',
        '충전', 'charging', 'BMS', '배터리관리시스템',
        'LFP', 'NCM', 'NCA', '리튬', 'lithium',
        '테슬라', 'Tesla', 'BYD'
    ]
    
    def __init__(self, dart_tool=None):
        """
        Initialize DART Tagger
        
        Args:
            dart_tool: DARTTool instance for corp_code lookup
        """
        self.dart_tool = dart_tool
        self._company_cache: Dict[str, str] = {}  # company_name -> corp_code
    
    def extract_company_names(self, text: str) -> List[str]:
        """
        텍스트에서 기업명 추출
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            추출된 기업명 리스트
        """
        found_companies = []
        
        # 전체 텍스트를 소문자로 변환하여 검색
        text_lower = text.lower()
        
        for company_name, aliases in self.KOREAN_EV_COMPANIES.items():
            for alias in aliases:
                if alias.lower() in text_lower:
                    if company_name not in found_companies:
                        found_companies.append(company_name)
                    break
        
        return found_companies
    
    def get_corp_code(self, company_name: str) -> str:
        """
        기업명으로 DART corp_code 조회
        
        Args:
            company_name: 기업명
            
        Returns:
            corp_code (8자리) 또는 빈 문자열
        """
        # 캐시 확인
        if company_name in self._company_cache:
            return self._company_cache[company_name]
        
        if not self.dart_tool:
            return ""
        
        # DART에서 검색
        try:
            # dart_tool의 corp_code_cache 사용
            if hasattr(self.dart_tool, 'corp_code_cache'):
                # 1. 정확한 매칭 우선 (완전 일치)
                for corp_name, info in self.dart_tool.corp_code_cache.items():
                    if company_name == corp_name:
                        corp_code = info.get('corp_code', '')
                        stock_code = info.get('stock_code', '')
                        if corp_code and stock_code:  # 상장 기업만
                            self._company_cache[company_name] = corp_code
                            print(f"   [OK] 기업 매칭 (정확): {company_name} → {corp_name} ({corp_code})")
                            return corp_code
                
                # 2. 포함 매칭 (긴 이름 우선)
                matches = []
                for corp_name, info in self.dart_tool.corp_code_cache.items():
                    stock_code = info.get('stock_code', '')
                    if not stock_code:  # 비상장 기업 제외
                        continue
                    
                    if company_name in corp_name:
                        matches.append((corp_name, info, len(corp_name)))
                
                # 길이가 가장 짧은 것(가장 정확한 매칭) 선택
                if matches:
                    matches.sort(key=lambda x: x[2])  # 길이 순 정렬
                    best_match = matches[0]
                    corp_name, info, _ = best_match
                    corp_code = info.get('corp_code', '')
                    self._company_cache[company_name] = corp_code
                    print(f"   [OK] 기업 매칭 (포함): {company_name} → {corp_name} ({corp_code})")
                    return corp_code
                
                # 3. 별칭으로 시도
                if company_name in self.KOREAN_EV_COMPANIES:
                    for alias in self.KOREAN_EV_COMPANIES[company_name]:
                        # 정확한 매칭
                        for corp_name, info in self.dart_tool.corp_code_cache.items():
                            if alias == corp_name:
                                corp_code = info.get('corp_code', '')
                                stock_code = info.get('stock_code', '')
                                if corp_code and stock_code:
                                    self._company_cache[company_name] = corp_code
                                    print(f"   [OK] 기업 매칭 (별칭-정확): {company_name} → {corp_name} ({corp_code})")
                                    return corp_code
                        
                        # 포함 매칭
                        matches = []
                        for corp_name, info in self.dart_tool.corp_code_cache.items():
                            stock_code = info.get('stock_code', '')
                            if not stock_code:
                                continue
                            if alias in corp_name:
                                matches.append((corp_name, info, len(corp_name)))
                        
                        if matches:
                            matches.sort(key=lambda x: x[2])
                            best_match = matches[0]
                            corp_name, info, _ = best_match
                            corp_code = info.get('corp_code', '')
                            self._company_cache[company_name] = corp_code
                            print(f"   [OK] 기업 매칭 (별칭-포함): {company_name} → {corp_name} ({corp_code})")
                            return corp_code
        
        except Exception as e:
            print(f"   [WARNING] corp_code 조회 실패 ({company_name}): {e}")
        
        return ""
    
    def tag_disclosure(self, disclosure: Dict[str, Any]) -> Dict[str, Any]:
        """
        공시 데이터에 태그 추가
        
        Args:
            disclosure: DART 공시 데이터
            
        Returns:
            태그가 추가된 공시 데이터
        """
        title = disclosure.get('title', '') or disclosure.get('report_nm', '')
        
        # 중요도 태깅
        importance = 'low'
        for level, keywords in self.DISCLOSURE_IMPORTANCE.items():
            for keyword in keywords:
                if keyword in title:
                    importance = level
                    break
            if importance == 'high':
                break
        
        # EV 관련성 체크
        is_ev_related = False
        ev_keywords_found = []
        
        content = f"{title} {disclosure.get('content', '')}"
        content_lower = content.lower()
        
        for keyword in self.EV_KEYWORDS:
            if keyword.lower() in content_lower:
                is_ev_related = True
                ev_keywords_found.append(keyword)
        
        # 태그 추가
        disclosure['tags'] = {
            'importance': importance,
            'is_ev_related': is_ev_related,
            'ev_keywords': ev_keywords_found,
            'tagged_at': datetime.now().isoformat()
        }
        
        return disclosure
    
    def filter_ev_disclosures(self, disclosures: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        EV 관련 공시만 필터링
        
        Args:
            disclosures: 공시 리스트
            
        Returns:
            EV 관련 공시만 포함된 리스트
        """
        ev_disclosures = []
        
        for disclosure in disclosures:
            # 태그가 없으면 추가
            if 'tags' not in disclosure:
                disclosure = self.tag_disclosure(disclosure)
            
            # EV 관련이거나 중요도가 high인 경우 포함
            if disclosure['tags']['is_ev_related'] or disclosure['tags']['importance'] == 'high':
                ev_disclosures.append(disclosure)
        
        return ev_disclosures
    
    def collect_company_disclosures(
        self, 
        company_names: List[str], 
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        여러 기업의 공시 데이터 수집
        
        Args:
            company_names: 기업명 리스트
            days: 수집 기간 (일)
            
        Returns:
            태그된 공시 데이터 리스트
        """
        all_disclosures = []
        
        if not self.dart_tool:
            print("   [WARNING] DART tool이 초기화되지 않았습니다.")
            return all_disclosures
        
        for company_name in company_names:
            corp_code = self.get_corp_code(company_name)
            
            if not corp_code:
                print(f"   [SKIP] {company_name} - corp_code를 찾을 수 없습니다.")
                continue
            
            try:
                # DART에서 최근 공시 수집
                disclosures = self.dart_tool.get_recent_disclosures(corp_code, days=days)
                
                if disclosures:
                    print(f"   [OK] {company_name}: {len(disclosures)}개 공시 수집")
                    
                    # 각 공시에 기업명 추가 및 태깅
                    for disclosure in disclosures:
                        disclosure['company_name'] = company_name
                        disclosure['corp_code'] = corp_code
                        disclosure = self.tag_disclosure(disclosure)
                    
                    all_disclosures.extend(disclosures)
                else:
                    print(f"   [INFO] {company_name}: 공시 없음")
                    
            except Exception as e:
                print(f"   [ERROR] {company_name} 공시 수집 실패: {e}")
        
        return all_disclosures
    
    def get_disclosure_summary(self, disclosures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        공시 데이터 요약 통계
        
        Args:
            disclosures: 공시 리스트
            
        Returns:
            요약 정보
        """
        summary = {
            'total': len(disclosures),
            'by_importance': {'high': 0, 'medium': 0, 'low': 0},
            'ev_related': 0,
            'by_company': {},
            'recent_important': []
        }
        
        for disclosure in disclosures:
            # 태그 확인
            tags = disclosure.get('tags', {})
            importance = tags.get('importance', 'low')
            is_ev_related = tags.get('is_ev_related', False)
            company_name = disclosure.get('company_name', 'Unknown')
            
            # 통계 업데이트
            summary['by_importance'][importance] += 1
            
            if is_ev_related:
                summary['ev_related'] += 1
            
            if company_name not in summary['by_company']:
                summary['by_company'][company_name] = 0
            summary['by_company'][company_name] += 1
            
            # 중요한 공시 수집 (최대 10개)
            if importance == 'high' and len(summary['recent_important']) < 10:
                summary['recent_important'].append({
                    'company': company_name,
                    'title': disclosure.get('title', '') or disclosure.get('report_nm', ''),
                    'date': disclosure.get('rcept_dt', '') or disclosure.get('date', ''),
                })
        
        return summary

