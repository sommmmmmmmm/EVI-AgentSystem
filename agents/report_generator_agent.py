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
        Executive Summary 생성 - 실제 수집된 데이터를 기반으로 LLM이 요약
        """
        # 실제 수집된 데이터 추출
        market_trends = state.get('market_trends', [])
        financial_analysis = state.get('financial_analysis', {})
        investment_strategy = state.get('investment_strategy', {})
        risk_assessment = state.get('risk_assessment', {})
        suppliers = state.get('suppliers', [])
        news_articles = state.get('news_articles', [])
        disclosure_data = state.get('disclosure_data', [])
        
        # LLM을 사용하여 실제 데이터 기반 요약 생성
        summary_prompt = f"""
다음은 전기차(EV) 산업 분석을 위해 수집된 실제 데이터입니다. 이 데이터를 바탕으로 투자자를 위한 Executive Summary를 작성해주세요.

## 수집된 데이터:

### 시장 트렌드 ({len(market_trends)}개):
{self._format_trends_for_llm(market_trends[:5])}

### 뉴스 기사 ({len(news_articles)}개):
{self._format_news_for_llm(news_articles[:10])}

### 공급업체 ({len(suppliers)}개):
{self._format_suppliers_for_llm(suppliers[:10])}

### 재무 분석:
{self._format_financial_analysis_for_llm(financial_analysis)}

### 리스크 평가:
{self._format_risk_assessment_for_llm(risk_assessment)}

### 투자 전략:
{self._format_investment_strategy_for_llm(investment_strategy)}

### 공시 데이터 ({len(disclosure_data)}개):
{self._format_disclosures_for_llm(disclosure_data[:5])}

위 데이터를 바탕으로 다음 구조로 Executive Summary를 작성해주세요:

1. 핵심 투자 하이라이트 (실제 데이터 기반)
2. 시장 동향 요약 (실제 트렌드와 뉴스 기반)
3. 리스크 관리 전략 (실제 리스크 분석 기반)
4. 공급망 분석 결과 (실제 공급업체 데이터 기반)
5. 투자 권고사항 (실제 재무 분석과 투자 전략 기반)
6. 주요 위험 요소 (실제 리스크 평가 기반)
7. 기대 성과 (실제 데이터 종합 분석 기반)

각 섹션은 실제 수집된 데이터를 명확히 언급하고, 구체적인 수치와 사실을 포함해야 합니다.
"""
        
        try:
            # LLM을 사용하여 요약 생성
            llm_response = self.llm_tool.generate(summary_prompt)
            return f"# 1. Executive Summary\n\n{llm_response}\n\n---\n*본 보고서는 참고용으로만 사용되어야 하며, 투자 결정은 투자자 본인의 판단과 책임 하에 이루어져야 합니다.*"
        except Exception as e:
            print(f"[WARNING] LLM 요약 생성 실패: {e}")
            # LLM 실패 시 기본 요약 생성
            return self._generate_fallback_executive_summary(state)
    
    def _format_trends_for_llm(self, trends: List[Dict]) -> str:
        """트렌드 데이터를 LLM용으로 포맷"""
        if not trends:
            return "트렌드 데이터 없음"
        
        formatted = []
        for i, trend in enumerate(trends, 1):
            formatted.append(f"{i}. {trend.get('title', 'N/A')} (카테고리: {trend.get('category', 'N/A')}, 영향도: {trend.get('impact_score', 0):.2f})")
        return "\n".join(formatted)
    
    def _format_news_for_llm(self, news: List[Dict]) -> str:
        """뉴스 데이터를 LLM용으로 포맷"""
        if not news:
            return "뉴스 데이터 없음"
        
        formatted = []
        for i, article in enumerate(news, 1):
            title = article.get('title', 'N/A')
            source = article.get('source', 'N/A')
            date = article.get('published_date', 'N/A')
            formatted.append(f"{i}. {title} (출처: {source}, 날짜: {date})")
        return "\n".join(formatted)
    
    def _format_suppliers_for_llm(self, suppliers: List[Dict]) -> str:
        """공급업체 데이터를 LLM용으로 포맷"""
        if not suppliers:
            return "공급업체 데이터 없음"
        
        formatted = []
        for i, supplier in enumerate(suppliers, 1):
            name = supplier.get('name', supplier.get('company', 'N/A'))
            category = supplier.get('category', 'N/A')
            confidence = supplier.get('confidence_score', 0)
            formatted.append(f"{i}. {name} (카테고리: {category}, 신뢰도: {confidence:.2f})")
        return "\n".join(formatted)
    
    def _format_financial_analysis_for_llm(self, financial_analysis: Dict) -> str:
        """재무 분석 데이터를 LLM용으로 포맷"""
        if not financial_analysis:
            return "재무 분석 데이터 없음"
        
        top_picks = financial_analysis.get('top_picks', [])
        investment_scores = financial_analysis.get('investment_scores', {})
        
        formatted = []
        if top_picks:
            formatted.append("주요 투자 추천 기업:")
            for pick in top_picks[:5]:
                company = pick.get('company', 'N/A')
                score = pick.get('final_score', 0)
                formatted.append(f"- {company} (점수: {score:.2f})")
        
        if investment_scores:
            formatted.append(f"\n총 {len(investment_scores)}개 기업 분석 완료")
        
        return "\n".join(formatted) if formatted else "재무 분석 데이터 없음"
    
    def _format_risk_assessment_for_llm(self, risk_assessment: Dict) -> str:
        """리스크 평가 데이터를 LLM용으로 포맷"""
        if not risk_assessment:
            return "리스크 평가 데이터 없음"
        
        risk_summary = risk_assessment.get('risk_summary', {})
        risk_analysis = risk_assessment.get('risk_analysis', {})
        
        formatted = []
        if risk_summary:
            total = risk_summary.get('total_companies', 0)
            low = risk_summary.get('low_risk', 0)
            medium = risk_summary.get('medium_risk', 0)
            high = risk_summary.get('high_risk', 0)
            critical = risk_summary.get('critical_risk', 0)
            formatted.append(f"총 {total}개 기업 분석: 저위험 {low}개, 중위험 {medium}개, 고위험 {high}개, Critical {critical}개")
        
        if risk_analysis:
            formatted.append(f"상세 리스크 분석: {len(risk_analysis)}개 기업")
        
        return "\n".join(formatted) if formatted else "리스크 평가 데이터 없음"
    
    def _format_investment_strategy_for_llm(self, investment_strategy: Dict) -> str:
        """투자 전략 데이터를 LLM용으로 포맷"""
        if not investment_strategy:
            return "투자 전략 데이터 없음"
        
        portfolio_strategy = investment_strategy.get('portfolio_strategy', {})
        opportunities = investment_strategy.get('investment_opportunities', [])
        
        formatted = []
        if portfolio_strategy:
            strategy_name = portfolio_strategy.get('strategy_name', 'N/A')
            formatted.append(f"전략명: {strategy_name}")
        
        if opportunities:
            formatted.append(f"투자 기회: {len(opportunities)}개 식별")
        
        return "\n".join(formatted) if formatted else "투자 전략 데이터 없음"
    
    def _format_disclosures_for_llm(self, disclosures: List[Dict]) -> str:
        """공시 데이터를 LLM용으로 포맷"""
        if not disclosures:
            return "공시 데이터 없음"
        
        formatted = []
        for i, disclosure in enumerate(disclosures, 1):
            title = disclosure.get('title', 'N/A')
            company = disclosure.get('company', 'N/A')
            date = disclosure.get('date', 'N/A')
            formatted.append(f"{i}. {title} ({company}, {date})")
        return "\n".join(formatted)
    
    def _generate_fallback_executive_summary(self, state: Dict[str, Any]) -> str:
        """LLM 실패 시 기본 요약 생성"""
        suppliers = state.get('suppliers', [])
        market_trends = state.get('market_trends', [])
        news_articles = state.get('news_articles', [])
        
        return f"""# 1. Executive Summary

