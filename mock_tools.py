"""
Mock Tools for Testing without API Keys
API 키 없이 테스트할 수 있는 Mock 툴들
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import random


class MockWebSearchTool:
    """Mock Web Search Tool - API 키 없이 테스트용"""
    
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Mock 웹 검색 결과 반환"""
        print(f"   🔍 [MOCK] Web Search: {query[:50]}... ({num_results}개 결과)")
        
        # 쿼리 타입에 따라 다른 Mock 데이터 반환
        results = []
        
        for i in range(min(num_results, 3)):  # 최대 3개
            result = {
                'title': f"[Mock News] {query[:30]} - Article {i+1}",
                'content': self._generate_mock_content(query),
                'url': f"https://example.com/news/{i+1}",
                'date': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                'source': f"Mock News Source {i+1}"
            }
            results.append(result)
        
        return results
    
    def _generate_mock_content(self, query: str) -> str:
        """쿼리에 따른 Mock 컨텐츠 생성"""
        
        if 'governance' in query.lower() or 'legal' in query.lower():
            return """
            The company has been implementing strong corporate governance practices.
            Recent board changes have strengthened oversight capabilities.
            No significant legal issues have been reported in the recent period.
            """
        
        if 'management' in query.lower():
            return """
            The management team has demonstrated strong leadership.
            Recent strategic initiatives show positive direction.
            Executive team has extensive industry experience.
            """
        
        return f"""
        Recent developments regarding {query} show positive trends.
        Industry analysts remain optimistic about future prospects.
        Market conditions continue to support growth opportunities.
        """


class MockLLMTool:
    """Mock LLM Tool - OpenAI API 없이 테스트용"""
    
    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """Mock LLM 응답 생성"""
        print(f"   🤖 [MOCK] LLM Generate: {len(prompt)} chars prompt")
        
        # 프롬프트 분석하여 적절한 Mock 응답 생성
        if 'is_risk' in prompt:
            # 리스크 분석 요청
            return self._generate_risk_analysis()
        
        if '정성적' in prompt or 'qualitative' in prompt.lower():
            return self._generate_qualitative_analysis()
        
        if '시장 트렌드' in prompt or 'market trend' in prompt.lower():
            return self._generate_market_trend()
        
        if '투자 전략' in prompt or 'investment strategy' in prompt.lower():
            return self._generate_investment_strategy()
        
        if '보고서' in prompt or 'report' in prompt.lower():
            return self._generate_report()
        
        return "Mock LLM response generated successfully."
    
    def _generate_risk_analysis(self) -> str:
        """리스크 분석 Mock 응답"""
        responses = [
            '''```json
{
    "is_risk": false,
    "severity": "low",
    "description": "No significant risk identified",
    "confidence": 0.8
}```''',
            '''```json
{
    "is_risk": true,
    "severity": "medium",
    "description": "Minor operational challenges identified",
    "confidence": 0.7
}```'''
        ]
        return random.choice(responses)
    
    def _generate_qualitative_analysis(self) -> str:
        """정성적 분석 Mock 응답"""
        return """
**Strategic Positioning**: The company demonstrates strong market positioning with innovative product portfolio.

**Technology Leadership**: Significant R&D investments have resulted in competitive advantages in key technologies.

**Management Quality**: Experienced leadership team with proven track record in industry.

**Future Outlook**: Positive growth prospects supported by strong market fundamentals.
"""
    
    def _generate_market_trend(self) -> str:
        """시장 트렌드 Mock 응답"""
        return """
**Market Growth**: Industry showing strong growth momentum with 15-20% annual growth expected.

**Key Drivers**: 
- Increasing demand for EV components
- Government policy support
- Technological advancement

**Competitive Landscape**: Market consolidation expected with leading players strengthening positions.
"""
    
    def _generate_investment_strategy(self) -> str:
        """투자 전략 Mock 응답"""
        return """
**Investment Approach**: Balanced portfolio with focus on quality growth companies.

**Risk Management**: Diversification across supply chain with emphasis on technology leaders.

**Timeline**: Medium to long-term investment horizon (3-5 years).
"""
    
    def _generate_report(self) -> str:
        """보고서 Mock 응답"""
        return """
# Investment Analysis Report

## Executive Summary
This analysis provides comprehensive evaluation of investment opportunities in the electric vehicle supply chain.

## Key Findings
- Strong growth potential in battery and component sectors
- Leading companies demonstrate solid fundamentals
- Favorable market conditions support positive outlook

## Recommendations
- Focus on technology leaders with proven track records
- Monitor regulatory developments closely
- Maintain diversified portfolio approach
"""


