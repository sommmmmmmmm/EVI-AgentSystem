"""
LangGraph  
"""

from langgraph.graph import StateGraph, END
from typing import Dict, Any
import traceback
from datetime import datetime

from .state import ReportState
from agents.market_trend_agent import MarketTrendAgent
from agents.supplier_matching_agent import SupplierMatchingAgent
from agents.financial_analyzer_agent import FinancialAnalyzerAgent
from agents.risk_assessment_agent_improved import RiskAssessmentAgent
from agents.investment_strategy_agent import InvestmentStrategyAgent
from agents.report_generator_agent import ReportGeneratorAgent


def create_workflow(web_search_tool, llm_tool, dart_tool):
    """
       
    CoT      
    """
    
    # Agent  ( )
    market_agent = MarketTrendAgent(web_search_tool, llm_tool, dart_tool)
    supplier_agent = SupplierMatchingAgent(web_search_tool, llm_tool)
    financial_agent = FinancialAnalyzerAgent(web_search_tool, llm_tool, dart_tool)
    risk_agent = RiskAssessmentAgent(web_search_tool, llm_tool)
    strategy_agent = InvestmentStrategyAgent(web_search_tool, llm_tool)
    report_agent = ReportGeneratorAgent(llm_tool)
    
    # ==========================================
    #   
    # ==========================================
    
    def market_trend_node(state: ReportState) -> ReportState:
        """
        1.    (CoT   )
        """
        print("\n" + "="*60)
        print(" [MarketTrendAgent]  - CoT  ")
        print("="*60)
        
        try:
            #  CoT
            result = market_agent.analyze_market_trends(state)

            # State  (  )
            state['news_articles'] = result.get('news_articles', [])
            state['keywords'] = result.get('keywords', [])
            state['categorized_keywords'] = result.get('categorized_keywords', {})
            state['market_trends'] = result.get('market_trends', [])

            #   suppliers  ( suppliers )
            discovered_companies = result.get('discovered_companies', [])
            if discovered_companies:
                existing_suppliers = state.get('suppliers', [])
                existing_suppliers.extend(discovered_companies)
                state['suppliers'] = existing_suppliers
                print(f"   [OK]   : {len(discovered_companies)}")

            state['messages'].append(
                f"[OK] MarketTrendAgent  (CoT) - {datetime.now().isoformat()}"
            )

            print(f"   [OK] : {len(result.get('news_articles', []))}")
            print(f"   [OK] : {len(result.get('keywords', []))}")
            print(f"   [OK] : {len(result.get('market_trends', []))}")
            print(f"   [OK] : {len(state['suppliers'])}")
            print(f"   [OK] : {len(state['source_manager'].citations)}")
            print("[OK] \n")
            
        except Exception as e:
            error_msg = f"[FAIL] MarketTrendAgent : {str(e)}"
            print(error_msg)
            
            state['errors'].append({
                'agent': 'MarketTrendAgent',
                'error': str(e),
                'traceback': traceback.format_exc(),
                'timestamp': datetime.now().isoformat()
            })
            
            # API 실패 시 빈 데이터로 설정
            state['categorized_keywords'] = {}
        
        return state
    
    def supplier_matching_node(state: ReportState) -> ReportState:
        """
        2.   ( )
        """
        print("\n" + "="*60)
        print(" [SupplierMatchingAgent] ")
        print("="*60)
        
        try:
            #   
            result = supplier_agent.match_suppliers(state)
            
            #  state 
            state['suppliers'] = result.get('suppliers', [])
            state['supplier_discovery_summary'] = result.get('discovery_summary', {})
            
            state['messages'].append(
                f"[OK] SupplierMatchingAgent  - {datetime.now().isoformat()}"
            )
            
            suppliers = result.get('suppliers', [])
            print(f"   [OK]  : {len(suppliers)}")
            print(f"   [OK] : {result.get('discovery_summary', {}).get('high_confidence', 0)}")
            print(f"   [OK] : {result.get('discovery_summary', {}).get('medium_confidence', 0)}")
            print(f"   [OK] : {result.get('discovery_summary', {}).get('low_confidence', 0)}")
            print("[OK] \n")
            
        except Exception as e:
            error_msg = f"[FAIL] SupplierMatchingAgent : {str(e)}"
            print(error_msg)
            
            state['errors'].append({
                'agent': 'SupplierMatchingAgent',
                'error': str(e),
                'traceback': traceback.format_exc(),
                'timestamp': datetime.now().isoformat()
            })
            
            # API 실패 시 빈 데이터로 설정
            state['suppliers'] = []
        
        return state
    
    def financial_analysis_node(state: ReportState) -> ReportState:
        """
        3.   (CoT   )
        """
        print("\n" + "="*60)
        print(" [FinancialAnalyzerAgent]  - CoT  ")
        print("="*60)
        
        try:
            #  CoT    
            result = financial_agent.analyze_financials(state)
            
            # State  (  )
            state['financial_analysis'] = result.get('financial_analysis', {})
            
            state['messages'].append(
                f"[OK] FinancialAnalyzerAgent  (CoT) - {datetime.now().isoformat()}"
            )
            
            investment_scores = result.get('financial_analysis', {}).get('investment_scores', {})
            print(f"   [OK]  : {len(investment_scores)}")
            print(f"   [OK]  : {len(result.get('financial_analysis', {}).get('top_picks', []))}")
            print(f"   [OK] : {len(state['source_manager'].citations)}")
            print("[OK] \n")
            
        except Exception as e:
            error_msg = f"[FAIL] FinancialAnalyzerAgent : {str(e)}"
            print(error_msg)
            
            state['errors'].append({
                'agent': 'FinancialAnalyzerAgent',
                'error': str(e),
                'traceback': traceback.format_exc(),
                'timestamp': datetime.now().isoformat()
            })
            
            state['financial_analysis'] = {
                'investment_scores': {},
                'top_picks': [],
                'error': str(e)
            }
        
        return state
    
    def risk_assessment_node(state: ReportState) -> ReportState:
        """
        4.   ( )
        """
        print("\n" + "="*60)
        print("[WARNING] [RiskAssessmentAgent] ")
        print("="*60)
        
        try:
            #   
            result = risk_agent.analyze_risks(state)
            
            state['risk_assessment'] = result.get('risk_assessment', {})
            
            state['messages'].append(
                f"[OK] RiskAssessmentAgent  - {datetime.now().isoformat()}"
            )
            
            print(f"   [OK]  : {result.get('risk_assessment', {}).get('total_score', 'N/A')}")
            print("[OK] \n")
            
        except Exception as e:
            error_msg = f"[FAIL] RiskAssessmentAgent : {str(e)}"
            print(error_msg)
            
            state['errors'].append({
                'agent': 'RiskAssessmentAgent',
                'error': str(e),
                'traceback': traceback.format_exc(),
                'timestamp': datetime.now().isoformat()
            })
            
            state['risk_assessment'] = {
                'total_score': 50,
                'risk_level': {'level': 'Medium', 'label': ''},
                'error': str(e)
            }
        
        return state
    
    def investment_strategy_node(state: ReportState) -> ReportState:
        """
        5.    ( )
        """
        print("\n" + "="*60)
        print(" [InvestmentStrategyAgent] ")
        print("="*60)
        
        try:
            #   
            result = strategy_agent.develop_investment_strategy(state)
            
            state['investment_strategy'] = result.get('investment_strategy', {})
            
            state['messages'].append(
                f"[OK] InvestmentStrategyAgent  - {datetime.now().isoformat()}"
            )
            
            print(f"   [OK]  : {len(result.get('investment_strategy', {}).get('top_picks', []))}")
            print("[OK] \n")
            
        except Exception as e:
            error_msg = f"[FAIL] InvestmentStrategyAgent : {str(e)}"
            print(error_msg)
            
            state['errors'].append({
                'agent': 'InvestmentStrategyAgent',
                'error': str(e),
                'traceback': traceback.format_exc(),
                'timestamp': datetime.now().isoformat()
            })
            
            state['investment_strategy'] = {
                'top_picks': [],
                'error': str(e)
            }
        
        return state
    
    def report_generation_node(state: ReportState) -> ReportState:
        """
        6.    (CoT      )
        """
        print("\n" + "="*60)
        print(" [ReportGeneratorAgent]  - CoT  ")
        print("="*60)
        
        try:
            #  CoT    
            result = report_agent.generate_report(state)
            
            # State  (  )
            state['final_report'] = result.get('final_report', {})
            state['glossary'] = result.get('glossary', {})
            state['investor_guide'] = result.get('investor_guide', {})
            
            state['messages'].append(
                f"[OK] ReportGeneratorAgent  (CoT) - {datetime.now().isoformat()}"
            )
            
            print(f"   [OK]  : {len(result.get('final_report', {}))}")
            print(f"   [OK]  : {len(result.get('glossary', {}))}")
            print(f"   [OK]  : {len(result.get('investor_guide', {}))} ")
            print(f"   [OK]  : {len(state['source_manager'].citations)}")
            print("[OK] \n")
            
        except Exception as e:
            error_msg = f"[FAIL] ReportGeneratorAgent : {str(e)}"
            print(error_msg)
            
            state['errors'].append({
                'agent': 'ReportGeneratorAgent',
                'error': str(e),
                'traceback': traceback.format_exc(),
                'timestamp': datetime.now().isoformat()
            })
            
            state['final_report'] = {
                'error': '  '
            }
        
        return state
    
    # ==========================================
    #  
    # ==========================================
    
    workflow = StateGraph(ReportState)
    
    #
    workflow.add_node("market_trend_node", market_trend_node)
    workflow.add_node("supplier_matching_node", supplier_matching_node)
    workflow.add_node("financial_analysis_node", financial_analysis_node)
    workflow.add_node("risk_assessment_node", risk_assessment_node)
    workflow.add_node("investment_strategy_node", investment_strategy_node)
    workflow.add_node("report_generation_node", report_generation_node)

    #   ( )
    workflow.set_entry_point("market_trend_node")

    workflow.add_edge("market_trend_node", "supplier_matching_node")
    workflow.add_edge("supplier_matching_node", "financial_analysis_node")
    workflow.add_edge("financial_analysis_node", "risk_assessment_node")
    workflow.add_edge("risk_assessment_node", "investment_strategy_node")
    workflow.add_edge("investment_strategy_node", "report_generation_node")
    workflow.add_edge("report_generation_node", END)
    
    #
    # checkpointer=None  checkpointing
    app = workflow.compile(checkpointer=None)

    return app
