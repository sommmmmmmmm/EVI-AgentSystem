"""
Financial Analyzer Agent -      
  70%,   30%    
"""

from typing import Dict, Any, List
from models.citation import SourceManager, SourceType, Citation
from config.settings import config
from datetime import datetime
import json
import re
from tools.disclosure_routing_tools import DisclosureRouter  # 🆕 공시 라우팅 도구
from tools.llm_qualitative_analysis_tools import LLMQualitativeAnalyzer  # 🆕 LLM 정성 분석 도구 (실제 뉴스+공시 기반)
from tools.scoring_missing_data_tools import ScoringWithMissingData  # 🆕 결측값 처리 도구


class FinancialAnalyzerAgent:
    """
         
    -   70%:   , , ,   
    -   30%:   (, , ROE, PER )   
    -     
    """
    
    def __init__(self, web_search_tool, llm_tool, dart_tool):
        self.web_search_tool = web_search_tool
        self.llm_tool = llm_tool
        self.dart_tool = dart_tool
        
        #    
        self.qualitative_weight = config.financial_analysis_weights['qualitative']  # 0.7
        self.quantitative_weight = config.financial_analysis_weights['quantitative']  # 0.3
        
        # 🆕 새로운 도구들
        self.disclosure_router = DisclosureRouter()  # 공시 데이터 라우팅
        self.qualitative_analyzer = LLMQualitativeAnalyzer(llm_tool=llm_tool)  # 실제 데이터 기반 LLM 정성 분석
        self.scoring_tool = ScoringWithMissingData()  # 결측값 처리
    
    def analyze_financials(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
             
        
        Args:
            state:    (suppliers, market_trends, analyst_reports  )
            
        Returns:
               
        """
        
        try:
            print("      ...")
            
            # 1.     ( )
            target_companies = self._select_target_companies_from_suppliers(state)
            
            # 2.    (70%)
            qualitative_analysis = self._perform_qualitative_analysis(target_companies, state)
            
            # 3.    (30%)
            quantitative_analysis = self._perform_quantitative_analysis(target_companies, state)
            
            # 4.    
            investment_scores = self._calculate_investment_scores(
                qualitative_analysis, quantitative_analysis, target_companies
            )
            
            # 5.  
            structured_result = self._structure_financial_analysis_result(
                qualitative_analysis, quantitative_analysis, investment_scores, state
            )
            
            print(f"[OK]    - {len(target_companies)}  ")
            
            return structured_result
            
        except Exception as e:
            error_msg = f"FinancialAnalyzerAgent   : {str(e)}"
            print(f"[FAIL] {error_msg}")
            
            state['errors'].append({
                'agent': 'FinancialAnalyzerAgent',
                'error': error_msg,
                'timestamp': datetime.now().isoformat()
            })
            
            return {
                'financial_analysis': {},
                'analysis_metadata': {
                    'status': 'error',
                    'error_message': error_msg
                }
            }
    
    def _select_target_companies_from_suppliers(self, state: Dict[str, Any]) -> List[str]:
        """
              
        """
        target_companies = []
        
        #  1:  (  )
        suppliers = state.get('suppliers', [])
        supplier_companies = []
        for supplier in suppliers:
            company_name = supplier.get('company', '')
            confidence = supplier.get('overall_confidence', 0.0)
            if company_name:
                supplier_companies.append({
                    'name': company_name,
                    'confidence': confidence,
                    'source': 'supplier'
                })
        
        #  2: EV OEM  (  )
        ev_oems = config.ev_oems
        for oem in ev_oems:
            target_companies.append({
                'name': oem,
                'confidence': 1.0,  #  OEM  
                'source': 'oem'
            })
        
        #  3:    
        all_candidates = target_companies + supplier_companies
        
        #  4:   ( )
        seen = set()
        deduplicated = []
        for item in all_candidates:
            name = item['name']
            if name not in seen:
                seen.add(name)
                deduplicated.append(item)
        
        #  5:   ( )
        deduplicated.sort(key=lambda x: x['confidence'], reverse=True)
        
        #  6:   ( 30  )
        #    /     
        final_companies = [item['name'] for item in deduplicated[:30]]
        
        print(f"   :  {len(final_companies)} ")
        print(f"   OEM: {len([c for c in deduplicated if c['source'] == 'oem'])}")
        print(f"   : {len([c for c in deduplicated if c['source'] == 'supplier'])}")
        
        return final_companies
    
    def _perform_qualitative_analysis(self, companies: List[str], state: Dict[str, Any]) -> Dict[str, Any]:
        """
           (70% )
        -   , , ,   
        -    
        -   
        """
        qualitative_results = {}
        
        for company in companies:
            try:
                # 1.      ( )
                analyst_sentiment_analysis = self._analyze_analyst_sentiment(company, state)
                
                # 2.    
                market_trend_analysis = self._analyze_market_trend_impact(company, state)
                
                # 3.   
                supplier_relationship_analysis = self._analyze_supplier_relationships(company, state)
                
                # 4.   
                qualitative_score = self._calculate_qualitative_score(
                    analyst_sentiment_analysis, market_trend_analysis, supplier_relationship_analysis
                )
                
                qualitative_results[company] = {
                    'analyst_sentiment_analysis': analyst_sentiment_analysis,
                    'market_trend_analysis': market_trend_analysis,
                    'supplier_relationship_analysis': supplier_relationship_analysis,
                    'qualitative_score': qualitative_score,
                    'analysis_weight': self.qualitative_weight
                }
                
            except Exception as e:
                print(f"    ({company}): {e}")
                qualitative_results[company] = {
                    'qualitative_score': 0.0,
                    'error': str(e)
                }
        
        return qualitative_results
    
    def _analyze_market_trend_impact(self, company: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """
             
        """
        market_trends = state.get('market_trends', [])
        categorized_keywords = state.get('categorized_keywords', {})
        
        impact_score = 0.0
        trend_impacts = []
        
        for trend in market_trends:
            trend_category = trend.get('category', '')
            trend_keywords = trend.get('keywords', [])
            
            #    
            relevance_score = self._calculate_trend_relevance(company, trend_category, trend_keywords)
            
            if relevance_score > 0.3:
                trend_impact = {
                    'trend_id': trend.get('id', ''),
                    'trend_title': trend.get('title', ''),
                    'trend_category': trend_category,
                    'relevance_score': relevance_score,
                    'impact_description': f"{company} {trend_category}    "
                }
                trend_impacts.append(trend_impact)
                impact_score += relevance_score * trend.get('impact_score', 0.5)
        
        return {
            'overall_impact_score': min(impact_score, 1.0),
            'trend_impacts': trend_impacts,
            'analysis_method': 'market_trend_correlation'
        }
    
    def _calculate_trend_relevance(self, company: str, trend_category: str, trend_keywords: List[str]) -> float:
        """
            
        """
        company_lower = company.lower()
        relevance_score = 0.0
        
        #   
        category_scores = {
            '': 0.8,
            '': 0.7,
            '': 0.6,
            '': 0.9,
            '': 0.7,
            '': 0.5
        }
        
        base_score = category_scores.get(trend_category, 0.3)
        
        #    
        for keyword in trend_keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in company_lower:
                relevance_score += 0.2
            elif any(word in company_lower for word in keyword_lower.split()):
                relevance_score += 0.1
        
        return min(base_score + relevance_score, 1.0)
    
    def _analyze_supplier_relationships(self, company: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """
          
        """
        suppliers = state.get('suppliers', [])
        
        #      
        relevant_relationships = []
        relationship_score = 0.0
        
        for supplier in suppliers:
            if supplier.get('company') == company:
                relationships = supplier.get('relationships', [])
                for rel in relationships:
                    relationship_info = {
                        'oem': rel.get('oem', ''),
                        'relationship_type': rel.get('relationship_type', ''),
                        'confidence': rel.get('confidence', 0.0),
                        'analysis_method': rel.get('analysis_method', '')
                    }
                    relevant_relationships.append(relationship_info)
                    
                    #   
                    if rel.get('relationship_type') == '':
                        relationship_score += rel.get('confidence', 0.0) * 0.8
                    elif rel.get('relationship_type') == '':
                        relationship_score += rel.get('confidence', 0.0) * 0.6
        
        return {
            'relationship_score': min(relationship_score, 1.0),
            'relevant_relationships': relevant_relationships,
            'analysis_method': 'supplier_relationship_analysis'
        }
    
    def _analyze_technology_competitiveness(self, company: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """
          
        """
        categorized_keywords = state.get('categorized_keywords', {})
        tech_keywords = categorized_keywords.get('_', [])
        
        competitiveness_score = 0.0
        tech_strengths = []
        
        #     
        for keyword in tech_keywords:
            keyword_lower = keyword.lower()
            company_lower = company.lower()
            
            #    
            if (keyword_lower in company_lower or 
                any(word in company_lower for word in keyword_lower.split())):
                
                tech_strength = {
                    'technology': keyword,
                    'relevance_score': 0.7,
                    'description': f"{company} {keyword}  "
                }
                tech_strengths.append(tech_strength)
                competitiveness_score += 0.1
        
        return {
            'competitiveness_score': min(competitiveness_score, 1.0),
            'tech_strengths': tech_strengths,
            'analysis_method': 'technology_keyword_analysis'
        }
    
    def _calculate_qualitative_score(self, analyst_sentiment: Dict[str, Any], 
                                   market_analysis: Dict[str, Any], 
                                   supplier_analysis: Dict[str, Any]) -> float:
        """
           (  60%,   25%,   15%)
        """
        #    (60%)
        sentiment_score = analyst_sentiment.get('analysis_result', {}).get('sentiment_score', 0.5)
        
        #    (25%)
        market_score = market_analysis.get('overall_impact_score', 0.0)
        
        #    (15%)
        supplier_score = supplier_analysis.get('relationship_score', 0.0)
        
        #   
        qualitative_score = (
            sentiment_score * 0.6 +      #   60%
            market_score * 0.25 +        #   25%
            supplier_score * 0.15        #   15%
        )
        
        return qualitative_score
    
    def _perform_quantitative_analysis(self, companies: List[str], state: Dict[str, Any]) -> Dict[str, Any]:
        """  """
        quantitative_results = {}
        
        for company in companies:
            try:
                # DART API    
                financial_analysis = self.dart_tool.get_company_financial_analysis(company)
                
                #    
                if not financial_analysis.get('data_available', False):
                    print(f"   [WARNING] {company} -    ( )")
                    quantitative_results[company] = {
                        'quantitative_score': None,  # None 
                        'data_available': False,
                        'excluded': True,
                        'reason': financial_analysis.get('error', ' ')
                    }
                    continue
                
                #      
                financial_metrics_analysis = self._analyze_financial_metrics_from_dart(
                    financial_analysis
                )
                
                quantitative_score = self._calculate_quantitative_score(
                    financial_metrics_analysis
                )
                
                quantitative_results[company] = {
                    'financial_metrics_analysis': financial_metrics_analysis,
                    'quantitative_score': quantitative_score,
                    'analysis_weight': self.quantitative_weight,
                    'data_available': True,
                    'data_source': financial_analysis.get('data_source')
                }
                
            except Exception as e:
                print(f"    ({company}): {e}")
                quantitative_results[company] = {
                    'quantitative_score': None,
                    'data_available': False,
                    'excluded': True,
                    'error': str(e)
                }
        
        return quantitative_results
    
    def _analyze_financial_metrics_from_dart(self, financial_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """DART API    """
        financial_data = financial_analysis.get('financial_data', {})
        financial_ratios = financial_analysis.get('financial_ratios', {})
        
        #     
        score = 0.0
        
        # ROE (25%)
        roe = financial_ratios.get('roe', 0.0)
        if roe > 0.15:
            score += 0.25
        elif roe > 0.1:
            score += 0.2
        elif roe > 0.05:
            score += 0.1
        
        #  (25%)
        operating_margin = financial_ratios.get('operating_margin', 0.0)
        if operating_margin > 0.15:
            score += 0.25
        elif operating_margin > 0.1:
            score += 0.2
        elif operating_margin > 0.05:
            score += 0.1
        
        # ROA (20%)
        roa = financial_ratios.get('roa', 0.0)
        if roa > 0.1:
            score += 0.2
        elif roa > 0.05:
            score += 0.15
        elif roa > 0.02:
            score += 0.1
        
        #  (15%)
        debt_ratio = financial_ratios.get('debt_ratio', 0.0)
        if debt_ratio < 0.3:
            score += 0.15
        elif debt_ratio < 0.5:
            score += 0.1
        elif debt_ratio < 0.7:
            score += 0.05
        
        #  (15%)
        current_ratio = financial_ratios.get('current_ratio', 0.0)
        if current_ratio > 1.5:
            score += 0.15
        elif current_ratio > 1.2:
            score += 0.1
        elif current_ratio > 1.0:
            score += 0.05
        
        return {
            'financial_data': financial_data,
            'financial_ratios': financial_ratios,
            'financial_score': min(score, 1.0),
            'analysis_summary': f"ROE {roe*100:.1f}%,  {operating_margin*100:.1f}%, ROA {roa*100:.1f}%",
            'confidence_score': 0.9,
            'data_source': 'DART_API'
        }
    
    def _analyze_analyst_sentiment(self, company: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        정성 분석 - LLM 기반 실제 뉴스/공시 분석 (하드코딩 전문가 의견 대신)
        """
        try:
            print(f"    {company} LLM 정성 분석 중 (실제 뉴스+공시 기반)...")
            
            # 실제 데이터 기반 LLM 정성 분석
            news_articles = state.get('news_articles', [])
            disclosures = state.get('disclosure_data', [])
            market_trends = state.get('market_trends', [])
            suppliers = state.get('suppliers', [])
            
            # LLM 정성 분석 실행
            llm_analysis = self.qualitative_analyzer.analyze_company_qualitative(
                company_name=company,
                news_articles=news_articles,
                disclosures=disclosures,
                market_trends=market_trends,
                supplier_relationships=suppliers
            )
            
            if llm_analysis:
                # LLM 분석 점수를 0-1 스케일로 변환
                overall_rating = llm_analysis.get('overall_rating', 5.0)  # 1-10 scale
                sentiment_score = overall_rating / 10.0  # Convert to 0-1
                confidence = llm_analysis.get('confidence', 50) / 100.0  # Convert to 0-1
                
                # 센티먼트 결정
                if sentiment_score >= 0.7:
                    sentiment = "positive"
                elif sentiment_score <= 0.3:
                    sentiment = "negative"
                else:
                    sentiment = "neutral"
                
                data_sources = llm_analysis.get('data_sources', {})
                
                return {
                    'analysis_result': {
                        "overall_sentiment": sentiment,
                        "sentiment_score": sentiment_score,
                        "market_outlook": f"뉴스 {data_sources.get('news_count', 0)}건, 공시 {data_sources.get('disclosure_count', 0)}건 기반",
                        "investment_psychology": llm_analysis.get('competitive_position', ''),
                        "competitive_position": llm_analysis.get('competitive_position', ''),
                        "key_investment_points": llm_analysis.get('key_strengths', []),
                        "risk_factors": llm_analysis.get('key_risks', []),
                        "growth_drivers": llm_analysis.get('growth_drivers', []),
                        "confidence_score": confidence,
                        "recommendation": llm_analysis.get('recommendation', 'Hold')
                    },
                    'confidence_score': confidence,
                    'data_sources': data_sources,
                    'analysis_method': llm_analysis.get('method', 'LLM-based (real data)')
                }
            else:
                print(f"    [WARNING] {company} LLM 분석 실패, 기본값 사용")
                return {
                    'analysis_result': {
                        "overall_sentiment": "neutral",
                        "sentiment_score": 0.5,
                        "market_outlook": "데이터 부족",
                        "investment_psychology": "데이터 부족",
                        "competitive_position": "데이터 부족",
                        "key_investment_points": ["전문가 의견 데이터 부족"],
                        "risk_factors": ["데이터 부족"],
                        "confidence_score": 0.0
                    },
                    'confidence_score': 0.0,
                    'analysis_method': 'expert_opinion_analysis'
                }
            
        except Exception as e:
            print(f"    [ERROR] 분석가 센티먼트 분석 실패 ({company}): {e}")
            return {
                'analysis_result': {
                    "overall_sentiment": "error",
                    "sentiment_score": 0.5,
                    "market_outlook": "분석 실패",
                    "investment_psychology": "분석 실패",
                    "competitive_position": "분석 실패",
                    "key_investment_points": ["분석 실패"],
                    "risk_factors": ["분석 실패"],
                    "confidence_score": 0.0
                },
                'confidence_score': 0.0
            }
    
    def _analyze_financial_metrics(self, company: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        DART API      (, , ROE, PER )
        """
        try:
            # DART API    
            financial_analysis = self.dart_tool.get_company_financial_analysis(company)

            #    
            if not financial_analysis.get('data_available', False):
                print(f"   [WARNING] {company}:    -  ")
                return {
                    'financial_data': {},
                    'financial_ratios': {},
                    'financial_score': 0.0,
                    'analysis_summary': "  ",
                    'confidence_score': 0.0,
                    'data_source': 'NONE',
                    'excluded_from_analysis': True,
                    'error': financial_analysis.get('error', ' ')
                }

            financial_data = financial_analysis.get('financial_data', {})
            financial_ratios = financial_analysis.get('financial_ratios', {})

            #     
            score = 0.0

            # ROE (25%)
            roe = financial_ratios.get('roe', 0.0)
            if roe > 0.15:
                score += 0.25
            elif roe > 0.1:
                score += 0.2
            elif roe > 0.05:
                score += 0.1

            #  (25%)
            operating_margin = financial_ratios.get('operating_margin', 0.0)
            if operating_margin > 0.15:
                score += 0.25
            elif operating_margin > 0.1:
                score += 0.2
            elif operating_margin > 0.05:
                score += 0.1

            # ROA (20%)
            roa = financial_ratios.get('roa', 0.0)
            if roa > 0.1:
                score += 0.2
            elif roa > 0.05:
                score += 0.15
            elif roa > 0.02:
                score += 0.1

            #  (15%)
            debt_ratio = financial_ratios.get('debt_ratio', 0.0)
            if debt_ratio < 0.3:
                score += 0.15
            elif debt_ratio < 0.5:
                score += 0.1
            elif debt_ratio < 0.7:
                score += 0.05

            #  (15%)
            current_ratio = financial_ratios.get('current_ratio', 0.0)
            if current_ratio > 1.5:
                score += 0.15
            elif current_ratio > 1.2:
                score += 0.1
            elif current_ratio > 1.0:
                score += 0.05

            return {
                'financial_data': financial_data,
                'financial_ratios': financial_ratios,
                'financial_score': min(score, 1.0),
                'analysis_summary': f"ROE {roe*100:.1f}%,  {operating_margin*100:.1f}%, ROA {roa*100:.1f}%",
                'confidence_score': 0.9,  # DART API   
                'data_source': 'DART_API'
            }
            
        except Exception as e:
            print(f"DART API     ({company}): {e}")
            return {
                'financial_data': {},
                'financial_ratios': {},
                'financial_score': 0.0,
                'analysis_summary': " ",
                'confidence_score': 0.0,
                'data_source': 'ERROR',
                'excluded_from_analysis': True,
                'error': str(e)
            }
    
        """
           
        """
        analyst_reports = state.get('analyst_reports', [])
        
        relevant_reports = []
        analyst_score = 0.0
        
        for report in analyst_reports:
            report_content = report.get('content', '').lower()
            company_lower = company.lower()
            
            #    
            if company_lower in report_content:
                report_info = {
                    'firm': report.get('firm', ''),
                    'title': report.get('title', ''),
                    'content_snippet': report_content[:200],
                    'relevance_score': 0.8
                }
                relevant_reports.append(report_info)
                analyst_score += 0.2
        
        return {
            'analyst_score': min(analyst_score, 1.0),
            'relevant_reports': relevant_reports,
            'analysis_method': 'analyst_report_analysis'
        }
    
    def _analyze_disclosure_data(self, company: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """
          
        """
        disclosure_data = state.get('disclosure_data', [])
        
        relevant_disclosures = []
        disclosure_score = 0.0
        
        for disclosure in disclosure_data:
            disclosure_content = disclosure.get('content', '').lower()
            company_lower = company.lower()
            
            #    
            if company_lower in disclosure_content:
                disclosure_info = {
                    'title': disclosure.get('title', ''),
                    'content_snippet': disclosure_content[:200],
                    'relevance_score': 0.7
                }
                relevant_disclosures.append(disclosure_info)
                disclosure_score += 0.15
        
        return {
            'disclosure_score': min(disclosure_score, 1.0),
            'relevant_disclosures': relevant_disclosures,
            'analysis_method': 'disclosure_analysis'
        }
    
    def _calculate_quantitative_score(self, financial_metrics: Dict[str, Any]) -> float:
        """
           (  )
        """
        return financial_metrics.get('financial_score', 0.0)
    
    def _calculate_investment_scores(self, qualitative_analysis: Dict[str, Any], 
                                   quantitative_analysis: Dict[str, Any], 
                                   companies: List[str]) -> Dict[str, Any]:
        """    (   )"""
        investment_scores = {}
        
        for company in companies:
            qual_data = qualitative_analysis.get(company, {})
            quant_data = quantitative_analysis.get(company, {})
            
            #    
            if not quant_data.get('data_available', False):
                print(f"   [WARNING] {company} -    (  )")
                continue
            
            qualitative_score = qual_data.get('qualitative_score', 0.0)
            quantitative_score = quant_data.get('quantitative_score', 0.0)
            
            #   
            final_score = (
                qualitative_score * self.qualitative_weight +
                quantitative_score * self.quantitative_weight
            )
            
            investment_scores[company] = {
                'final_score': final_score,
                'qualitative_score': qualitative_score,
                'quantitative_score': quantitative_score,
                'data_source': quant_data.get('data_source', 'UNKNOWN')
            }
        
        return investment_scores
    
    def _structure_financial_analysis_result(self, qualitative_analysis: Dict[str, Any], 
                                           quantitative_analysis: Dict[str, Any], 
                                           investment_scores: Dict[str, Any], 
                                           state: Dict[str, Any]) -> Dict[str, Any]:
        """
           
        """
        #    
        top_picks = sorted(investment_scores.items(), 
                          key=lambda x: x[1]['final_score'], reverse=True)[:10]
        
        return {
            'financial_analysis': {
                'investment_scores': investment_scores,
                'top_picks': [
                    {
                        'company': company, 
                        'final_score': data['final_score'],
                        'qualitative_score': data['qualitative_score'],
                        'quantitative_score': data['quantitative_score']
                    } 
                    for company, data in top_picks
                ],
                'qualitative_analysis': qualitative_analysis,
                'quantitative_analysis': quantitative_analysis,
                'analysis_weights': {
                    'qualitative': self.qualitative_weight,
                    'quantitative': self.quantitative_weight
                }
            },
            'analysis_metadata': {
                'status': 'completed',
                'timestamp': datetime.now().isoformat(),
                'total_companies_analyzed': len(investment_scores),
                'top_pick_count': len(top_picks),
                'analysis_method': 'hybrid_qualitative_quantitative'
            }
        }
    
