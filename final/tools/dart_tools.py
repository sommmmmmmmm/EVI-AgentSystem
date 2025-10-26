"""
DART API  ( )
     
"""

import os
import requests
import json
import zipfile
import io
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET


class DARTTool:
    """
    DART API       
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://opendart.fss.or.kr/api"
        self.session = requests.Session()
        self.corp_code_cache = {}  #  → corp_code 
        
        #     
        print("[DART     ...]")
        self._load_corp_codes()
    
    def _load_corp_codes(self):
        """
              (ZIP   )
        """
        try:
            url = f"{self.base_url}/corpCode.xml"
            params = {'crtfc_key': self.api_key}
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            # ZIP   
            zip_file = zipfile.ZipFile(io.BytesIO(response.content))
            xml_data = zip_file.read('CORPCODE.xml')
            
            # XML 
            root = ET.fromstring(xml_data)
            
            for corp in root.findall('list'):
                corp_code = corp.find('corp_code').text
                corp_name = corp.find('corp_name').text
                stock_code = corp.find('stock_code').text if corp.find('stock_code') is not None else None
                
                #     
                self.corp_code_cache[corp_name] = {
                    'corp_code': corp_code,
                    'stock_code': stock_code,
                    'corp_name': corp_name
                }
                
                #   (: "" → "")
                if '' in corp_name:
                    short_name = corp_name.replace('', '').strip()
                    if short_name not in self.corp_code_cache:
                        self.corp_code_cache[short_name] = {
                            'corp_code': corp_code,
                            'stock_code': stock_code,
                            'corp_name': corp_name
                        }
            
            print(f"[OK] DART   {len(self.corp_code_cache)}  ")
            
        except Exception as e:
            print(f"[FAIL] DART    : {e}")
            # API    
            if "API" in str(e) or "401" in str(e):
                print("[WARNING]  API  !")
    
    def get_company_list(self, corp_cls: str = "Y") -> List[Dict[str, Any]]:
        """
           ( )
        
        Args:
            corp_cls:  (Y: , K: , N: , E: )
        
        Returns:
             
        """
        companies = []
        for corp_name, info in self.corp_code_cache.items():
            if info.get('stock_code'):  # 
                companies.append({
                    'corp_code': info['corp_code'],
                    'corp_name': info['corp_name'],
                    'stock_code': info['stock_code']
                })
        
        return companies
    
    def search_company(self, company_name: str) -> Optional[Dict[str, Any]]:
        """
            (  )
        
        Args:
            company_name: 
        
        Returns:
              (corp_code, stock_code )
        """
        try:
            # 1.   
            if company_name in self.corp_code_cache:
                return self.corp_code_cache[company_name]
            
            # 2.    
            variations = [
                company_name,
                f"{company_name}",
                f"{company_name}",
                company_name.replace("", "").strip(),
                company_name.replace("", "").strip(),
                company_name.replace("()", "").strip()
            ]
            
            for variation in variations:
                if variation in self.corp_code_cache:
                    print(f"    '{company_name}' → '{variation}'  ")
                    return self.corp_code_cache[variation]
            
            # 3.   ( )
            for cached_name, info in self.corp_code_cache.items():
                if company_name in cached_name or cached_name in company_name:
                    print(f"    '{company_name}' → '{cached_name}'  ")
                    return info
            
            # 4.    ( )
            foreign_companies = {
                '': None,
                'Tesla': None,
                'BYD': None,
                'BMW': None,
                '': None,
                '': None,
                'GM': None,
                '': None
            }
            
            if company_name in foreign_companies:
                print(f"   [WARNING] '{company_name}'   DART  ")
                return None
            
            print(f"   [WARNING] '{company_name}' DART   ")
            return None
            
        except Exception as e:
            print(f"[FAIL]   : {e}")
            return None
    
    def get_disclosure_list(self, corp_code: str, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """
          
        
        Args:
            corp_code:  
            start_date:  (YYYYMMDD)
            end_date:  (YYYYMMDD)
        
        Returns:
             
        """
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            
            url = f"{self.base_url}/list.json"
            params = {
                'crtfc_key': self.api_key,
                'corp_code': corp_code,
                'bgn_de': start_date,
                'end_de': end_date,
                'page_count': 100
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == '000':
                return data.get('list', [])
            else:
                error_msg = data.get('message', 'Unknown error')
                print(f"[FAIL]    : {error_msg}")
                return []
                
        except Exception as e:
            print(f"[FAIL]    : {e}")
            return []
    
    def get_financial_data(self, corp_code: str, year: int, reprt_code: str = "11011") -> Dict[str, Any]:
        """
          
        
        Args:
            corp_code:  
            year: 
            reprt_code:  
                - 11011:  ()
                - 11012: 
                - 11013: 1
                - 11014: 3
        
        Returns:
             
        """
        try:
            # fnlttSinglAcntAll.json  (   )
            url = f"{self.base_url}/fnlttSinglAcntAll.json"
            params = {
                'crtfc_key': self.api_key,
                'corp_code': corp_code,
                'bsns_year': str(year),
                'reprt_code': reprt_code,
                'fs_div': 'CFS'  # 
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == '000':
                return self._parse_financial_data(data.get('list', []))
            else:
                error_msg = data.get('message', 'Unknown error')
                print(f"[FAIL]   : {error_msg}")
                return {}
                
        except Exception as e:
            print(f"[FAIL]   : {e}")
            return {}
    
    def _parse_financial_data(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
            
        """
        financial_data = {
            'revenue': 0,           # 
            'operating_profit': 0,  # 
            'net_income': 0,        # 
            'total_assets': 0,      # 
            'total_equity': 0,      # 
            'total_debt': 0,        # 
            'current_assets': 0,    # 
            'current_liabilities': 0, # 
            'cash_flow_operating': 0, # 
            'cash_flow_investing': 0, # 
            'cash_flow_financing': 0  # 
        }
        
        #   ( )
        account_mapping = {
            '': 'revenue',
            '()': 'revenue',
            '': 'operating_profit',
            '()': 'operating_profit',
            '': 'net_income',
            '()': 'net_income',
            '': 'total_assets',
            '': 'total_equity',
            '': 'total_debt',
            '': 'current_assets',
            '': 'current_liabilities',
            '': 'cash_flow_operating',
            '': 'cash_flow_investing',
            '': 'cash_flow_financing'
        }
        
        for item in raw_data:
            account_name = item.get('account_nm', '')
            amount_str = item.get('thstrm_amount', '0')
            
            #  
            try:
                amount = float(str(amount_str).replace(',', ''))
            except (ValueError, AttributeError):
                amount = 0
            
            #  
            for key, value in account_mapping.items():
                if key in account_name:
                    financial_data[value] = amount
                    break
        
        return financial_data
    
    def calculate_financial_ratios(self, financial_data: Dict[str, Any], stock_price: float = None) -> Dict[str, float]:
        """
           (ROE, ROA, PER, PBR  )
        
        Args:
            financial_data:  
            stock_price:  (PER, PBR )
        
        Returns:
             
        """
        ratios = {}
        
        try:
            #  
            ratios['roe'] = (financial_data.get('net_income', 0) / financial_data.get('total_equity', 1)) if financial_data.get('total_equity', 0) > 0 else 0.0
            
            ratios['operating_margin'] = (financial_data.get('operating_profit', 0) / financial_data.get('revenue', 1)) if financial_data.get('revenue', 0) > 0 else 0.0
            
            ratios['roa'] = (financial_data.get('net_income', 0) / financial_data.get('total_assets', 1)) if financial_data.get('total_assets', 0) > 0 else 0.0
            
            #  
            ratios['debt_ratio'] = (financial_data.get('total_debt', 0) / financial_data.get('total_equity', 1)) if financial_data.get('total_equity', 0) > 0 else 0.0
            
            ratios['current_ratio'] = (financial_data.get('current_assets', 0) / financial_data.get('current_liabilities', 1)) if financial_data.get('current_liabilities', 0) > 0 else 0.0
            
            #  
            ratios['asset_turnover'] = (financial_data.get('revenue', 0) / financial_data.get('total_assets', 1)) if financial_data.get('total_assets', 0) > 0 else 0.0
            
            #    (  )
            if stock_price and stock_price > 0:
                shares_outstanding = financial_data.get('total_equity', 0) / 500
                
                if shares_outstanding > 0:
                    eps = financial_data.get('net_income', 0) / shares_outstanding
                    ratios['per'] = (stock_price / eps) if eps > 0 else 0.0
                    
                    bps = financial_data.get('total_equity', 0) / shares_outstanding
                    ratios['pbr'] = (stock_price / bps) if bps > 0 else 0.0
                    
                    ratios['market_cap'] = stock_price * shares_outstanding
                else:
                    ratios['per'] = 0.0
                    ratios['pbr'] = 0.0
                    ratios['market_cap'] = 0.0
            else:
                ratios['per'] = 0.0
                ratios['pbr'] = 0.0
                ratios['market_cap'] = 0.0
            
            return ratios
            
        except Exception as e:
            print(f"[FAIL]    : {e}")
            return {}
    
    def get_company_financial_analysis(self, company_name: str) -> Dict[str, Any]:
        """  (DART →  →  )"""
        
        # 1. DART 
        result = self._try_dart_data(company_name)
        if result['data_available']:
            return result
        
        # 2.     ()
        result = self._try_naver_finance(company_name)
        if result['data_available']:
            return result
        
        # 3.   -  
        return {
            'error': f"'{company_name}'     ",
            'company_name': company_name,
            'data_available': False,
            'excluded_from_analysis': True
        }
    
    def _try_dart_data(self, company_name: str) -> Dict[str, Any]:
        """DART API    """
        try:
            print(f"    DART '{company_name}'  ...")
            
            # 1.  
            company_info = self.search_company(company_name)
            
            if not company_info:
                print(f"   [FAIL] DART '{company_name}'   ")
                return {'data_available': False}
            
            corp_code = company_info['corp_code']
            print(f"   [OK] corp_code: {corp_code}")
            
            # 2.    (2024 → 2023 )
            financial_data = None
            for year in [2024, 2023, 2022]:
                financial_data = self.get_financial_data(corp_code, year, "11011")
                if financial_data and financial_data.get('revenue', 0) > 0:
                    print(f"   [OK] {year}    ")
                    break
            
            if not financial_data or financial_data.get('revenue', 0) == 0:
                print(f"   [FAIL]   ")
                return {'data_available': False}
            
            # 3.   (  API  )
            stock_price = self._get_real_stock_price(company_name, company_info.get('stock_code'))
            
            # 4.   
            ratios = self.calculate_financial_ratios(financial_data, stock_price)
            
            # 5.   
            disclosures = self.get_disclosure_list(corp_code)
            
            return {
                'company_info': company_info,
                'financial_data': financial_data,
                'financial_ratios': ratios,
                'stock_price': stock_price,
                'recent_disclosures': disclosures[:10],
                'analysis_date': datetime.now().isoformat(),
                'data_source': 'DART_API',
                'data_available': True
            }
            
        except Exception as e:
            print(f"[FAIL] DART   : {e}")
            return {'data_available': False}
    
    def _try_naver_finance(self, company_name: str) -> Dict[str, Any]:
        """해외 기업 재무 데이터 수집 (우선순위: SEC EDGAR > Alpha Vantage > Yahoo Finance)"""
        try:
            print(f"    해외 기업 '{company_name}' 재무 데이터 수집 중...")

            # 1. SEC EDGAR API 시도 (미국 기업, 무료, 공식 데이터)
            print(f"   [INFO] SEC EDGAR API 시도 중...")
            sec_result = self._try_sec_edgar(company_name)
            if sec_result['data_available']:
                return sec_result

            # 2. Alpha Vantage API 시도 (.env ALPHA_VANTAGE_ENABLED=1인 경우)
            import os
            alpha_vantage_enabled = os.getenv('ALPHA_VANTAGE_ENABLED', '0') == '1'

            if alpha_vantage_enabled:
                print(f"   [INFO] Alpha Vantage API 시도 중 (ALPHA_VANTAGE_ENABLED=1)")
                alpha_vantage_result = self._try_alpha_vantage(company_name)
                if alpha_vantage_result['data_available']:
                    return alpha_vantage_result
            else:
                print(f"   [INFO] Alpha Vantage API 비활성화 (ALPHA_VANTAGE_ENABLED=0)")

            # 3. Yahoo Finance API 시도 (주가 정보만)
            print(f"   [INFO] Yahoo Finance API 시도 중...")
            yahoo_result = self._try_yahoo_finance(company_name)
            if yahoo_result['data_available']:
                return yahoo_result

            # 4. 모든 API 실패 시 에러 반환
            print(f"[ERROR] '{company_name}'의 재무 데이터를 가져올 수 없습니다.")
            return {
                'error': f"'{company_name}'의 재무 데이터를 가져올 수 없습니다",
                'company_name': company_name,
                'data_available': False,
                'excluded_from_analysis': True
            }

        except Exception as e:
            print(f"[FAIL] 해외 기업 데이터 수집 실패: {e}")
            return {'data_available': False}
    
    def _try_alpha_vantage(self, company_name: str) -> Dict[str, Any]:
        """Alpha Vantage API (SEC EDGAR 실패 시 사용)"""
        try:
            from tools.alpha_vantage_tools import AlphaVantageTool
            
            alpha_vantage = AlphaVantageTool()
            result = alpha_vantage.get_company_financial_data(company_name)
            
            if result['data_available']:
                print(f"   [OK] Alpha Vantage '{company_name}' 데이터 수집")
            
            return result
            
        except ImportError:
            print(f"   [WARNING] Alpha Vantage 도구 없음")
            return {'data_available': False}
        except Exception as e:
            print(f"   [FAIL] Alpha Vantage 실패: {e}")
            return {'data_available': False}
    
    def _try_sec_edgar(self, company_name: str) -> Dict[str, Any]:
        """SEC EDGAR API (미국 기업 우선)"""
        try:
            from tools.sec_edgar_tools import SECEdgarTool
            
            sec_edgar = SECEdgarTool()
            result = sec_edgar.get_company_financial_data(company_name)
            
            if result['data_available']:
                print(f"   [OK] SEC EDGAR '{company_name}' 데이터 수집")
            
            return result
            
        except ImportError:
            print(f"   [WARNING] SEC EDGAR 도구 없음")
            return {'data_available': False}
        except Exception as e:
            print(f"   [FAIL] SEC EDGAR 실패: {e}")
            return {'data_available': False}
    
    def _try_yahoo_finance(self, company_name: str) -> Dict[str, Any]:
        """Yahoo Finance API """
        try:
            from tools.yahoo_finance_tools import YahooFinanceTool
            
            yahoo_finance = YahooFinanceTool()
            result = yahoo_finance.get_company_financial_data(company_name)
            
            if result['data_available']:
                print(f"   [OK] Yahoo Finance '{company_name}'   ")
            
            return result
            
        except ImportError:
            print(f"   [WARNING] Yahoo Finance    ")
            return {'data_available': False}
        except Exception as e:
            print(f"   [FAIL] Yahoo Finance  : {e}")
            return {'data_available': False}
    
    def _generate_overseas_financial_data(self, company_name: str, company_info: Dict[str, str]) -> Dict[str, Any]:
        """해외 기업 데이터를 가져올 수 없을 때 에러 반환"""
        print(f"[ERROR] '{company_name}'의 해외 재무 데이터를 가져올 수 없습니다. API 키를 확인하세요.")
        return {
            'error': f"'{company_name}'의 해외 재무 데이터를 가져올 수 없습니다",
            'company_name': company_name,
            'data_available': False,
            'excluded_from_analysis': True
        }
    
    def _get_real_stock_price(self, company_name: str, stock_code: str = None) -> float:
        """   (Yahoo Finance  )"""
        try:
            # 1. Yahoo Finance   
            if stock_code:
                from tools.yahoo_finance_tools import YahooFinanceTool
                yahoo_tool = YahooFinanceTool()

                #  : .KS  .KQ 
                ticker = f"{stock_code}.KS"  # KOSPI
                stock_data = yahoo_tool.get_stock_price(ticker)

                if not stock_data.get('data_available'):
                    ticker = f"{stock_code}.KQ"  # KOSDAQ
                    stock_data = yahoo_tool.get_stock_price(ticker)

                if stock_data.get('data_available') and stock_data.get('current_price'):
                    price = stock_data['current_price']
                    print(f"   [OK] Yahoo Finance   : {company_name} = {price:,.0f}")
                    return float(price)

            # 2.     
            print(f"   [WARNING]    -  ")
            return 50000.0

        except Exception as e:
            print(f"   [WARNING]    : {e} -  ")
            return 50000.0
    
    def get_recent_disclosures(self, corp_code: str, days: int = 30) -> List[Dict[str, Any]]:
        """   """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        return self.get_disclosure_list(
            corp_code, 
            start_date.strftime("%Y%m%d"),
            end_date.strftime("%Y%m%d")
        )
    
    def search_ev_companies(self) -> List[Dict[str, Any]]:
        """   """
        ev_keywords = ['', '', 'EV', '', '', '', 'BMS', '']
        
        ev_companies = []
        for corp_name, info in self.corp_code_cache.items():
            if any(keyword in corp_name for keyword in ev_keywords):
                if info.get('stock_code'):  # 
                    ev_companies.append(info)
        
        print(f"   [OK]    {len(ev_companies)} ")
        return ev_companies