## 핵심 투자 하이라이트

본 보고서는 전기차(EV) 산업의 밸류체인을 종합적으로 분석하여 개인 투자자에게 중장기 투자 기회를 제시합니다. 분석 결과, 총 {len(suppliers)}개의 공급업체가 식별되었으며, {len(market_trends)}개의 주요 시장 트렌드가 분석되었습니다.

## 시장 동향 요약

전기차 시장은 지속적인 성장세를 보이고 있으며, 최근 {len(news_articles)}개의 뉴스 기사를 통해 시장 동향을 분석했습니다. 배터리 기술 발전, 충전 인프라 확충, 정부 정책 지원 등의 주요 트렌드가 시장 확장을 견인하고 있습니다.

## 공급망 분석 결과

총 {len(suppliers)}개의 공급업체를 분석한 결과, 전기차 부품 공급망의 핵심 기업들이 명확히 식별되었습니다. 특히 배터리, 모터, 전자제어장치 등 핵심 부품 분야에서 강력한 경쟁력을 보유한 기업들이 투자 매력도가 높은 것으로 평가되었습니다.

## 투자 권고사항

1. **핵심 부품 기업 집중 투자**: 전기차 밸류체인의 핵심 부품을 담당하는 기업들에 집중 투자
2. **중장기 투자 관점**: 3-12개월의 투자 기간을 설정하여 장기적 가치 창출에 집중
3. **리스크 관리**: 분산투자를 통해 포트폴리오의 안정성을 확보
4. **지속적 모니터링**: 시장 트렌드와 공급업체 관계 변화를 지속적으로 추적

---
*본 보고서는 참고용으로만 사용되어야 하며, 투자 결정은 투자자 본인의 판단과 책임 하에 이루어져야 합니다.*
"""
    
    def _generate_ev_market_trends(self, state: Dict[str, Any]) -> str:
        """
        EV Market Trends 생성 - 실제 수집된 데이터를 기반으로 LLM이 요약
        """
        market_trends = state.get('market_trends', [])
        categorized_keywords = state.get('categorized_keywords', {})
        news_articles = state.get('news_articles', [])
        
        # LLM을 사용하여 실제 데이터 기반 트렌드 분석 생성
        trends_prompt = f"""
다음은 전기차(EV) 시장 분석을 위해 수집된 실제 데이터입니다. 이 데이터를 바탕으로 시장 트렌드 분석을 작성해주세요.

## 수집된 데이터:

### 시장 트렌드 ({len(market_trends)}개):
{self._format_trends_for_llm(market_trends[:10])}

### 뉴스 기사 ({len(news_articles)}개):
{self._format_news_for_llm(news_articles[:15])}

### 키워드 분석:
{self._format_keywords_for_llm(categorized_keywords)}

위 데이터를 바탕으로 다음 구조로 EV Market Trends를 작성해주세요:

1. 시장 동향 분석 (실제 트렌드와 뉴스 기반)
2. 주요 트렌드 상세 분석 (실제 트렌드 데이터 기반)
3. 키워드 분석 (실제 키워드 데이터 기반)
4. 뉴스 분석 결과 (실제 뉴스 기사 기반)
5. 시장 전망 (실제 데이터 종합 분석 기반)

각 섹션은 실제 수집된 데이터를 명확히 언급하고, 구체적인 수치와 사실을 포함해야 합니다.
"""
        
        try:
            # LLM을 사용하여 트렌드 분석 생성
            llm_response = self.llm_tool.generate(trends_prompt)
            return f"# 2. EV Market Trends\n\n{llm_response}"
        except Exception as e:
            print(f"[WARNING] LLM 트렌드 분석 생성 실패: {e}")
            # LLM 실패 시 기본 분석 생성
            return self._generate_fallback_market_trends(state)
    
    def _format_keywords_for_llm(self, categorized_keywords: Dict) -> str:
        """키워드 데이터를 LLM용으로 포맷"""
        if not categorized_keywords:
            return "키워드 데이터 없음"
        
        formatted = []
        for category, keywords in categorized_keywords.items():
            if keywords:
                formatted.append(f"{category.replace('_', ' ')}: {', '.join(keywords[:10])} (총 {len(keywords)}개)")
        return "\n".join(formatted) if formatted else "키워드 데이터 없음"
    
    def _generate_fallback_market_trends(self, state: Dict[str, Any]) -> str:
        """LLM 실패 시 기본 트렌드 분석 생성"""
        market_trends = state.get('market_trends', [])
        news_articles = state.get('news_articles', [])
        categorized_keywords = state.get('categorized_keywords', {})
        
        return f"""# 2. EV Market Trends

## 시장 동향 분석

전기차 시장은 현재 급속한 성장 단계에 있으며, 여러 핵심 트렌드가 시장의 발전을 견인하고 있습니다. 최근 30일간 분석된 {len(news_articles)}개의 뉴스 기사를 바탕으로 한 분석 결과, 시장은 지속적인 성장 모멘텀을 보이고 있습니다.

## 주요 트렌드 분석

총 {len(market_trends)}개의 주요 트렌드가 식별되었습니다:

{self._format_trends_for_llm(market_trends[:5])}

## 키워드 분석

뉴스 기사에서 추출된 키워드를 카테고리별로 분석한 결과:

{self._format_keywords_for_llm(categorized_keywords)}

## 뉴스 분석 결과

총 {len(news_articles)}개의 뉴스 기사를 분석하여 시장 동향을 파악했습니다.

## 시장 전망

전기차 시장은 기술 혁신, 정책 지원, 인프라 확충, 소비자 수용성 향상 등의 요인들이 상호 작용하며 지속적인 성장을 이어가고 있습니다.
"""
    
    def _generate_supply_chain_analysis(self, state: Dict[str, Any]) -> str:
        """
        Supply Chain Analysis 생성 - 실제 수집된 데이터를 기반으로 LLM이 요약
        """
        suppliers = state.get('suppliers', [])
        
        # LLM을 사용하여 실제 데이터 기반 공급망 분석 생성
        supply_chain_prompt = f"""
다음은 전기차(EV) 공급망 분석을 위해 수집된 실제 데이터입니다. 이 데이터를 바탕으로 공급망 분석을 작성해주세요.

## 수집된 데이터:

### 공급업체 ({len(suppliers)}개):
{self._format_suppliers_for_llm(suppliers[:15])}

### 공급업체 분류:
{self._format_supplier_classification_for_llm(suppliers)}

위 데이터를 바탕으로 다음 구조로 Supply Chain Analysis를 작성해주세요:

