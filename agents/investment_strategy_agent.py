"""
Investment Strategy Agent -       
 ,  ,  ,      
"""

from typing import Dict, Any, List
from config.settings import config, INVESTMENT_STRATEGY_CONFIG
from datetime import datetime
import json


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
        """  """
        opportunities = []
        
        #      
        financial_analysis = analysis.get('financial_analysis', {})
        companies = financial_analysis.get('companies', {})
        
        for company, data in companies.items():
            if data.get('data_available', False):
                opportunity = self._analyze_company_opportunity(company, data, analysis)
                if opportunity:
                    opportunities.append(opportunity)
        
        #     
        supplier_analysis = analysis.get('supplier_analysis', {})
        suppliers = supplier_analysis.get('suppliers', [])
        
        for supplier in suppliers:
            opportunity = self._analyze_supplier_opportunity(supplier, analysis)
            if opportunity:
                opportunities.append(opportunity)
        
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
        """   """
        try:
            company_name = supplier.get('name', supplier.get('company', ''))
            if not company_name:
                return None
            
            #   
            relationship = supplier.get('relationship', {})
            confidence = supplier.get('overall_confidence', 0.0)
            
            #   
            attractiveness = confidence * 0.7  #   
            
            if attractiveness < 0.3:
                return None
            
            return {
                'company': company_name,
                'type': 'supplier_investment',
                'attractiveness_score': attractiveness,
                'relationship_type': relationship.get('type', 'unknown'),
                'confidence': confidence,
                'investment_thesis': f"{company_name}     .",
                'target_price': None,  #    
                'time_horizon': 'medium_term'
            }
            
        except Exception as e:
            print(f"   [FAIL]     : {e}")
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