class MockDARTTool:
    """Mock DART Tool - DART API 없이 테스트용"""
    
    def get_company_info(self, company_name: str) -> Dict[str, Any]:
        """Mock 기업 정보 반환"""
        print(f"   📄 [MOCK] DART: Getting info for {company_name}")
        
        return {
            'company_name': company_name,
            'stock_code': f"0{random.randint(10000, 99999)}",
            'industry': 'Electric Vehicle Components',
            'established_date': '2010-01-01'
        }
    
    def get_financial_statements(self, company_name: str, year: int = 2024) -> Dict[str, Any]:
        """Mock 재무제표 반환"""
        print(f"   📊 [MOCK] DART: Getting financial statements for {company_name}")
        
        # 기본 매출 규모 (랜덤)
        base_revenue = random.randint(500000, 5000000) * 1000000  # 5천억~5조
        
        return {
            'company': company_name,
            'year': year,
            'data_available': True,
            
            # 손익계산서
            'income_statement': {
                'revenue': base_revenue,
                'cogs': base_revenue * 0.70,  # 매출원가 70%
                'gross_profit': base_revenue * 0.30,
                'operating_income': base_revenue * 0.12,
                'net_income': base_revenue * 0.08,
                'rnd_expense': base_revenue * random.uniform(0.08, 0.18),  # R&D 8-18%
                'depreciation': base_revenue * 0.05,
                'operating_margin': 0.12,
                'net_margin': 0.08
            },
            
            # 재무상태표
            'balance_sheet': {
                'total_assets': base_revenue * 2.5,
                'current_assets': base_revenue * 1.2,
                'non_current_assets': base_revenue * 1.3,
                'intangible_assets': base_revenue * random.uniform(0.2, 0.4),  # 무형자산 20-40%
                'inventory': base_revenue * 0.15,
                'accounts_receivable': base_revenue * 0.20,
                'cash': base_revenue * 0.30,
                
                'total_liabilities': base_revenue * 1.5,
                'current_liabilities': base_revenue * 0.8,
                'non_current_liabilities': base_revenue * 0.7,
                'accounts_payable': base_revenue * 0.15,
                
                'total_equity': base_revenue * 1.0,
                'retained_earnings': base_revenue * 0.5
            },
            
            # 현금흐름표
            'cash_flow_statement': {
                'operating_cash_flow': base_revenue * 0.15,
                'investing_cash_flow': -base_revenue * 0.10,
                'financing_cash_flow': base_revenue * 0.05,
                'capex': base_revenue * random.uniform(0.10, 0.25),  # CapEx 10-25%
                'free_cash_flow': base_revenue * 0.08
            },
            
            # 전년도 데이터 (비교용)
            'previous_year': {
                'revenue': base_revenue * 0.90,
                'net_income': base_revenue * 0.07,
                'depreciation': base_revenue * 0.045,
                'total_assets': base_revenue * 2.3
            }
        }
    
    def search_disclosures(self, company_name: str, **kwargs) -> List[Dict[str, Any]]:
        """Mock 공시 정보 반환"""
        print(f"   📋 [MOCK] DART: Searching disclosures for {company_name}")
        
        disclosures = []
        for i in range(random.randint(2, 5)):
            disclosures.append({
                'title': f"[공시] {company_name} - {['사업보고서', '분기보고서', '주요사항보고'][i % 3]}",
                'date': (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
                'url': f"https://dart.fss.or.kr/mock/{i}",
                'category': ['사업보고서', '분기보고서', '주요사항보고'][i % 3]
            })
        
        return disclosures


def create_mock_tools():
    """Mock 툴 세트 생성"""
    return {
        'web_search': MockWebSearchTool(),
        'llm': MockLLMTool(),
        'dart': MockDARTTool()
    }


if __name__ == "__main__":
    # 테스트
    print("="*70)
    print("Mock Tools Test")
    print("="*70)
    
    tools = create_mock_tools()
    
    # Web Search 테스트
    print("\n[1] Web Search Test:")
    results = tools['web_search'].search("LG Energy Solution governance", num_results=2)
    print(f"   ✓ {len(results)} results returned")
    
    # LLM 테스트
    print("\n[2] LLM Test:")
    response = tools['llm'].generate("Analyze market trends")
    print(f"   ✓ Response length: {len(response)} chars")
    
    # DART 테스트
    print("\n[3] DART Test:")
    financials = tools['dart'].get_financial_statements("LG에너지솔루션")
    print(f"   ✓ Revenue: {financials['income_statement']['revenue']:,.0f} KRW")
    print(f"   ✓ R&D Ratio: {financials['income_statement']['rnd_expense'] / financials['income_statement']['revenue']:.2%}")
    
    print("\n" + "="*70)
    print("✓ All Mock Tools Working!")