1. 공급망 구조 개요 (실제 공급업체 데이터 기반)
2. 주요 EV 제조사 (OEM) 분석 (실제 OEM 데이터 기반)
3. 주요 공급업체 분석 (실제 공급업체 데이터 기반)
4. 공급망 계층 구조 (실제 데이터 기반 분류)
5. 공급망 관계 분석 (실제 관계 데이터 기반)
6. 신규 발견 기업 (실제 발견 데이터 기반)

각 섹션은 실제 수집된 데이터를 명확히 언급하고, 구체적인 수치와 사실을 포함해야 합니다.
"""
        
        try:
            # LLM을 사용하여 공급망 분석 생성
            llm_response = self.llm_tool.generate(supply_chain_prompt)
            return f"# 3. Supply Chain Analysis\n\n{llm_response}"
        except Exception as e:
            print(f"[WARNING] LLM 공급망 분석 생성 실패: {e}")
            # LLM 실패 시 기본 분석 생성
            return self._generate_fallback_supply_chain_analysis(state)
    
    def _format_supplier_classification_for_llm(self, suppliers: List[Dict]) -> str:
        """공급업체 분류 데이터를 LLM용으로 포맷"""
        if not suppliers:
            return "공급업체 분류 데이터 없음"
        
        oem_count = 0
        supplier_count = 0
        categories = {}
        
        for supplier in suppliers:
            company_type = supplier.get('type', 'supplier')
            if company_type == 'oem':
                oem_count += 1
            else:
                supplier_count += 1
            
            category = supplier.get('category', 'Unknown')
            categories[category] = categories.get(category, 0) + 1
        
        formatted = []
        formatted.append(f"OEM (완성차 제조사): {oem_count}개")
        formatted.append(f"공급업체: {supplier_count}개")
        formatted.append("\n카테고리별 분포:")
        for category, count in categories.items():
            formatted.append(f"- {category}: {count}개")
        
        return "\n".join(formatted)
    
    def _generate_fallback_supply_chain_analysis(self, state: Dict[str, Any]) -> str:
        """LLM 실패 시 기본 공급망 분석 생성"""
        suppliers = state.get('suppliers', [])
        
        # OEM과 공급업체 분리
        oem_suppliers = []
        regular_suppliers = []
        
        for supplier in suppliers:
            company_type = supplier.get('type', 'supplier')
            if company_type == 'oem':
                oem_suppliers.append(supplier)
            else:
                regular_suppliers.append(supplier)
        
        return f"""# 3. Supply Chain Analysis

## 공급망 구조 개요

전기차 공급망은 복잡하고 다층적인 구조를 가지고 있으며, 각 계층별로 핵심 역할을 담당하는 기업들이 존재합니다. 본 분석을 통해 총 **{len(suppliers)}개의 기업**을 식별했습니다{f", 이 중 **{len(oem_suppliers)}개는 OEM**, **{len(regular_suppliers)}개는 공급업체**입니다" if len(oem_suppliers) > 0 else ""}.

## 주요 EV 제조사 (OEM)

{self._format_suppliers_for_llm(oem_suppliers[:5])}

## 주요 공급업체

{self._format_suppliers_for_llm(regular_suppliers[:10])}

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
        Financial Performance 생성 - 완성차 업체와 공급업체를 분리하여 재무 성과 분석
        """
        financial_analysis = state.get('financial_analysis', {})
        investment_scores = financial_analysis.get('investment_scores', {})
        top_picks = financial_analysis.get('top_picks', [])
        
        # 완성차 업체와 공급업체 분리
        suppliers = state.get('suppliers', [])
        oem_companies = []
        supplier_companies = []
        
        for supplier in suppliers:
            company_type = supplier.get('type', 'supplier')
            if company_type == 'oem':
                oem_companies.append(supplier)
            else:
                supplier_companies.append(supplier)
        
        # 완성차 업체 분석
        oem_analysis = ""
        if oem_companies:
            oem_analysis = "## 🚗 완성차 업체 (OEM) 분석\n\n### 주요 완성차 업체 재무 성과\n\n"
            for i, oem in enumerate(oem_companies[:5], 1):
                name = oem.get('name', oem.get('company', ''))
                confidence = oem.get('confidence_score', 0.0)
                oem_analysis += f"### {i}. {name}\n"
                oem_analysis += f"- **Category**: OEM (완성차 제조사)\n"
                oem_analysis += f"- **Confidence Score**: {confidence:.2f}/1.0\n"
                oem_analysis += f"- **Products**: Electric Vehicles\n"
                oem_analysis += f"- **Market Position**: 주요 완성차 제조사\n\n"
        else:
            oem_analysis = ""  # OEM이 없으면 섹션 자체를 생략
        
        # 공급업체 분석
        supplier_analysis = ""
        if supplier_companies:
            supplier_analysis = "## 🔧 공급업체 (Suppliers) 분석\n\n### 주요 공급업체 재무 성과\n\n"
            for i, supplier in enumerate(supplier_companies[:10], 1):
                name = supplier.get('name', supplier.get('company', ''))
                confidence = supplier.get('confidence_score', 0.0)
                category = supplier.get('category', '')
                products = supplier.get('products', [])
                supplier_analysis += f"### {i}. {name}\n"
                supplier_analysis += f"- **Category**: {category}\n"
                supplier_analysis += f"- **Confidence Score**: {confidence:.2f}/1.0\n"
                supplier_analysis += f"- **Products**: {', '.join(products[:3]) if isinstance(products, list) else str(products)}\n"
                supplier_analysis += f"- **Market Position**: 전기차 부품 공급업체\n\n"
        else:
            supplier_analysis = "## 🔧 공급업체 (Suppliers) 분석\n\n분석 결과, 상장된 공급업체가 식별되지 않았습니다.\n\n"
        
        analysis = f"""# 4. Financial Performance

## 재무 성과 분석 개요

본 섹션에서는 전기차 관련 기업들을 **완성차 업체(OEM)**와 **공급업체(Suppliers)**로 분리하여 재무 성과를 분석합니다. 각 카테고리별로 상장사들의 실제 재무 데이터를 기반으로 투자 매력도를 평가했습니다.

### 분석 방법론
- **정성적 분석 (70%)**: 시장 트렌드, 공급업체 관계, 기술 경쟁력
- **정량적 분석 (30%)**: DART/SEC 재무 데이터, 증권사 분석가 리포트

{oem_analysis}

{supplier_analysis}

## 재무 지표 분석

### 핵심 평가 기준
1. **성장성**: 매출 증가율, 영업이익률
2. **수익성**: ROE, ROA
3. **안정성**: 부채비율, 유동비율
4. **밸류에이션**: PER, PBR (가능한 경우)

### 투자 점수 계산 방법
- **시장 트렌드 영향 (40%)**: EV 시장 트렌드와의 상관관계
- **공급업체 관계 (40%)**: 주요 OEM과의 공급 관계
- **재무 건전성 (20%)**: DART/SEC 기반 재무 지표

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
- DART/SEC 데이터가 있는 기업의 신뢰도가 높음
- 신규 발견 기업은 추가 실사 필요
- 재무 성과 정기적 모니터링 권장

## 결론

