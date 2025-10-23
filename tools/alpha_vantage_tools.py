"""
Alpha Vantage API를 사용한 해외 기업 재무 데이터 수집
"""

import os
import requests
import time
from typing import Dict, Any, Optional
from datetime import datetime


class AlphaVantageTool:
    """
    Alpha Vantage API를 사용한 해외 기업 재무 분석 도구
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_API_KEY')
        self.base_url = "https://www.alphavantage.co/query"
        self.session = requests.Session()
        
        if not self.api_key:
            print("[WARNING] Alpha Vantage API 키가 설정되지 않았습니다.")
            print("   .env 파일에 ALPHA_VANTAGE_API_KEY를 추가하세요.")
        else:
            print(f"[OK] Alpha Vantage API 키 설정됨")
    
    def get_company_financial_data(self, company_name: str) -> Dict[str, Any]:
        """
        해외 기업 재무 데이터 수집
        """
        if not self.api_key:
            return {
                'data_available': False,
                'error': 'Alpha Vantage API 키가 없습니다'
            }
        
        try:
            # 1. 심볼 가져오기
            symbol = self._get_company_symbol(company_name)
            if not symbol:
                return {
                    'data_available': False,
                    'error': f"'{company_name}'의 주식 심볼을 찾을 수 없습니다"
                }
            
            print(f"    Alpha Vantage '{company_name}' ({symbol}) 데이터 수집 중...")
            
            # 2. 회사 개요 정보
            overview = self._get_company_overview(symbol)
            if not overview:
                return {
                    'data_available': False,
                    'error': '회사 개요 정보를 가져올 수 없습니다'
                }
            
            # 3. 손익계산서
            income_statement = self._get_income_statement(symbol)
            
            # 4. 재무상태표
            balance_sheet = self._get_balance_sheet(symbol)
            
            # 5. 현금흐름표
            cash_flow = self._get_cash_flow(symbol)
            
            # 6. 재무 데이터 통합
            financial_data = self._merge_financial_data(
                income_statement, balance_sheet, cash_flow
            )
            
            # 7. 재무비율 계산
            ratios = self._calculate_financial_ratios(
                financial_data, overview
            )
            
            return {
                'company_info': {
                    'corp_name': company_name,
                    'symbol': symbol,
                    'country': overview.get('Country', 'Unknown'),
                    'sector': overview.get('Sector', 'Unknown'),
                    'industry': overview.get('Industry', 'Unknown'),
                    'exchange': overview.get('Exchange', 'Unknown')
                },
                'financial_data': financial_data,
                'financial_ratios': ratios,
                'stock_price': float(overview.get('50DayMovingAverage', 0)),
                'market_cap': float(overview.get('MarketCapitalization', 0)),
                'recent_disclosures': [],
                'analysis_date': datetime.now().isoformat(),
                'data_source': 'ALPHA_VANTAGE',
                'data_available': True
            }
            
        except Exception as e:
            print(f"[FAIL] Alpha Vantage 데이터 수집 실패: {e}")
            return {
                'data_available': False,
                'error': str(e)
            }
    
    def _get_company_symbol(self, company_name: str) -> Optional[str]:
        """
        회사명으로 주식 심볼 조회
        """
        # 주요 기업 심볼 매핑
        symbol_mapping = {
            # 해외 자동차
            'Tesla': 'TSLA',
            '테슬라': 'TSLA',
            'BYD': '1211.HK',  # 홍콩 거래소
            'BMW': 'BMW.DE',
            'Mercedes': 'MBG.DE',
            'Mercedes-Benz': 'MBG.DE',
            '벤츠': 'MBG.DE',
            'Volkswagen': 'VOW.DE',
            '폭스바겐': 'VOW.DE',
            'GM': 'GM',
            'General Motors': 'GM',
            'Ford': 'F',
            '포드': 'F',
            'Toyota': 'TM',
            '도요타': 'TM',
            'Honda': 'HMC',
            '혼다': 'HMC',
            'Nissan': 'NSANY',
            '닛산': 'NSANY',
            
            # 배터리/부품
            'CATL': '300750.SZ',
            'Panasonic': 'PCRFY',
            '파나소닉': 'PCRFY',
            'Bosch': 'BOSCHLTD.NS',
            '보쉬': 'BOSCHLTD.NS',
            'Continental': 'CON.DE',
            '콘티넨탈': 'CON.DE',
            'Magna': 'MGA',
            '마그나': 'MGA',
            'Infineon': 'IFX.DE',
            'Mobileye': 'MBLY',
            'NIO': 'NIO',
            '니오': 'NIO',
            'Xpeng': 'XPEV',
            '샤오펑': 'XPEV',
            'Li Auto': 'LI',
            'Lucid': 'LCID',
            'Rivian': 'RIVN',
            '리비안': 'RIVN'
        }
        
        return symbol_mapping.get(company_name, None)
    
    def _get_company_overview(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        회사 개요 정보 조회
        """
        try:
            params = {
                'function': 'OVERVIEW',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # API 제한 확인
            if 'Note' in data:
                print(f"   [WARNING] Alpha Vantage API 제한: {data['Note']}")
                return None
            
            if 'Symbol' not in data:
                print(f"   [WARNING] 회사 개요 정보 없음")
                return None
            
            time.sleep(12)  # API 제한: 5 calls/min
            return data
            
        except Exception as e:
            print(f"   [WARNING] 회사 개요 조회 실패: {e}")
            return None
    
    def _get_income_statement(self, symbol: str) -> Dict[str, Any]:
        """
        손익계산서 조회
        """
        try:
            params = {
                'function': 'INCOME_STATEMENT',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'annualReports' in data and len(data['annualReports']) > 0:
                latest = data['annualReports'][0]
                time.sleep(12)  # API 제한
                return {
                    'revenue': float(latest.get('totalRevenue', 0)),
                    'operating_profit': float(latest.get('operatingIncome', 0)),
                    'net_income': float(latest.get('netIncome', 0)),
                    'gross_profit': float(latest.get('grossProfit', 0))
                }
            
            return {}
            
        except Exception as e:
            print(f"   [WARNING] 손익계산서 조회 실패: {e}")
            return {}
    
    def _get_balance_sheet(self, symbol: str) -> Dict[str, Any]:
        """
        재무상태표 조회
        """
        try:
            params = {
                'function': 'BALANCE_SHEET',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'annualReports' in data and len(data['annualReports']) > 0:
                latest = data['annualReports'][0]
                time.sleep(12)  # API 제한
                return {
                    'total_assets': float(latest.get('totalAssets', 0)),
                    'total_equity': float(latest.get('totalShareholderEquity', 0)),
                    'total_debt': float(latest.get('longTermDebt', 0)) + float(latest.get('shortTermDebt', 0)),
                    'current_assets': float(latest.get('totalCurrentAssets', 0)),
                    'current_liabilities': float(latest.get('totalCurrentLiabilities', 0))
                }
            
            return {}
            
        except Exception as e:
            print(f"   [WARNING] 재무상태표 조회 실패: {e}")
            return {}
    
    def _get_cash_flow(self, symbol: str) -> Dict[str, Any]:
        """
        현금흐름표 조회
        """
        try:
            params = {
                'function': 'CASH_FLOW',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'annualReports' in data and len(data['annualReports']) > 0:
                latest = data['annualReports'][0]
                time.sleep(12)  # API 제한
                return {
                    'cash_flow_operating': float(latest.get('operatingCashflow', 0)),
                    'cash_flow_investing': float(latest.get('cashflowFromInvestment', 0)),
                    'cash_flow_financing': float(latest.get('cashflowFromFinancing', 0))
                }
            
            return {}
            
        except Exception as e:
            print(f"   [WARNING] 현금흐름표 조회 실패: {e}")
            return {}
    
    def _merge_financial_data(self, income: Dict, balance: Dict, cash_flow: Dict) -> Dict[str, Any]:
        """
        재무제표 데이터 통합
        """
        return {
            # 손익계산서
            'revenue': income.get('revenue', 0),
            'operating_profit': income.get('operating_profit', 0),
            'net_income': income.get('net_income', 0),
            'gross_profit': income.get('gross_profit', 0),
            
            # 재무상태표
            'total_assets': balance.get('total_assets', 0),
            'total_equity': balance.get('total_equity', 0),
            'total_debt': balance.get('total_debt', 0),
            'current_assets': balance.get('current_assets', 0),
            'current_liabilities': balance.get('current_liabilities', 0),
            
            # 현금흐름표
            'cash_flow_operating': cash_flow.get('cash_flow_operating', 0),
            'cash_flow_investing': cash_flow.get('cash_flow_investing', 0),
            'cash_flow_financing': cash_flow.get('cash_flow_financing', 0)
        }
    
    def _calculate_financial_ratios(self, financial_data: Dict[str, Any], overview: Dict[str, Any]) -> Dict[str, float]:
        """
        재무비율 계산
        """
        ratios = {}
        
        try:
            # 수익성 지표
            ratios['roe'] = (financial_data.get('net_income', 0) / financial_data.get('total_equity', 1)) if financial_data.get('total_equity', 0) > 0 else 0.0
            
            ratios['operating_margin'] = (financial_data.get('operating_profit', 0) / financial_data.get('revenue', 1)) if financial_data.get('revenue', 0) > 0 else 0.0
            
            ratios['roa'] = (financial_data.get('net_income', 0) / financial_data.get('total_assets', 1)) if financial_data.get('total_assets', 0) > 0 else 0.0
            
            # 안정성 지표
            ratios['debt_ratio'] = (financial_data.get('total_debt', 0) / financial_data.get('total_equity', 1)) if financial_data.get('total_equity', 0) > 0 else 0.0
            
            ratios['current_ratio'] = (financial_data.get('current_assets', 0) / financial_data.get('current_liabilities', 1)) if financial_data.get('current_liabilities', 0) > 0 else 0.0
            
            # 활동성 지표
            ratios['asset_turnover'] = (financial_data.get('revenue', 0) / financial_data.get('total_assets', 1)) if financial_data.get('total_assets', 0) > 0 else 0.0
            
            # 밸류에이션 지표 (Alpha Vantage에서 제공)
            ratios['per'] = float(overview.get('PERatio', 0))
            ratios['pbr'] = float(overview.get('PriceToBookRatio', 0))
            ratios['market_cap'] = float(overview.get('MarketCapitalization', 0))
            
            return ratios
            
        except Exception as e:
            print(f"   [FAIL] 재무비율 계산 실패: {e}")
            return {}

