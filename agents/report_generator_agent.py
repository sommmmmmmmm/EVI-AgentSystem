"""
Report Generator Agent -       
 ,  ,  ,  ,        
          
"""

from typing import Dict, Any, List
from models.citation import SourceManager, SourceType, Citation
from config.settings import config, INVESTMENT_STRATEGY_CONFIG
from datetime import datetime
import json
import re


class ReportGeneratorAgent:
    """
          
    -  ,  ,  ,  ,   
    -      
    -           
    -    (3-12) 
    """
    
    def __init__(self, llm_tool):
        self.llm_tool = llm_tool
        
        #   
        self.report_templates = self._initialize_report_templates()
        
        #   
        self.target_audience = INVESTMENT_STRATEGY_CONFIG['target_audience']
    
    def generate_report(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
             
        
        Args:
            state:      
            
        Returns:
              
        """
        
        try:
            print("       ...")
            
            # 1.   
            report_structure = self._design_report_structure(state)
            
            # 2.    
            report_sections = self._generate_report_sections(state, report_structure)
            
            # 3.   
            final_report = self._integrate_sources_into_report(report_sections, state)
            
            # 4.   
            glossary = self._generate_glossary(state)
            
            # 5.   
            investor_guide = self._generate_investor_guide(state)
            
            print("[OK]    ")
            
            return {
                'final_report': final_report,
                'glossary': glossary,
                'investor_guide': investor_guide,
                'report_metadata': {
                    'status': 'completed',
                    'timestamp': datetime.now().isoformat(),
                    'total_sections': len(final_report),
                    'total_sources': len(state.get('source_manager', SourceManager()).citations),
                    'target_audience': self.target_audience,
                    'investment_horizon': INVESTMENT_STRATEGY_CONFIG['investment_horizon']
                }
            }
            
        except Exception as e:
            error_msg = f"ReportGeneratorAgent    : {str(e)}"
            print(f"[FAIL] {error_msg}")
            
            if 'errors' in state:
                state['errors'].append({
                    'agent': 'ReportGeneratorAgent',
                    'error': error_msg,
                    'timestamp': datetime.now().isoformat()
                })
            
            return {
                'final_report': {},
                'glossary': {},
                'investor_guide': {},
                'report_metadata': {
                    'status': 'error',
                    'error_message': error_msg
                }
            }
    
    def _initialize_report_templates(self) -> Dict[str, Any]:
        """
          
        """
        return {
            'executive_summary': {
                'title': 'Executive Summary',
                'description': ' ',
                'key_points': [' ', ' ', ' ', ' ']
            },
            'ev_market_trends': {
                'title': 'EV Market Trends',
                'description': '     ',
                'key_points': [' ', ' ', ' ', ' ']
            },
            'supply_chain_analysis': {
                'title': 'Supply Chain Analysis',
                'description': '    ',
                'key_points': [' ', ' ', '  ', ' ']
            },
            'financial_performance': {
                'title': 'Financial Performance',
                'description': '     ',
                'key_points': [' ', ' ', '', '']
            },
            'risk_assessment': {
                'title': 'Risk Assessment',
                'description': '     ',
                'key_points': [' ', ' ', ' ', ' ']
            },
            'investment_strategy': {
                'title': 'Investment Strategy',
                'description': '    ',
                'key_points': [' ', ' ', ' ', ' ']
            },
            'glossary': {
                'title': 'Glossary',
                'description': '    ',
                'key_points': [' ', ' ', ' ', ' ']
            },
            'risk_disclaimer': {
                'title': 'Risk Disclaimer',
                'description': '     ',
                'key_points': [' ', ' ', ' ', ' ']
            },
            'references_appendix': {
                'title': 'References & Appendix',
                'description': '  ',
                'key_points': [' ', ' ', ' ', ' ']
            }
        }
    
    def _design_report_structure(self, state: Dict[str, Any]) -> Dict[str, str]:
        """
          
        """
        structure = {}
        
        for section_key, template in self.report_templates.items():
            structure[section_key] = template['description']
        
        return structure
    
    def _generate_report_sections(self, state: Dict[str, Any], report_structure: Dict[str, str]) -> Dict[str, str]:
        """
        보고서 9섹션 생성 - 줄글로 내용 채우기
        """
        report_sections = {}
        
        # 1. Executive Summary - 핵심 투자 하이라이트와 주요 추천사항
        report_sections['executive_summary'] = self._generate_executive_summary(state)
        
        # 2. EV Market Trends - 전기차 시장 동향과 트렌드 분석
        report_sections['ev_market_trends'] = self._generate_ev_market_trends(state)
        
        # 3. Supply Chain Analysis - 공급망 구조와 핵심 공급업체 분석
        report_sections['supply_chain_analysis'] = self._generate_supply_chain_analysis(state)
        
        # 4. Financial Performance - 재무 성과와 투자 매력도 분석
        report_sections['financial_performance'] = self._generate_financial_performance(state)
        
        # 5. Risk Assessment - 리스크 평가와 위험 요소 분석
        report_sections['risk_assessment'] = self._generate_risk_assessment(state)
        
        # 6. Investment Strategy - 투자 전략과 포트폴리오 구성
        report_sections['investment_strategy'] = self._generate_investment_strategy(state)
        
        # 7. Glossary - 전문 용어 사전
        report_sections['glossary'] = self._generate_glossary_section(state)
        
        # 8. Risk Disclaimer - 투자 위험 고지사항
        report_sections['risk_disclaimer'] = self._generate_risk_disclaimer(state)
        
        # 9. References & Appendix - 참고문헌과 부록
        report_sections['references_appendix'] = self._generate_references_appendix(state)
        
        return report_sections
    
    def _generate_executive_summary(self, state: Dict[str, Any]) -> str:
        """
        Executive Summary 생성 - 핵심 투자 하이라이트와 주요 추천사항을 줄글로 작성
        """
        # 데이터 추출
        market_trends = state.get('market_trends', [])
        financial_analysis = state.get('financial_analysis', {})
        investment_strategy = state.get('investment_strategy', {})
        risk_assessment = state.get('risk_assessment', {})
        suppliers = state.get('suppliers', [])
        
        # 주요 투자 기회
        top_picks = financial_analysis.get('top_picks', [])
        top_companies = [pick.get('company', '') for pick in top_picks[:3]]
        
        # 시장 트렌드
        key_trends = [trend.get('title', '') for trend in market_trends[:3]]
        
        # 투자 전략
        portfolio_strategy = investment_strategy.get('portfolio_strategy', {})
        strategy_name = portfolio_strategy.get('strategy_name', '균형형 포트폴리오')
        
        # 리스크 관리
        risk_grades = risk_assessment.get('risk_grades', {})
        low_risk_count = len([g for g in risk_grades.values() if isinstance(g, dict) and g.get('grade') == 'Low'])
        
        # 공급망 분석
        supplier_count = len(suppliers)
        
        summary = f"""# 1. Executive Summary

## 핵심 투자 하이라이트

본 보고서는 전기차(EV) 산업의 밸류체인을 종합적으로 분석하여 개인 투자자에게 중장기 투자 기회를 제시합니다. 분석 결과, {', '.join(top_companies) if top_companies else '주요 EV 관련 기업들'}이 핵심 투자 대상으로 선정되었으며, {strategy_name} 전략을 통해 {INVESTMENT_STRATEGY_CONFIG.get('investment_horizon', '3-12개월')} 투자 기간 동안 안정적인 수익을 추구할 수 있습니다.

## 시장 동향 요약

전기차 시장은 지속적인 성장세를 보이고 있으며, {', '.join(key_trends) if key_trends else '배터리 기술 발전, 충전 인프라 확충, 정부 정책 지원'} 등의 주요 트렌드가 시장 확장을 견인하고 있습니다. 특히 중국과 유럽을 중심으로 한 글로벌 시장의 성장이 두드러지며, 한국 기업들의 기술 경쟁력 확보를 통한 시장 점유율 확대가 기대됩니다.

## 리스크 관리 전략

분석 결과 {low_risk_count}개의 저위험 기업이 식별되었으며, 이를 바탕으로 분산투자 전략을 적용하여 포트폴리오의 안정성을 확보했습니다. 원자재 가격 변동성, 정부 정책 변화, 기술 개발 속도, 경쟁 심화 등의 주요 리스크 요인에 대해서는 지속적인 모니터링을 통해 대응할 계획입니다.

## 공급망 분석 결과

총 {supplier_count}개의 공급업체를 분석한 결과, 전기차 부품 공급망의 핵심 기업들이 명확히 식별되었습니다. 특히 배터리, 모터, 전자제어장치 등 핵심 부품 분야에서 강력한 경쟁력을 보유한 기업들이 투자 매력도가 높은 것으로 평가되었습니다.

## 투자 권고사항

1. **핵심 부품 기업 집중 투자**: 전기차 밸류체인의 핵심 부품을 담당하는 기업들에 집중 투자하여 시장 성장의 혜택을 최대화합니다.

2. **중장기 투자 관점**: 3-12개월의 투자 기간을 설정하여 단기 변동성에 흔들리지 않고 장기적 가치 창출에 집중합니다.

3. **리스크 관리**: 고위험 기업을 배제하고 분산투자를 통해 포트폴리오의 안정성을 확보합니다.

4. **지속적 모니터링**: 시장 트렌드와 공급업체 관계 변화를 지속적으로 추적하여 투자 전략을 조정합니다.

## 주요 위험 요소

원자재 가격 변동성, 정부 정책 변화, 기술 개발 속도, 경쟁 심화 등의 요인들이 투자 성과에 영향을 미칠 수 있으므로, 이러한 리스크 요인들을 면밀히 관찰하고 적절한 대응 방안을 마련해야 합니다.

## 기대 성과

시장 트렌드, 공급망 관계, 재무 성과, 리스크 평가를 종합적으로 분석한 결과를 바탕으로, 성장하는 전기차 시장에 노출을 원하는 개인 투자자들에게 실행 가능한 투자 전략을 제시합니다. 이를 통해 안정적이면서도 수익성 있는 투자 기회를 제공할 것으로 기대됩니다.

---
*본 보고서는 참고용으로만 사용되어야 하며, 투자 결정은 투자자 본인의 판단과 책임 하에 이루어져야 합니다.*
"""
        
        return summary
    
    def _generate_ev_market_trends(self, state: Dict[str, Any]) -> str:
        """
        EV Market Trends 생성 - 전기차 시장 동향과 트렌드 분석을 줄글로 작성
        """
        market_trends = state.get('market_trends', [])
        categorized_keywords = state.get('categorized_keywords', {})
        news_articles = state.get('news_articles', [])
        
        # 주요 트렌드 분석
        trend_analysis = ""
        for i, trend in enumerate(market_trends[:5], 1):
            trend_analysis += f"""
### {i}. {trend.get('title', 'Trend')}
- **Category**: {trend.get('category', 'General')}
- **Impact Score**: {trend.get('impact_score', 0):.1f}/1.0
- **Description**: {trend.get('description', '')}
- **Keywords**: {', '.join(trend.get('keywords', [])[:5])}
"""
        
        # 키워드 분석
        keyword_analysis = ""
        for category, keywords in categorized_keywords.items():
            if keywords:
                keyword_analysis += f"""
#### {category.replace('_', ' ')}
Top keywords: {', '.join(keywords[:8])} ({len(keywords)} total identified)
"""
        
        # 뉴스 분석
        news_summary = f"Total {len(news_articles)} news articles analyzed from recent 7 days"
        
        analysis = f"""# 2. EV Market Trends

## 시장 동향 분석

전기차 시장은 현재 급속한 성장 단계에 있으며, 여러 핵심 트렌드가 시장의 발전을 견인하고 있습니다. 최근 7일간 분석된 {len(news_articles)}개의 뉴스 기사를 바탕으로 한 분석 결과, 시장은 지속적인 성장 모멘텀을 보이고 있으며 배터리 기술과 충전 인프라가 주요 동력으로 작용하고 있습니다.

{trend_analysis if trend_analysis else "분석 기간 동안 주요 트렌드가 식별되지 않았습니다."}

## 키워드 분석

시장 동향을 더욱 정확히 파악하기 위해 뉴스 기사에서 추출된 키워드를 카테고리별로 분석한 결과, 다음과 같은 패턴을 확인할 수 있습니다:

{keyword_analysis if keyword_analysis else "키워드 분류 정보를 사용할 수 없습니다."}

## 뉴스 분석 결과

{news_summary}

### 뉴스에서 도출된 주요 인사이트
- 시장이 지속적인 성장 모멘텀을 보이고 있음
- 배터리 기술과 충전 인프라가 핵심 동력으로 작용
- 주요 시장에서 정부 정책 지원이 강력하게 유지됨
- 핵심 인구층에서 소비자 채택이 가속화되고 있음

## 시장 전망

전기차 시장은 배터리 기술과 충전 인프라 개발을 핵심 동력으로 하여 지속적인 성장을 보이고 있습니다. 정부의 친환경 정책과 소비자의 환경 인식 증가가 시장 성장을 뒷받침하고 있으며, 특히 중국과 유럽을 중심으로 한 글로벌 시장의 성장이 두드러집니다.

### 주요 성장 동력
1. **기술 혁신**: 배터리 성능 향상과 충전 속도 개선
2. **정책 지원**: 정부 보조금 및 인센티브 확대
3. **인프라 확충**: 충전소 네트워크 성장
4. **소비자 수용성**: 환경 인식 증가와 경제성 개선

### 시장 리스크
1. **원자재 가격**: 배터리 원자재 가격 변동성 (리튬, 니켈 등)
2. **경쟁 심화**: 신규 진입자들의 경쟁 압박 증가
3. **기술 변화**: 기존 기술에 영향을 미치는 신기술 출현 리스크
4. **정책 변화**: 정부 정책 수정 가능성

## 결론

전기차 시장은 기술 혁신, 정책 지원, 인프라 확충, 소비자 수용성 향상 등의 요인들이 상호 작용하며 지속적인 성장을 이어가고 있습니다. 다만 원자재 가격 변동성, 경쟁 심화, 기술 변화, 정책 변화 등의 리스크 요인들도 존재하므로, 투자 시 이러한 요소들을 종합적으로 고려해야 합니다.
"""
        
        return analysis
    
    def _generate_supply_chain_analysis(self, state: Dict[str, Any]) -> str:
        """
        Supply Chain Analysis 생성 - 공급망 구조와 핵심 공급업체 분석을 줄글로 작성
        """
        suppliers = state.get('suppliers', [])
        
        # 공급업체 분석
        supplier_analysis = ""
        for i, supplier in enumerate(suppliers[:10], 1):
            company = supplier.get('company', '')
            category = supplier.get('category', '')
            products = supplier.get('products', [])
            relationships = supplier.get('relationships', [])
            confidence = supplier.get('overall_confidence', 0.0)
            source = supplier.get('source', 'unknown')
            
            supplier_analysis += f"""
### {i}. {company}
- **Category**: {category}
- **Products**: {', '.join(products[:3])}
- **OEM Relationships**: {len(relationships)} identified
- **Confidence Score**: {confidence:.2f}/1.0
- **Discovery Source**: {'Database' if source == 'database' else 'Web Search (New Discovery)'}
"""
            
            if relationships:
                rel_summary = ', '.join([rel.get('oem', '') for rel in relationships[:3]])
                supplier_analysis += f"- **Key Partners**: {rel_summary}\n"
        
        # 신규 발견 기업 수
        new_discoveries = len([s for s in suppliers if s.get('source') == 'web_search'])
        
        analysis = f"""# 3. Supply Chain Analysis

## 공급망 구조 개요

전기차 공급망은 복잡하고 다층적인 구조를 가지고 있으며, 각 계층별로 핵심 역할을 담당하는 기업들이 존재합니다. 본 분석을 통해 총 **{len(suppliers)}개의 공급업체**를 식별했으며, 이 중 **{new_discoveries}개는 신규 발견된 기업**입니다.

{supplier_analysis if supplier_analysis else "분석에서 공급업체가 식별되지 않았습니다."}

## 공급망 계층 구조

전기차 공급망은 다음과 같은 계층 구조로 구성되어 있습니다:

### 1차 공급업체 (Tier 1 Suppliers)
- **배터리**: LG에너지솔루션, 삼성SDI, SK온, CATL
- **모터**: 현대모비스, LG마그나
- **충전**: LS전선, 효성

### 2차 공급업체 (Tier 2 Suppliers)
- **소재**: POSCO케미컬, LG화학
- **부품**: 각종 전자 및 기계 부품 공급업체

### 완성차 제조사 (OEMs)
- **국내**: 현대자동차, 기아
- **해외**: 테슬라, BMW, 폭스바겐, GM, 포드

## 핵심 공급업체 분석

공급망 분석을 통해 식별된 주요 공급업체들은 각각의 전문 분야에서 핵심 역할을 담당하고 있습니다. 특히 배터리, 모터, 전자제어장치 등 전기차의 핵심 부품을 담당하는 기업들이 높은 투자 매력도를 보이고 있습니다.

## 투자 기회 분석

### 신규 발견 기업
공급망 분석을 통해 다음과 같은 투자 기회를 식별했습니다:

1. **안정적 공급업체**: 주요 OEM과 강력한 공급 관계를 맺고 있는 기업들
2. **성장 잠재력**: EV 시장 성장의 혜택을 받을 것으로 예상되는 기업들
3. **기술 리더십**: 핵심 기술 우위를 보유한 공급업체들

### 공급업체 투자 매력도
- **높음**: 주요 OEM과 직접 공급 관계를 맺고 있는 기업
- **중간**: 간접 공급 관계 또는 성장 잠재력을 보유한 기업
- **낮음**: 공급 관계가 불분명하거나 경쟁력이 부족한 기업

## 공급망 리스크 분석

공급망의 안정성을 위해 다음과 같은 리스크 요인들을 고려해야 합니다:

1. **단일 공급업체 의존도**: 특정 공급업체에 과도하게 의존하는 경우
2. **지리적 집중도**: 특정 지역에 공급업체가 집중된 경우
3. **기술 의존도**: 특정 기술에 과도하게 의존하는 경우
4. **정치적 리스크**: 국제 관계나 정책 변화에 따른 공급 중단 위험

## 결론

전기차 공급망은 복잡하지만 체계적인 구조를 가지고 있으며, 각 계층별로 핵심 역할을 담당하는 기업들이 명확히 식별되었습니다. 투자 시에는 공급업체의 기술력, OEM과의 관계, 시장 지위 등을 종합적으로 고려하여 안정적이면서도 성장 잠재력이 높은 기업들을 선별하는 것이 중요합니다.
"""
        
        return analysis
    
    def _generate_financial_performance(self, state: Dict[str, Any]) -> str:
        """
        Financial Performance 생성 - 재무 성과와 투자 매력도 분석을 줄글로 작성
        """
        financial_analysis = state.get('financial_analysis', {})
        investment_scores = financial_analysis.get('investment_scores', {})
        top_picks = financial_analysis.get('top_picks', [])
        
        #   
        top_analysis = ""
        for i, pick in enumerate(top_picks[:8], 1):
            company = pick.get('company', '')
            final_score = pick.get('final_score', 0.0)
            qualitative_score = pick.get('qualitative_score', 0.0)
            quantitative_score = pick.get('quantitative_score', 0.0)
            
            #   
            quant_data = financial_analysis.get('quantitative_analysis', {}).get(company, {})
            data_source = quant_data.get('financial_metrics_analysis', {}).get('data_source', 'UNKNOWN')
            
            top_analysis += f"""
### {i}. {company}
- **Total Score**: {final_score:.2f}/1.0
- **Qualitative Score**: {qualitative_score:.2f} (70% weight)
- **Quantitative Score**: {quantitative_score:.2f} (30% weight)
- **Investment Appeal**: {'High' if final_score > 0.8 else 'Medium' if final_score > 0.6 else 'Low'}
- **Data Source**: {data_source}
"""
        
        analysis = f"""# 4. Financial Performance

## 재무 성과 분석 개요

본 섹션에서는 전기차 관련 기업들의 재무 성과를 종합적으로 분석하여 투자 매력도를 평가했습니다. 정량적 분석(30%)과 정성적 분석(70%)을 결합하여 각 기업의 투자 가치를 객관적으로 평가했습니다.

### 분석 방법론
- **정성적 분석 (70%)**: 시장 트렌드, 공급업체 관계, 기술 경쟁력
- **정량적 분석 (30%)**: DART 재무 데이터, 증권사 분석가 리포트

### 주요 투자 추천 기업

{top_analysis if top_analysis else "재무 분석 결과를 사용할 수 없습니다."}

## 재무 지표 분석

### 핵심 평가 기준
1. **성장성**: 매출 증가율, 영업이익률
2. **수익성**: ROE, ROA
3. **안정성**: 부채비율, 유동비율
4. **밸류에이션**: PER, PBR (가능한 경우)

### 투자 점수 계산 방법
- **시장 트렌드 영향 (40%)**: EV 시장 트렌드와의 상관관계
- **공급업체 관계 (40%)**: 주요 OEM과의 공급 관계
- **재무 건전성 (20%)**: DART 기반 재무 지표

## 투자 권고사항

### 권장 투자 배분
- **핵심 종목**: 포트폴리오의 60-70%
- **지원 종목**: 포트폴리오의 20-30%
- **현금**: 포트폴리오의 10-20%

### 투자 기간
- **단기 (3-6개월)**: 시장 변동성 활용
- **중기 (6-12개월)**: 성장 스토리 실현
- **장기 (12개월 이상)**: 구조적 성장 기대

### 중요 사항
- DART 데이터가 있는 기업의 신뢰도가 높음
- 신규 발견 기업은 추가 실사 필요
- 재무 성과 정기적 모니터링 권장

## 결론

재무 성과 분석을 통해 전기차 관련 기업들의 투자 매력도를 객관적으로 평가했습니다. 투자 시에는 단순히 재무 지표만을 고려하는 것이 아니라, 시장 동향, 기술 경쟁력, 공급망 지위 등을 종합적으로 고려하여 안정적이면서도 성장 잠재력이 높은 기업들을 선별하는 것이 중요합니다.
"""
        
        return analysis
    
    def _generate_risk_assessment(self, state: Dict[str, Any]) -> str:
        """
        Risk Assessment 생성 - 리스크 평가와 위험 요소 분석을 줄글로 작성
        """
        risk_assessment = state.get('risk_assessment', {})
        risk_grades = risk_assessment.get('risk_grades', {})
        high_risk_companies = risk_assessment.get('high_risk_companies', [])
        low_risk_companies = risk_assessment.get('low_risk_companies', [])
        
        #   
        risk_analysis = ""
        for company, grade_info in list(risk_grades.items())[:10]:
            grade = grade_info.get('grade', 'Medium')
            grade_korean = grade_info.get('grade_korean', '')
            score = grade_info.get('score', 0.0)
            
            risk_analysis += f"""
### {company}
- **Risk Grade**: {grade} ({grade_korean})
- **Risk Score**: {score:.2f}/1.0
- **Assessment**: {grade_info.get('description', 'Standard risk profile')}
"""
        
        analysis = f"""
# 5. Risk Assessment

## [WARNING] Risk Grade Analysis

{risk_analysis if risk_analysis else "No risk analysis results available."}

##  Risk Distribution

### High Risk Companies ({len(high_risk_companies)})
{', '.join(high_risk_companies) if high_risk_companies else 'None identified'}

### Low Risk Companies ({len(low_risk_companies)})
{', '.join(low_risk_companies) if low_risk_companies else 'None identified'}

##  Key Risk Factors

### Quantitative Risk (80% weight)
1. **Financial Risk**
   - Debt ratio: Risk if >50%
   - Current ratio: Risk if <1.0
   - ROE: Risk if <10%
   - Operating margin: Risk if <5%

2. **Market Risk**
   - Beta: Risk if >1.2 (high volatility)
   - Volatility: Risk if >30%
   - Market cap: Risk if <100B KRW

### Qualitative Risk (20% weight)
1. **Governance Risk**
   - Management stability concerns
   - Board composition imbalance
   - Audit quality issues

2. **Legal Risk**
   - Litigation exposure
   - Regulatory compliance issues

##  Risk Mitigation Strategies

### Portfolio Level
1. **Diversification**: Sector and company diversification
2. **Risk Limits**: Limit high-risk company exposure
3. **Cash Reserves**: Maintain liquidity

### Individual Stock Level
1. **Regular Monitoring**: Track financial metrics
2. **Event Tracking**: Monitor major disclosures and news
3. **Stop Loss**: Set clear stop-loss criteria

##  Monitoring Points

1. **Major OEM Disclosures**: Track supply relationship changes
2. **Battery Raw Material Prices**: Monitor raw material price fluctuations
3. **Government Policy Changes**: Watch for eco-friendly policy modifications
4. **Competitor Actions**: Analyze competitor strategies and performance
"""
        
        return analysis
    
    def _generate_investment_strategy(self, state: Dict[str, Any]) -> str:
        """
        Investment Strategy 생성 - 투자 전략과 포트폴리오 구성을 줄글로 작성
        """
        investment_strategy = state.get('investment_strategy', {})
        portfolio_strategy = investment_strategy.get('portfolio_strategy', {})
        investment_opportunities = investment_strategy.get('investment_opportunities', [])
        risk_management = investment_strategy.get('risk_management', {})
        timing_strategy = investment_strategy.get('timing_strategy', {})
        
        #  
        portfolio_analysis = ""
        recommended_companies = portfolio_strategy.get('recommended_companies', [])
        
        for i, company_info in enumerate(recommended_companies[:8], 1):
            company = company_info.get('company', '')
            weight = company_info.get('weight', 0.0)
            rationale = company_info.get('rationale', '')
            time_horizon = company_info.get('time_horizon', '')
            
            portfolio_analysis += f"""
### {i}. {company}
- **Target Weight**: {weight:.1%}
- **Investment Period**: {time_horizon}
- **Rationale**: {rationale}
"""
        
        #   
        opportunities_analysis = ""
        for i, opp in enumerate(investment_opportunities[:5], 1):
            company = opp.get('company', '')
            opportunity_type = opp.get('opportunity_type', '')
            opportunity_score = opp.get('opportunity_score', 0.0)
            
            opportunities_analysis += f"""
{i}. **{company}**: {opportunity_type} (Score: {opportunity_score:.2f})
"""
        
        analysis = f"""
# 6. Investment Strategy

##  Portfolio Strategy

### Strategy Overview
- **Strategy Name**: {portfolio_strategy.get('strategy_name', 'Balanced Strategy')}
- **Description**: {portfolio_strategy.get('strategy_description', '')}
- **Expected Return**: {portfolio_strategy.get('total_investment_score', 0.0):.2f}

### Recommended Portfolio Composition

{portfolio_analysis if portfolio_analysis else "No portfolio recommendations available."}

### Asset Allocation
- **Growth Stocks**: {portfolio_strategy.get('target_allocation', {}).get('growth_stocks', 0.5):.1%}
- **Value Stocks**: {portfolio_strategy.get('target_allocation', {}).get('value_stocks', 0.4):.1%}
- **Cash**: {portfolio_strategy.get('target_allocation', {}).get('cash', 0.1):.1%}

##  Investment Opportunities

{opportunities_analysis if opportunities_analysis else "No specific opportunities identified."}

## ⏰ Investment Timing

### Entry Strategy
- **Approach**: {timing_strategy.get('entry_strategy', 'Gradual accumulation')}
- **Market Outlook**: {timing_strategy.get('market_outlook', 'Positive')}

### Timing Factors
{chr(10).join([f"- {factor}" for factor in timing_strategy.get('timing_factors', [])]) if timing_strategy.get('timing_factors') else "- Monitor EV market growth rate"}

##  Risk Management

### Risk Management Strategy
- **Risk Tolerance**: {risk_management.get('risk_tolerance', 'Medium')}
- **Diversification**: {risk_management.get('diversification_strategy', 'Sector diversification')}

### Risk Controls
{chr(10).join([f"- {control.get('description', '')}" for control in risk_management.get('risk_controls', [])]) if risk_management.get('risk_controls') else "- Exclude high-risk companies"}

### Monitoring Points
{chr(10).join([f"- {point}" for point in risk_management.get('monitoring_points', [])]) if risk_management.get('monitoring_points') else "- Monitor major OEM disclosures"}

##  Investment Execution Guide

### Phase 1: Portfolio Construction
1. Buy recommended stocks according to target weights
2. Use gradual accumulation to manage average cost
3. Maintain cash reserves for opportunities

### Phase 2: Ongoing Monitoring
1. Monthly portfolio rebalancing review
2. Quarterly stock performance evaluation
3. Semi-annual investment strategy review

### Phase 3: Risk Management
1. Set and adhere to stop-loss criteria
2. Limit high-risk stock exposure
3. Develop market volatility response plan

## [WARNING] Investment Precautions

1. **Principal Loss Risk**: All investments carry risk of principal loss
2. **Market Volatility**: EV-related stocks may exhibit high volatility
3. **Policy Risk**: Government policy changes may affect performance
4. **Technology Risk**: Technology development may affect existing investments

---
*This investment strategy is for reference only. Investment decisions should be made at the investor's own judgment and responsibility.*
"""
        
        return analysis
    
    def _generate_glossary_section(self, state: Dict[str, Any]) -> str:
        """
        Glossary 생성 - 전문 용어 사전을 줄글로 작성
        """
        glossary = self._generate_glossary(state)
        
        glossary_text = "# 7. Glossary\n\n"
        
        # 카테고리별 용어 분류
        categories = {
            'EV Terms': ['EV', 'BEV', 'PHEV', 'HEV', 'FCEV'],
            'Battery Terms': ['Battery', 'Cell', 'BMS', 'LFP', 'NCM', 'NCA'],
            'Charging Terms': ['Charging', 'DC', 'AC', 'Supercharger'],
            'Supply Chain': ['OEM', 'Tier 1', 'Tier 2', 'Supplier'],
            'Financial Terms': ['PER', 'PBR', 'ROE', 'ROA', 'EBITDA', 'FCF'],
            'Investment Terms': ['Portfolio', 'Diversification', 'Risk', 'Return']
        }
        
        for category, terms in categories.items():
            glossary_text += f"## {category}\n\n"
            for term in terms:
                if term in glossary:
                    glossary_text += f"- **{term}**: {glossary[term]}\n"
            glossary_text += "\n"
        
        return glossary_text
    
    def _generate_risk_disclaimer(self, state: Dict[str, Any]) -> str:
        """
        Risk Disclaimer 생성 - 투자 위험 고지사항을 줄글로 작성
        """
        disclaimer = """
# 8. Risk Disclaimer

## [WARNING] Investment Risk Warning

### General Investment Risks
1. **Principal Loss Risk**: All investments carry the risk of principal loss
2. **Market Volatility**: EV-related stocks may exhibit high volatility
3. **Policy Risk**: Government policy changes may affect investment performance
4. **Technology Risk**: Technology development may pose risks to existing technologies
5. **Competition Risk**: Intensifying competition may impact company performance

### Specific EV Market Risks
1. **Raw Material Price Volatility**: Fluctuations in battery raw material prices
2. **Regulatory Changes**: Changes in environmental regulations and policies
3. **Technology Disruption**: Emergence of new technologies affecting existing ones
4. **Supply Chain Disruption**: Global supply chain issues affecting production
5. **Consumer Adoption**: Uncertainty in consumer acceptance of EV technology

### Risk Management Recommendations
1. **Diversification**: Spread investments across multiple companies and sectors
2. **Position Sizing**: Limit individual stock positions to manage risk
3. **Regular Monitoring**: Continuously monitor market conditions and company performance
4. **Stop Loss**: Set clear stop-loss levels to limit potential losses
5. **Due Diligence**: Conduct thorough research before making investment decisions

##  Legal Disclaimer

### Investment Advisory Disclaimer
- This report is for informational purposes only and does not constitute investment advice
- Past performance does not guarantee future results
- All investment decisions should be made based on individual risk tolerance and financial situation
- Investors should consult with qualified financial advisors before making investment decisions

### Data Accuracy Disclaimer
- While we strive for accuracy, we cannot guarantee the completeness or accuracy of all information
- Market conditions and company information may change rapidly
- Investors should verify information independently before making decisions

### Limitation of Liability
- We are not liable for any investment losses resulting from the use of this report
- Investors assume full responsibility for their investment decisions
- This report should not be the sole basis for investment decisions

##  Investor Responsibilities

### Pre-Investment Considerations
1. **Risk Assessment**: Evaluate your risk tolerance and investment objectives
2. **Financial Situation**: Consider your financial capacity and investment horizon
3. **Market Understanding**: Ensure understanding of EV market dynamics
4. **Professional Advice**: Seek professional financial advice when needed

### Ongoing Responsibilities
1. **Portfolio Monitoring**: Regularly review and adjust your portfolio
2. **Market Awareness**: Stay informed about market developments and company news
3. **Risk Management**: Implement appropriate risk management strategies
4. **Performance Review**: Periodically assess investment performance against objectives

---
*This disclaimer is effective as of the report generation date and may be updated periodically.*
"""
        return disclaimer
    
    def _generate_references_appendix(self, state: Dict[str, Any]) -> str:
        """
        References & Appendix 생성 - 참고문헌과 부록을 줄글로 작성
        """
        news_articles = state.get('news_articles', [])
        disclosure_data = state.get('disclosure_data', [])
        
        #   
        source_manager = state.get('source_manager')
        references_section = ""
        
        if source_manager and hasattr(source_manager, 'generate_references_section'):
            references_section = source_manager.generate_references_section()
        
        appendix = f"""
# 9. References & Appendix

##  Data Sources Summary

### News Articles ({len(news_articles)} articles)
{chr(10).join([f"- {article.get('title', 'Untitled')}" for article in news_articles[:10]]) if news_articles else "No news articles available"}

### Disclosure Data ({len(disclosure_data)} disclosures)
{chr(10).join([f"- {disclosure.get('title', 'Untitled')}" for disclosure in disclosure_data[:10]]) if disclosure_data else "No disclosure data available"}

##  Analysis Methodology

### Market Trend Analysis
- **Data Sources**: E-Daily, Hankyung, Money Today news
- **Analysis Period**: Recent 7 days
- **Keywords**: EV, electric vehicle, battery, charging
- **Method**: Keyword extraction and categorization

### Supply Chain Analysis
- **Data Sources**: Web search and supplier database
- **Method**: Keyword-based supplier discovery
- **Relationship Classification**: Supply/Cooperation/Competition/Unclear

### Financial Analysis
- **Qualitative (70%)**: Market trends, supplier relationships
- **Quantitative (30%)**: DART financial data, analyst reports

### Risk Analysis
- **Quantitative (80%)**: Financial ratios, market indicators
- **Qualitative (20%)**: Governance, legal risks

##  Data Quality Assessment

### Reliability Levels
- **High**: Official DART disclosures, major securities reports
- **Medium**: News articles, industry reports  
- **Low**: Web search results, unverified sources

##  Additional Resources

### Related Terms
- **EV**: Electric Vehicle
- **BEV**: Battery Electric Vehicle
- **OEM**: Original Equipment Manufacturer
- **Tier 1/2**: Supplier grade classification

### Reference Websites
- DART (dart.fss.or.kr)
- Korea Exchange (krx.co.kr)
- Securities firm research centers

##  Detailed References

{references_section if references_section else "Citation system not available"}

---
*This appendix provides detailed information for the investment report and should be used as reference material for investment decisions.*
"""
        
        return appendix
    
    def _integrate_sources_into_report(self, report_sections: Dict[str, str], state: Dict[str, Any]) -> Dict[str, str]:
        """
           
        """
        enhanced_sections = {}
        
        for section_name, content in report_sections.items():
            #    
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            enhanced_content = content + f"\n\n---\n*Generated: {timestamp}*"
            enhanced_sections[section_name] = enhanced_content
        
        return enhanced_sections
    
    def _generate_glossary(self, state: Dict[str, Any]) -> Dict[str, str]:
        """
        전문 용어 사전 생성
        """
        glossary = {
            # EV 관련 용어
            'EV': 'Electric Vehicle - 전기로 구동되는 자동차',
            'BEV': 'Battery Electric Vehicle - 배터리만으로 구동되는 순수 전기차',
            'PHEV': 'Plug-in Hybrid Electric Vehicle - 플러그인 하이브리드 전기차',
            'HEV': 'Hybrid Electric Vehicle - 하이브리드 전기차',
            'FCEV': 'Fuel Cell Electric Vehicle - 연료전지 전기차',
            
            # 배터리 관련 용어
            'Battery': '배터리 - 전기차의 동력원이 되는 에너지 저장 장치',
            'Cell': '셀 - 배터리의 기본 단위',
            'BMS': 'Battery Management System - 배터리 관리 시스템',
            'LFP': 'Lithium Iron Phosphate - 리튬인산철 배터리',
            'NCM': 'Nickel Cobalt Manganese - 니켈 코발트 망간 배터리',
            'NCA': 'Nickel Cobalt Aluminum - 니켈 코발트 알루미늄 배터리',
            
            # 충전 관련 용어
            'Charging': '충전 - 전기차 배터리에 전기를 공급하는 과정',
            'DC': 'Direct Current - 직류 충전',
            'AC': 'Alternating Current - 교류 충전',
            'Supercharger': 'Tesla 슈퍼차저 - 고속 충전소',
            
            # 공급망 관련 용어
            'OEM': 'Original Equipment Manufacturer - 완성차 제조사',
            'Tier 1': '1차 공급업체 - OEM에 직접 공급하는 업체',
            'Tier 2': '2차 공급업체 - Tier 1에 공급하는 업체',
            'Supplier': '공급업체 - 자동차 부품을 공급하는 기업',
            
            # 재무 관련 용어
            'PER': 'Price-to-Earnings Ratio - 주가수익비율',
            'PBR': 'Price-to-Book Ratio - 주가순자산비율',
            'ROE': 'Return on Equity - 자기자본이익률',
            'ROA': 'Return on Assets - 총자산이익률',
            'EBITDA': 'Earnings Before Interest, Taxes, Depreciation and Amortization - 세전이자비용차감전이익',
            'FCF': 'Free Cash Flow - 잉여현금흐름',
            
            # 투자 관련 용어
            'Portfolio': '포트폴리오 - 투자자산의 조합',
            'Diversification': '분산투자 - 리스크 분산을 위한 투자 전략',
            'Risk': '리스크 - 투자 손실 가능성',
            'Return': '수익률 - 투자 수익의 비율'
        }
        
        return glossary
    
    def _generate_investor_guide(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
          
        """
        guide = {
            'target_audience': self.target_audience,
            'investment_horizon': INVESTMENT_STRATEGY_CONFIG.get('investment_horizon', 'medium-term'),
            'risk_tolerance': INVESTMENT_STRATEGY_CONFIG.get('risk_tolerance', 'medium'),
            'focus_areas': INVESTMENT_STRATEGY_CONFIG.get('focus_areas', ['EV', 'Battery', 'Charging']),
            'investment_steps': [
                '1. Set investment goals (return, period, risk)',
                '2. Build portfolio (recommended stocks and weights)',
                '3. Gradual accumulation (average cost management)',
                '4. Regular monitoring (monthly rebalancing)',
                '5. Risk management (stop-loss adherence)'
            ],
            'monitoring_schedule': {
                'daily': ['Check price movements', 'Monitor news'],
                'weekly': ['Portfolio performance check', 'Market trend analysis'],
                'monthly': ['Rebalancing review', 'Performance evaluation'],
                'quarterly': ['Strategy review', 'Risk factor analysis']
            },
            'risk_warnings': [
                'Principal loss risk',
                'Market volatility risk',
                'Policy change risk',
                'Technology disruption risk',
                'Competition intensification risk'
            ],
            'disclaimer': 'This report is for reference only. Investment decisions should be made at the investor\'s own judgment and responsibility.'
        }
        
        return guide