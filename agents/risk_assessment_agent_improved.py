"""
Risk Assessment Agent -       ( )
   (80%) +    (20%)
"""

from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
import json
import math
import re


class RiskAssessmentAgent:
    """
         
    -    80%: ,  ,    
    -    20%: , , , ,  
    """
    
    #    
    RISK_SEVERITY_SCORES = {
        'critical': 30,  # , ,  , CEO  
        'high': 20,      #  ,   ,  
        'medium': 10,    #  ,  ,   
        'low': 5         #  ,   
    }
    
    #    
    RISK_KEYWORD_MAPPING = {
        'critical': [
            '', '', '', '', '', '',
            '', 'class action', ' ',
            '', '', '', '',
            'CEO ', 'CEO ', ' '
        ],
        'high': [
            ' ', '', '', '',
            'CFO ', 'COO ', '  ',
            ' ', ' ', ' ',
            ' ', ' ', ' '
        ],
        'medium': [
            '', ' ', '',
            ' ', ' ', ' ',
            ' ', ' ', ' ',
            '', '', ''
        ],
        'low': [
            ' ', '', ' ',
            '  ', ' ',
            ' ', ' '
        ]
    }
    
    def __init__(self, web_search_tool, llm_tool, config=None):
        self.web_search_tool = web_search_tool
        self.llm_tool = llm_tool
        
        #   (config  ,  )
        if config and hasattr(config, 'risk_analysis_weights'):
            self.quantitative_weight = config.risk_analysis_weights.get('quantitative', 0.8)
            self.qualitative_weight = config.risk_analysis_weights.get('qualitative', 0.2)
        else:
            self.quantitative_weight = 0.8
            self.qualitative_weight = 0.2
        
        #    
        self.risk_criteria = self._initialize_risk_criteria()
        
        #    (    )
        self.listed_companies = {
            'LG', 'SDI', '', 'SK', 'LG',
            '', 'BYD', 'CATL', 'Panasonic', 'Samsung SDI',
            'Tesla', 'Ford', 'GM', 'Toyota', 'Honda', 'Nissan',
            'BMW', 'Mercedes', 'Volkswagen', 'Audi', 'Porsche'
        }
    
    def _initialize_risk_criteria(self) -> Dict[str, Any]:
        """   """
        return {
            'quantitative': {
                'financial_ratios': {
                    'debt_ratio': {
                        'critical': 1.0,   # 100% 
                        'high': 0.7,       # 70% 
                        'medium': 0.5,     # 50% 
                        'low': 0.3         # 30% 
                    },
                    'current_ratio': {
                        'critical': 0.5,   # 0.5 
                        'high': 1.0,       # 1.0 
                        'medium': 1.2,     # 1.2 
                        'low': 1.5         # 1.5 
                    },
                    'roe': {
                        'critical': -0.05,  #  
                        'high': 0.03,       # 3% 
                        'medium': 0.08,     # 8% 
                        'low': 0.15         # 15% 
                    },
                    'operating_margin': {
                        'critical': -0.05,  #  
                        'high': 0.02,       # 2% 
                        'medium': 0.05,     # 5% 
                        'low': 0.10         # 10% 
                    }
                },
                'market_metrics': {
                    'volatility': {
                        'critical': 0.6,    # 60% 
                        'high': 0.4,        # 40% 
                        'medium': 0.25,     # 25% 
                        'low': 0.15         # 15% 
                    },
                    'beta': {
                        'critical': 2.0,    # 2.0 
                        'high': 1.5,        # 1.5 
                        'medium': 1.2,      # 1.2 
                        'low': 0.8          # 0.8~1.2
                    },
                    'max_drawdown': {
                        'critical': 0.5,    # 50%  
                        'high': 0.3,        # 30%  
                        'medium': 0.2,      # 20%  
                        'low': 0.1          # 10%  
                    }
                },
                'liquidity_metrics': {
                    'trading_volume_ratio': {
                        'critical': 0.001,  #   
                        'high': 0.01,       #  
                        'medium': 0.05,     #  
                        'low': 0.1          #  
                    }
                }
            }
        }
    
    def analyze_risks(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
             
        """
        try:
            print("[WARNING]      ...")
            
            #    
            companies = self._extract_companies_from_state(state)
            
            if not companies:
                print("   [WARNING]    .")
                return {
                    'risk_analysis': {},
                    'risk_summary': {
                        'total_companies': 0,
                        'critical_risk': 0,
                        'high_risk': 0,
                        'medium_risk': 0,
                        'low_risk': 0
                    }
                }
            
            #    
            risk_results = {}
            for company in companies:
                try:
                    print(f"    {company}   ...")
                    risk_analysis = self._analyze_company_risks(company, state)
                    risk_results[company] = risk_analysis
                except Exception as e:
                    print(f"   [FAIL] {company}   : {e}")
                    risk_results[company] = {
                        'overall_risk_score': 0.5,
                        'risk_level': 'medium',
                        'error': str(e)
                    }
            
            #   
            risk_summary = self._generate_risk_summary(risk_results)
            
            print(f"[OK]    - {len(companies)}  ")
            
            return {
                'risk_analysis': risk_results,
                'risk_summary': risk_summary
            }
            
        except Exception as e:
            print(f"[FAIL]   : {e}")
            return {
                'risk_analysis': {},
                'risk_summary': {
                    'total_companies': 0,
                    'critical_risk': 0,
                    'high_risk': 0,
                    'medium_risk': 0,
                    'low_risk': 0,
                    'error': str(e)
                }
            }
    
    def _extract_companies_from_state(self, state: Dict[str, Any]) -> List[str]:
        """    """
        companies = []

        #
        suppliers = state.get('suppliers', [])
        for supplier in suppliers:
            if isinstance(supplier, dict):
                company_name = supplier.get('name', supplier.get('company', ''))
                #       ( , 1 )
                if company_name and len(company_name.strip()) > 1 and not company_name.startswith('_'):
                    companies.append(company_name)

        #
        financial_analysis = state.get('financial_analysis', {})
        if isinstance(financial_analysis, dict):
            for key, value in financial_analysis.items():
                #  state  ('analysis_weights', 'top_picks' )
                if isinstance(value, dict) and 'company_name' in value:
                    company_name = value['company_name']
                    if company_name and len(company_name.strip()) > 1:
                        companies.append(company_name)
                # key    (      )
                elif key in self.listed_companies and len(key) > 1:
                    companies.append(key)

        #    ( )
        filtered_companies = [c for c in companies if len(c.strip()) > 1 and not c.startswith('_')]

        return list(set(filtered_companies))
    
    def _analyze_company_risks(self, company: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """   """
        try:
            # 1.    (80%)
            quantitative_risks = self._analyze_quantitative_risks(company, state)
            
            # 2.    (20%)
            qualitative_risks = self._analyze_qualitative_risks(company, state)
            
            # 3.    
            overall_risk_score = self._calculate_overall_risk_score(
                quantitative_risks, qualitative_risks
            )
            
            # 4.   
            risk_level = self._determine_risk_level(overall_risk_score)
            
            # 5.   
            risk_summary = self._generate_company_risk_summary(
                company, quantitative_risks, qualitative_risks, overall_risk_score
            )
            
            return {
                'company': company,
                'quantitative_risks': quantitative_risks,
                'qualitative_risks': qualitative_risks,
                'overall_risk_score': overall_risk_score,
                'risk_level': risk_level,
                'risk_summary': risk_summary,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"   [FAIL] {company}    : {e}")
            return {
                'company': company,
                'quantitative_risks': {},
                'qualitative_risks': {},
                'overall_risk_score': 0.5,
                'risk_level': 'medium',
                'error': str(e)
            }
    
    def _analyze_quantitative_risks(self, company: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """   (80% )"""
        try:
            #     
            financial_analysis = state.get('financial_analysis', {})
            company_data = financial_analysis.get(company, {})
            
            if not company_data.get('data_available', False):
                #     
                is_listed = self._is_listed_company(company, state)
                risk_score = 0.7 if is_listed else 0.5  #    
                
                return {
                    'financial_ratio_risk': risk_score,
                    'market_risk': risk_score,
                    'liquidity_risk': risk_score,
                    'quantitative_score': risk_score,
                    'data_available': False,
                    'data_missing_reason': '  ' if is_listed else '  '
                }
            
            #    ( )
            financial_ratio_risk = self._analyze_financial_ratio_risk_continuous(company, state)
            
            #    ( )
            market_risk = self._analyze_market_risk_actual(company, state)
            
            #    ( )
            liquidity_risk = self._analyze_liquidity_risk_actual(company, state)
            
            #    ( )
            quantitative_score = (
                financial_ratio_risk * 0.5 +   #  50%
                market_risk * 0.3 +             #   30%
                liquidity_risk * 0.2            #   20%
            )
            
            return {
                'financial_ratio_risk': financial_ratio_risk,
                'market_risk': market_risk,
                'liquidity_risk': liquidity_risk,
                'quantitative_score': quantitative_score,
                'data_available': True
            }
            
        except Exception as e:
            print(f"   [FAIL] {company}    : {e}")
            return {
                'financial_ratio_risk': 0.5,
                'market_risk': 0.5,
                'liquidity_risk': 0.5,
                'quantitative_score': 0.5,
                'data_available': False,
                'error': str(e)
            }
    
    def _is_listed_company(self, company: str, state: Dict[str, Any]) -> bool:
        """  """
        #  state   
        #     
        korean_companies = ['LG', 'SDI', '', '', 'SK']
        return company in korean_companies
    
    def _analyze_financial_ratio_risk_continuous(self, company: str, state: Dict[str, Any]) -> float:
        """   -   """
        financial_criteria = self.risk_criteria['quantitative']['financial_ratios']
        
        #      
        financial_analysis = state.get('financial_analysis', {})
        quantitative_analysis = financial_analysis.get('quantitative_analysis', {})
        company_data = quantitative_analysis.get(company, {})
        
        if not company_data.get('data_available', False):
            #   -    
            if self._is_listed_company(company, state):
                print(f"      [WARNING] {company}      -  ")
                return 0.7  #      
            else:
                print(f"      ℹ {company}   -  ")
                return 0.5  #    
        
        financial_metrics = company_data.get('financial_metrics_analysis', {})
        financial_ratios = financial_metrics.get('financial_ratios', {})
        
        risk_scores = []
        
        # 1.   ( )
        debt_ratio = financial_ratios.get('debt_ratio', 0.5)
        debt_risk = self._calculate_continuous_risk_score(
            value=debt_ratio,
            thresholds=financial_criteria['debt_ratio'],
            higher_is_riskier=True
        )
        risk_scores.append(('debt_ratio', debt_risk, 0.3))
        
        # 2.   ( )
        current_ratio = financial_ratios.get('current_ratio', 1.2)
        current_risk = self._calculate_continuous_risk_score(
            value=current_ratio,
            thresholds=financial_criteria['current_ratio'],
            higher_is_riskier=False  #   
        )
        risk_scores.append(('current_ratio', current_risk, 0.25))
        
        # 3. ROE  ( )
        roe = financial_ratios.get('roe', 0.08)
        roe_risk = self._calculate_continuous_risk_score(
            value=roe,
            thresholds=financial_criteria['roe'],
            higher_is_riskier=False  # ROE  
        )
        risk_scores.append(('roe', roe_risk, 0.25))
        
        # 4.   ( )
        operating_margin = financial_ratios.get('operating_margin', 0.05)
        margin_risk = self._calculate_continuous_risk_score(
            value=operating_margin,
            thresholds=financial_criteria['operating_margin'],
            higher_is_riskier=False  #   
        )
        risk_scores.append(('operating_margin', margin_risk, 0.2))
        
        #   
        total_risk = sum(score * weight for _, score, weight in risk_scores)
        total_weight = sum(weight for _, _, weight in risk_scores)
        
        return total_risk / total_weight if total_weight > 0 else 0.5
    
    def _calculate_continuous_risk_score(
        self, 
        value: float, 
        thresholds: Dict[str, float],
        higher_is_riskier: bool = True
    ) -> float:
        """
            ( )
        
        Args:
            value:  
            thresholds: {'critical': x, 'high': y, 'medium': z, 'low': w}
            higher_is_riskier: True   , False  
        
        Returns:
            0.0 () ~ 1.0 ( )
        """
        critical = thresholds['critical']
        high = thresholds['high']
        medium = thresholds['medium']
        low = thresholds['low']
        
        if higher_is_riskier:
            #    (: )
            if value >= critical:
                return 1.0
            elif value >= high:
                # critical high   
                return 0.75 + 0.25 * (value - high) / (critical - high)
            elif value >= medium:
                return 0.5 + 0.25 * (value - medium) / (high - medium)
            elif value >= low:
                return 0.25 + 0.25 * (value - low) / (medium - low)
            else:
                return 0.25 * value / low if low > 0 else 0.0
        else:
            #    (: , ROE)
            if value <= critical:
                return 1.0
            elif value <= high:
                return 0.75 + 0.25 * (high - value) / (high - critical)
            elif value <= medium:
                return 0.5 + 0.25 * (medium - value) / (medium - high)
            elif value <= low:
                return 0.25 + 0.25 * (low - value) / (low - medium)
            else:
                # low    
                return max(0.0, 0.25 * (1 - (value - low) / low))
    
    def _analyze_market_risk_actual(self, company: str, state: Dict[str, Any]) -> float:
        """   -   """
        try:
            print(f"       {company}    ...")
            
            # state   
            market_data = state.get('market_data', {}).get(company, {})
            
            if not market_data:
                print(f"      [WARNING] {company}    -  ")
                return 0.7  #    
            
            #    
            volatility = market_data.get('volatility', None)
            if volatility is not None:
                #  0.2() ~ 0.6()  0.3 ~ 0.8   
                volatility_risk = min(max((volatility - 0.2) / 0.4 * 0.5 + 0.3, 0.3), 0.8)
                print(f"       : {volatility:.3f} → : {volatility_risk:.3f}")
            else:
                volatility_risk = 0.5  #   
                print(f"      [WARNING]   ")
            
            #    
            beta = market_data.get('beta', None)
            if beta is not None:
                #  0.5() ~ 2.0()  0.3 ~ 0.8   
                beta_risk = min(max(abs(beta - 1.0) * 0.4 + 0.3, 0.3), 0.8)
                print(f"       : {beta:.3f} → : {beta_risk:.3f}")
            else:
                beta_risk = 0.5  #   
                print(f"      [WARNING]   ")
            
            #     
            max_drawdown = market_data.get('max_drawdown', None)
            if max_drawdown is not None:
                #  0.1() ~ 0.5()  0.3 ~ 0.8   
                drawdown_risk = min(max(abs(max_drawdown) * 1.5 + 0.3, 0.3), 0.8)
                print(f"       : {max_drawdown:.3f} → : {drawdown_risk:.3f}")
            else:
                drawdown_risk = 0.5  #   
                print(f"      [WARNING]   ")
            
            #     
            volume_ratio = market_data.get('trading_volume_ratio', None)
            if volume_ratio is not None:
                #   0.05() ~ 0.2()  0.8 ~ 0.2    ()
                volume_risk = max(0.2, 0.8 - volume_ratio * 3)
                print(f"       : {volume_ratio:.3f} → : {volume_risk:.3f}")
            else:
                volume_risk = 0.5  #   
                print(f"      [WARNING]   ")
            
            #   (     )
            weights = []
            risks = []
            
            if volatility is not None:
                weights.append(0.4)
                risks.append(volatility_risk)
            if beta is not None:
                weights.append(0.3)
                risks.append(beta_risk)
            if max_drawdown is not None:
                weights.append(0.2)
                risks.append(drawdown_risk)
            if volume_ratio is not None:
                weights.append(0.1)
                risks.append(volume_risk)
            
            if weights and risks:
                #  
                total_weight = sum(weights)
                normalized_weights = [w / total_weight for w in weights]
                
                market_risk = sum(w * r for w, r in zip(normalized_weights, risks))
                print(f"      [OK]  : {market_risk:.3f} (  )")
            else:
                market_risk = 0.7  #   
                print(f"      [WARNING]     -  ")
            
            return min(max(market_risk, 0.1), 1.0)
            
        except Exception as e:
            print(f"   [FAIL] {company}    : {e}")
            return 0.7  #    
    
    def _analyze_liquidity_risk_actual(self, company: str, state: Dict[str, Any]) -> float:
        """   -  """
        try:
            liquidity_criteria = self.risk_criteria['quantitative']['liquidity_metrics']
            
            # state   
            market_data = state.get('market_data', {}).get(company, {})
            
            #   (  / )
            trading_volume_ratio = market_data.get('trading_volume_ratio', 0.05)
            
            #     
            liquidity_risk = self._calculate_continuous_risk_score(
                value=trading_volume_ratio,
                thresholds=liquidity_criteria['trading_volume_ratio'],
                higher_is_riskier=False  #   
            )
            
            return liquidity_risk
            
        except Exception as e:
            print(f"   [WARNING] {company}    ,  : {e}")
            return 0.2  # 
    
    def _analyze_qualitative_risks(self, company: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """   (20% ) -   """
        try:
            print(f"       {company}    ...")
            
            # 1.     (  )
            governance_risks = self._search_governance_risks(company)
            legal_risks = self._search_legal_risks(company)
            management_risks = self._search_management_risks(company)
            
            # 2.   
            all_risks = governance_risks + legal_risks + management_risks
            
            # 3.    
            deduplicated_risks = self._deduplicate_risks(all_risks)
            
            # 4.    0 
            if not deduplicated_risks:
                print(f"      ℹ {company} -    ")
                return {
                    'governance_risks': [],
                    'legal_risks': [],
                    'management_risks': [],
                    'all_risks': [],
                    'governance_score': 0.0,
                    'legal_score': 0.0,
                    'management_score': 0.0,
                    'qualitative_score': 0.0,
                    'risk_count': 0,
                    'data_source': 'real_web_search',
                    'no_risks_found': True
                }
            
            # 5.    (    )
            qualitative_score = self._calculate_qualitative_score(deduplicated_risks)
            
            # 6.  
            governance_score = self._calculate_category_score(
                [r for r in deduplicated_risks if r['category'] == 'governance']
            )
            legal_score = self._calculate_category_score(
                [r for r in deduplicated_risks if r['category'] == 'legal']
            )
            management_score = self._calculate_category_score(
                [r for r in deduplicated_risks if r['category'] == 'management']
            )
            
            print(f"      [OK] {company} -   {len(deduplicated_risks)} ")
            
            return {
                'governance_risks': [r for r in deduplicated_risks if r['category'] == 'governance'],
                'legal_risks': [r for r in deduplicated_risks if r['category'] == 'legal'],
                'management_risks': [r for r in deduplicated_risks if r['category'] == 'management'],
                'all_risks': deduplicated_risks,
                'governance_score': governance_score,
                'legal_score': legal_score,
                'management_score': management_score,
                'qualitative_score': qualitative_score,
                'risk_count': len(deduplicated_risks),
                'data_source': 'real_web_search',
                'no_risks_found': False
            }
            
        except Exception as e:
            print(f"   [FAIL] {company}    : {e}")
            return {
                'governance_risks': [],
                'legal_risks': [],
                'management_risks': [],
                'all_risks': [],
                'governance_score': 0.0,
                'legal_score': 0.0,
                'management_score': 0.0,
                'qualitative_score': 0.0,
                'risk_count': 0,
                'data_source': 'real_web_search',
                'error': str(e)
            }
    
    def _search_governance_risks(self, company: str) -> List[Dict[str, Any]]:
        """거버넌스 리스크 검색"""
        try:
            # 거버넌스 관련 검색 쿼리
            search_queries = [
                f"{company} governance issues",
                f"{company} corporate governance problems",
                f"{company} board management risks"
            ]
            
            risks = []
            for query in search_queries:
                #    
                search_results = self._search_web_risks(query, company, 'governance')
                
                # LLM      
                extracted_risks = self._extract_risks_with_llm(
                    search_results, company, 'governance'
                )
                risks.extend(extracted_risks)
            
            return risks
            
        except Exception as e:
            print(f"      [WARNING]    : {e}")
            return []
    
    def _search_legal_risks(self, company: str) -> List[Dict[str, Any]]:
        """법적 리스크 검색"""
        try:
            search_queries = [
                f"{company} legal issues",
                f"{company} regulatory problems",
                f"{company} compliance violations"
            ]
            
            risks = []
            for query in search_queries:
                search_results = self._search_web_risks(query, company, 'legal')
                extracted_risks = self._extract_risks_with_llm(
                    search_results, company, 'legal'
                )
                risks.extend(extracted_risks)
            
            return risks
            
        except Exception as e:
            print(f"      [WARNING]    : {e}")
            return []
    
    def _search_management_risks(self, company: str) -> List[Dict[str, Any]]:
        """경영 리스크 검색"""
        try:
            search_queries = [
                f"{company} management issues",
                f"{company} leadership problems",
                f"{company} executive scandals"
            ]
            
            risks = []
            for query in search_queries:
                search_results = self._search_web_risks(query, company, 'management')
                extracted_risks = self._extract_risks_with_llm(
                    search_results, company, 'management'
                )
                risks.extend(extracted_risks)
            
            return risks
            
        except Exception as e:
            print(f"      [WARNING]    : {e}")
            return []
    
    def _search_web_risks(self, query: str, company: str, category: str) -> List[Dict[str, Any]]:
        """      """
        try:
            print(f"         : {query}")
            
            #    
            search_results = self.web_search_tool.search(query, num_results=1)  # API 한도 최적화: 1개로 축소
            
            if not search_results:
                print(f"      ℹ   : {query}")
                return []
            
            #     
            risks = []
            for result in search_results:
                risk_data = {
                    'title': result.get('title', ''),
                    'content': result.get('content', ''),
                    'date': result.get('date', datetime.now().isoformat()),
                    'url': result.get('url', ''),
                    'company': company,
                    'category': category
                }
                risks.append(risk_data)
            
            print(f"      [OK]   {len(risks)} : {query}")
            return risks
            
        except Exception as e:
            print(f"      [FAIL]    ({query}): {e}")
            return []
    
    def _extract_risks_with_llm(
        self, 
        search_results: List[Dict[str, Any]], 
        company: str,
        category: str
    ) -> List[Dict[str, Any]]:
        """LLM        """
        if not search_results:
            return []
        
        risks = []
        
        for result in search_results:
            content = result.get('content', '')
            title = result.get('title', '')
            date_str = result.get('date', '')
            
            # LLM   
            risk_analysis = self._analyze_risk_with_llm(title, content, company, category)
            
            if not risk_analysis:
                continue
            
            #   (timezone-aware )
            try:
                if 'Z' in date_str:
                    risk_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                elif '+' in date_str or date_str.endswith('00:00'):
                    risk_date = datetime.fromisoformat(date_str)
                else:
                    risk_date = datetime.fromisoformat(date_str)
            except:
                risk_date = datetime.now()
            
            #   
            time_weight = self._calculate_time_decay(risk_date)
            
            #   
            risk = {
                'company': company,
                'category': category,
                'severity': risk_analysis['severity'],
                'description': risk_analysis['description'],
                'content': content[:200],  #  200
                'date': risk_date.isoformat(),
                'time_weight': time_weight,
                'source_url': result.get('url', ''),
                'score': self.RISK_SEVERITY_SCORES[risk_analysis['severity']] * time_weight,
                'confidence': risk_analysis.get('confidence', 0.5)
            }
            
            risks.append(risk)
        
        return risks
    
    def _analyze_risk_with_llm(self, title: str, content: str, company: str, category: str) -> Optional[Dict[str, Any]]:
        """LLM   """
        try:
            print(f"      🤖 LLM  : {title[:50]}...")
            
            prompt = f"""
    {company} {category}   .

: {title}
: {content[:500]}

  JSON :
{{
    "is_risk": true/false,
    "severity": "critical/high/medium/low",
    "description": " ",
    "confidence": 0.0-1.0
}}

  :
- critical: , ,  , CEO  
- high:  ,   ,  
- medium:  ,  ,  
- low:  ,   

  is_risk: false .
"""
            
            response = self.llm_tool.generate(prompt)
            print(f"       LLM : {response[:100]}...")
            
            # JSON  
            import json
            try:
                analysis = json.loads(response)
                if not analysis.get('is_risk', False):
                    print(f"      ℹ LLM :  ")
                    return None
                
                result = {
                    'severity': analysis.get('severity', 'medium'),
                    'description': analysis.get('description', title),
                    'confidence': analysis.get('confidence', 0.5)
                }
                print(f"      [OK] LLM  : {result['severity']} (: {result['confidence']})")
                return result
            except json.JSONDecodeError:
                print(f"      [WARNING] JSON  ,   ")
                print(f"[ERROR] JSON 파싱 실패로 '{title}' 리스크 분석을 수행할 수 없습니다.")
                return None
                
        except Exception as e:
            print(f"      [FAIL] LLM   : {e}")
            print(f"[ERROR] LLM API 실패로 '{title}' 리스크 분석을 수행할 수 없습니다.")
            return None
    
    def _fallback_risk_analysis(self, title: str, content: str) -> Optional[Dict[str, Any]]:
        """LLM 실패 시 에러 반환"""
        print(f"[ERROR] LLM API가 실패하여 '{title}' 리스크 분석을 수행할 수 없습니다.")
        return None
    
    def _is_listed_company(self, company: str, state: Dict[str, Any]) -> bool:
        """   """
        try:
            # 1.    
            if company in self.listed_companies:
                return True
            
            # 2.      
            market_data = state.get('market_data', {}).get(company, {})
            if market_data and any(key in market_data for key in ['volatility', 'beta', 'trading_volume_ratio']):
                return True
            
            # 3.       ( )
            financial_analysis = state.get('financial_analysis', {}).get(company, {})
            if financial_analysis.get('data_available', False):
                return True
            
            # 4.      
            listed_keywords = ['', '()', 'Co.', 'Ltd.', 'Corp.', 'Inc.']
            if any(keyword in company for keyword in listed_keywords):
                return True
            
            return False
            
        except Exception as e:
            print(f"      [WARNING] {company}    : {e}")
            return False
    
    def _determine_severity(self, content: str) -> str:
        """    """
        content_lower = content.lower()
        
        #   
        for severity in ['critical', 'high', 'medium', 'low']:
            keywords = self.RISK_KEYWORD_MAPPING[severity]
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    return severity
        
        #    medium
        return 'medium'
    
    def _calculate_time_decay(self, risk_date: datetime) -> float:
        """
             ( )
        -  1: 1.0 ( )
        - 1: 0.9 ( )
        - 3: 0.7 ()
        - 6: 0.5 ()
        - 1: 0.3 ()
        - 1 : 0.1 ( )
        """
        days_ago = (datetime.now() - risk_date).days
        
        #   
        if days_ago <= 7:      # 1 :  
            return 1.0
        elif days_ago <= 30:   # 1 :  
            return 0.9
        elif days_ago <= 90:   # 3 :  
            return 0.7
        elif days_ago <= 180:  # 6 :  
            return 0.5
        elif days_ago <= 365:  # 1 :   
            return 0.3
        else:                  # 1 :  
            return 0.1
    
    def _deduplicate_risks(self, risks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """    ( )"""
        if not risks:
            return []
        
        #     (  )
        unique_risks = {}
        
        for risk in risks:
            key = (risk['category'], risk['description'][:50])  #  50  
            
            if key not in unique_risks:
                unique_risks[key] = risk
            else:
                #    
                if risk['date'] > unique_risks[key]['date']:
                    unique_risks[key] = risk
        
        return list(unique_risks.values())
    
    def _calculate_qualitative_score(self, risks: List[Dict[str, Any]]) -> float:
        """
            
        -   (  ×  ) 
        - 0~100  
        - 0~1.0  
        """
        if not risks:
            return 0.0  #   = 0.0 ()
        
        #    
        total_score = sum(risk['score'] for risk in risks)
        
        #  (100 )
        # critical 3 + high 2  100
        # critical: 30, high: 20 → 30*3 + 20*2 = 130
        normalized_score = min(total_score / 100.0, 1.0)
        
        return normalized_score
    
    def _calculate_category_score(self, risks: List[Dict[str, Any]]) -> float:
        """  """
        if not risks:
            return 0.0
        
        total_score = sum(risk['score'] for risk in risks)
        return min(total_score / 50.0, 1.0)  # 50  
    
    def _calculate_overall_risk_score(
        self, 
        quantitative_risks: Dict[str, Any], 
        qualitative_risks: Dict[str, Any]
    ) -> float:
        """    ( 80% +  20%)"""
        quantitative_score = quantitative_risks.get('quantitative_score', 0.5)
        qualitative_score = qualitative_risks.get('qualitative_score', 0.0)
        
        overall_score = (
            quantitative_score * self.quantitative_weight +
            qualitative_score * self.qualitative_weight
        )
        
        return overall_score
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """   (4)"""
        if risk_score >= 0.75:
            return 'critical'
        elif risk_score >= 0.6:
            return 'high'
        elif risk_score >= 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _generate_company_risk_summary(
        self,
        company: str,
        quantitative_risks: Dict[str, Any],
        qualitative_risks: Dict[str, Any],
        overall_risk_score: float
    ) -> str:
        """   """
        risk_level = self._determine_risk_level(overall_risk_score)
        
        #   
        quant_score = quantitative_risks.get('quantitative_score', 0.5)
        financial_risk = quantitative_risks.get('financial_ratio_risk', 0.5)
        market_risk = quantitative_risks.get('market_risk', 0.5)
        
        #   
        qual_score = qualitative_risks.get('qualitative_score', 0.0)
        risk_count = qualitative_risks.get('risk_count', 0)
        
        summary = f"""
{company}   :
-   : {risk_level.upper()} ({overall_risk_score:.2f})
-  : {quant_score:.2f} (: {financial_risk:.2f}, : {market_risk:.2f})
-  : {qual_score:.2f} ( : {risk_count})
        """.strip()
        
        return summary
    
    def _generate_risk_summary(self, risk_results: Dict[str, Any]) -> Dict[str, Any]:
        """   """
        total_companies = len(risk_results)
        
        if total_companies == 0:
            return {
                'total_companies': 0,
                'critical_risk': 0,
                'high_risk': 0,
                'medium_risk': 0,
                'low_risk': 0,
                'average_risk_score': 0.0
            }
        
        #  
        critical_risk = sum(1 for r in risk_results.values() if r.get('risk_level') == 'critical')
        high_risk = sum(1 for r in risk_results.values() if r.get('risk_level') == 'high')
        medium_risk = sum(1 for r in risk_results.values() if r.get('risk_level') == 'medium')
        low_risk = sum(1 for r in risk_results.values() if r.get('risk_level') == 'low')
        
        #   
        average_risk_score = sum(
            r.get('overall_risk_score', 0.5) for r in risk_results.values()
        ) / total_companies
        
        return {
            'total_companies': total_companies,
            'critical_risk': critical_risk,
            'high_risk': high_risk,
            'medium_risk': medium_risk,
            'low_risk': low_risk,
            'average_risk_score': average_risk_score
        }


# 테스트 코드 제거됨 - Mock 데이터 사용 금지
