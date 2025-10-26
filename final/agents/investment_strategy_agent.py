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
        """기업 투자 기회 분석 (재무 데이터 포함)"""
        try:
            # 재무 점수
            financial_score = company_data.get('final_score', 0.0)
            
            # 리스크 점수
            risk_analysis = analysis.get('risk_analysis', {})
            risk_data = risk_analysis.get('risk_analysis', {}).get(company, {})
            risk_score = risk_data.get('overall_risk_score', 0.5)
            
            # 투자 매력도
            attractiveness = self._calculate_investment_attractiveness(financial_score, risk_score)
            
            if attractiveness < 0.3:  # 매력도가 낮으면 제외
                return None
            
            # 🆕 재무 데이터 추가 (financial_analysis에서 가져오기)
            financial_analysis = analysis.get('financial_analysis', {})
            quantitative_analysis = financial_analysis.get('quantitative_analysis', {})
            company_financial = quantitative_analysis.get(company, {})
            
            # financial_ratios 추가
            financial_ratios = {}
            if company_financial.get('data_available', False):
                metrics = company_financial.get('financial_metrics_analysis', {})
                financial_ratios = metrics.get('financial_ratios', {})
            
            # 🆕 확장된 company_data (재무 비율 포함)
            enriched_company_data = {
                **company_data,
                'financial_ratios': financial_ratios,
                'company_type': 'oem' if company in ['Tesla', 'Ford', 'GM', 'BMW', 'Volkswagen', 'Hyundai', 'BYD'] else 'supplier'
            }
            
            return {
                'company': company,
                'type': 'direct_investment',
                'attractiveness_score': attractiveness,
                'financial_score': financial_score,
                'risk_score': risk_score,
                'investment_thesis': self._generate_investment_thesis(company, enriched_company_data),
                'target_price': self._estimate_target_price(company, enriched_company_data),
                'time_horizon': self._estimate_time_horizon(company, enriched_company_data)
            }
            
        except Exception as e:
            print(f"   [FAIL] {company}    : {e}")
            return None
    
    def _analyze_supplier_opportunity(self, supplier: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """공급업체 투자 기회 분석 (재무 데이터 포함)"""
        try:
            company_name = supplier.get('name', supplier.get('company', ''))
            if not company_name or company_name.strip() == '':
                return None
            
            # 신뢰도 점수
            confidence = supplier.get('confidence_score', supplier.get('overall_confidence', 0.0))
            
            # 최소 신뢰도 보장
            if confidence == 0.0:
                confidence = 0.5
            
            # 매력도 계산 (더 관대한 기준)
            attractiveness = max(0.4, confidence * 0.8)  # 최소 0.4 보장
            
            # 조건 완화: attractiveness < 0.2만 제외
            if attractiveness < 0.2:
                return None
            
            # 🆕 재무 데이터 추가 (financial_analysis에서 가져오기)
            financial_analysis = analysis.get('financial_analysis', {})
            quantitative_analysis = financial_analysis.get('quantitative_analysis', {})
            company_financial = quantitative_analysis.get(company_name, {})
            
            # financial_ratios 추가
            financial_ratios = {}
            if company_financial.get('data_available', False):
                metrics = company_financial.get('financial_metrics_analysis', {})
                financial_ratios = metrics.get('financial_ratios', {})
            
            # 기업 유형
            category = supplier.get('category', 'Unknown')
            products = supplier.get('products', [])
            product_desc = ', '.join(products[:2]) if products else f"{category} components"
            
            # 🆕 확장된 company_data (재무 비율 포함)
            enriched_company_data = {
                'financial_ratios': financial_ratios,
                'company_type': supplier.get('company_type', 'supplier'),
                'category': category,
                'products': products
            }
            
            # 🆕 재무 데이터가 있으면 동적 생성, 없으면 기본 논리
            if financial_ratios:
                investment_thesis = self._generate_investment_thesis(company_name, enriched_company_data)
            else:
                investment_thesis = f"{company_name}는 EV 공급망의 {category} 분야 전문 기업으로, {product_desc}를 제공하여 전기차 시장 성장의 혜택을 받을 것으로 예상됩니다."
            
            return {
                'company': company_name,
                'type': 'supplier_investment',
                'attractiveness_score': round(attractiveness, 2),
                'relationship_type': category,
                'confidence': round(confidence, 2),
                'investment_thesis': investment_thesis,
                'target_price': self._estimate_target_price(company_name, enriched_company_data),
                'time_horizon': self._estimate_time_horizon(company_name, enriched_company_data),
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
        """투자 논리 생성 (3단계 Fallback)"""
        
        # Plan A: LLM API (최고 품질)
        try:
            if self.llm_tool:
                prompt = f"""
                기업명: {company}
                재무 데이터: {company_data.get('financial_ratios', {})}
                
                위 정보를 바탕으로 간단한 투자 논리를 작성하세요 (3-4문장).
                """
                response = self.llm_tool.generate(prompt)
                if response and len(response.strip()) > 20:
                    print(f"[Plan A] ✅ LLM으로 {company} 투자 논리 생성")
                    return response.strip()
        except Exception as e:
            print(f"[Plan A] ❌ LLM API 실패: {e}")
        
        # Plan B: 재무 데이터 기반 동적 생성 (중간 품질, 기업마다 다름!)
        try:
            thesis = self._generate_thesis_from_financial_data(company, company_data)
            if thesis:
                print(f"[Plan B] ✅ 재무 데이터로 {company} 투자 논리 생성")
                return thesis
        except Exception as e:
            print(f"[Plan B] ❌ 재무 데이터 기반 생성 실패: {e}")
        
        # Plan C: 기본 템플릿 (최소 품질, 그래도 기업 유형별로 다름)
        print(f"[Plan C] ⚠️ 기본 템플릿으로 {company} 투자 논리 생성")
        return self._generate_basic_thesis_template(company, company_data)
    
    def _estimate_target_price(self, company: str, company_data: Dict[str, Any]) -> float:
        """목표가 추정 (Fallback 포함)"""
        
        # Plan A: LLM API
        try:
            if self.llm_tool:
                prompt = f"{company}의 적정 목표가를 추정하세요."
                response = self.llm_tool.generate(prompt)
                # 숫자 추출 시도
                import re
                numbers = re.findall(r'\d+\.?\d*', response)
                if numbers:
                    price = float(numbers[0])
                    if price > 0:
                        return price
        except:
            pass
        
        # Plan B: PER 기반 추정
        try:
            current_price = company_data.get('stock_price', 0)
            if current_price > 0:
                # 20% 상승 가정 (보수적)
                return round(current_price * 1.2, 2)
        except:
            pass
        
        # Plan C: None (N/A 표시)
        return None
    
    def _generate_thesis_from_financial_data(self, company: str, company_data: Dict[str, Any]) -> str:
        """Plan B: 재무 데이터로 동적 투자 논리 생성 (기업마다 다름!)"""
        
        # 재무 비율 추출
        ratios = company_data.get('financial_ratios', {})
        if not ratios:
            return None
        
        roe = ratios.get('roe', 0.0) * 100
        operating_margin = ratios.get('operating_margin', 0.0) * 100
        debt_ratio = ratios.get('debt_ratio', 0.0) * 100
        current_ratio = ratios.get('current_ratio', 0.0)
        
        # 1. 수익성 평가 (ROE)
        if roe > 20:
            roe_comment = f"매우 우수한 자기자본이익률(ROE {roe:.1f}%)"
            roe_score = 5
        elif roe > 15:
            roe_comment = f"우수한 자기자본이익률(ROE {roe:.1f}%)"
            roe_score = 4
        elif roe > 10:
            roe_comment = f"양호한 자기자본이익률(ROE {roe:.1f}%)"
            roe_score = 3
        elif roe > 5:
            roe_comment = f"적정 수준의 자기자본이익률(ROE {roe:.1f}%)"
            roe_score = 2
        else:
            roe_comment = f"낮은 자기자본이익률(ROE {roe:.1f}%)"
            roe_score = 1
        
        # 2. 영업이익률 평가
        if operating_margin > 15:
            margin_comment = f"높은 영업이익률({operating_margin:.1f}%)"
            margin_score = 5
        elif operating_margin > 10:
            margin_comment = f"우수한 영업이익률({operating_margin:.1f}%)"
            margin_score = 4
        elif operating_margin > 5:
            margin_comment = f"적정 영업이익률({operating_margin:.1f}%)"
            margin_score = 3
        elif operating_margin > 0:
            margin_comment = f"낮은 영업이익률({operating_margin:.1f}%)"
            margin_score = 2
        else:
            margin_comment = f"영업손실 발생({operating_margin:.1f}%)"
            margin_score = 1
        
        # 3. 재무 안정성 평가 (부채비율)
        if debt_ratio < 30:
            debt_comment = f"매우 안정적인 재무구조(부채비율 {debt_ratio:.1f}%)"
            debt_score = 5
        elif debt_ratio < 50:
            debt_comment = f"안정적인 재무구조(부채비율 {debt_ratio:.1f}%)"
            debt_score = 4
        elif debt_ratio < 100:
            debt_comment = f"적정 수준의 부채비율({debt_ratio:.1f}%)"
            debt_score = 3
        elif debt_ratio < 150:
            debt_comment = f"다소 높은 부채비율({debt_ratio:.1f}%)"
            debt_score = 2
        else:
            debt_comment = f"높은 부채비율({debt_ratio:.1f}%)로 재무 리스크 존재"
            debt_score = 1
        
        # 4. 유동성 평가
        if current_ratio > 2.0:
            liquidity_comment = f"충분한 유동성(유동비율 {current_ratio:.2f})"
        elif current_ratio > 1.5:
            liquidity_comment = f"양호한 유동성(유동비율 {current_ratio:.2f})"
        elif current_ratio > 1.0:
            liquidity_comment = f"적정 유동성(유동비율 {current_ratio:.2f})"
        else:
            liquidity_comment = f"유동성 부족(유동비율 {current_ratio:.2f})"
        
        # 5. 종합 평가 점수 (1-5)
        total_score = (roe_score + margin_score + debt_score) / 3
        
        # 6. 투자 의견 결정
        if total_score >= 4.5:
            investment_opinion = "적극 매수 추천"
        elif total_score >= 4.0:
            investment_opinion = "매수 추천"
        elif total_score >= 3.0:
            investment_opinion = "보유 권장"
        elif total_score >= 2.0:
            investment_opinion = "신중한 접근 필요"
        else:
            investment_opinion = "투자 유보 권장"
        
        # 7. 기업 유형 확인
        company_type = company_data.get('company_type', 'supplier')
        is_oem = company_type == 'oem'
        
        # 8. 최종 투자 논리 생성 (기업마다 다름!)
        if is_oem:
            thesis = f"""{company}는 {roe_comment}을 기록하며 전기차 시장의 주요 OEM으로 자리매김하고 있습니다. 
{margin_comment}로 수익성을 확보하고 있으며, {debt_comment}를 유지하고 있습니다. 
{liquidity_comment}를 보이고 있어, 전기차 시장 성장에 따른 수혜가 예상됩니다. ({investment_opinion})"""
        else:
            thesis = f"""{company}는 전기차 공급망의 핵심 기업으로 {roe_comment}을 달성했습니다. 
{margin_comment}와 {debt_comment}를 바탕으로 안정적인 성장이 기대됩니다. 
{liquidity_comment}를 갖추고 있어, 전기차 수요 증가에 따른 투자 가치가 있습니다. ({investment_opinion})"""
        
        return thesis.strip()
    
    def _generate_basic_thesis_template(self, company: str, company_data: Dict[str, Any]) -> str:
        """Plan C: 최소한의 템플릿 (그래도 기업 유형별로 다름)"""
        
        company_type = company_data.get('company_type', 'supplier')
        is_oem = company_type == 'oem'
        
        # OEM vs 공급업체에 따라 다른 논리
        if is_oem:
            templates = [
                f"{company}는 전기차 시장의 주요 OEM 제조사로, 글로벌 시장 점유율 확대가 예상됩니다.",
                f"{company}는 전기차 전환 전략을 적극 추진 중이며, 시장 성장에 따른 수혜가 기대됩니다.",
                f"{company}는 전기차 라인업 확대와 기술 경쟁력 강화를 통해 시장 리더십을 확보하고 있습니다."
            ]
        else:
            templates = [
                f"{company}는 전기차 공급망의 핵심 기업으로, 배터리 수요 증가에 따른 성장이 기대됩니다.",
                f"{company}는 주요 OEM과의 공급 계약을 통해 안정적인 매출 성장이 전망됩니다.",
                f"{company}는 전기차 부품 공급 분야의 기술력을 바탕으로 시장 확대가 예상됩니다."
            ]
        
        # 기업명 해시값으로 템플릿 선택 (같은 기업은 항상 같은 템플릿)
        idx = hash(company) % len(templates)
        return templates[idx]
    
    def _estimate_time_horizon(self, company: str, company_data: Dict[str, Any]) -> str:
        """투자 기간 추정 (Fallback 포함)"""
        
        # Plan A: LLM API
        try:
            if self.llm_tool:
                prompt = f"{company}의 적정 투자 기간을 추정하세요 (단기/중기/장기)."
                response = self.llm_tool.generate(prompt)
                if response and len(response.strip()) > 5:
                    return response.strip()
        except:
            pass
        
        # Plan B: 재무 안정성 기반
        try:
            ratios = company_data.get('financial_ratios', {})
            if ratios:
                debt_ratio = ratios.get('debt_ratio', 0)
                roe = ratios.get('roe', 0)
                current_ratio = ratios.get('current_ratio', 0)
                
                # 안정성 점수 계산
                stability_score = 0
                if debt_ratio < 0.5:
                    stability_score += 2
                elif debt_ratio < 1.0:
                    stability_score += 1
                
                if roe > 0.15:
                    stability_score += 2
                elif roe > 0.1:
                    stability_score += 1
                
                if current_ratio > 1.5:
                    stability_score += 1
                
                # 투자 기간 결정
                if stability_score >= 4:
                    return "장기 투자 권장 (12개월 이상)"
                elif stability_score >= 2:
                    return "중기 투자 권장 (6-12개월)"
                else:
                    return "단기 투자 권장 (3-6개월)"
        except:
            pass
        
        # Plan C: 기본값
        return "중기 투자 권장 (6-12개월)"
    
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
        """포트폴리오 추천 (비중 정규화 적용)"""
        if not opportunities:
            return {
                'portfolio_type': 'cash_heavy',
                'allocation': {'cash': 1.0},
                'recommendation': '투자 기회를 찾지 못했습니다. 현금 보유를 권장합니다.'
            }
        
        # 상위 5개 투자 기회 선정
        top_opportunities = sorted(opportunities, key=lambda x: x.get('attractiveness_score', 0), reverse=True)[:5]
        
        # 1단계: 초기 비중 계산 (투자 점수 기반)
        raw_weights = []
        for opp in top_opportunities:
            score = opp.get('attractiveness_score', 0.5)
            raw_weights.append(score)
        
        # 2단계: 비중 정규화 (합계 90%, 나머지 10%는 현금)
        total_raw = sum(raw_weights)
        allocation = {}
        
        if total_raw > 0:
            # 각 기업에 90%를 점수 비율로 배분
            for opp, raw_weight in zip(top_opportunities, raw_weights):
                normalized_weight = (raw_weight / total_raw) * 0.9  # 90%를 배분
                allocation[opp['company']] = normalized_weight
        else:
            # 점수가 모두 0인 경우 균등 배분
            equal_weight = 0.9 / len(top_opportunities)
            for opp in top_opportunities:
                allocation[opp['company']] = equal_weight
        
        # 3단계: 현금 10% 추가
        allocation['cash'] = 0.1
        
        # 검증: 합계가 1.0(100%)인지 확인
        total_allocation = sum(allocation.values())
        if abs(total_allocation - 1.0) > 0.001:  # 부동소수점 오차 허용
            print(f"   [WARNING] 포트폴리오 비중 합계 오류: {total_allocation:.4f} (목표: 1.0)")
            # 오차 보정
            allocation['cash'] += (1.0 - total_allocation)
        
        print(f"   [OK] 포트폴리오 비중 합계: {sum(allocation.values()):.4f} (100.00%)")
        
        return {
            'portfolio_type': 'growth_balanced',
            'allocation': allocation,
            'recommendation': f"{len(top_opportunities)}개 기업에 분산 투자 (현금 10% 보유)"
        }