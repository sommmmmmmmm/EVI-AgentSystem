"""
SEC EDGAR API를 사용한 미국 상장 기업 재무 데이터 수집
공식 재무제표 데이터로 신뢰도 매우 높음
"""

import os
import requests
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import json


class SECEdgarTool:
    """
    SEC EDGAR API를 사용한 미국 상장 기업 재무 분석 도구
    - 무료 API (User-Agent만 필요)
    - 공식 재무제표 데이터
    - 10-K, 10-Q 보고서 접근
    """
    
    def __init__(self, user_agent: str = None):
        # SEC는 User-Agent 필수 (이메일 포함 권장)
        self.user_agent = user_agent or "EVI-Agent/1.0 (evi-agent@example.com)"
        self.base_url = "https://data.sec.gov"
        self.session = requests.Session()
        # Host 헤더는 자동으로 설정되도록 제거 (수동 설정 시 404 발생 가능)
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept-Encoding': 'gzip, deflate'
        })
        
        print(f"[OK] SEC EDGAR API 초기화 완료 (User-Agent: {self.user_agent})")
    
    def get_company_financial_data(self, company_name: str) -> Dict[str, Any]:
        """
        미국 상장 기업 재무 데이터 수집
        """
        try:
            # 1. CIK 코드 가져오기
            cik = self._get_cik(company_name)
            if not cik:
                return {
                    'data_available': False,
                    'error': f"'{company_name}'의 CIK 코드를 찾을 수 없습니다"
                }
            
            print(f"    SEC EDGAR '{company_name}' (CIK: {cik}) 데이터 수집 중...")
            
            # 2. 회사 정보 가져오기
            company_facts = self._get_company_facts(cik)
            if not company_facts:
                return {
                    'data_available': False,
                    'error': '회사 재무 데이터를 가져올 수 없습니다'
                }
            
            # 3. 재무 데이터 추출
            financial_data = self._extract_financial_data(company_facts)
            
            # 4. 재무비율 계산
            ratios = self._calculate_financial_ratios(financial_data)
            
            # 5. 회사 개요 정보
            company_info = self._get_company_info(cik, company_name)
            
            return {
                'company_info': company_info,
                'financial_data': financial_data,
                'financial_ratios': ratios,
                'stock_price': 0,  # Yahoo Finance에서 별도 조회
                'market_cap': financial_data.get('market_cap', 0),
                'recent_disclosures': [],
                'analysis_date': datetime.now().isoformat(),
                'data_source': 'SEC_EDGAR',
                'data_available': True
            }
            
        except Exception as e:
            print(f"[FAIL] SEC EDGAR 데이터 수집 실패: {e}")
            return {
                'data_available': False,
                'error': str(e)
            }
    
    def _normalize_cik(self, cik: str) -> str:
        """
        CIK를 10자리 형식으로 정규화 (앞에 0 패딩)
        
        Args:
            cik: CIK 코드 (숫자 문자열)
            
        Returns:
            10자리로 패딩된 CIK (예: '0001318605')
        """
        # 숫자만 추출
        cik_digits = ''.join(filter(str.isdigit, cik))
        # 10자리로 패딩
        return cik_digits.zfill(10)
    
    def _get_cik(self, company_name: str) -> Optional[str]:
        """
        회사명으로 CIK 코드 조회 (10자리 형식)
        """
        # 주요 기업 CIK 매핑 (10자리 숫자로 패딩)
        cik_mapping = {
            # 미국 자동차
            'Tesla': '0001318605',
            '테슬라': '0001318605',
            'GM': '0001467858',
            'General Motors': '0001467858',
            'Ford': '0000037996',
            '포드': '0000037996',
            'Rivian': '0001874178',
            '리비안': '0001874178',
            'Lucid': '0001811210',
            
            # 중국 자동차 (미국 상장)
            'Nio': '0001736541',
            'NIO': '0001736541',
            'Xpeng': '0001806059',
            'XPEV': '0001806059',
            'Li Auto': '0001799209',
            'LI': '0001799209',
            
            # 미국 배터리/부품
            'Albemarle': '0000915913',
            'QuantumScape': '0001811414',
            
            # 빅테크
            'Apple': '0000320193',
            'Microsoft': '0000789019',
            'Amazon': '0001018724',
            'Alphabet': '0001652044',
            'Google': '0001652044',
            'Meta': '0001326801',
            'Facebook': '0001326801',
            
            # 반도체/부품
            'Intel': '0000050863',
            'AMD': '0000002488',
            'NVIDIA': '0001045810',
            'Qualcomm': '0000804328',
            'Texas Instruments': '0000097476'
        }
        
        cik = cik_mapping.get(company_name)
        if cik:
            # 이미 10자리로 패딩되어 있는지 확인
            return self._normalize_cik(cik)
        
        # 매핑에 없으면 검색 API 사용 (간단한 구현)
        print(f"   [WARNING] '{company_name}'의 CIK 매핑 없음")
        return None
    
    def _get_company_facts(self, cik: str) -> Optional[Dict[str, Any]]:
        """
        회사의 모든 재무 팩트 데이터 조회
        
        Args:
            cik: 10자리 CIK 코드 (예: '0001318605')
        """
        try:
            # CIK를 10자리로 정규화 (혹시 모를 경우를 대비)
            cik_padded = self._normalize_cik(cik)
            
            # SEC API 형식: https://data.sec.gov/api/xbrl/companyfacts/CIK0001318605.json
            url = f"{self.base_url}/api/xbrl/companyfacts/CIK{cik_padded}.json"
            
            print(f"   [DEBUG] SEC API 호출: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # SEC API는 10초에 10회 제한 (1초 대기)
            time.sleep(1)
            
            return data
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"   ❌ [에러] CIK {cik_padded}의 데이터를 찾을 수 없습니다 (404)")
                print(f"   → URL: {url}")
                print(f"   → CIK 형식을 확인하세요. 10자리여야 합니다 (예: CIK0001318605.json)")
            elif e.response.status_code == 403:
                print(f"   ❌ [에러] SEC API 접근 거부 (403)")
                print(f"   → User-Agent 헤더를 확인하세요: {self.user_agent}")
            elif e.response.status_code == 429:
                print(f"   ❌ [에러] SEC API 요청 한도 초과 (429)")
                print(f"   → Rate limit: 10 requests/second을 초과했습니다")
            else:
                print(f"   ❌ [에러] SEC API HTTP 오류: {e.response.status_code}")
            return None
            
        except Exception as e:
            print(f"   ❌ [에러] 회사 팩트 조회 실패: {e}")
            return None
    
    def _extract_financial_data(self, company_facts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Company Facts에서 재무 데이터 추출
        """
        financial_data = {
            'revenue': 0,
            'operating_profit': 0,
            'net_income': 0,
            'total_assets': 0,
            'total_equity': 0,
            'total_debt': 0,
            'current_assets': 0,
            'current_liabilities': 0,
            'cash_flow_operating': 0,
            'cash_flow_investing': 0,
            'cash_flow_financing': 0,
            'gross_profit': 0,
            'market_cap': 0
        }
        
        try:
            # US-GAAP 표준 계정과목
            us_gaap = company_facts.get('facts', {}).get('us-gaap', {})
            
            # 최신 연간 데이터 추출 (10-K)
            def get_latest_annual_value(account_name: str) -> float:
                """특정 계정과목의 최신 연간 데이터 가져오기"""
                if account_name not in us_gaap:
                    return 0
                
                units = us_gaap[account_name].get('units', {})
                # USD 단위 데이터 찾기
                usd_data = units.get('USD', [])
                
                # 10-K (연간 보고서) 데이터만 필터링
                annual_data = [
                    d for d in usd_data 
                    if d.get('form') == '10-K' and d.get('val')
                ]
                
                if not annual_data:
                    return 0
                
                # 가장 최신 데이터
                latest = sorted(annual_data, key=lambda x: x.get('end', ''), reverse=True)[0]
                return float(latest.get('val', 0))
            
            # 재무제표 항목 매핑
            financial_data['revenue'] = get_latest_annual_value('Revenues') or \
                                       get_latest_annual_value('RevenueFromContractWithCustomerExcludingAssessedTax')
            
            financial_data['net_income'] = get_latest_annual_value('NetIncomeLoss') or \
                                          get_latest_annual_value('ProfitLoss')
            
            financial_data['operating_profit'] = get_latest_annual_value('OperatingIncomeLoss')
            
            financial_data['gross_profit'] = get_latest_annual_value('GrossProfit')
            
            financial_data['total_assets'] = get_latest_annual_value('Assets')
            
            financial_data['total_equity'] = get_latest_annual_value('StockholdersEquity') or \
                                            get_latest_annual_value('StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest')
            
            financial_data['current_assets'] = get_latest_annual_value('AssetsCurrent')
            
            financial_data['current_liabilities'] = get_latest_annual_value('LiabilitiesCurrent')
            
            # 부채는 장기부채 + 단기부채
            long_term_debt = get_latest_annual_value('LongTermDebt') or \
                           get_latest_annual_value('LongTermDebtNoncurrent')
            short_term_debt = get_latest_annual_value('ShortTermBorrowings') or \
                            get_latest_annual_value('LongTermDebtCurrent')
            financial_data['total_debt'] = long_term_debt + short_term_debt
            
            # 현금흐름
            financial_data['cash_flow_operating'] = get_latest_annual_value('NetCashProvidedByUsedInOperatingActivities')
            
            financial_data['cash_flow_investing'] = get_latest_annual_value('NetCashProvidedByUsedInInvestingActivities')
            
            financial_data['cash_flow_financing'] = get_latest_annual_value('NetCashProvidedByUsedInFinancingActivities')
            
            # 시가총액 (EntityPublicFloat로 추정 가능, 없으면 0)
            financial_data['market_cap'] = get_latest_annual_value('EntityPublicFloat')
            
            return financial_data
            
        except Exception as e:
            print(f"   [WARNING] 재무 데이터 추출 실패: {e}")
            return financial_data
    
    def _calculate_financial_ratios(self, financial_data: Dict[str, Any]) -> Dict[str, float]:
        """
        재무비율 계산
        """
        ratios = {}
        
        try:
            # 수익성 지표
            ratios['roe'] = (financial_data.get('net_income', 0) / financial_data.get('total_equity', 1)) \
                           if financial_data.get('total_equity', 0) > 0 else 0.0
            
            ratios['operating_margin'] = (financial_data.get('operating_profit', 0) / financial_data.get('revenue', 1)) \
                                        if financial_data.get('revenue', 0) > 0 else 0.0
            
            ratios['roa'] = (financial_data.get('net_income', 0) / financial_data.get('total_assets', 1)) \
                           if financial_data.get('total_assets', 0) > 0 else 0.0
            
            ratios['gross_margin'] = (financial_data.get('gross_profit', 0) / financial_data.get('revenue', 1)) \
                                    if financial_data.get('revenue', 0) > 0 else 0.0
            
            # 안정성 지표
            ratios['debt_ratio'] = (financial_data.get('total_debt', 0) / financial_data.get('total_equity', 1)) \
                                  if financial_data.get('total_equity', 0) > 0 else 0.0
            
            ratios['current_ratio'] = (financial_data.get('current_assets', 0) / financial_data.get('current_liabilities', 1)) \
                                     if financial_data.get('current_liabilities', 0) > 0 else 0.0
            
            # 활동성 지표
            ratios['asset_turnover'] = (financial_data.get('revenue', 0) / financial_data.get('total_assets', 1)) \
                                      if financial_data.get('total_assets', 0) > 0 else 0.0
            
            # 기타
            ratios['market_cap'] = financial_data.get('market_cap', 0)
            
            return ratios
            
        except Exception as e:
            print(f"   [FAIL] 재무비율 계산 실패: {e}")
            return {}
    
    def _get_company_info(self, cik: str, company_name: str) -> Dict[str, str]:
        """
        회사 기본 정보
        """
        return {
            'corp_name': company_name,
            'cik': cik,
            'country': 'US',
            'sector': 'Automotive',  # 실제로는 submissions API에서 가져와야 함
            'industry': 'Electric Vehicles'
        }
    
    def get_recent_filings(self, cik: str, form_type: str = '10-K') -> List[Dict[str, Any]]:
        """
        최근 SEC 제출 서류 조회
        
        Args:
            cik: 10자리 CIK 코드 (예: '0001318605')
            form_type: 서류 유형 (10-K, 10-Q, 8-K 등)
        """
        try:
            # CIK를 10자리로 정규화
            cik_padded = self._normalize_cik(cik)
            
            # SEC API 형식: https://data.sec.gov/submissions/CIK0001318605.json
            url = f"{self.base_url}/submissions/CIK{cik_padded}.json"
            
            print(f"   [DEBUG] SEC Submissions API 호출: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            filings = data.get('filings', {}).get('recent', {})
            
            # 해당 form_type 필터링
            results = []
            forms = filings.get('form', [])
            filing_dates = filings.get('filingDate', [])
            accession_numbers = filings.get('accessionNumber', [])
            primary_documents = filings.get('primaryDocument', [])
            
            for i, form in enumerate(forms):
                if form == form_type:
                    results.append({
                        'form': form,
                        'form_type': form,
                        'filing_date': filing_dates[i] if i < len(filing_dates) else '',
                        'date': filing_dates[i] if i < len(filing_dates) else '',
                        'accession_number': accession_numbers[i] if i < len(accession_numbers) else '',
                        'primary_document': primary_documents[i] if i < len(primary_documents) else '',
                        'description': f'{form} filing'
                    })
            
            time.sleep(1)
            return results[:10]  # 최근 10개만
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"   ❌ [에러] CIK {cik_padded}의 Submissions를 찾을 수 없습니다 (404)")
                print(f"   → URL: {url}")
            elif e.response.status_code == 403:
                print(f"   ❌ [에러] SEC API 접근 거부 (403)")
            elif e.response.status_code == 429:
                print(f"   ❌ [에러] SEC API 요청 한도 초과 (429)")
            else:
                print(f"   ❌ [에러] SEC API HTTP 오류: {e.response.status_code}")
            return []
            
        except Exception as e:
            print(f"   ❌ [에러] SEC 제출 서류 조회 실패: {e}")
            return []

