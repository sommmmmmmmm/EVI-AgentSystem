"""
Investment Strategy Agent -       
 ,  ,  ,      
"""

from typing import Dict, Any, List
from config.settings import config, INVESTMENT_STRATEGY_CONFIG
from datetime import datetime
import json
from tools.scoring_missing_data_tools import ScoringWithMissingData  # 🆕 결측값 처리 도구


class InvestmentStrategyAgent:
    """
          
    -  ,  ,  ,   
    -       (3-12)
    -       
    """
    
    def __init__(self, web_search_tool, llm_tool):
        self.web_search_tool = web_search_tool
        self.llm_tool = llm_tool
        
        #   
        self.investment_horizon = INVESTMENT_STRATEGY_CONFIG['investment_horizon']
        self.target_audience = INVESTMENT_STRATEGY_CONFIG['target_audience']
        
        # 🆕 결측값 처리 도구
        self.scoring_tool = ScoringWithMissingData()
        
        # 상장사 여부 확인을 위한 리스트
        self.listed_companies = {
            'SK': 'SK Innovation (096770.KS)',
            'Samsung': 'Samsung SDI (006400.KS)', 
            'Panasonic': 'Panasonic Holdings (6752.T)',
            'Magna': 'Magna International (MGA)',
            'Bosch': 'Robert Bosch GmbH (비상장)',
            'CATL': 'CATL (300750.SZ)',
            'LG': 'LG Energy Solution (373220.KS)',
            'BYD': 'BYD (002594.SZ)',
            'Tesla': 'Tesla (TSLA)',
            'GM': 'General Motors (GM)',
            'Ford': 'Ford Motor (F)',
            'BMW': 'BMW (BMW.DE)',
            'Volkswagen': 'Volkswagen (VOW.DE)',
            'Hyundai': 'Hyundai Motor (005380.KS)',
            'Kia': 'Kia (000270.KS)'
        }
    
    def _is_listed_company(self, company_name: str) -> bool:
        """
        기업이 상장사인지 확인
        """
        company_name_clean = company_name.replace(' ', '').replace('On', '').replace('SDI', '').replace('Energy', '').replace('Solution', '')
        
        for listed_name in self.listed_companies.keys():
            if listed_name.lower() in company_name_clean.lower():
                return True
        return False
    
    def _get_company_ticker(self, company_name: str) -> str:
        """
        기업의 티커 심볼 반환
        """
        company_name_clean = company_name.replace(' ', '').replace('On', '').replace('SDI', '').replace('Energy', '').replace('Solution', '')
        
        for listed_name, ticker_info in self.listed_companies.items():
            if listed_name.lower() in company_name_clean.lower():
                return ticker_info
        return f"{company_name} (비상장)"
    
    def develop_investment_strategy(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
             
        """
        try:
            print("       ...")
            
            # 1.   
            integrated_analysis = self._integrate_analysis_results(state)
            
            # 2.   
            investment_opportunities = self._identify_investment_opportunities(integrated_analysis)
            
            # 3.   
            investment_strategy = self._develop_strategy(investment_opportunities, integrated_analysis)
            
            # 4.   
            risk_management = self._develop_risk_management_strategy(integrated_analysis)
            
            # 5.  
            portfolio_recommendation = self._recommend_portfolio(investment_opportunities, integrated_analysis)
            
            print(f"[OK]     - {len(investment_opportunities)}   ")
            
            return {
                'investment_strategy': investment_strategy,
                'investment_opportunities': investment_opportunities,
                'risk_management': risk_management,
                'portfolio_recommendation': portfolio_recommendation,
                'strategy_metadata': {
                    'investment_horizon': self.investment_horizon,
                    'target_audience': self.target_audience,
                    'analysis_date': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            print(f"[FAIL]    : {e}")
            return {
                'investment_strategy': {},
                'investment_opportunities': [],
                'risk_management': {},
                'portfolio_recommendation': {},
                'error': str(e)
            }
    
    def _integrate_analysis_results(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """  """
        return {
            'market_trends': state.get('market_trends', {}),
            'supplier_analysis': state.get('supplier_analysis', {}),
            'financial_analysis': state.get('financial_analysis', {}),
            'risk_analysis': state.get('risk_analysis', {})
        }
    
    def _identify_investment_opportunities(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """투자 기회 식별 - 재무 데이터가 없어도 공급업체 기반으로 투자 기회 생성"""
        opportunities = []
        
        # 1. 재무 분석 기반 투자 기회 (data_available 조건 완화)
        financial_analysis = analysis.get('financial_analysis', {})
        companies = financial_analysis.get('companies', {})
        
        for company, data in companies.items():
            # data_available 조건을 완화하고, 최소한의 데이터가 있으면 투자 기회로 간주
            if data.get('data_available', False) or data.get('qualitative_score', 0) > 0:
                opportunity = self._analyze_company_opportunity(company, data, analysis)
                if opportunity:
                    opportunities.append(opportunity)
        
        # 2. 공급업체 기반 투자 기회 (더 적극적으로 포함)
        supplier_analysis = analysis.get('supplier_analysis', {})
        suppliers = supplier_analysis.get('suppliers', [])
        
        print(f"   [DEBUG] 공급업체 기반 투자 기회 분석: {len(suppliers)}개 공급업체")
        
        for supplier in suppliers:
            opportunity = self._analyze_supplier_opportunity(supplier, analysis)
            if opportunity:
                opportunities.append(opportunity)
                print(f"   [DEBUG] 공급업체 투자 기회 추가: {supplier.get('name', 'Unknown')}")
        
        # 3. 최소 투자 기회 보장 (공급업체가 있으면 최소 1개는 생성)
        if not opportunities and suppliers:
            print("   [WARNING] 투자 기회가 없어서 기본 투자 기회 생성")
            # 가장 신뢰도가 높은 공급업체를 투자 기회로 생성
            best_supplier = max(suppliers, key=lambda x: x.get('confidence_score', 0))
            basic_opportunity = {
                'company': best_supplier.get('name', 'Unknown'),
                'type': 'supplier_investment',
                'attractiveness_score': 0.5,  # 기본 점수
                'financial_score': 0.3,
                'risk_score': 0.5,
                'investment_thesis': f"{best_supplier.get('name', 'Unknown')}는 EV 공급망의 핵심 기업으로 투자 가치가 있습니다.",
                'target_price': 'N/A',
                'stop_loss_level': 0.15,
                'position_sizing': 'small',
                'monitoring_frequency': 'weekly'
            }
            opportunities.append(basic_opportunity)
        
        print(f"   [DEBUG] 총 {len(opportunities)}개 투자 기회 식별")
        return opportunities
    
    def _analyze_company_opportunity(self, company: str, company_data: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """    """
        try:
            #  
            financial_score = company_data.get('final_score', 0.0)
            
            #  
            risk_analysis = analysis.get('risk_analysis', {})
            risk_data = risk_analysis.get('risk_analysis', {}).get(company, {})
            risk_score = risk_data.get('overall_risk_score', 0.5)
            
            #   
            attractiveness = self._calculate_investment_attractiveness(financial_score, risk_score)
            
            if attractiveness < 0.3:  #   
                return None
            
            return {
                'company': company,
                'type': 'direct_investment',
                'attractiveness_score': attractiveness,
                'financial_score': financial_score,
                'risk_score': risk_score,
                'investment_thesis': self._generate_investment_thesis(company, company_data),
                'target_price': self._estimate_target_price(company, company_data),
                'time_horizon': self._estimate_time_horizon(company, company_data)
            }
            
        except Exception as e:
            print(f"   [FAIL] {company}    : {e}")
            return None
    
    def _analyze_supplier_opportunity(self, supplier: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """공급업체 투자 기회 분석 - 조건 완화"""
        try:
            company_name = supplier.get('name', supplier.get('company', ''))
            if not company_name or company_name.strip() == '':
                return None
            
            # 신뢰도 점수 (confidence_score 또는 overall_confidence 사용)
            confidence = supplier.get('confidence_score', supplier.get('overall_confidence', 0.0))
            
            # 최소 신뢰도 보장 (0.0이면 기본값 0.5 사용)
            if confidence == 0.0:
                confidence = 0.5
            
            # 매력도 계산 (더 관대한 기준)
            attractiveness = max(0.4, confidence * 0.8)  # 최소 0.4 보장
            
            # 조건 완화: attractiveness < 0.2만 제외
            if attractiveness < 0.2:
                return None
            
            # 투자 논리 생성
            category = supplier.get('category', 'Unknown')
            products = supplier.get('products', [])
            product_desc = ', '.join(products[:2]) if products else f"{category} components"
            
            investment_thesis = f"{company_name}는 EV 공급망의 {category} 분야 전문 기업으로, {product_desc}를 제공하여 전기차 시장 성장의 혜택을 받을 것으로 예상됩니다."
            
            return {
                'company': company_name,
                'type': 'supplier_investment',
                'attractiveness_score': round(attractiveness, 2),
                'relationship_type': supplier.get('category', 'supplier'),
                'confidence': round(confidence, 2),
                'investment_thesis': investment_thesis,
                'target_price': 'N/A',  # 공급업체는 타겟 가격 없음
                'time_horizon': 'medium_term',
                'position_sizing': 'small' if attractiveness < 0.6 else 'medium',
                'stop_loss_level': 0.15,
                'monitoring_frequency': 'weekly'
            }
            
        except Exception as e:
            print(f"   [FAIL] 공급업체 투자 기회 분석 실패: {e}")
            return None
    
    def _calculate_investment_attractiveness(self, financial_score: float, risk_score: float) -> float:
        """  """
        #    ,    
        return (financial_score * 0.7) + ((1 - risk_score) * 0.3)
    
    def _generate_investment_thesis(self, company: str, company_data: Dict[str, Any]) -> str:
        """API 실패 시 에러 메시지 반환"""
        return f"[ERROR] '{company}'의 투자 논리를 생성할 수 없습니다. API 키를 확인하세요."
    
    def _estimate_target_price(self, company: str, company_data: Dict[str, Any]) -> float:
        """API 실패 시 0 반환"""
        print(f"[ERROR] '{company}'의 목표가를 계산할 수 없습니다. API 키를 확인하세요.")
        return 0.0
    
    def _estimate_time_horizon(self, company: str, company_data: Dict[str, Any]) -> str:
        """API 실패 시 에러 메시지 반환"""
        return f"[ERROR] '{company}'의 투자 기간을 계산할 수 없습니다. API 키를 확인하세요."
    
    def _develop_strategy(self, opportunities: List[Dict[str, Any]], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """  """
        if not opportunities:
            return {
                'strategy_type': 'conservative',
                'recommendation': '   .',
                'action_plan': ['  ', '  ']
            }
        
        #    
        sorted_opportunities = sorted(opportunities, key=lambda x: x.get('attractiveness_score', 0), reverse=True)
        
        #  3  
        top_opportunities = sorted_opportunities[:3]
        
        return {
            'strategy_type': 'growth_focused',
            'recommendation': f"{len(top_opportunities)}    ",
            'action_plan': [
                '  ',
                '  ',
                '  '
            ],
            'target_companies': [opp['company'] for opp in top_opportunities]
        }
    
    def _develop_risk_management_strategy(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """   """
        return {
            'risk_tolerance': 'medium',
            'diversification_strategy': 'sector_diversification',
            'stop_loss_level': 0.15,
            'position_sizing': 'equal_weight',
            'monitoring_frequency': 'weekly'
        }
    
    def _recommend_portfolio(self, opportunities: List[Dict[str, Any]], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """  """
        if not opportunities:
            return {
                'portfolio_type': 'cash_heavy',
                'allocation': {'cash': 1.0},
                'recommendation': '      '
            }
        
        #    
        top_opportunities = sorted(opportunities, key=lambda x: x.get('attractiveness_score', 0), reverse=True)[:5]
        
        allocation = {}
        total_weight = 0.0
        
        for i, opp in enumerate(top_opportunities):
            weight = 0.2 - (i * 0.03)  #    
            allocation[opp['company']] = weight
            total_weight += weight
        
        #  
        allocation['cash'] = 1.0 - total_weight
        
        return {
            'portfolio_type': 'growth_balanced',
            'allocation': allocation,
            'recommendation': f"{len(top_opportunities)}    "
        }