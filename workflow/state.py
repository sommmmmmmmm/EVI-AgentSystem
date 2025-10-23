"""
State  (TypedDict)
"""

from typing import TypedDict, List, Dict, Any, Optional, Annotated
import operator
from models.citation import SourceManager, Citation


class ReportState(TypedDict):
    """
       State
    """
    
    # ==========================================
    # 
    # ==========================================
    
    config: Dict[str, Any]
    """
     
    {
        'report_month': '2025-10',
        'days_ago': 14,
        'keywords': ['', 'EV', '']
    }
    """
    
    # ==========================================
    # MarketTrendAgent 
    # ==========================================
    
    news_articles: List[Dict[str, Any]]
    """  """
    
    keywords: List[str]
    """ """
    
    categorized_keywords: Dict[str, List[str]]
    """
     
    {'': [...], '_': [...], ...}
    """
    
    market_trends: List[Dict[str, Any]]
    """ """
    
    # ==========================================
    # SupplierMatchingAgent 
    # ==========================================
    
    suppliers: List[Dict[str, Any]]
    """
      
    [{'company': 'LG', 'relationship': {...}, ...}]
    """
    
    # ==========================================
    # FinancialAnalyzerAgent 
    # ==========================================
    
    financial_analysis: Dict[str, Any]
    """
      
    {
        'top_picks': [...],
        'investment_scores': {...}
    }
    """
    
    # ==========================================
    # RiskAssessmentAgent 
    # ==========================================
    
    risk_assessment: Dict[str, Any]
    """
      
    {
        'total_score': 48,
        'category_scores': {...},
        'recommendations': [...]
    }
    """
    
    # ==========================================
    # InvestmentStrategyAgent 
    # ==========================================
    
    investment_strategy: Dict[str, Any]
    """
     
    {
        'market_phase': '...',
        'strategies': {...},
        'top_picks': [...]
    }
    """
    
    # ==========================================
    # ReportGeneratorAgent 
    # ==========================================
    
    glossary: Dict[str, str]
    """ """
    
    final_report: Dict[str, str]
    """
     
    {
        '1_summary': '...',
        '2_market': '...',
        ...
    }
    """
    
    # ==========================================
    #   
    # ==========================================
    
    source_manager: SourceManager
    """  -    """
    
    citations: Dict[str, Citation]
    """  """
    
    # ==========================================
    # 
    # ==========================================
    
    errors: Annotated[List[Dict], operator.add]
    """ """
    
    messages: Annotated[List[str], operator.add]
    """ """


def create_initial_state(config: Dict[str, Any]) -> ReportState:
    """
     State
    """
    source_manager = SourceManager()

    return {
        'config': config,
        'news_articles': [],
        'keywords': config.get('keywords', []),  # config keywords 
        'categorized_keywords': {},
        'market_trends': [],
        'suppliers': [],
        'financial_analysis': {},
        'risk_assessment': {},
        'investment_strategy': {},
        'glossary': {},
        'final_report': {},
        'source_manager': source_manager,
        'citations': {},
        'errors': [],
        'messages': []
    }