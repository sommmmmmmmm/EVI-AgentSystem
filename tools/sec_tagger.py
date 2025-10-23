"""
SEC EDGAR Tagger Tool
Purpose: Extract overseas company names and collect SEC filings.
"""

from typing import List, Dict, Any
from datetime import datetime


class SECTagger:
    """
    SEC EDGAR 공시 데이터 태깅 및 기업 매칭 도구
    """
    
    # 주요 해외 전기차 관련 기업 리스트
    OVERSEAS_EV_COMPANIES = {
        # 미국 완성차 (SEC EDGAR)
        'Tesla': {'ticker': 'TSLA', 'cik': '1318605', 'name': 'Tesla Inc', 'source': 'SEC EDGAR'},
        'GM': {'ticker': 'GM', 'cik': '0001467858', 'name': 'General Motors Company', 'source': 'SEC EDGAR'},
        'Ford': {'ticker': 'F', 'cik': '0000037996', 'name': 'Ford Motor Company', 'source': 'SEC EDGAR'},
        'Rivian': {'ticker': 'RIVN', 'cik': '0001874178', 'name': 'Rivian Automotive Inc', 'source': 'SEC EDGAR'},
        'Lucid': {'ticker': 'LCID', 'cik': '0001811210', 'name': 'Lucid Group Inc', 'source': 'SEC EDGAR'},
        
        # 유럽 완성차 (Yahoo Finance)
        'BMW': {'ticker': 'BMW.DE', 'cik': None, 'name': 'BMW AG', 'source': 'Yahoo Finance'},
        'Mercedes': {'ticker': 'MBG.DE', 'cik': None, 'name': 'Mercedes-Benz Group AG', 'source': 'Yahoo Finance'},
        'Volkswagen': {'ticker': 'VOW3.DE', 'cik': None, 'name': 'Volkswagen AG', 'source': 'Yahoo Finance'},
        
        # 중국 완성차 (Yahoo Finance / SEC EDGAR)
        'BYD': {'ticker': '1211.HK', 'cik': None, 'name': 'BYD Company Limited', 'source': 'Yahoo Finance'},
        'Nio': {'ticker': 'NIO', 'cik': '0001736541', 'name': 'NIO Inc', 'source': 'SEC EDGAR'},
        'Xpeng': {'ticker': 'XPEV', 'cik': '0001806059', 'name': 'XPeng Inc', 'source': 'SEC EDGAR'},
        'Li Auto': {'ticker': 'LI', 'cik': '0001799209', 'name': 'Li Auto Inc', 'source': 'SEC EDGAR'},
        
        # 일본 배터리 (Yahoo Finance)
        'Panasonic': {'ticker': '6752.T', 'cik': None, 'name': 'Panasonic Holdings Corporation', 'source': 'Yahoo Finance'},
        
        # 미국 배터리/부품 (SEC EDGAR)
        'Albemarle': {'ticker': 'ALB', 'cik': '0000915913', 'name': 'Albemarle Corporation', 'source': 'SEC EDGAR'},
        'QuantumScape': {'ticker': 'QS', 'cik': '0001811414', 'name': 'QuantumScape Corporation', 'source': 'SEC EDGAR'},
    }
    
    # 공시 유형별 중요도
    FILING_IMPORTANCE = {
        'high': ['10-K', '10-Q', '8-K', 'DEF 14A', 'S-1'],
        'medium': ['10-K/A', '10-Q/A', '8-K/A'],
        'low': ['4', '3', '5', 'SC 13G', 'SC 13D']
    }
    
    # EV 관련 키워드
    EV_KEYWORDS = [
        'electric vehicle', 'EV', 'battery', 'lithium',
        'charging', 'autonomous', 'self-driving',
        'energy storage', 'powertrain', 'electrification',
        'zero emission', 'clean energy', 'sustainability'
    ]
    
    def __init__(self, sec_tool=None):
        """
        Initialize SEC Tagger
        
        Args:
            sec_tool: SECEdgarTool instance
        """
        self.sec_tool = sec_tool
        self._company_cache: Dict[str, str] = {}  # company_name -> cik
    
    def extract_company_names(self, text: str) -> List[str]:
        """
        텍스트에서 해외 기업명 추출
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            추출된 기업명 리스트
        """
        found_companies = []
        
        text_lower = text.lower()
        
        for company_name in self.OVERSEAS_EV_COMPANIES.keys():
            if company_name.lower() in text_lower:
                if company_name not in found_companies:
                    found_companies.append(company_name)
        
        return found_companies
    
    def get_cik(self, company_name: str) -> str:
        """
        기업명으로 SEC CIK 조회
        
        Args:
            company_name: 기업명
            
        Returns:
            CIK 또는 빈 문자열
        """
        # 캐시 확인
        if company_name in self._company_cache:
            return self._company_cache[company_name]
        
        # 딕셔너리에서 조회
        if company_name in self.OVERSEAS_EV_COMPANIES:
            cik = self.OVERSEAS_EV_COMPANIES[company_name].get('cik')
            if cik:
                self._company_cache[company_name] = cik
                return cik
        
        return ""
    
    def tag_filing(self, filing: Dict[str, Any]) -> Dict[str, Any]:
        """
        공시 데이터에 태그 추가
        
        Args:
            filing: SEC 공시 데이터
            
        Returns:
            태그가 추가된 공시 데이터
        """
        form_type = filing.get('form', '') or filing.get('form_type', '')
        
        # 중요도 태깅
        importance = 'low'
        for level, form_types in self.FILING_IMPORTANCE.items():
            if form_type in form_types:
                importance = level
                break
        
        # EV 관련성 체크 (제목 및 설명)
        is_ev_related = False
        ev_keywords_found = []
        
        content = f"{filing.get('title', '')} {filing.get('description', '')}"
        content_lower = content.lower()
        
        for keyword in self.EV_KEYWORDS:
            if keyword.lower() in content_lower:
                is_ev_related = True
                ev_keywords_found.append(keyword)
        
        # 태그 추가
        filing['tags'] = {
            'importance': importance,
            'is_ev_related': is_ev_related,
            'ev_keywords': ev_keywords_found,
            'tagged_at': datetime.now().isoformat()
        }
        
        return filing
    
    def filter_ev_filings(self, filings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        EV 관련 공시만 필터링
        
        Args:
            filings: 공시 리스트
            
        Returns:
            EV 관련 공시만 포함된 리스트
        """
        ev_filings = []
        
        for filing in filings:
            # 태그가 없으면 추가
            if 'tags' not in filing:
                filing = self.tag_filing(filing)
            
            # 중요도가 high이면 무조건 포함, 아니면 EV 관련만
            if filing['tags']['importance'] == 'high' or filing['tags']['is_ev_related']:
                ev_filings.append(filing)
        
        return ev_filings
    
    def collect_company_filings(
        self, 
        company_names: List[str], 
        max_filings: int = 5
    ) -> List[Dict[str, Any]]:
        """
        여러 기업의 SEC 공시 데이터 수집
        
        Args:
            company_names: 기업명 리스트
            max_filings: 기업당 최대 수집 개수
            
        Returns:
            태그된 공시 데이터 리스트
        """
        all_filings = []
        
        if not self.sec_tool:
            print("   [WARNING] SEC EDGAR tool이 초기화되지 않았습니다.")
            return all_filings
        
        # 중요한 form types
        important_forms = ['10-K', '10-Q', '8-K']
        
        for company_name in company_names:
            cik = self.get_cik(company_name)
            
            if not cik:
                # 미국 기업이 아니면 Yahoo Finance 사용 (공시는 없음)
                company_info = self.OVERSEAS_EV_COMPANIES.get(company_name, {})
                source = company_info.get('source', 'Unknown')
                print(f"   [INFO] {company_name} - {source}에서 데이터 수집 (공시 없음)")
                continue
            
            try:
                # 각 form type별로 공시 수집
                company_filings = []
                for form_type in important_forms:
                    filings = self.sec_tool.get_recent_filings(cik, form_type=form_type)
                    if filings:
                        # max_filings 개수만큼만 가져오기
                        company_filings.extend(filings[:2])  # 각 type당 2개씩
                
                if company_filings:
                    # max_filings 제한
                    company_filings = company_filings[:max_filings]
                    print(f"   [OK] {company_name}: {len(company_filings)}개 공시 수집")
                    
                    # 각 공시에 기업명 추가 및 태깅
                    for filing in company_filings:
                        filing['company_name'] = company_name
                        filing['cik'] = cik
                        filing = self.tag_filing(filing)
                    
                    all_filings.extend(company_filings)
                else:
                    print(f"   [INFO] {company_name}: 공시 없음")
                    
            except Exception as e:
                print(f"   [ERROR] {company_name} 공시 수집 실패: {e}")
        
        return all_filings
    
    def get_filing_summary(self, filings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        공시 데이터 요약 통계
        
        Args:
            filings: 공시 리스트
            
        Returns:
            요약 정보
        """
        summary = {
            'total': len(filings),
            'by_importance': {'high': 0, 'medium': 0, 'low': 0},
            'ev_related': 0,
            'by_company': {},
            'recent_important': []
        }
        
        for filing in filings:
            # 태그 확인
            tags = filing.get('tags', {})
            importance = tags.get('importance', 'low')
            is_ev_related = tags.get('is_ev_related', False)
            company_name = filing.get('company_name', 'Unknown')
            
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
                    'title': filing.get('form', '') or filing.get('form_type', ''),
                    'description': filing.get('description', '')[:100],
                    'date': filing.get('filing_date', '') or filing.get('date', ''),
                })
        
        return summary

