"""
Risk Assessment Agent -       ( )
   (80%) +    (20%)
"""

from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
import json
import math
import re
from tools.json_parser import parse_llm_json  # 🆕 강력한 JSON 파서


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
        """리스크 평가 기준 초기화 - 3가지 핵심 리스크"""
        return {
            'quantitative': {
                'technology_investment': {
                    'rnd_ratio': {
                        'critical': 0.25,   # 25% 이상 (매출 대비 과도)
                        'high': 0.20,       # 20% 이상
                        'medium': 0.15,     # 15% 이상
                        'low': 0.10         # 10% 이상 (혁신 기업)
                    },
                    'intangible_ratio': {
                        'critical': 0.50,   # 50% 이상 (총자산 대비)
                        'high': 0.40,       # 40% 이상
                        'medium': 0.30,     # 30% 이상
                        'low': 0.20         # 20% 이상
                    }
                },
                'working_capital': {
                    'wc_to_sales_ratio': {
                        'critical': 0.40,   # 40% 이상 (과다)
                        'high': 0.30,       # 30% 이상
                        'medium': 0.20,     # 20% 이상
                        'low': 0.10         # 10% 이상 (적정)
                    },
                    'cash_conversion_cycle': {
                        'critical': 120,    # 120일 이상
                        'high': 90,         # 90일 이상
                        'medium': 60,       # 60일 이상
                        'low': 30           # 30일 이상 (양호)
                    }
                },
                'growth_stage': {
                    'capex_ratio': {
                        'critical': 0.30,   # 30% 이상 (매출 대비 과도)
                        'high': 0.20,       # 20% 이상
                        'medium': 0.15,     # 15% 이상
                        'low': 0.10         # 10% 이상 (성장단계)
                    },
                    'depreciation_growth': {
                        'critical': 0.50,   # 50% 이상 증가
                        'high': 0.30,       # 30% 이상 증가
                        'medium': 0.20,     # 20% 이상 증가
                        'low': 0.10         # 10% 이상 증가
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
            
            # 🆕 상대적 리스크 재분류 (최소 1개씩 보장)
            risk_results = self._reclassify_risk_levels_relative(risk_results)
            
            #   
            risk_summary = self._generate_risk_summary(risk_results)
            
            print(f"[OK]    - {len(companies)}  ")
            print(f"   저위험: {risk_summary.get('low_risk', 0)}개")
            print(f"   중위험: {risk_summary.get('medium_risk', 0)}개")
            print(f"   고위험: {risk_summary.get('high_risk', 0)}개")
            print(f"   Critical: {risk_summary.get('critical_risk', 0)}개")
            
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
        """정량적 리스크 분석 (80% 가중치) - 3가지 핵심 지표"""
        try:
            # 재무제표 데이터 확인
            financial_analysis = state.get('financial_analysis', {})
            company_data = financial_analysis.get(company, {})
            
            if not company_data.get('data_available', False):
                # 데이터 없을 경우
                is_listed = self._is_listed_company(company, state)
                risk_score = 0.7 if is_listed else 0.5
                
                return {
                    'technology_investment_risk': risk_score,
                    'working_capital_risk': risk_score,
                    'growth_stage_risk': risk_score,
                    'quantitative_score': risk_score,
                    'data_available': False,
                    'data_missing_reason': '상장기업 데이터 부족' if is_listed else '비상장 기업'
                }
            
            # 1. 기술투자 리스크 (40%)
            tech_investment_risk = self._analyze_technology_investment_risk(company, state)
            
            # 2. 운전자본 리스크 (35%)
            working_capital_risk = self._analyze_working_capital_risk(company, state)
            
            # 3. 성장단계 리스크 (25%)
            growth_stage_risk = self._analyze_growth_stage_risk(company, state)
            
            # 가중 평균 계산
            quantitative_score = (
                tech_investment_risk * 0.40 +    # 기술투자 40%
                working_capital_risk * 0.35 +    # 운전자본 35%
                growth_stage_risk * 0.25         # 성장단계 25%
            )
            
            return {
                'technology_investment_risk': tech_investment_risk,
                'working_capital_risk': working_capital_risk,
                'growth_stage_risk': growth_stage_risk,
                'quantitative_score': quantitative_score,
                'data_available': True
            }
            
        except Exception as e:
            print(f"정량적 분석 [FAIL] {company} 리스크 분석 실패: {e}")
            return {
                'technology_investment_risk': 0.5,
                'working_capital_risk': 0.5,
                'growth_stage_risk': 0.5,
                'quantitative_score': 0.5,
                'data_available': False,
                'error': str(e)
            }
    
    def _analyze_technology_investment_risk(self, company: str, state: Dict[str, Any]) -> float:
        """기술투자 리스크 분석 (R&D 비용 비중 + 무형자산 비중)"""
        try:
            tech_criteria = self.risk_criteria['quantitative']['technology_investment']
            
            # 재무제표 데이터 추출
            financial_analysis = state.get('financial_analysis', {})
            company_data = financial_analysis.get(company, {})
            
            # 재무제표에서 데이터 추출
            income_statement = company_data.get('income_statement', {})
            balance_sheet = company_data.get('balance_sheet', {})
            
            # R&D 비용 / 매출
            rnd_expense = income_statement.get('rnd_expense', 0)
            revenue = income_statement.get('revenue', 1)
            rnd_ratio = rnd_expense / revenue if revenue > 0 else 0.0
            
            # 무형자산 / 총자산
            intangible_assets = balance_sheet.get('intangible_assets', 0)
            total_assets = balance_sheet.get('total_assets', 1)
            intangible_ratio = intangible_assets / total_assets if total_assets > 0 else 0.0
            
            # 각 지표의 리스크 점수 계산
            rnd_risk = self._calculate_continuous_risk_score(
                value=rnd_ratio,
                thresholds=tech_criteria['rnd_ratio'],
                higher_is_riskier=True  # R&D 비중이 높을수록 위험
            )
            
            intangible_risk = self._calculate_continuous_risk_score(
                value=intangible_ratio,
                thresholds=tech_criteria['intangible_ratio'],
                higher_is_riskier=True  # 무형자산 비중이 높을수록 위험
            )
            
            # 가중 평균 (R&D 60%, 무형자산 40%)
            tech_investment_risk = rnd_risk * 0.6 + intangible_risk * 0.4
            
            print(f"      기술투자 리스크: R&D비중={rnd_ratio:.2%}, 무형자산비중={intangible_ratio:.2%}, 리스크={tech_investment_risk:.3f}")
            
            return tech_investment_risk
            
        except Exception as e:
            print(f"      [WARNING] {company} 기술투자 리스크 분석 실패: {e}")
            return 0.5
    
    def _analyze_working_capital_risk(self, company: str, state: Dict[str, Any]) -> float:
        """운전자본 리스크 분석 (운전자본/매출 + CCC)"""
        try:
            wc_criteria = self.risk_criteria['quantitative']['working_capital']
            
            # 재무제표 데이터 추출
            financial_analysis = state.get('financial_analysis', {})
            company_data = financial_analysis.get(company, {})
            
            balance_sheet = company_data.get('balance_sheet', {})
            income_statement = company_data.get('income_statement', {})
            
            # 운전자본 = 유동자산 - 유동부채
            current_assets = balance_sheet.get('current_assets', 0)
            current_liabilities = balance_sheet.get('current_liabilities', 0)
            working_capital = current_assets - current_liabilities
            
            # 운전자본 / 매출
            revenue = income_statement.get('revenue', 1)
            wc_to_sales = working_capital / revenue if revenue > 0 else 0.0
            
            # CCC (현금전환주기) 계산
            # CCC = 재고회전일수 + 매출채권회전일수 - 매입채무회전일수
            inventory = balance_sheet.get('inventory', 0)
            accounts_receivable = balance_sheet.get('accounts_receivable', 0)
            accounts_payable = balance_sheet.get('accounts_payable', 0)
            cogs = income_statement.get('cogs', revenue * 0.7)  # 기본값: 매출의 70%
            
            # 회전일수 계산 (간이 계산)
            inventory_days = (inventory / cogs * 365) if cogs > 0 else 0
            receivable_days = (accounts_receivable / revenue * 365) if revenue > 0 else 0
            payable_days = (accounts_payable / cogs * 365) if cogs > 0 else 0
            
            ccc = inventory_days + receivable_days - payable_days
            
            # 각 지표의 리스크 점수 계산
            wc_risk = self._calculate_continuous_risk_score(
                value=abs(wc_to_sales),  # 절댓값 사용 (과다/과소 모두 위험)
                thresholds=wc_criteria['wc_to_sales_ratio'],
                higher_is_riskier=True
            )
            
            ccc_risk = self._calculate_continuous_risk_score(
                value=ccc,
                thresholds=wc_criteria['cash_conversion_cycle'],
                higher_is_riskier=True  # CCC가 길수록 위험
            )
            
            # 가중 평균 (운전자본비율 50%, CCC 50%)
            working_capital_risk = wc_risk * 0.5 + ccc_risk * 0.5
            
            print(f"      운전자본 리스크: WC/매출={wc_to_sales:.2%}, CCC={ccc:.1f}일, 리스크={working_capital_risk:.3f}")
            
            return working_capital_risk
            
        except Exception as e:
            print(f"      [WARNING] {company} 운전자본 리스크 분석 실패: {e}")
            return 0.5
    
    def _analyze_growth_stage_risk(self, company: str, state: Dict[str, Any]) -> float:
        """성장단계 리스크 분석 (CapEx/매출 + 감가상각비 증가율)"""
        try:
            growth_criteria = self.risk_criteria['quantitative']['growth_stage']
            
            # 재무제표 데이터 추출
            financial_analysis = state.get('financial_analysis', {})
            company_data = financial_analysis.get(company, {})
            
            cash_flow = company_data.get('cash_flow_statement', {})
            income_statement = company_data.get('income_statement', {})
            
            # CapEx / 매출
            capex = abs(cash_flow.get('capex', 0))  # 투자는 음수로 표시되므로 절댓값
            revenue = income_statement.get('revenue', 1)
            capex_ratio = capex / revenue if revenue > 0 else 0.0
            
            # 감가상각비 증가율
            depreciation_current = income_statement.get('depreciation', 0)
            depreciation_previous = company_data.get('previous_year', {}).get('depreciation', depreciation_current)
            
            if depreciation_previous > 0:
                depreciation_growth = (depreciation_current - depreciation_previous) / depreciation_previous
            else:
                depreciation_growth = 0.0
            
            # 각 지표의 리스크 점수 계산
            capex_risk = self._calculate_continuous_risk_score(
                value=capex_ratio,
                thresholds=growth_criteria['capex_ratio'],
                higher_is_riskier=True  # CapEx 비중이 높을수록 투자 부담
            )
            
            depreciation_risk = self._calculate_continuous_risk_score(
                value=abs(depreciation_growth),  # 절댓값 (증가/감소 모두 고려)
                thresholds=growth_criteria['depreciation_growth'],
                higher_is_riskier=True
            )
            
            # 가중 평균 (CapEx 60%, 감가상각 40%)
            growth_stage_risk = capex_risk * 0.6 + depreciation_risk * 0.4
            
            print(f"      성장단계 리스크: CapEx/매출={capex_ratio:.2%}, 감가상각증가율={depreciation_growth:.2%}, 리스크={growth_stage_risk:.3f}")
            
            return growth_stage_risk
            
        except Exception as e:
            print(f"      [WARNING] {company} 성장단계 리스크 분석 실패: {e}")
            return 0.5
    
    def _is_listed_company(self, company: str, state: Dict[str, Any]) -> bool:
        """상장 여부 확인"""
        # state 데이터 확인
        # 간단한 휴리스틱
        korean_companies = ['LG', 'SDI', '삼성', '현대', 'SK']
        return company in korean_companies
    
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
            
            prompt = f"""You are a risk assessment model. Analyze the following information and return ONLY a valid JSON object.

**IMPORTANT**: Return ONLY the JSON object. No markdown fences (```), no commentary, no explanations.

Company: {company}
Category: {category}
Title: {title}
Content: {content[:500]}

Required JSON format:
{{
    "is_risk": true/false,
    "severity": "critical" | "high" | "medium" | "low",
    "description": "brief explanation in Korean",
    "confidence": 0.0-1.0
}}

Severity guidelines:
- critical: 파산, 대규모 소송, 중대 사고, CEO 사임
- high: 주가 급락, 실적 악화, 규제 위반
- medium: 경영 불확실성, 경쟁 심화, 비용 증가
- low: 소규모 법적 이슈, 일반 경영 변화

If there is no significant risk, set "is_risk": false.

Return ONLY the JSON object now:"""
            
            response = self.llm_tool.generate(prompt)
            print(f"       LLM : {response[:100]}...")
            
            # JSON 파싱 (마크다운 코드 블록 제거)
            import json
            try:
                # 🆕 강력한 JSON 파서 사용 (markdown, 자연어, 잘못된 형식 모두 처리)
                analysis = parse_llm_json(
                    response,
                    fallback_data={
                        'is_risk': False,
                        'severity': 'medium',
                        'description': title,
                        'confidence': 0.3
                    }
                )
                
                if not analysis:
                    print(f"      ⚠️ JSON 파싱 완전 실패, fallback 사용")
                    return None
                
                if not analysis.get('is_risk', False):
                    print(f"      ℹ LLM 분석: 리스크 없음")
                    return None
                
                result = {
                    'severity': analysis.get('severity', 'medium'),
                    'description': analysis.get('description', title),
                    'confidence': analysis.get('confidence', 0.5)
                }
                print(f"      [OK] LLM 분석: {result['severity']} (신뢰도: {result['confidence']})")
                return result
            except Exception as e:
                print(f"      [ERROR] JSON 처리 예외: {e}")
                print(f"[ERROR] '{title}' 리스크 분석 실패")
                return None
                
        except Exception as e:
            print(f"      [FAIL] LLM   : {e}")
            print(f"[ERROR] LLM API 실패로 '{title}' 리스크 분석을 수행할 수 없습니다.")
            return None
    
    def _fallback_risk_analysis(self, title: str, content: str) -> Optional[Dict[str, Any]]:
        """LLM 실패 시 에러 반환"""
        print(f"[ERROR] LLM API가 실패하여 '{title}' 리스크 분석을 수행할 수 없습니다.")
        return None
    
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
        """기업 리스크 요약 생성"""
        risk_level = self._determine_risk_level(overall_risk_score)
        
        # 정량적 리스크 (새로운 3가지 지표)
        quant_score = quantitative_risks.get('quantitative_score', 0.5)
        tech_risk = quantitative_risks.get('technology_investment_risk', 0.5)
        wc_risk = quantitative_risks.get('working_capital_risk', 0.5)
        growth_risk = quantitative_risks.get('growth_stage_risk', 0.5)
        
        # 정성적 리스크
        qual_score = qualitative_risks.get('qualitative_score', 0.0)
        risk_count = qualitative_risks.get('risk_count', 0)
        
        summary = f"""
{company} 리스크 평가:
- 종합 등급: {risk_level.upper()} ({overall_risk_score:.2f})
- 정량적 리스크: {quant_score:.2f} (기술투자: {tech_risk:.2f}, 운전자본: {wc_risk:.2f}, 성장단계: {growth_risk:.2f})
- 정성적 리스크: {qual_score:.2f} (리스크 이슈: {risk_count}건)
        """.strip()
        
        return summary
    
    def _reclassify_risk_levels_relative(self, risk_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        상대적 리스크 재분류 - 최소 1개씩 보장
        
        Args:
            risk_results: 기업별 리스크 분석 결과
            
        Returns:
            재분류된 리스크 결과
        """
        if not risk_results or len(risk_results) < 2:
            return risk_results
        
        # 점수 기준으로 정렬
        sorted_companies = sorted(
            risk_results.items(),
            key=lambda x: x[1].get('overall_risk_score', 0.5)
        )
        
        total = len(sorted_companies)
        
        # 상대적 분류 (1/3씩, 최소 1개 보장)
        low_count = max(1, total // 3)
        medium_count = max(1, total // 3)
        high_count = total - low_count - medium_count
        
        # Critical은 상위 10%만 (최소 0개, 최대 전체의 10%)
        critical_count = min(max(0, total // 10), high_count)
        
        print(f"\n   === 상대적 리스크 재분류 ===")
        print(f"   총 {total}개 기업")
        print(f"   저위험: {low_count}개 (하위 33%)")
        print(f"   중위험: {medium_count}개 (중간 33%)")
        print(f"   고위험: {high_count}개 (상위 33%)")
        print(f"   Critical: {critical_count}개 (상위 10%)")
        print(f"   =============================\n")
        
        # 재분류 적용
        for i, (company, data) in enumerate(sorted_companies):
            if i < low_count:
                new_level = 'low'
            elif i < low_count + medium_count:
                new_level = 'medium'
            elif i < low_count + medium_count + high_count - critical_count:
                new_level = 'high'
            else:
                new_level = 'critical'
            
            # 기존 데이터 업데이트
            risk_results[company]['risk_level'] = new_level
            risk_results[company]['risk_level_method'] = 'relative_classification'
            
            # 로그
            old_level = data.get('risk_level', 'unknown')
            score = data.get('overall_risk_score', 0.5)
            if old_level != new_level:
                print(f"   {company}: {old_level} → {new_level} (점수: {score:.2f})")
        
        return risk_results
    
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