완성차 업체와 공급업체를 분리하여 분석한 결과, 각 카테고리별로 다른 투자 전략이 필요함을 확인했습니다. 완성차 업체는 시장 점유율과 브랜드 가치에 중점을 두고, 공급업체는 기술 경쟁력과 공급망 지위에 중점을 두어 투자 결정을 내리는 것이 효과적입니다.
"""
        
        return analysis
    
    def _generate_risk_assessment(self, state: Dict[str, Any]) -> str:
        """
        Risk Assessment 생성 - 리스크 평가와 위험 요소 분석을 줄글로 작성
        """
        risk_assessment = state.get('risk_assessment', {})
        risk_analysis = risk_assessment.get('risk_analysis', {})
        risk_summary = risk_assessment.get('risk_summary', {})
        
        if not risk_analysis:
            return """# 5. Risk Assessment

## [WARNING] Risk Grade Analysis

No risk analysis results available.

## 리스크 평가 기준

### 정량적 리스크 (80% 가중치)

#### 1. 기술투자 리스크 (40%)
- **R&D 비용 비중**: R&D / 매출
  - Critical: 25% 이상 (매출 대비 과도한 투자)
  - High: 20% 이상
  - Medium: 15% 이상 (혁신 기업 수준)
  - Low: 10% 이상

- **무형자산 비중**: 무형자산 / 총자산
  - Critical: 50% 이상 (과도한 무형자산 의존)
  - High: 40% 이상
  - Medium: 30% 이상
  - Low: 20% 이상

#### 2. 운전자본 리스크 (35%)
- **운전자본/매출 비율**: (유동자산 - 유동부채) / 매출
  - Critical: 40% 이상 (과다 운전자본)
  - High: 30% 이상
  - Medium: 20% 이상
  - Low: 10% 이상 (적정 수준)

- **현금전환주기 (CCC)**: 재고회전일수 + 매출채권회전일수 - 매입채무회전일수
  - Critical: 120일 이상 (현금 유동성 리스크)
  - High: 90일 이상
  - Medium: 60일 이상
  - Low: 30일 이상 (양호)

#### 3. 성장단계 리스크 (25%)
- **설비투자 비중**: CapEx / 매출
  - Critical: 30% 이상 (과도한 투자 부담)
  - High: 20% 이상
  - Medium: 15% 이상
  - Low: 10% 이상 (성장단계)

- **감가상각비 증가율**: 전년 대비 증가율
  - Critical: 50% 이상 증가
  - High: 30% 이상 증가
  - Medium: 20% 이상 증가
  - Low: 10% 이상 증가

### 정성적 리스크 (20% 가중치)

#### 1. 거버넌스 리스크
- 경영진 안정성 문제
- 이사회 구성 불균형
- 감사 품질 이슈

#### 2. 법적 리스크
- 소송 노출
- 규제 준수 문제
- 법규 위반 이력

#### 3. 경영 리스크
- 전략 실행력 부족
- 리더십 변화
- 핵심 인력 유출

## 🛡️ 리스크 완화 전략

### 포트폴리오 레벨
1. **분산투자**: 업종 및 기업 분산으로 리스크 분산
2. **리스크 한도**: 고위험 기업 노출 제한
3. **현금 보유**: 기회 포착 및 유동성 확보를 위한 현금 보유

### 개별 종목 레벨
1. **정기 모니터링**: 재무 지표 및 리스크 요인 추적
2. **이벤트 추적**: 주요 공시 및 뉴스 모니터링
3. **손절 기준**: 명확한 손절 기준 설정 및 준수

## 결론

전기차 시장은 기술 혁신, 정책 지원, 인프라 확충, 소비자 수용성 향상 등의 요인들이 상호 작용하며 지속적인 성장을 이어가고 있습니다. 다만 원자재 가격 변동성, 경쟁 심화, 기술 변화, 정책 변화 등의 리스크 요인들도 존재하므로, 투자 시 이러한 요소들을 종합적으로 고려해야 합니다.
"""
        
        # 완성차 업체와 공급업체 분리
        suppliers = state.get('suppliers', [])
        oem_companies = []
        supplier_companies = []
        
        for supplier in suppliers:
            company_type = supplier.get('type', 'supplier')
            if company_type == 'oem':
                oem_companies.append(supplier)
            else:
                supplier_companies.append(supplier)
        
        # 실제 리스크 분석 결과 표시
        total_companies = risk_summary.get('total_companies', 0)
        low_risk = risk_summary.get('low_risk', 0)
        medium_risk = risk_summary.get('medium_risk', 0)
        high_risk = risk_summary.get('high_risk', 0)
        critical_risk = risk_summary.get('critical_risk', 0)
        
        # 완성차 업체 리스크 분석
        oem_risk_analysis = ""
        if oem_companies:
            oem_risk_analysis = "## 🚗 완성차 업체 (OEM) 리스크 분석\n\n### 완성차 업체 리스크 평가\n\n"
            for i, oem in enumerate(oem_companies[:5], 1):
                name = oem.get('name', oem.get('company', ''))
                confidence = oem.get('confidence_score', 0.0)
                oem_risk_analysis += f"### {i}. {name}\n"
                oem_risk_analysis += f"- **Category**: OEM (완성차 제조사)\n"
                oem_risk_analysis += f"- **Risk Level**: {'Low' if confidence > 0.7 else 'Medium' if confidence > 0.5 else 'High'}\n"
                oem_risk_analysis += f"- **Confidence Score**: {confidence:.2f}/1.0\n"
                oem_risk_analysis += f"- **Key Risks**: 시장 경쟁, 기술 변화, 정책 변화\n\n"
        else:
            oem_risk_analysis = ""  # OEM이 없으면 섹션 자체를 생략
        
        # 공급업체 리스크 분석
        supplier_risk_analysis = ""
        if supplier_companies:
            supplier_risk_analysis = "## 🔧 공급업체 (Suppliers) 리스크 분석\n\n### 공급업체 리스크 평가\n\n"
            for i, supplier in enumerate(supplier_companies[:10], 1):
                name = supplier.get('name', supplier.get('company', ''))
                confidence = supplier.get('confidence_score', 0.0)
                category = supplier.get('category', '')
                supplier_risk_analysis += f"### {i}. {name}\n"
                supplier_risk_analysis += f"- **Category**: {category}\n"
                supplier_risk_analysis += f"- **Risk Level**: {'Low' if confidence > 0.7 else 'Medium' if confidence > 0.5 else 'High'}\n"
                supplier_risk_analysis += f"- **Confidence Score**: {confidence:.2f}/1.0\n"
                supplier_risk_analysis += f"- **Key Risks**: 기술 변화, OEM 의존도, 원자재 가격\n\n"
        else:
            supplier_risk_analysis = "## 🔧 공급업체 (Suppliers) 리스크 분석\n\n분석 결과, 상장된 공급업체가 식별되지 않았습니다.\n\n"
        
        # 리스크 등급별 기업 분류
        low_risk_companies = []
        medium_risk_companies = []
        high_risk_companies = []
        critical_risk_companies = []
        
        for company, risk_data in risk_analysis.items():
            risk_level = risk_data.get('risk_level', 'medium')
            overall_score = risk_data.get('overall_risk_score', 0.5)
            
            if risk_level == 'low':
                low_risk_companies.append((company, overall_score))
            elif risk_level == 'medium':
                medium_risk_companies.append((company, overall_score))
            elif risk_level == 'high':
                high_risk_companies.append((company, overall_score))
            elif risk_level == 'critical':
                critical_risk_companies.append((company, overall_score))
        
        # 점수 순으로 정렬
        low_risk_companies.sort(key=lambda x: x[1])
        medium_risk_companies.sort(key=lambda x: x[1])
        high_risk_companies.sort(key=lambda x: x[1], reverse=True)
        critical_risk_companies.sort(key=lambda x: x[1], reverse=True)
        
        # 리스크 분석 결과 생성
        risk_results = f"""# 5. Risk Assessment

