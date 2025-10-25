"""
Disclosure Data Routing Tools

Fixes:
1. CIK zero-padding to 10 digits
2. Country-based API routing (US=EDGAR, KR=DART, etc.)
3. Fallback skeleton JSON (no 0 replacement)
4. SEC User-Agent with contact
"""

from typing import Dict, Any, List, Optional
import re


class DisclosureRouter:
    """
    Routes disclosure requests to appropriate API based on country/exchange
    """
    
    # Country to API mapping
    COUNTRY_TO_API = {
        'US': 'SEC_EDGAR',
        'KR': 'DART',
        'CN': 'CN_EXCHANGE',  # SSE/SZSE
        'HK': 'HKEX',
        'JP': 'JPX',
        'DE': 'BaFin',  # German Federal Financial Supervisory Authority
        'GB': 'LSE',  # London Stock Exchange
        'FR': 'AMF',  # French Financial Markets Authority
    }
    
    # Ticker prefix to country
    TICKER_PREFIX_TO_COUNTRY = {
        '.SS': 'CN',  # Shanghai
        '.SZ': 'CN',  # Shenzhen
        '.HK': 'HK',  # Hong Kong
        '.KS': 'KR',  # Korea Stock Exchange
        '.KQ': 'KR',  # KOSDAQ
        '.T': 'JP',   # Tokyo
        '.L': 'GB',   # London
        '.PA': 'FR',  # Paris
        '.DE': 'DE',  # XETRA (Germany)
    }
    
    # Known CIK mapping (10-digit padded)
    KNOWN_CIKS = {
        'Tesla': '0001318605',
        'General Motors': '0001467858',
        'Ford Motor': '0000037996',
        'Rivian': '0001874178',
        'NIO': '0001736541',
        'Lucid': '0001811210',
        'Fisker': '0001720990',
        'QuantumScape': '0001811414',
        # Add more as needed
    }
    
    def __init__(self):
        pass
    
    def normalize_cik(self, cik: str) -> str:
        """
        Normalize CIK to 10-digit format with zero-padding
        
        Args:
            cik: CIK string (may be numeric or already padded)
            
        Returns:
            10-digit zero-padded CIK
        """
        # Remove non-numeric characters
        cik_numeric = re.sub(r'\D', '', cik)
        
        if not cik_numeric:
            raise ValueError(f"Invalid CIK: {cik}")
        
        # Zero-pad to 10 digits
        return cik_numeric.zfill(10)
    
    def detect_country(
        self,
        company_name: str,
        ticker: Optional[str] = None,
        exchange: Optional[str] = None
    ) -> str:
        """
        Detect company's country based on name, ticker, or exchange
        
        Args:
            company_name: Company name
            ticker: Stock ticker (optional)
            exchange: Exchange name (optional)
            
        Returns:
            Country code (e.g., 'US', 'KR', 'CN')
        """
        # Check ticker suffix
        if ticker:
            for suffix, country in self.TICKER_PREFIX_TO_COUNTRY.items():
                if ticker.endswith(suffix):
                    return country
        
        # Check exchange name
        if exchange:
            exchange_lower = exchange.lower()
            if 'nyse' in exchange_lower or 'nasdaq' in exchange_lower:
                return 'US'
            elif 'korea' in exchange_lower or 'kospi' in exchange_lower or 'kosdaq' in exchange_lower:
                return 'KR'
            elif 'shanghai' in exchange_lower or 'shenzhen' in exchange_lower:
                return 'CN'
            elif 'hong kong' in exchange_lower or 'hkex' in exchange_lower:
                return 'HK'
            elif 'tokyo' in exchange_lower:
                return 'JP'
            elif 'london' in exchange_lower or 'lse' in exchange_lower:
                return 'GB'
            elif 'paris' in exchange_lower:
                return 'FR'
            elif 'frankfurt' in exchange_lower or 'xetra' in exchange_lower:
                return 'DE'
        
        # Check company name patterns (Korean companies)
        if any(char in company_name for char in '가-힣'):
            return 'KR'
        
        # Known patterns
        if any(name in company_name for name in ['Tesla', 'Ford', 'GM', 'General Motors', 'Rivian', 'Lucid']):
            return 'US'
        
        if any(name in company_name for name in ['Samsung', 'LG', 'SK', 'Hyundai', 'Kia']):
            return 'KR'
        
        if any(name in company_name for name in ['BYD', 'NIO', 'XPeng', 'Li Auto', 'CATL']):
            return 'CN'
        
        if any(name in company_name for name in ['Toyota', 'Honda', 'Nissan', 'Panasonic']):
            return 'JP'
        
        if any(name in company_name for name in ['BMW', 'Volkswagen', 'Mercedes', 'Porsche']):
            return 'DE'
        
        # Default to US for unknown
        return 'US'
    
    def route_disclosure_request(
        self,
        company_name: str,
        ticker: Optional[str] = None,
        exchange: Optional[str] = None,
        cik: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Route disclosure request to appropriate API
        
        Args:
            company_name: Company name
            ticker: Stock ticker (optional)
            exchange: Exchange name (optional)
            cik: CIK for US companies (optional)
            
        Returns:
            Routing information dict
        """
        # Detect country
        country = self.detect_country(company_name, ticker, exchange)
        
        # Get API
        api = self.COUNTRY_TO_API.get(country, 'UNKNOWN')
        
        # Prepare routing info
        routing_info = {
            'company_name': company_name,
            'country': country,
            'api': api,
            'ticker': ticker,
            'exchange': exchange,
            'success': True,
            'error': None
        }
        
        # Handle US companies (SEC EDGAR)
        if api == 'SEC_EDGAR':
            if cik:
                try:
                    normalized_cik = self.normalize_cik(cik)
                    routing_info['cik'] = normalized_cik
                    routing_info['api_url'] = f"https://data.sec.gov/submissions/CIK{normalized_cik}.json"
                except ValueError as e:
                    routing_info['success'] = False
                    routing_info['error'] = str(e)
            elif company_name in self.KNOWN_CIKS:
                routing_info['cik'] = self.KNOWN_CIKS[company_name]
                routing_info['api_url'] = f"https://data.sec.gov/submissions/CIK{routing_info['cik']}.json"
            else:
                routing_info['success'] = False
                routing_info['error'] = 'CIK required for SEC EDGAR but not provided'
        
        # Handle Korean companies (DART)
        elif api == 'DART':
            routing_info['api_url'] = 'https://opendart.fss.or.kr/api/list.json'
            routing_info['note'] = 'DART API requires corp_code lookup first'
        
        # Handle Chinese companies
        elif api == 'CN_EXCHANGE':
            routing_info['api_url'] = 'http://www.sse.com.cn/ or http://www.szse.cn/'
            routing_info['note'] = 'CN exchange APIs require specific implementation'
        
        # Handle other exchanges
        else:
            routing_info['success'] = False
            routing_info['error'] = f'API {api} not yet implemented'
        
        return routing_info
    
    def create_fallback_skeleton(
        self,
        company_name: str,
        error_message: str
    ) -> Dict[str, Any]:
        """
        Create fallback skeleton response (no 0 replacement)
        
        Args:
            company_name: Company name
            error_message: Error message
            
        Returns:
            Skeleton dict with nulls (not 0s)
        """
        return {
            'company_name': company_name,
            'data_available': False,
            'error': error_message,
            'disclosures': [],
            'financial_data': {
                'revenue': None,
                'operating_income': None,
                'net_income': None,
                'total_assets': None,
                'total_equity': None,
                'total_debt': None,
            },
            'ratios': {
                'roe': None,
                'roa': None,
                'operating_margin': None,
                'debt_ratio': None,
                'current_ratio': None,
            },
            'note': f'Data collection failed for {company_name}: {error_message}'
        }
    
    def get_sec_request_headers(
        self,
        user_agent_name: str = 'EVI-AgentSystem',
        contact_email: str = 'contact@example.com'
    ) -> Dict[str, str]:
        """
        Get SEC EDGAR compliant request headers
        
        Args:
            user_agent_name: Application name
            contact_email: Contact email (REQUIRED by SEC)
            
        Returns:
            Headers dict
        """
        return {
            'User-Agent': f'{user_agent_name}/1.0 ({contact_email})',
            'Accept': 'application/json',
            # Do NOT set 'Host' header manually - let requests handle it
        }


def test_disclosure_router():
    """Test the disclosure router"""
    
    print("="*70)
    print("Disclosure Router Test")
    print("="*70)
    
    router = DisclosureRouter()
    
    # Test 1: CIK normalization
    print("\n[Test 1] CIK Normalization")
    test_ciks = ['1318605', '0001318605', 'CIK1318605', '37996']
    for cik in test_ciks:
        try:
            normalized = router.normalize_cik(cik)
            print(f"  {cik:15s} → {normalized}")
        except ValueError as e:
            print(f"  {cik:15s} → ERROR: {e}")
    
    # Test 2: Country detection
    print("\n[Test 2] Country Detection")
    test_companies = [
        ('Tesla', 'TSLA', 'NASDAQ'),
        ('Samsung SDI', '006400.KS', 'KOSPI'),
        ('BYD', '1211.HK', 'HKEX'),
        ('BMW', 'BMW.DE', 'XETRA'),
        ('현대자동차', '005380.KS', 'KOSPI'),
    ]
    
    for name, ticker, exchange in test_companies:
        country = router.detect_country(name, ticker, exchange)
        print(f"  {name:20s} → {country}")
    
    # Test 3: Routing
    print("\n[Test 3] Disclosure Request Routing")
    
    # US company with CIK
    route1 = router.route_disclosure_request(
        company_name='Tesla',
        ticker='TSLA',
        cik='1318605'
    )
    print(f"\n  Tesla:")
    print(f"    Country: {route1['country']}")
    print(f"    API: {route1['api']}")
    print(f"    CIK: {route1.get('cik', 'N/A')}")
    print(f"    URL: {route1.get('api_url', 'N/A')[:60]}...")
    
    # Korean company
    route2 = router.route_disclosure_request(
        company_name='LG에너지솔루션',
        ticker='373220.KS'
    )
    print(f"\n  LG에너지솔루션:")
    print(f"    Country: {route2['country']}")
    print(f"    API: {route2['api']}")
    print(f"    Success: {route2['success']}")
    
    # Chinese company
    route3 = router.route_disclosure_request(
        company_name='BYD',
        ticker='1211.HK'
    )
    print(f"\n  BYD:")
    print(f"    Country: {route3['country']}")
    print(f"    API: {route3['api']}")
    print(f"    Success: {route3['success']}")
    
    # Test 4: Fallback skeleton
    print("\n[Test 4] Fallback Skeleton")
    skeleton = router.create_fallback_skeleton(
        company_name='Unknown Corp',
        error_message='API 404 error'
    )
    print(f"  Data available: {skeleton['data_available']}")
    print(f"  Revenue: {skeleton['financial_data']['revenue']}")
    print(f"  ROE: {skeleton['ratios']['roe']}")
    print(f"  Note: {skeleton['note'][:50]}...")
    
    # Test 5: SEC headers
    print("\n[Test 5] SEC Request Headers")
    headers = router.get_sec_request_headers(
        user_agent_name='EVI-AgentSystem',
        contact_email='admin@example.com'
    )
    print(f"  User-Agent: {headers['User-Agent']}")
    print(f"  Accept: {headers['Accept']}")
    
    print("\n" + "="*70)
    print("✓ All tests completed!")
    print("="*70)


if __name__ == "__main__":
    test_disclosure_router()

