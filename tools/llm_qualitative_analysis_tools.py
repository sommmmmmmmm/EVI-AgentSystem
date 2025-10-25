"""
LLM-Based Qualitative Analysis Tool
실제 뉴스 + 공시 데이터 기반 정성적 분석

This tool generates qualitative analysis based on:
- Real news articles (100+ articles)
- DART/SEC disclosure data
- Market trends
- Supply chain relationships
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json


class LLMQualitativeAnalyzer:
    """
    LLM-based qualitative analysis using real data
    실제 데이터 기반 LLM 정성 분석
    """
    
    def __init__(self, llm_tool=None):
        """
        Initialize with LLM tool
        
        Args:
            llm_tool: LLM tool for generating qualitative analysis
        """
        self.llm_tool = llm_tool
        self.company_aliases = self._load_company_aliases()
    
    def _load_company_aliases(self) -> Dict[str, str]:
        """
        Company name alias mapping (English ↔ Korean, abbreviations)
        회사명 별칭 매핑
        """
        return {
            # Tesla
            'Tesla': 'Tesla',
            'tesla': 'Tesla',
            'TSLA': 'Tesla',
            '테슬라': 'Tesla',
            
            # LG Energy Solution
            'LG Energy Solution': 'LG Energy Solution',
            'LG에너지솔루션': 'LG Energy Solution',
            'LG에너지': 'LG Energy Solution',
            'LGES': 'LG Energy Solution',
            'LG Energy': 'LG Energy Solution',
            
            # Samsung SDI
            'Samsung SDI': 'Samsung SDI',
            '삼성SDI': 'Samsung SDI',
            'SDI': 'Samsung SDI',
            
            # SK On
            'SK On': 'SK On',
            'SK온': 'SK On',
            'SKOn': 'SK On',
            
            # BYD
            'BYD': 'BYD',
            'byd': 'BYD',
            '비야디': 'BYD',
            
            # BMW
            'BMW': 'BMW',
            'bmw': 'BMW',
            
            # GM
            'GM': 'GM',
            'General Motors': 'GM',
            'gm': 'GM',
            
            # Ford
            'Ford': 'Ford',
            'Ford Motor': 'Ford',
            'ford': 'Ford',
            
            # Mercedes-Benz
            'Mercedes': 'Mercedes-Benz',
            'Mercedes-Benz': 'Mercedes-Benz',
            'Benz': 'Mercedes-Benz',
            '벤츠': 'Mercedes-Benz',
            
            # Volkswagen
            'Volkswagen': 'Volkswagen',
            'VW': 'Volkswagen',
            '폭스바겐': 'Volkswagen',
        }
    
    def _normalize_company_name(self, company_name: str) -> str:
        """
        Normalize company name using alias mapping
        회사명 정규화
        """
        return self.company_aliases.get(company_name, company_name)
    
    def analyze_company_qualitative(
        self,
        company_name: str,
        news_articles: List[Dict[str, Any]],
        disclosures: List[Dict[str, Any]],
        market_trends: List[Dict[str, Any]],
        supplier_relationships: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive qualitative analysis for a company
        
        Args:
            company_name: Company name to analyze
            news_articles: Recent news articles about the company
            disclosures: Recent disclosure data (DART/SEC)
            market_trends: Market trends analysis
            supplier_relationships: Supply chain relationships
        
        Returns:
            Dict with qualitative analysis including:
            - overall_rating: 1-10 score
            - confidence: 0-100 confidence level
            - key_strengths: List of strengths
            - key_risks: List of risks
            - growth_drivers: Future growth factors
            - competitive_position: Market position analysis
            - sentiment_score: News sentiment (-1 to 1)
            - recommendation: Buy/Hold/Sell
        """
        normalized_name = self._normalize_company_name(company_name)
        
        # Filter company-specific data
        company_news = self._filter_company_news(normalized_name, news_articles)
        company_disclosures = self._filter_company_disclosures(normalized_name, disclosures)
        company_suppliers = self._filter_company_suppliers(normalized_name, supplier_relationships)
        
        # If no data available, return low confidence analysis
        if not company_news and not company_disclosures:
            return self._generate_low_confidence_analysis(company_name)
        
        # Generate qualitative analysis using LLM
        if self.llm_tool:
            analysis = self._llm_based_analysis(
                normalized_name,
                company_news,
                company_disclosures,
                market_trends,
                company_suppliers
            )
        else:
            analysis = self._rule_based_analysis(
                normalized_name,
                company_news,
                company_disclosures,
                market_trends,
                company_suppliers
            )
        
        return analysis
    
    def _filter_company_news(self, company_name: str, news_articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter news articles related to the company
        회사 관련 뉴스 필터링
        """
        filtered = []
        keywords = [company_name.lower()]
        
        # Add alias keywords
        for alias, canonical in self.company_aliases.items():
            if canonical == company_name:
                keywords.append(alias.lower())
        
        for article in news_articles:
            title = article.get('title', '').lower()
            content = article.get('content', '').lower()
            
            if any(keyword in title or keyword in content for keyword in keywords):
                filtered.append(article)
        
        return filtered[:10]  # Top 10 most relevant
    
    def _filter_company_disclosures(self, company_name: str, disclosures: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter disclosure data related to the company
        회사 관련 공시 필터링
        """
        filtered = []
        
        for disclosure in disclosures:
            disc_company = disclosure.get('company_name', '')
            normalized_disc = self._normalize_company_name(disc_company)
            
            if normalized_disc == company_name:
                filtered.append(disclosure)
        
        return filtered[:5]  # Top 5 most recent
    
    def _filter_company_suppliers(self, company_name: str, supplier_relationships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter supplier relationships related to the company
        회사 관련 공급망 필터링
        """
        filtered = []
        
        for relationship in supplier_relationships:
            oem_name = relationship.get('oem_name', '')
            supplier_name = relationship.get('supplier_name', '')
            
            normalized_oem = self._normalize_company_name(oem_name)
            normalized_supplier = self._normalize_company_name(supplier_name)
            
            if normalized_oem == company_name or normalized_supplier == company_name:
                filtered.append(relationship)
        
        return filtered
    
    def _llm_based_analysis(
        self,
        company_name: str,
        news: List[Dict[str, Any]],
        disclosures: List[Dict[str, Any]],
        trends: List[Dict[str, Any]],
        suppliers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate qualitative analysis using LLM
        LLM 기반 정성 분석 생성
        """
        # Prepare context for LLM
        context = self._prepare_llm_context(company_name, news, disclosures, trends, suppliers)
        
        # Generate analysis using LLM
        prompt = f"""
You are a professional financial analyst specializing in the EV industry. 
Analyze the following company based on real news, disclosure data, and market trends.

Company: {company_name}

=== RECENT NEWS ({len(news)} articles) ===
{self._format_news_for_prompt(news)}

=== DISCLOSURE DATA ({len(disclosures)} filings) ===
{self._format_disclosures_for_prompt(disclosures)}

=== MARKET TRENDS ===
{self._format_trends_for_prompt(trends)}

=== SUPPLY CHAIN ({len(suppliers)} relationships) ===
{self._format_suppliers_for_prompt(suppliers)}

Provide a comprehensive qualitative analysis in JSON format with:
1. overall_rating (1-10): Overall investment attractiveness
2. confidence (0-100): Confidence level based on data availability
3. key_strengths (list): 3-5 key competitive strengths
4. key_risks (list): 3-5 major risk factors
5. growth_drivers (list): 3-5 future growth catalysts
6. competitive_position (string): Market position analysis (150 words)
7. sentiment_score (-1 to 1): Overall news sentiment
8. recommendation (Buy/Hold/Sell): Investment recommendation
9. reasoning (string): Brief explanation for the rating (200 words)

Output ONLY valid JSON. No markdown, no explanations.
"""
        
        try:
            response = self.llm_tool.generate(prompt, max_tokens=1500, temperature=0.3)
            analysis = json.loads(response)
            
            # Add metadata
            analysis['analysis_date'] = datetime.now().isoformat()
            analysis['data_sources'] = {
                'news_count': len(news),
                'disclosure_count': len(disclosures),
                'supplier_count': len(suppliers)
            }
            analysis['method'] = 'LLM-based (real data)'
            
            return analysis
            
        except Exception as e:
            print(f"   ⚠️ LLM analysis failed: {e}")
            # Fallback to rule-based
            return self._rule_based_analysis(company_name, news, disclosures, trends, suppliers)
    
    def _rule_based_analysis(
        self,
        company_name: str,
        news: List[Dict[str, Any]],
        disclosures: List[Dict[str, Any]],
        trends: List[Dict[str, Any]],
        suppliers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate qualitative analysis using rule-based heuristics
        규칙 기반 정성 분석 생성 (LLM 실패 시 폴백)
        """
        # Calculate sentiment from news
        sentiment_score = self._calculate_news_sentiment(news)
        
        # Calculate data confidence
        confidence = min(100, (len(news) * 5) + (len(disclosures) * 10) + (len(suppliers) * 5))
        
        # Determine rating based on sentiment and data
        overall_rating = self._calculate_overall_rating(sentiment_score, confidence, len(suppliers))
        
        # Extract key information
        key_strengths = self._extract_strengths(news, disclosures, suppliers)
        key_risks = self._extract_risks(news, disclosures)
        growth_drivers = self._extract_growth_drivers(news, trends)
        
        # Determine recommendation
        if overall_rating >= 7.5:
            recommendation = "Buy"
        elif overall_rating >= 5.5:
            recommendation = "Hold"
        else:
            recommendation = "Sell"
        
        return {
            'overall_rating': round(overall_rating, 1),
            'confidence': confidence,
            'key_strengths': key_strengths,
            'key_risks': key_risks,
            'growth_drivers': growth_drivers,
            'competitive_position': f"{company_name} shows {'strong' if overall_rating >= 7 else 'moderate' if overall_rating >= 5 else 'weak'} market position based on available data.",
            'sentiment_score': round(sentiment_score, 2),
            'recommendation': recommendation,
            'reasoning': f"Rating based on {len(news)} news articles, {len(disclosures)} disclosures, and {len(suppliers)} supply chain relationships. Sentiment score: {sentiment_score:.2f}.",
            'analysis_date': datetime.now().isoformat(),
            'data_sources': {
                'news_count': len(news),
                'disclosure_count': len(disclosures),
                'supplier_count': len(suppliers)
            },
            'method': 'Rule-based (fallback)'
        }
    
    def _calculate_news_sentiment(self, news: List[Dict[str, Any]]) -> float:
        """
        Calculate sentiment score from news articles
        뉴스 감성 점수 계산
        """
        if not news:
            return 0.0
        
        positive_keywords = ['growth', 'surge', 'profit', 'expansion', 'innovation', 'breakthrough', 'success', 'deal']
        negative_keywords = ['loss', 'decline', 'risk', 'concern', 'delay', 'recall', 'investigation', 'lawsuit']
        
        sentiment_sum = 0.0
        
        for article in news:
            text = f"{article.get('title', '')} {article.get('content', '')}".lower()
            
            positive_count = sum(1 for kw in positive_keywords if kw in text)
            negative_count = sum(1 for kw in negative_keywords if kw in text)
            
            if positive_count + negative_count > 0:
                article_sentiment = (positive_count - negative_count) / (positive_count + negative_count)
                sentiment_sum += article_sentiment
        
        return sentiment_sum / len(news) if news else 0.0
    
    def _calculate_overall_rating(self, sentiment: float, confidence: int, supplier_count: int) -> float:
        """
        Calculate overall rating based on multiple factors
        종합 평가 점수 계산
        """
        base_rating = 5.0  # Neutral
        
        # Sentiment contribution (±2 points)
        sentiment_contribution = sentiment * 2.0
        
        # Confidence contribution (±1 point)
        confidence_contribution = (confidence - 50) / 50  # Normalize around 50
        
        # Supplier count contribution (±1 point)
        supplier_contribution = min(1.0, supplier_count / 5) if supplier_count > 0 else -0.5
        
        overall = base_rating + sentiment_contribution + confidence_contribution + supplier_contribution
        
        return max(1.0, min(10.0, overall))  # Clamp between 1-10
    
    def _extract_strengths(self, news: List[Dict[str, Any]], disclosures: List[Dict[str, Any]], suppliers: List[Dict[str, Any]]) -> List[str]:
        """
        Extract key strengths from data
        핵심 강점 추출
        """
        strengths = []
        
        if len(news) >= 5:
            strengths.append("High media visibility and market attention")
        
        if len(disclosures) >= 3:
            strengths.append("Active in regulatory filings and transparency")
        
        if len(suppliers) >= 3:
            strengths.append("Strong supply chain network")
        
        # Add generic strengths if not enough
        if len(strengths) < 3:
            strengths.extend([
                "Established position in EV market",
                "Strategic partnerships and collaborations"
            ])
        
        return strengths[:5]
    
    def _extract_risks(self, news: List[Dict[str, Any]], disclosures: List[Dict[str, Any]]) -> List[str]:
        """
        Extract key risks from data
        주요 리스크 추출
        """
        risks = []
        
        if len(news) < 3:
            risks.append("Limited market visibility and news coverage")
        
        if len(disclosures) < 2:
            risks.append("Limited disclosure transparency")
        
        # Add generic risks
        risks.extend([
            "Market competition intensification",
            "Raw material price volatility",
            "Technology transition risks"
        ])
        
        return risks[:5]
    
    def _extract_growth_drivers(self, news: List[Dict[str, Any]], trends: List[Dict[str, Any]]) -> List[str]:
        """
        Extract growth drivers from news and trends
        성장 동력 추출
        """
        drivers = []
        
        if len(trends) > 0:
            for trend in trends[:2]:
                drivers.append(f"{trend.get('trend_name', 'Market trend')}: {trend.get('description', '')[:50]}...")
        
        # Add generic drivers
        drivers.extend([
            "Global EV market expansion",
            "Battery technology advancement",
            "Government policy support"
        ])
        
        return drivers[:5]
    
    def _generate_low_confidence_analysis(self, company_name: str) -> Dict[str, Any]:
        """
        Generate low-confidence placeholder analysis when data is insufficient
        데이터 부족 시 낮은 신뢰도 분석 생성
        """
        return {
            'overall_rating': 5.0,
            'confidence': 10,
            'key_strengths': [
                f"{company_name} operates in EV industry",
                "Insufficient data for detailed analysis"
            ],
            'key_risks': [
                "Insufficient data for comprehensive risk assessment",
                "Limited market information available"
            ],
            'growth_drivers': [
                "General EV market growth"
            ],
            'competitive_position': f"Insufficient data to assess {company_name}'s competitive position.",
            'sentiment_score': 0.0,
            'recommendation': "Hold",
            'reasoning': "Insufficient news and disclosure data for confident analysis. Recommend Hold until more information becomes available.",
            'analysis_date': datetime.now().isoformat(),
            'data_sources': {
                'news_count': 0,
                'disclosure_count': 0,
                'supplier_count': 0
            },
            'method': 'Low-confidence placeholder'
        }
    
    def _prepare_llm_context(self, company_name: str, news: List, disclosures: List, trends: List, suppliers: List) -> str:
        """Prepare formatted context for LLM"""
        return f"Company: {company_name}, News: {len(news)}, Disclosures: {len(disclosures)}"
    
    def _format_news_for_prompt(self, news: List[Dict[str, Any]]) -> str:
        """Format news for LLM prompt"""
        if not news:
            return "No recent news available."
        
        formatted = []
        for i, article in enumerate(news[:5], 1):
            formatted.append(f"{i}. {article.get('title', 'N/A')} - {article.get('published_date', 'N/A')}")
        
        return "\n".join(formatted)
    
    def _format_disclosures_for_prompt(self, disclosures: List[Dict[str, Any]]) -> str:
        """Format disclosures for LLM prompt"""
        if not disclosures:
            return "No recent disclosures available."
        
        formatted = []
        for i, disc in enumerate(disclosures[:3], 1):
            formatted.append(f"{i}. {disc.get('title', 'N/A')} - {disc.get('filing_date', 'N/A')}")
        
        return "\n".join(formatted)
    
    def _format_trends_for_prompt(self, trends: List[Dict[str, Any]]) -> str:
        """Format trends for LLM prompt"""
        if not trends:
            return "No specific trends identified."
        
        formatted = []
        for i, trend in enumerate(trends[:3], 1):
            formatted.append(f"{i}. {trend.get('trend_name', 'N/A')}: {trend.get('description', 'N/A')[:100]}")
        
        return "\n".join(formatted)
    
    def _format_suppliers_for_prompt(self, suppliers: List[Dict[str, Any]]) -> str:
        """Format suppliers for LLM prompt"""
        if not suppliers:
            return "No supply chain data available."
        
        formatted = []
        for i, supplier in enumerate(suppliers[:5], 1):
            formatted.append(f"{i}. {supplier.get('supplier_name', 'N/A')} ↔ {supplier.get('oem_name', 'N/A')}")
        
        return "\n".join(formatted)
    
    def generate_consensus_analysis(
        self,
        companies: List[str],
        news_articles: List[Dict[str, Any]],
        disclosures: List[Dict[str, Any]],
        market_trends: List[Dict[str, Any]],
        supplier_relationships: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Generate qualitative analysis for multiple companies
        
        Args:
            companies: List of company names
            news_articles: All news articles
            disclosures: All disclosure data
            market_trends: Market trends
            supplier_relationships: All supplier relationships
        
        Returns:
            Dict mapping company name to analysis
        """
        results = {}
        
        print(f"\n    🔍 LLM 정성 분석 시작 ({len(companies)}개 기업)")
        
        for company in companies:
            print(f"       분석 중: {company}...")
            
            analysis = self.analyze_company_qualitative(
                company,
                news_articles,
                disclosures,
                market_trends,
                supplier_relationships
            )
            
            results[company] = analysis
            
            print(f"       ✅ {company}: 평점 {analysis['overall_rating']}/10 (신뢰도 {analysis['confidence']}%)")
        
        print(f"    ✅ 정성 분석 완료\n")
        
        return results