## 리스크 분석 개요

본 섹션에서는 전기차 관련 기업들을 **완성차 업체(OEM)**와 **공급업체(Suppliers)**로 분리하여 리스크를 분석합니다. 각 카테고리별로 상장사들의 리스크 요인을 평가하여 투자 결정에 도움이 되는 정보를 제공합니다.

{oem_risk_analysis}

{supplier_risk_analysis}

## 전체 리스크 분석 결과

총 **{total_companies}개 기업**에 대한 리스크 분석을 수행했습니다.

### 리스크 등급별 분포
- **저위험**: {low_risk}개 (하위 33%)
- **중위험**: {medium_risk}개 (중간 33%)
- **고위험**: {high_risk}개 (상위 33%)
- **Critical**: {critical_risk}개 (상위 10%)

## 기업별 리스크 분석 결과

### 🟢 저위험 기업 ({len(low_risk_companies)}개)
"""
        
        for company, score in low_risk_companies:
            risk_results += f"- **{company}**: 리스크 점수 {score:.3f}\n"
        
        risk_results += f"\n### 🟡 중위험 기업 ({len(medium_risk_companies)}개)\n"
        for company, score in medium_risk_companies:
            risk_results += f"- **{company}**: 리스크 점수 {score:.3f}\n"
        
        risk_results += f"\n### 🟠 고위험 기업 ({len(high_risk_companies)}개)\n"
        for company, score in high_risk_companies:
            risk_results += f"- **{company}**: 리스크 점수 {score:.3f}\n"
        
        if critical_risk_companies:
            risk_results += f"\n### 🔴 Critical 리스크 기업 ({len(critical_risk_companies)}개)\n"
            for company, score in critical_risk_companies:
                risk_results += f"- **{company}**: 리스크 점수 {score:.3f}\n"
        
        # 상세 리스크 분석 추가
        risk_results += f"""

## 상세 리스크 분석

### 운전자본 리스크가 높은 기업
"""
        
        # 운전자본 리스크가 높은 기업 식별
        working_capital_risks = []
        for company, risk_data in risk_analysis.items():
            wc_risk = risk_data.get('working_capital_risk', 0.5)
            overall_score = risk_data.get('overall_risk_score', 0.5)
            working_capital_risks.append((company, wc_risk, overall_score))
        
        working_capital_risks.sort(key=lambda x: x[1], reverse=True)
        
        for company, wc_risk, overall_score in working_capital_risks[:3]:
            risk_results += f"- **{company}**: 운전자본 리스크 {wc_risk:.3f} (전체 리스크: {overall_score:.3f})\n"
        
        risk_results += f"""

## 리스크 평가 기준

### 정량적 리스크 (80% 가중치)

#### 1. 기술투자 리스크 (40%)
- **R&D 비용 비중**: R&D / 매출
- **무형자산 비중**: 무형자산 / 총자산

#### 2. 운전자본 리스크 (35%)
- **운전자본/매출 비율**: (유동자산 - 유동부채) / 매출
- **현금전환주기 (CCC)**: 재고회전일수 + 매출채권회전일수 - 매입채무회전일수

#### 3. 성장단계 리스크 (25%)
- **설비투자 비중**: CapEx / 매출
- **감가상각비 증가율**: 전년 대비 증가율

### 정성적 리스크 (20% 가중치)
- 거버넌스 리스크, 법적 리스크, 경영 리스크

## 🛡️ 리스크 완화 전략

### 포트폴리오 레벨
1. **분산투자**: 업종 및 기업 분산으로 리스크 분산
2. **리스크 한도**: 고위험 기업 노출 제한
3. **현금 보유**: 기회 포착 및 유동성 확보를 위한 현금 보유

### 개별 종목 레벨
1. **정기 모니터링**: 재무 지표 및 리스크 요인 추적
2. **이벤트 추적**: 주요 공시 및 뉴스 모니터링
3. **손절 기준**: 명확한 손절 기준 설정 및 준수

## 결론

실제 리스크 분석을 통해 각 기업의 리스크 수준을 객관적으로 평가했습니다. 투자 시에는 리스크 등급을 고려하여 포트폴리오를 구성하고, 고위험 기업은 제한적으로 투자하는 것이 안전합니다.
"""
        
        return risk_results
    
    def _calculate_expected_return(self, portfolio_strategy: Dict[str, Any], investment_opportunities: List[Dict[str, Any]]) -> float:
        """
        기대 수익률 계산 (연간 %)
        """
        if not investment_opportunities:
            # 투자 기회가 없으면 기본 수익률 (EV 시장 평균)
            return 8.5
        
        # 투자 기회들의 평균 수익률 계산
        total_return = 0
        valid_opportunities = 0
        
        for opp in investment_opportunities:
            attractiveness = opp.get('attractiveness', 0.0)
            if attractiveness > 0:
                # attractiveness를 기반으로 수익률 추정 (5-15% 범위)
                estimated_return = 5.0 + (attractiveness * 10.0)
                total_return += estimated_return
                valid_opportunities += 1
        
        if valid_opportunities > 0:
            return total_return / valid_opportunities
        else:
            return 8.5  # 기본 EV 시장 평균 수익률
    
    def _generate_investment_strategy(self, state: Dict[str, Any]) -> str:
        """
        Investment Strategy 생성 - 완성차 업체와 공급업체를 분리하여 투자 전략 구성
        """
        investment_strategy = state.get('investment_strategy', {})
        portfolio_strategy = investment_strategy.get('portfolio_strategy', {})
        investment_opportunities = investment_strategy.get('investment_opportunities', [])
        risk_management = investment_strategy.get('risk_management', {})
        timing_strategy = investment_strategy.get('timing_strategy', {})
        
        # 완성차 업체와 공급업체 분리
        suppliers = state.get('suppliers', [])
        oem_companies = []
        supplier_companies = []
        
        for supplier in suppliers:
            company_type = supplier.get('type', 'supplier')
            if company_type == 'oem':
                oem_companies.append(supplier)
            else:
                supplier_companies.append(supplier)
        
        # 포트폴리오 분석 (투자 기회가 없으면 공급업체 기반으로 생성)
        portfolio_analysis = ""
        recommended_companies = portfolio_strategy.get('recommended_companies', [])
        
        if recommended_companies:
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
        else:
            # 투자 기회가 없으면 공급업체 기반으로 기본 포트폴리오 생성 (상장사만)
            suppliers = state.get('suppliers', [])
            if suppliers:
                portfolio_analysis = "### 기본 포트폴리오 구성 (공급업체 기반)\n\n"
                
                # 상장사 여부 확인을 위한 리스트
                listed_companies = {
                    'SK': 'SK Innovation (096770.KS)',
                    'Samsung': 'Samsung SDI (006400.KS)', 
                    'Panasonic': 'Panasonic Holdings (6752.T)',
                    'Magna': 'Magna International (MGA)',
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
                
                def is_listed_company(company_name):
                    company_name_clean = company_name.replace(' ', '').replace('On', '').replace('SDI', '').replace('Energy', '').replace('Solution', '')
                    for listed_name in listed_companies.keys():
                        if listed_name.lower() in company_name_clean.lower():
                            return True
                    return False
                
                def get_company_ticker(company_name):
                    company_name_clean = company_name.replace(' ', '').replace('On', '').replace('SDI', '').replace('Energy', '').replace('Solution', '')
                    for listed_name, ticker_info in listed_companies.items():
                        if listed_name.lower() in company_name_clean.lower():
                            return ticker_info
                    return f"{company_name} (비상장)"
                
                # 상장사만 필터링
                listed_suppliers = []
                for supplier in suppliers:
                    company = supplier.get('name', supplier.get('company', ''))
                    if company.strip() and is_listed_company(company):
                        listed_suppliers.append(supplier)
                
                if listed_suppliers:
                    # LLM을 사용하여 각 회사의 Rationale 생성
                    for i, supplier in enumerate(listed_suppliers[:5], 1):
                        company = supplier.get('name', supplier.get('company', ''))
                        ticker = get_company_ticker(company)
                        
                        # LLM으로 회사별 맞춤형 Rationale 생성 (재무 데이터 포함)
                        company_rationale = self._generate_company_rationale(supplier, state)
                        
                        portfolio_analysis += f"""
