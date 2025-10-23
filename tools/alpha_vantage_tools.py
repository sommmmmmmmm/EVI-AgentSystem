"""
Alpha Vantage API      
 API   
"""

import os
import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime
import time


class AlphaVantageTool:
    """
    Alpha Vantage API      
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
        self.base_url = "https://www.alphavantage.co/query"
        self.session = requests.Session()
        
        # API   (: 5 calls/minute, 500 calls/day)
        self.last_call_time = 0
        self.min_call_interval = 12  # 12  (5 calls/minute)
    
    def get_company_financial_data(self, company_name: str) -> Dict[str, Any]:
        """
        Alpha Vantage API     
        """
        try:
            #   
            symbol = self._get_company_symbol(company_name)
            if not symbol:
                return {'data_available': False, 'error': f"'{company_name}'    "}
            
            print(f"    Alpha Vantage '{company_name}' ({symbol})  ...")
            
            # API   
            self._wait_for_rate_limit()
            
            #   
            basic_info = self._get_company_overview(symbol)
            if not basic_info:
                return {'data_available': False, 'error': '   '}
            
            #   
            financial_data = self._get_income_statement(symbol)
            balance_sheet = self._get_balance_sheet(symbol)
            cash_flow = self._get_cash_flow(symbol)
            
            #  
            integrated_financial_data = self._integrate_financial_data(
                financial_data, balance_sheet, cash_flow
            )
            
            #   
            ratios = self._calculate_financial_ratios(integrated_financial_data, basic_info)
            
            #     
            has_financial_data = (
                integrated_financial_data.get('revenue', 0) > 0 or
                integrated_financial_data.get('operating_profit', 0) > 0 or
                integrated_financial_data.get('net_income', 0) > 0
            )
            
            return {
                'company_info': {
                    'corp_name': company_name,
                    'symbol': symbol,
                    'country': basic_info.get('Country', 'Unknown'),
                    'sector': basic_info.get('Sector', 'Unknown'),
                    'industry': basic_info.get('Industry', 'Unknown'),
                    'description': basic_info.get('Description', ''),
                    'market_cap': basic_info.get('MarketCapitalization', 0)
                },
                'financial_data': integrated_financial_data,
                'financial_ratios': ratios,
                'stock_price': float(basic_info.get('PERatio', 0)) if basic_info.get('PERatio') else 0,
                'market_cap': int(basic_info.get('MarketCapitalization', 0)) if basic_info.get('MarketCapitalization') else 0,
                'recent_disclosures': [],
                'analysis_date': datetime.now().isoformat(),
                'data_source': 'ALPHA_VANTAGE',
                'data_available': has_financial_data  #      True
            }
            
        except Exception as e:
            print(f"[FAIL] Alpha Vantage   : {e}")
            return {'data_available': False, 'error': str(e)}
    
    def _get_company_symbol(self, company_name: str) -> Optional[str]:
        """
         Alpha Vantage  
        """
        symbol_mapping = {
            '': 'TSLA',
            'Tesla': 'TSLA',
            'BYD': 'BYDDY',
            'BMW': 'BMW.DE',
            '': 'MBG.DE',
            'Mercedes-Benz': 'MBG.DE',
            '': 'VOW.DE',
            'Volkswagen': 'VOW.DE',
            'GM': 'GM',
            'General Motors': 'GM',
            '': 'F',
            'Ford': 'F',
            '': 'BOSCH.NS',
            'Bosch': 'BOSCH.NS',
            '': 'CON.DE',
            'Continental': 'CON.DE',
            'ABB': 'ABB',
            '': 'MGA',
            'Magna': 'MGA',
            '': 'IFX.DE',
            'Infineon': 'IFX.DE',
            '': 'MBLY',
            'Mobileye': 'MBLY'
        }
        
        return symbol_mapping.get(company_name, None)
    
    def _wait_for_rate_limit(self):
        """
        API   
        """
        import os
        if os.getenv('ALPHA_VANTAGE_ENABLED', '0').lower() not in ('1','true'):
            return
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time
        
        if time_since_last_call < self.min_call_interval:
            wait_time = self.min_call_interval - time_since_last_call
            print(f"   ⏳ API   : {wait_time:.1f}")
            if wait_time > 5:
                wait_time = 5
            time.sleep(wait_time)
        
        self.last_call_time = time.time()
    
    def _get_company_overview(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
           
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
            
            if 'Error Message' in data:
                print(f"   [FAIL] Alpha Vantage : {data['Error Message']}")
                return None
            
            if 'Note' in data:
                print(f"   [WARNING] API  : {data['Note']}")
                return None
            
            return data
            
        except Exception as e:
            print(f"   [FAIL]    : {e}")
            return None
    
    def _get_income_statement(self, symbol: str) -> Dict[str, Any]:
        """
         
        """
        try:
            self._wait_for_rate_limit()
            
            params = {
                'function': 'INCOME_STATEMENT',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'Error Message' in data or 'Note' in data:
                print(f"   [WARNING]   : {data.get('Error Message', data.get('Note', 'Unknown error'))}")
                return {}
            
            #    
            annual_reports = data.get('annualReports', [])
            if annual_reports:
                latest_report = annual_reports[0]
                
                return {
                    'revenue': float(latest_report.get('totalRevenue', 0)),
                    'operating_profit': float(latest_report.get('operatingIncome', 0)),
                    'net_income': float(latest_report.get('netIncome', 0)),
                    'gross_profit': float(latest_report.get('grossProfit', 0)),
                    'ebitda': float(latest_report.get('ebitda', 0))
                }
            
            return {}
            
        except Exception as e:
            print(f"   [FAIL]   : {e}")
            return {}
    
    def _get_balance_sheet(self, symbol: str) -> Dict[str, Any]:
        """
         
        """
        try:
            self._wait_for_rate_limit()
            
            params = {
                'function': 'BALANCE_SHEET',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'Error Message' in data or 'Note' in data:
                print(f"   [WARNING]   : {data.get('Error Message', data.get('Note', 'Unknown error'))}")
                return {}
            
            #    
            annual_reports = data.get('annualReports', [])
            if annual_reports:
                latest_report = annual_reports[0]
                
                return {
                    'total_assets': float(latest_report.get('totalAssets', 0)),
                    'total_equity': float(latest_report.get('totalShareholderEquity', 0)),
                    'total_debt': float(latest_report.get('totalDebt', 0)),
                    'current_assets': float(latest_report.get('totalCurrentAssets', 0)),
                    'current_liabilities': float(latest_report.get('totalCurrentLiabilities', 0)),
                    'cash': float(latest_report.get('cashAndCashEquivalentsAtCarryingValue', 0))
                }
            
            return {}
            
        except Exception as e:
            print(f"   [FAIL]   : {e}")
            return {}
    
    def _get_cash_flow(self, symbol: str) -> Dict[str, Any]:
        """
         
        """
        try:
            self._wait_for_rate_limit()
            
            params = {
                'function': 'CASH_FLOW',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'Error Message' in data or 'Note' in data:
                print(f"   [WARNING]   : {data.get('Error Message', data.get('Note', 'Unknown error'))}")
                return {}
            
            #    
            annual_reports = data.get('annualReports', [])
            if annual_reports:
                latest_report = annual_reports[0]
                
                return {
                    'cash_flow_operating': float(latest_report.get('operatingCashflow', 0)),
                    'cash_flow_investing': float(latest_report.get('cashflowFromInvestment', 0)),
                    'cash_flow_financing': float(latest_report.get('cashflowFromFinancing', 0))
                }
            
            return {}
            
        except Exception as e:
            print(f"   [FAIL]   : {e}")
            return {}
    
    def _integrate_financial_data(self, income: Dict[str, Any], balance: Dict[str, Any], cash_flow: Dict[str, Any]) -> Dict[str, Any]:
        """
          
        """
        integrated = {}
        
        #  
        integrated.update(income)
        
        #  
        integrated.update(balance)
        
        #  
        integrated.update(cash_flow)
        
        return integrated
    
    def _calculate_financial_ratios(self, financial_data: Dict[str, Any], basic_info: Dict[str, Any]) -> Dict[str, float]:
        """
          
        """
        ratios = {}
        
        try:
            revenue = financial_data.get('revenue', 0)
            net_income = financial_data.get('net_income', 0)
            operating_profit = financial_data.get('operating_profit', 0)
            total_assets = financial_data.get('total_assets', 0)
            total_equity = financial_data.get('total_equity', 0)
            total_debt = financial_data.get('total_debt', 0)
            current_assets = financial_data.get('current_assets', 0)
            current_liabilities = financial_data.get('current_liabilities', 0)
            
            #  
            ratios['roe'] = (net_income / total_equity) if total_equity > 0 else 0.0
            ratios['operating_margin'] = (operating_profit / revenue) if revenue > 0 else 0.0
            ratios['roa'] = (net_income / total_assets) if total_assets > 0 else 0.0
            
            #  
            ratios['debt_ratio'] = (total_debt / total_equity) if total_equity > 0 else 0.0
            ratios['current_ratio'] = (current_assets / current_liabilities) if current_liabilities > 0 else 0.0
            
            #  
            ratios['asset_turnover'] = (revenue / total_assets) if total_assets > 0 else 0.0
            
            #    (Alpha Vantage )
            pe_ratio = basic_info.get('PERatio')
            pb_ratio = basic_info.get('PriceToBookRatio')
            market_cap = basic_info.get('MarketCapitalization')
            
            ratios['per'] = float(pe_ratio) if pe_ratio else 0.0
            ratios['pbr'] = float(pb_ratio) if pb_ratio else 0.0
            ratios['market_cap'] = int(market_cap) if market_cap else 0
            
            return ratios
            
        except Exception as e:
            print(f"   [FAIL]    : {e}")
            return {}
