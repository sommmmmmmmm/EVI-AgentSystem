"""
Yahoo Finance API      
"""

import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import time


class YahooFinanceTool:
    """
    Yahoo Finance API      
    """
    
    def __init__(self):
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_company_financial_data(self, company_name: str) -> Dict[str, Any]:
        """
            
        """
        try:
            #   
            symbol = self._get_company_symbol(company_name)
            if not symbol:
                return {'data_available': False, 'error': f"'{company_name}'    "}
            
            print(f"    Yahoo Finance '{company_name}' ({symbol})  ...")
            
            #   
            basic_info = self._get_basic_info(symbol)
            if not basic_info:
                return {'data_available': False, 'error': '   '}
            
            #   
            financial_data = self._get_financial_data(symbol)
            
            #   
            price_data = self._get_price_data(symbol)
            
            #   
            ratios = self._calculate_financial_ratios(financial_data, price_data)
            
            return {
                'company_info': {
                    'corp_name': company_name,
                    'symbol': symbol,
                    'country': basic_info.get('country', 'Unknown'),
                    'sector': basic_info.get('sector', 'Unknown'),
                    'industry': basic_info.get('industry', 'Unknown')
                },
                'financial_data': financial_data,
                'financial_ratios': ratios,
                'stock_price': price_data.get('current_price', 0),
                'market_cap': price_data.get('market_cap', 0),
                'recent_disclosures': [],
                'analysis_date': datetime.now().isoformat(),
                'data_source': 'YAHOO_FINANCE',
                'data_available': True
            }
            
        except Exception as e:
            print(f"[FAIL] Yahoo Finance   : {e}")
            return {'data_available': False, 'error': str(e)}
    
    def _get_company_symbol(self, company_name: str) -> Optional[str]:
        """
         Yahoo Finance  
        """
        symbol_mapping = {
            #  
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
            '': 'BOSCH.NS',  #  
            'Bosch': 'BOSCH.NS',
            '': 'CON.DE',
            'Continental': 'CON.DE',
            'ABB': 'ABB',
            '': 'MGA',
            'Magna': 'MGA',
            '': 'IFX.DE',
            'Infineon': 'IFX.DE',
            '': 'MBLY',
            'Mobileye': 'MBLY',
            
            #   (Yahoo Finance  )
            'LG': '373220.KS',
            'LG Energy Solution': '373220.KS',
            'SDI': '006400.KS',
            'Samsung SDI': '006400.KS',
            'SK': '096770.KS',
            'SK On': '096770.KS',
            '': '012330.KS',
            'Hyundai Mobis': '012330.KS',
            '': '204320.KS',
            'Mando': '204320.KS',
            '': '298040.KS',
            '': '298040.KS',
            'LS': '001040.KS',
            'LS Cable': '001040.KS',
            '': '247540.KS',
            'EcoPro BM': '247540.KS',
            '': '003670.KS',
            'POSCO Chemical': '003670.KS',
            '': '018880.KS',
            'Hanon Systems': '018880.KS',
            '': '005930.KS',
            'Samsung Electronics': '005930.KS',
            'SK': '000660.KS',
            'SK Hynix': '000660.KS'
        }
        
        return symbol_mapping.get(company_name, None)
    
    def _get_basic_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
           
        """
        try:
            url = f"{self.base_url}/{symbol}"
            params = {
                'range': '1d',
                'interval': '1d',
                'includePrePost': 'false'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            result = data.get('chart', {}).get('result', [])
            
            if not result:
                return None
            
            meta = result[0].get('meta', {})
            
            return {
                'symbol': symbol,
                'currency': meta.get('currency', 'USD'),
                'exchange': meta.get('exchangeName', 'Unknown'),
                'country': self._get_country_from_exchange(meta.get('exchangeName', '')),
                'sector': 'Automotive',  # 
                'industry': 'Electric Vehicles'  # 
            }
            
        except Exception as e:
            print(f"   [WARNING]    : {e}")
            return None
    
    def _get_financial_data(self, symbol: str) -> Dict[str, Any]:
        """
           (  )
        """
        # Yahoo Finance    
        #       API  
        #       
        
        return {
            'revenue': 0,  #   
            'operating_profit': 0,  #   
            'net_income': 0,  #   
            'total_assets': 0,  #   
            'total_equity': 0,  #   
            'total_debt': 0,  #   
            'current_assets': 0,  #   
            'current_liabilities': 0,  #   
            'cash_flow_operating': 0,  #   
            'cash_flow_investing': 0,  #   
            'cash_flow_financing': 0  #   
        }
    
    def _get_price_data(self, symbol: str) -> Dict[str, Any]:
        """
           ( )
        """
        try:
            #    
            url = f"{self.base_url}/{symbol}"
            params = {
                'range': '1d',
                'interval': '1d',
                'includePrePost': 'false'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            result = data.get('chart', {}).get('result', [])
            
            if not result:
                return {'current_price': 0, 'market_cap': 0, 'volume': 0}
            
            meta = result[0].get('meta', {})
            quotes = result[0].get('indicators', {}).get('quote', [])
            
            current_price = 0
            volume = 0
            
            if quotes and quotes[0].get('close'):
                current_price = quotes[0]['close'][-1] if quotes[0]['close'] else 0
                volume = quotes[0]['volume'][-1] if quotes[0].get('volume') else 0
            
            #   API 
            market_cap = self._get_market_cap(symbol)
            
            return {
                'current_price': current_price,
                'market_cap': market_cap,
                'volume': volume,
                'currency': meta.get('currency', 'USD'),
                'exchange': meta.get('exchangeName', 'Unknown'),
                'fifty_two_week_high': meta.get('fiftyTwoWeekHigh', 0),
                'fifty_two_week_low': meta.get('fiftyTwoWeekLow', 0),
                'day_high': meta.get('regularMarketDayHigh', 0),
                'day_low': meta.get('regularMarketDayLow', 0)
            }
            
        except Exception as e:
            print(f"   [WARNING]    : {e}")
            return {'current_price': 0, 'market_cap': 0, 'volume': 0}
    
    def _get_market_cap(self, symbol: str) -> int:
        """
          ( API)
        """
        try:
            # Quote Summary API 
            summary_url = 'https://query1.finance.yahoo.com/v10/finance/quoteSummary/' + symbol
            summary_params = {
                'modules': 'price,summaryDetail'
            }
            
            response = self.session.get(summary_url, params=summary_params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                result = data.get('quoteSummary', {}).get('result', [])
                
                if result:
                    price_data = result[0].get('price', {})
                    market_cap = price_data.get('marketCap', 0)
                    if market_cap and market_cap > 0:
                        return market_cap
            
            #   *   ()
            #      API  
            return 0
            
        except Exception as e:
            print(f"   [WARNING]   : {e}")
            return 0
    
    def _calculate_financial_ratios(self, financial_data: Dict[str, Any], price_data: Dict[str, Any]) -> Dict[str, float]:
        """
               (   )
        """
        ratios = {}
        
        try:
            #    ( )
            current_price = price_data.get('current_price', 0)
            market_cap = price_data.get('market_cap', 0)
            volume = price_data.get('volume', 0)
            day_high = price_data.get('day_high', 0)
            day_low = price_data.get('day_low', 0)
            fifty_two_week_high = price_data.get('fifty_two_week_high', 0)
            fifty_two_week_low = price_data.get('fifty_two_week_low', 0)
            
            # 1.    ( )
            if day_high > 0 and day_low > 0 and current_price > 0:
                ratios['daily_volatility'] = ((day_high - day_low) / current_price)
            else:
                ratios['daily_volatility'] = 0.0
            
            # 2. 52  ( )
            if fifty_two_week_high > 0 and fifty_two_week_low > 0 and current_price > 0:
                ratios['yearly_volatility'] = ((fifty_two_week_high - fifty_two_week_low) / current_price)
            else:
                ratios['yearly_volatility'] = 0.0
            
            # 3. 52    (0~1,  )
            if fifty_two_week_high > 0 and fifty_two_week_low > 0 and current_price > 0:
                ratios['yearly_position'] = ((current_price - fifty_two_week_low) / (fifty_two_week_high - fifty_two_week_low))
            else:
                ratios['yearly_position'] = 0.0
            
            # 4.   (  )
            ratios['volume'] = volume
            ratios['market_cap'] = market_cap
            
            # 5.    (0~100,  )
            #   , 52  (0.5)   
            daily_vol_score = max(0, 100 - (ratios['daily_volatility'] * 1000))  # 10%  = 0
            yearly_pos_score = 100 - abs(ratios['yearly_position'] - 0.5) * 200  # 0.5   
            ratios['stability_score'] = (daily_vol_score + yearly_pos_score) / 2
            
            # 6.   (0~100, 52    )
            ratios['growth_score'] = ratios['yearly_position'] * 100
            
            # 7.    (0~100,    )
            #   (  )
            volume_score = min(100, (volume / 1000000) * 10) if volume > 0 else 0  # 100  = 10
            ratios['market_interest_score'] = volume_score
            
            # 8.   ()
            ratios['overall_score'] = (
                ratios['stability_score'] * 0.4 +      #  40%
                ratios['growth_score'] * 0.3 +         #  30%
                ratios['market_interest_score'] * 0.3  #   30%
            )
            
            #     0  (   )
            ratios['roe'] = 0.0
            ratios['operating_margin'] = 0.0
            ratios['roa'] = 0.0
            ratios['debt_ratio'] = 0.0
            ratios['current_ratio'] = 0.0
            ratios['asset_turnover'] = 0.0
            ratios['per'] = 0.0
            ratios['pbr'] = 0.0
            
            return ratios
            
        except Exception as e:
            print(f"   [FAIL]    : {e}")
            return {}
    
    def _get_country_from_exchange(self, exchange: str) -> str:
        """
          
        """
        exchange_country = {
            'NASDAQ': 'US',
            'NYSE': 'US',
            'XETRA': 'DE',
            'LSE': 'GB',
            'TSE': 'JP',
            'HKEX': 'HK',
            'NSE': 'IN'
        }
        
        for ex, country in exchange_country.items():
            if ex in exchange:
                return country
        
        return 'Unknown'