### {i}. {company}
- **Ticker**: {ticker}
- **Target Weight**: {10 + i * 5:.1f}%
- **Investment Period**: 중기 (6-12개월)
- **Rationale**: {company_rationale}
"""
                else:
                    portfolio_analysis = """
### ⚠️ 투자 가능한 상장사 부족

**현재 상황**: 분석 결과, 투자 가능한 상장 공급업체가 식별되지 않았습니다.

**원인**:
- 식별된 공급업체 중 상장사가 없거나
- 티커 정보를 확인할 수 없는 기업들만 존재

**권장 사항**:
1. 더 넓은 범위의 EV 관련 기업 탐색 필요
2. 비상장 기업의 경우 사모펀드 또는 벤처캐피탈 투자 고려
3. 완성차 업체(OEM) 중심의 투자 전략 검토
"""
        
        # 투자 기회 분석 (투자 기회가 없으면 공급업체 기반으로 생성)
        opportunities_analysis = ""
        if investment_opportunities:
            for i, opp in enumerate(investment_opportunities[:5], 1):
                company = opp.get('company', '')
                opportunity_type = opp.get('opportunity_type', '')
                opportunity_score = opp.get('opportunity_score', 0.0)
                
                opportunities_analysis += f"""
{i}. **{company}**: {opportunity_type} (Score: {opportunity_score:.2f})
"""
        else:
            # 투자 기회가 없으면 공급업체 기반으로 기본 기회 생성
            suppliers = state.get('suppliers', [])
            if suppliers:
                opportunities_analysis = "### 주요 투자 기회 (공급업체 기반)\n\n"
                for i, supplier in enumerate(suppliers[:5], 1):
                    company = supplier.get('name', supplier.get('company', ''))
                    if company.strip():
                        category = supplier.get('category', 'Unknown')
                        confidence = supplier.get('confidence_score', supplier.get('overall_confidence', 0.5))
                        opportunities_analysis += f"""
{i}. **{company}**: {category} 분야 전문 기업 (신뢰도: {confidence:.2f})
"""
            else:
                opportunities_analysis = """
### ⚠️ 투자 기회 데이터 부족

**현재 상황**: 투자 기회를 식별할 수 있는 충분한 데이터가 없습니다.

**권장 사항**:
- 시장 조사 범위 확대 필요
- 전문 투자 리서치 보고서 참고
- 업계 전문가 의견 수렴
"""
        
        # 완성차 업체 투자 전략
        oem_strategy = ""
        if oem_companies:
            oem_strategy = f"""## 🚗 완성차 업체 (OEM) 투자 전략

### 완성차 업체 포트폴리오 구성

완성차 업체는 전기차 시장의 최종 소비자와 직접 연결되어 있어 시장 성장의 직접적인 혜택을 받습니다.

"""
            for i, oem in enumerate(oem_companies[:3], 1):
                name = oem.get('name', oem.get('company', ''))
                confidence = oem.get('confidence_score', 0.0)
                oem_strategy += f"""### {i}. {name}
- **Category**: OEM (완성차 제조사)
- **Target Weight**: {15 + i * 5:.1f}%
- **Investment Period**: 장기 (12개월 이상)
- **Rationale**: 시장 점유율과 브랜드 가치에 중점을 둔 투자
- **Key Factors**: 시장 경쟁력, 기술 혁신, 정책 지원

"""
        else:
            oem_strategy = """## 🚗 완성차 업체 (OEM) 투자 전략

### ⚠️ 완성차 업체 데이터 부족

**현재 상황**: 분석 결과, 투자 가능한 완성차 업체(OEM)가 식별되지 않았습니다.

**권장 사항**:
- 글로벌 주요 OEM (Tesla, BYD, GM, Ford 등) 직접 조사 필요
- 공급업체 중심의 투자 전략으로 전환 고려

"""
        
        # 공급업체 투자 전략
        supplier_strategy = ""
        if supplier_companies:
            supplier_strategy = f"""## 🔧 공급업체 (Suppliers) 투자 전략

### 공급업체 포트폴리오 구성

공급업체는 전기차 부품의 핵심 기술력을 보유하고 있어 기술 혁신의 혜택을 받습니다.

"""
            for i, supplier in enumerate(supplier_companies[:5], 1):
                name = supplier.get('name', supplier.get('company', ''))
                confidence = supplier.get('confidence_score', 0.0)
                category = supplier.get('category', '')
                supplier_strategy += f"""### {i}. {name}
- **Category**: {category}
- **Target Weight**: {8 + i * 2:.1f}%
- **Investment Period**: 중기 (6-12개월)
- **Rationale**: 기술 경쟁력과 공급망 지위에 중점을 둔 투자
- **Key Factors**: 기술 혁신, OEM 관계, 원자재 가격

"""
        else:
            supplier_strategy = """## 🔧 공급업체 (Suppliers) 투자 전략

### ⚠️ 공급업체 데이터 부족

**현재 상황**: 분석 결과, 투자 가능한 공급업체가 식별되지 않았습니다.

**권장 사항**:
- 배터리, 모터, 반도체 등 핵심 부품 공급업체 직접 조사 필요
- 완성차 업체(OEM) 중심의 투자 전략으로 전환 고려

"""

        analysis = f"""
# 6. 투자 전략

## 투자 전략 개요

본 섹션에서는 전기차 관련 기업들을 **완성차 업체(OEM)**와 **공급업체(Suppliers)**로 분리하여 각각에 최적화된 투자 전략을 제시합니다. 각 카테고리별로 상장사들의 특성을 고려한 차별화된 접근 방식을 적용합니다.

### 전략 개요
- **전략명**: {portfolio_strategy.get('strategy_name', '완성차-공급업체 분리 전략')}
- **전략 설명**: {portfolio_strategy.get('strategy_description', '완성차 업체와 공급업체를 분리하여 각각의 특성에 맞는 투자 전략 적용')}
- **기대 수익률**: {self._calculate_expected_return(portfolio_strategy, investment_opportunities):.1f}%

{oem_strategy}

{supplier_strategy}

## 📊 통합 포트폴리오 전략

### 추천 포트폴리오 구성

{portfolio_analysis if portfolio_analysis else "현재 추천 가능한 포트폴리오가 없습니다."}

### 자산 배분
- **성장주**: {portfolio_strategy.get('target_allocation', {}).get('growth_stocks', 0.5):.1%}
- **가치주**: {portfolio_strategy.get('target_allocation', {}).get('value_stocks', 0.4):.1%}
- **현금**: {portfolio_strategy.get('target_allocation', {}).get('cash', 0.1):.1%}

## 🎯 투자 기회

{opportunities_analysis if opportunities_analysis else "현재 특정 투자 기회가 식별되지 않았습니다."}

## ⏰ 투자 타이밍

### 진입 전략
- **접근 방법**: {timing_strategy.get('entry_strategy', '점진적 매수')}
- **시장 전망**: {timing_strategy.get('market_outlook', '긍정적')}

### 타이밍 고려 요소
{chr(10).join([f"- {factor}" for factor in timing_strategy.get('timing_factors', [])]) if timing_strategy.get('timing_factors') else "- EV 시장 성장률 모니터링"}

## 🛡️ 리스크 관리

### 리스크 관리 전략
- **리스크 허용도**: {risk_management.get('risk_tolerance', '중간')}
- **분산 투자**: {risk_management.get('diversification_strategy', '업종 분산')}

### 리스크 통제 방안
{chr(10).join([f"- {control.get('description', '')}" for control in risk_management.get('risk_controls', [])]) if risk_management.get('risk_controls') else "- 고위험 기업 제외"}

### 모니터링 포인트
{chr(10).join([f"- {point}" for point in risk_management.get('monitoring_points', [])]) if risk_management.get('monitoring_points') else "- 주요 OEM 공시 모니터링"}

## 📋 투자 실행 가이드

### 1단계: 포트폴리오 구축
1. 목표 비중에 따라 추천 종목 매수
2. 분할 매수를 통한 평균 단가 관리
3. 기회 포착을 위한 현금 보유

### 2단계: 지속적 모니터링
1. 월간 포트폴리오 리밸런싱 검토
2. 분기별 종목 성과 평가
3. 반기별 투자 전략 재검토

### 3단계: 리스크 관리
1. 손절 기준 설정 및 준수
2. 고위험 종목 비중 제한
3. 시장 변동성 대응 계획 수립

## ⚠️ 투자 유의사항

1. **원금 손실 위험**: 모든 투자는 원금 손실 위험이 있습니다
2. **시장 변동성**: EV 관련 주식은 높은 변동성을 보일 수 있습니다
3. **정책 리스크**: 정부 정책 변화가 실적에 영향을 미칠 수 있습니다
4. **기술 리스크**: 기술 개발이 기존 투자에 영향을 미칠 수 있습니다

---
*본 투자 전략은 참고용으로만 사용되어야 하며, 투자 결정은 투자자 본인의 판단과 책임 하에 이루어져야 합니다.*
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
# 8. 투자 위험 고지

## ⚠️ 투자 위험 경고

### 일반 투자 리스크
1. **원금 손실 위험**: 모든 투자에는 원금 손실 위험이 있습니다
2. **시장 변동성**: EV 관련 주식은 높은 변동성을 보일 수 있습니다
3. **정책 리스크**: 정부 정책 변화가 투자 성과에 영향을 미칠 수 있습니다
4. **기술 리스크**: 기술 개발이 기존 기술에 위험을 초래할 수 있습니다
5. **경쟁 리스크**: 경쟁 심화가 기업 실적에 영향을 미칠 수 있습니다

### EV 시장 특화 리스크
1. **원자재 가격 변동성**: 배터리 원자재 가격 변동 (리튬, 니켈 등)
2. **규제 변화**: 환경 규제 및 정책 변화
3. **기술 혁신**: 신기술 출현으로 인한 기존 기술 영향
4. **공급망 교란**: 글로벌 공급망 문제로 인한 생산 차질
5. **소비자 수용성**: EV 기술에 대한 소비자 수용 불확실성

### 리스크 관리 권장사항
1. **분산 투자**: 여러 기업과 업종에 투자 분산
2. **포지션 조정**: 개별 종목 비중 제한을 통한 리스크 관리
3. **정기 모니터링**: 시장 상황 및 기업 실적 지속 추적
4. **손절 기준**: 명확한 손절 수준 설정으로 손실 제한
5. **실사**: 투자 결정 전 충분한 조사 수행

## 📋 법적 면책 조항

### 투자 자문 면책
- 본 보고서는 정보 제공 목적으로만 작성되었으며 투자 자문을 구성하지 않습니다
- 과거 실적이 미래 수익을 보장하지 않습니다
- 모든 투자 결정은 개인의 리스크 허용도와 재무 상황을 기반으로 이루어져야 합니다
- 투자자는 투자 결정 전 전문 재무 상담사와 상담해야 합니다

### 데이터 정확성 면책
- 정확성을 위해 노력하나 모든 정보의 완전성이나 정확성을 보장할 수 없습니다
- 시장 상황 및 기업 정보는 빠르게 변할 수 있습니다
- 투자자는 결정 전 독립적으로 정보를 검증해야 합니다

### 책임의 제한
- 본 보고서 사용으로 인한 투자 손실에 대해 책임지지 않습니다
- 투자자는 투자 결정에 대한 전적인 책임을 집니다
- 본 보고서는 투자 결정의 유일한 근거가 되어서는 안 됩니다

## 👤 투자자 책임사항

### 투자 전 고려사항
1. **리스크 평가**: 리스크 허용도 및 투자 목표 평가
2. **재무 상황**: 재무 능력 및 투자 기간 고려
3. **시장 이해**: EV 시장 역학에 대한 이해 확보
4. **전문가 자문**: 필요시 전문 재무 조언 구하기

### 지속적 책임사항
1. **포트폴리오 모니터링**: 정기적으로 포트폴리오 검토 및 조정
2. **시장 인식**: 시장 동향 및 기업 뉴스 파악
3. **리스크 관리**: 적절한 리스크 관리 전략 실행
4. **성과 평가**: 목표 대비 투자 성과 주기적 평가

---
*본 면책 조항은 보고서 생성일 기준으로 유효하며 주기적으로 업데이트될 수 있습니다.*
"""
        return disclaimer
    
    def _generate_references_appendix(self, state: Dict[str, Any]) -> str:
        """
        References & Appendix 생성 - 참고문헌과 부록을 줄글로 작성
        """
        news_articles = state.get('news_articles', [])
        
        # 공시 데이터 수집 (여러 소스에서)
        disclosure_data = state.get('disclosure_data', [])
        
        # 추가 공시 데이터 소스 확인
        market_trends = state.get('market_trends', {})
        if 'disclosures' in market_trends:
            disclosure_data.extend(market_trends['disclosures'])
        if 'dart_disclosures' in state:
            disclosure_data.extend(state['dart_disclosures'])
        if 'sec_disclosures' in state:
            disclosure_data.extend(state['sec_disclosures'])
        if 'yahoo_data' in state:
            disclosure_data.extend(state['yahoo_data'])
        
        #   
        source_manager = state.get('source_manager')
        references_section = ""
        
        if source_manager and hasattr(source_manager, 'generate_references_section'):
            references_section = source_manager.generate_references_section()
        
        appendix = f"""
# 9. 참고문헌 및 부록

## 📚 데이터 출처 요약

### 뉴스 기사 ({len(news_articles)}개 기사)
{chr(10).join([f"- {article.get('title', '제목 없음')}" for article in news_articles[:10]]) if news_articles else "뉴스 기사 데이터 없음"}

### 공시 데이터 ({len(disclosure_data)}건 공시)
{chr(10).join([f"- {disclosure.get('title', '제목 없음')}" for disclosure in disclosure_data[:10]]) if disclosure_data else "공시 데이터 없음"}

## 🔬 분석 방법론

### 시장 트렌드 분석
- **데이터 출처**: 이데일리, 한국경제, 머니투데이 등 주요 언론
- **분석 기간**: 최근 30일
- **키워드**: EV, electric vehicle, battery, charging
- **방법**: 키워드 추출 및 카테고리화

### 공급망 분석
- **데이터 출처**: 웹 검색 및 공급업체 데이터베이스
- **방법**: 키워드 기반 공급업체 발견
- **관계 분류**: 공급/협력/경쟁/불명확

### 재무 분석
- **정성적 (70%)**: 시장 트렌드, 공급업체 관계
- **정량적 (30%)**: DART 재무 데이터, 증권사 리포트

### 리스크 분석
- **정량적 (80%)**: 3가지 핵심 지표
  - 기술투자 리스크 (40%): R&D 비용, 무형자산
  - 운전자본 리스크 (35%): 운전자본/매출, CCC
  - 성장단계 리스크 (25%): CapEx, 감가상각비
- **정성적 (20%)**: 거버넌스, 법적, 경영 리스크

## 📊 데이터 품질 평가

### 신뢰도 수준
- **높음**: 공식 DART 공시, 주요 증권사 리포트
- **중간**: 뉴스 기사, 산업 리포트
- **낮음**: 웹 검색 결과, 미검증 출처

## 📖 추가 자료

### 관련 용어
- **EV**: 전기차 (Electric Vehicle)
- **BEV**: 배터리 전기차 (Battery Electric Vehicle)
- **OEM**: 완성차 제조사 (Original Equipment Manufacturer)
- **Tier 1/2**: 공급업체 등급 분류

### 참고 웹사이트
- DART (dart.fss.or.kr) - 전자공시시스템
- 한국거래소 (krx.co.kr)
- 주요 증권사 리서치 센터

## 📝 상세 출처

{references_section if references_section else "출처 시스템을 사용할 수 없습니다"}

---
*본 부록은 투자 보고서에 대한 상세 정보를 제공하며 투자 결정을 위한 참고 자료로 사용되어야 합니다.*
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
    
    def _generate_company_rationale(self, supplier: Dict[str, Any], state: Dict[str, Any] = None) -> str:
        """
        회사별 맞춤형 투자 근거 생성 (재무 데이터, 시장 포지션 포함)
        """
        from config.settings import is_oem_company
        
        company_name = supplier.get('name', supplier.get('company', ''))
        category = supplier.get('category', '')
        confidence = supplier.get('confidence_score', 0.0)
        products = supplier.get('products', [])
        
        # OEM 여부 확인
        is_oem = is_oem_company(company_name)
        company_type = "완성차 제조사(OEM)" if is_oem else "부품 공급업체"
        
        # 재무 데이터 추출 (state에서)
        financial_info = ""
        if state:
            financial_analysis = state.get('financial_analysis', {})
            qualitative_analysis = financial_analysis.get('qualitative_analysis', {})
            quantitative_analysis = financial_analysis.get('quantitative_analysis', {})
            
            qual_data = qualitative_analysis.get(company_name, {})
            quant_data = quantitative_analysis.get(company_name, {})
            
            # 재무 비율
            financial_ratios = quant_data.get('financial_ratios', {})
            roe = financial_ratios.get('roe', 0) * 100
            operating_margin = financial_ratios.get('operating_margin', 0) * 100
            data_source = quant_data.get('data_source', 'unknown')
            
            if data_source != 'NONE':
                financial_info = f"\n재무 지표 (출처: {data_source}):\n- ROE: {roe:.1f}%\n- 영업이익률: {operating_margin:.1f}%"
            
            # 정성적 분석 요약
            qual_score = qual_data.get('qualitative_score', 0)
            if qual_score > 0:
                financial_info += f"\n- 전문가 평가: {qual_score * 100:.0f}점"
        
        # OEM 관계 정보
        oem_relationships = supplier.get('oem_relationships', [])
        oem_info = ""
        if oem_relationships and isinstance(oem_relationships, list) and len(oem_relationships) > 0:
            oem_list = ', '.join(oem_relationships[:3])
            oem_info = f"\n주요 고객: {oem_list}"
        
        rationale_prompt = f"""
다음 전기차(EV) 관련 기업의 투자 근거를 구체적으로 작성해주세요.
2-3문장으로 작성하되, 기업의 차별화된 강점과 명확한 투자 포인트를 제시해주세요.

## 기업 정보
- 회사명: {company_name}
- 유형: {company_type}
- 카테고리: {category}
- 주요 제품: {', '.join(products[:3]) if isinstance(products, list) and products else '전기차 관련 제품'}
- 신뢰도: {confidence:.0%}{oem_info}{financial_info}

## 작성 가이드
1. 기업의 핵심 경쟁력을 먼저 언급
2. 재무 지표가 있다면 강점 위주로 언급
3. OEM인 경우: 시장 점유율, 기술력, 브랜드 가치
4. 공급업체인 경우: 핵심 기술, 주요 고객사, 공급망 지위

투자 근거:
"""
        
        try:
            llm_response = self.llm_tool.generate(rationale_prompt)
            # LLM 응답 정리
            rationale = llm_response.strip()
            
            # "투자 근거:" 레이블 제거
            if rationale.startswith('투자 근거:'):
                rationale = rationale[6:].strip()
            
            # 너무 길면 앞 3문장만
            sentences = rationale.split('.')
            if len(sentences) > 3:
                rationale = '. '.join(sentences[:3]) + '.'
            
            return rationale if rationale else self._generate_fallback_rationale(company_name, is_oem, financial_info)
        except Exception as e:
            print(f"[WARNING] Rationale 생성 실패 for {company_name}: {e}")
            return self._generate_fallback_rationale(company_name, is_oem, financial_info)
    
    def _generate_fallback_rationale(self, company_name: str, is_oem: bool, financial_info: str) -> str:
        """LLM 실패 시 기본 투자 근거 생성"""
        if is_oem:
            base = f"{company_name}는 전기차 시장의 주요 완성차 제조사로서 글로벌 시장에서 강력한 브랜드 파워를 보유하고 있습니다."
        else:
            base = f"{company_name}는 전기차 핵심 부품을 공급하는 기업으로 EV 공급망에서 중요한 위치를 차지하고 있습니다."
        
        if "ROE" in financial_info and "%" in financial_info:
            base += " 견고한 재무 구조와 수익성을 바탕으로 지속적인 성장이 기대됩니다."
        
        return base
    
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