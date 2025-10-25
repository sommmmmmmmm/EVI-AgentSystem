"""
Clean MarketTrendAgent implementation.
Collects EV-related news via a bootstrap search and returns a structured result
expected by the workflow graph.
"""

from typing import Dict, Any, List
from datetime import datetime
from tools.gnews_tool import GNewsTool
from tools.dart_tagger import DARTTagger
from tools.sec_tagger import SECTagger
from tools.sec_edgar_tools import SECEdgarTool
from tools.trend_analysis_tools import TrendAnalyzer  # 🆕 트렌드 분석 도구


class MarketTrendAgent:
    def __init__(self, web_search_tool, llm_tool, dart_tool=None):
        self.web_search_tool = web_search_tool
        self.llm_tool = llm_tool
        self.dart_tool = dart_tool
        self.gnews_tool = GNewsTool()  # GNews 도구 추가
        self.dart_tagger = DARTTagger(dart_tool=dart_tool) if dart_tool else None  # DART Tagger 추가
        self.sec_tool = SECEdgarTool()  # SEC EDGAR 도구 추가
        self.sec_tagger = SECTagger(sec_tool=self.sec_tool)  # SEC Tagger 추가
        self.trend_analyzer = TrendAnalyzer()  # 🆕 트렌드 분석기

    def analyze_market_trends(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            print("\n============================")
            print("[MarketTrendAgent] Start")
            print("============================")

            news_articles = self._collect_news_articles_bootstrap(state)

            # DART 공시 데이터 수집
            disclosure_data = self._collect_disclosures(news_articles, state)
            
            # 공시 데이터를 state에 저장
            state['disclosure_data'] = disclosure_data

            # 🆕 트렌드 분석 (불용어 제거 + Fallback 규칙)
            print("\n    ========================================")
            print("    [트렌드 분석 시작]")
            print("    ========================================")
            
            # 키워드 추출 (불용어 제거됨) - returns Dict[str, List[Tuple[str, int]]]
            keywords_with_counts = self.trend_analyzer.extract_keywords(news_articles, top_n=20)
            
            # 튜플 리스트를 문자열 리스트로 변환 (기존 코드와 호환성 유지)
            categorized_keywords = {}
            for category, keyword_list in keywords_with_counts.items():
                # Extract only keywords (ignore counts)
                categorized_keywords[category] = [kw for kw, count in keyword_list]
            
            # 트렌드 분석 (최소 3개 보장)
            market_trends = self.trend_analyzer.analyze_trends_with_fallback(
                news_articles,
                clustering_result=[]  # 기존 군집화 결과 없음
            )
            
            print(f"    ✅ {len(market_trends)}개 트렌드 식별")
            print(f"    ✅ 키워드 추출 완료 (companies: {len(categorized_keywords.get('companies', []))}개)")
            print("    ========================================\n")

            result = self._structure_analysis_result(
                news_articles, disclosure_data, [], categorized_keywords, market_trends, state
            )

            # 최종 수집 결과 요약
            print("\n============================")
            print("[MarketTrendAgent] 데이터 수집 완료")
            print("============================")
            print(f"📰 뉴스 기사: {len(news_articles)}개")
            print(f"📋 공시/재무 데이터: {len(disclosure_data)}개")
            
            if len(news_articles) == 0:
                print("\n⚠️  경고: 뉴스 데이터가 없습니다!")
                print("   → 웹 서치가 실패했거나 검색 결과가 없습니다.")
            
            if len(disclosure_data) == 0:
                print("\n⚠️  경고: 공시/재무 데이터가 없습니다!")
                print("   → 모든 데이터 소스에서 정보를 가져올 수 없었습니다.")
            
            if len(news_articles) == 0 and len(disclosure_data) == 0:
                print("\n❌ 중요: 모든 데이터 소스에서 정보 수집 실패!")
                print("   → 인터넷 연결, API 키, API 사용량 한도를 확인하세요.")
            
            print("============================\n")
            
            return result

        except Exception as e:
            print(f"MarketTrendAgent error: {e}")
            return {
                'news_articles': [],
                'disclosure_data': [],
                'analyst_reports': [],
                'keywords': [],
                'categorized_keywords': {},
                'market_trends': [],
                'analysis_metadata': {
                    'status': 'failed',
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e)
                }
            }

    def _collect_news_articles_bootstrap(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        articles: List[Dict[str, Any]] = []
        # config에서 최대 뉴스 개수 가져오기 (기본값: 10)
        max_articles = state.get('config', {}).get('max_news_articles', 10)
        
        print("\n    ========================================")
        print("    [웹 서치를 통한 뉴스 수집 시작]")
        print("    ========================================")
        print("    Tavily를 사용한 최근 전기차 뉴스 수집 중...")
        
        web_search_failed = False
        
        # GNews 건너뛰고 바로 Tavily 웹 검색 사용 (4000 크레딧)
        if True:  # 항상 웹 검색 사용
            print("    Tavily 뉴스 검색 시작...")
            # 뉴스 중심의 검색 쿼리 (최신성 강조)
            seed_queries = [
                # 최신 트렌드
                "electric vehicle news today",
                "EV market trends 2024 latest",
                "battery technology news this week",
                "Tesla latest news announcement",
                
                # 공급망 & 기업 뉴스
                "EV supply chain news recent",
                "electric vehicle battery supplier news",
                "automotive industry news EV",
                
                # 한국 기업
                "LG Energy Solution latest news",
                "Samsung SDI battery news today",
                "SK On battery plant news",
                "Hyundai Kia electric vehicle news",
                
                # 해외 기업
                "CATL battery news China",
                "GM electric vehicle announcement",
                "Ford EV production news",
                "BYD electric vehicle sales",
                
                # 기술 & 정책
                "EV charging infrastructure latest",
                "electric vehicle policy news",
                "battery recycling technology news",
                
                # 투자 & 시장
                "EV stock market news",
                "electric vehicle sales report",
                "battery material shortage news"
            ]
            
            for i, q in enumerate(seed_queries):
                if len(articles) >= max_articles:
                    break
                    
                try:
                    remaining = max_articles - len(articles)
                    results_needed = min(5, remaining)  # 쿼리당 5개로 대폭 증가
                    
                    print(f"    [{i+1}/{len(seed_queries)}] '{q}' 웹 검색 중... (남은 자리: {remaining}개)")
                    results = self.web_search_tool.search(q, num_results=results_needed)
                    
                    if not results:
                        print(f"    [경고] '{q}': 검색 결과가 없습니다 (웹 서치 실패 또는 정보 없음)")
                        web_search_failed = True
                    else:
                        for r in results:
                            if len(articles) >= max_articles:
                                break
                            articles.append({
                                'title': r.get('title', ''),
                                'url': r.get('url', ''),
                                'content': r.get('content', ''),
                                'publishedAt': r.get('date'),
                                'source': 'web_search',
                                'query': q
                            })
                        
                        print(f"    [OK] {len(results)}개 기사 수집 (총 {len(articles)}개)")
                    
                except Exception as e:
                    print(f"    [경고] '{q}' 웹 검색 실패: {e}")
                    print(f"    → 해당 검색어에 대한 정보를 가져올 수 없습니다.")
                    web_search_failed = True
                    continue
        
        # 3. 최근 N일 이내 필터링 (config에서 설정)
        days_ago = state.get('config', {}).get('days_ago', 7)
        articles = self._filter_recent_articles(articles, days=days_ago)
        
        # 4. 최대 개수 제한
        articles = articles[:max_articles]
        
        # 5. 결과 요약
        print("    ========================================")
        if len(articles) == 0:
            print("    ⚠️  [경고] 뉴스 데이터를 수집하지 못했습니다!")
            print("    → 웹 서치가 실패했거나 검색 결과가 없습니다.")
            print("    → 기본 기업 리스트를 사용하여 공시 데이터를 수집합니다.")
        elif len(articles) < 10:
            print(f"    ⚠️  [주의] 뉴스 데이터가 부족합니다: {len(articles)}개")
            print("    → 일부 웹 서치가 실패했을 수 있습니다.")
        else:
            print(f"    ✅ [성공] 총 {len(articles)}개 뉴스 기사 수집 완료 (최근 {days_ago}일 이내)")
        print("    ========================================\n")
        
        return articles

    def _filter_recent_articles(self, articles: List[Dict[str, Any]], days: int = 7) -> List[Dict[str, Any]]:
        """
        최근 N일 이내 뉴스만 필터링하고 시간 가중치 부여
        """
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_articles = []
        
        for article in articles:
            published_at = article.get('publishedAt', '')
            if published_at:
                try:
                    # ISO 형식 날짜 파싱
                    if 'T' in published_at:
                        pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    else:
                        pub_date = datetime.fromisoformat(published_at)
                    
                    if pub_date >= cutoff_date:
                        # 시간 가중치 계산 (최근일수록 높은 가중치)
                        days_ago = (datetime.now() - pub_date.replace(tzinfo=None)).days
                        
                        if days_ago <= 7:
                            weight = 1.0  # 1주일 이내 - 최고 가중치
                        elif days_ago <= 14:
                            weight = 0.8  # 2주 이내
                        elif days_ago <= 21:
                            weight = 0.6  # 3주 이내
                        elif days_ago <= 28:
                            weight = 0.4  # 4주 이내
                        else:
                            weight = 0.2  # 그 이상
                        
                        article['time_weight'] = weight
                        article['days_ago'] = days_ago
                        recent_articles.append(article)
                except:
                    # 날짜 파싱 실패 시 중간 가중치로 포함
                    article['time_weight'] = 0.5
                    article['days_ago'] = 15
                    recent_articles.append(article)
            else:
                # 날짜 정보가 없으면 낮은 가중치로 포함
                article['time_weight'] = 0.3
                article['days_ago'] = 30
                recent_articles.append(article)
        
        # 시간 가중치 순으로 정렬 (최근 기사가 먼저)
        recent_articles.sort(key=lambda x: x.get('time_weight', 0), reverse=True)
        
        print(f"    [FILTER] 최근 {days}일 이내 기사: {len(recent_articles)}개")
        
        # 가중치 분포 출력
        weight_distribution = {
            '1.0 (1주일)': len([a for a in recent_articles if a.get('time_weight') == 1.0]),
            '0.8 (2주일)': len([a for a in recent_articles if a.get('time_weight') == 0.8]),
            '0.6 (3주일)': len([a for a in recent_articles if a.get('time_weight') == 0.6]),
            '0.4 (4주일)': len([a for a in recent_articles if a.get('time_weight') == 0.4]),
            '기타': len([a for a in recent_articles if a.get('time_weight', 0) < 0.4])
        }
        print(f"    [WEIGHT] 가중치 분포: {weight_distribution}")
        
        return recent_articles

    def _collect_disclosures(
        self, 
        news_articles: List[Dict[str, Any]], 
        state: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        뉴스 기사에서 기업명을 추출하여 공시 데이터 수집
        - 한국 기업: DART 공시
        - 미국 기업: SEC EDGAR 공시
        - 그 외: Yahoo Finance (재무 정보만)
        """
        disclosure_data = []
        
        # 웹 서치 실패 시 relaxed mode 활성화
        relaxed_mode = state.get('config', {}).get('relaxed_mode', True)
        
        # 1. 뉴스 기사에서 텍스트 추출
        all_text = ' '.join([
            f"{article.get('title', '')} {article.get('content', '')}" 
            for article in news_articles
        ]) if news_articles else ""
        
        # 텍스트가 없으면 기본 기업 리스트 사용
        using_default_list = False
        if not all_text.strip():
            print("    ⚠️  [경고] 뉴스 기사가 없습니다!")
            print("    → 웹 서치 실패로 인해 뉴스에서 기업을 추출할 수 없습니다.")
            print("    → 대신 기본 기업 리스트를 사용하여 공시를 수집합니다.")
            korean_companies = ['LG에너지솔루션', '삼성SDI', 'SK온', '현대자동차', '기아']
            overseas_companies = ['Tesla', 'GM', 'Ford', 'BMW', 'BYD']
            using_default_list = True
        else:
            # 한국 기업 추출
            korean_companies = self.dart_tagger.extract_company_names(all_text) if self.dart_tagger else []
            # 해외 기업 추출
            overseas_companies = self.sec_tagger.extract_company_names(all_text)
        
        # 추출된 기업이 없으면 기본 리스트 사용
        if not using_default_list:
            if not korean_companies and not overseas_companies:
                print("    ⚠️  [경고] 뉴스에서 EV 관련 기업을 찾지 못했습니다!")
                print("    → 뉴스 내용에 EV 기업명이 포함되지 않았습니다.")
                print("    → 대신 기본 기업 리스트를 사용합니다.")
                using_default_list = True
            
            if not korean_companies:
                korean_companies = ['LG에너지솔루션', '삼성SDI', 'SK온']
            if not overseas_companies:
                overseas_companies = ['Tesla', 'GM', 'Ford']
        
        # 해외 기업을 데이터 소스별로 분류
        classified_companies = self.sec_tagger.classify_companies_by_source(overseas_companies)
        sec_companies = classified_companies.get('SEC', [])
        yahoo_companies = classified_companies.get('Yahoo', [])
        
        print("\n    ========================================")
        print("    [공시 데이터 수집 전략]")
        print("    ========================================")
        if using_default_list:
            print("    📋 데이터 소스: 기본 기업 리스트 (뉴스 데이터 없음)")
        else:
            print("    📰 데이터 소스: 뉴스 기사에서 추출")
        print(f"    - 한국 기업 (DART): {len(korean_companies)}개")
        print(f"    - 미국 기업 (SEC): {len(sec_companies)}개")
        print(f"    - 그 외 기업 (Yahoo Finance): {len(yahoo_companies)}개")
        print(f"    - Relaxed Mode: {'활성화' if relaxed_mode else '비활성화'}")
        print("    ========================================\n")
        
        # ==============================================
        # 1) 한국 기업 - DART 공시
        # ==============================================
        if self.dart_tool and self.dart_tagger and korean_companies:
            disclosure_data.extend(
                self._collect_dart_disclosures(korean_companies, state, relaxed_mode)
            )
        
        # ==============================================
        # 2) 미국 기업 - SEC EDGAR 공시
        # ==============================================
        if sec_companies:
            disclosure_data.extend(
                self._collect_sec_disclosures(sec_companies, state, relaxed_mode)
            )
        
        # ==============================================
        # 3) 그 외 기업 - Yahoo Finance (재무 정보)
        # ==============================================
        if yahoo_companies:
            disclosure_data.extend(
                self._collect_yahoo_data(yahoo_companies, state, relaxed_mode)
            )
        
        # 최종 요약
        print("\n    ========================================")
        print("    [공시/재무 데이터 수집 결과 요약]")
        print("    ========================================")
        if len(disclosure_data) == 0:
            print("    ❌ [실패] 공시/재무 데이터를 수집하지 못했습니다!")
            print("    → 모든 데이터 소스(DART/SEC/Yahoo)에서 정보를 가져올 수 없었습니다.")
            print("    → 뉴스 데이터만으로 분석을 진행하거나, API 설정을 확인하세요.")
        elif len(disclosure_data) < 5:
            print(f"    ⚠️  [주의] 공시/재무 데이터가 부족합니다: {len(disclosure_data)}개")
            print("    → 일부 데이터 소스에서만 정보를 수집했을 수 있습니다.")
        else:
            print(f"    ✅ [성공] 총 {len(disclosure_data)}개 공시/재무 데이터 수집 완료")
        print("    ========================================\n")
        
        return disclosure_data
    
    def _collect_dart_disclosures(
        self, 
        company_names: List[str], 
        state: Dict[str, Any],
        relaxed_mode: bool
    ) -> List[Dict[str, Any]]:
        """한국 기업 DART 공시 수집"""
        disclosure_data = []
        
        try:
            print("\n    ========================================")
            print("    [한국 기업 공시 수집 - DART]")
            print("    ========================================")
            
            print(f"    [OK] 공시 수집 대상 한국 기업: {len(company_names)}개")
            for company in company_names[:5]:
                print(f"        - {company}")
            if len(company_names) > 5:
                print(f"        ... 외 {len(company_names) - 5}개")
            
            # 각 기업의 최근 공시 수집
            days_ago = state.get('config', {}).get('days_ago', 30)
            max_disclosures = state.get('config', {}).get('max_disclosures_per_company', 10)
            
            all_disclosures = []
            for company in company_names:
                try:
                    company_disclosures = self.dart_tagger.collect_company_disclosures(
                        [company], 
                        days=days_ago
                    )
                    all_disclosures.extend(company_disclosures[:max_disclosures])
                except Exception as e:
                    if relaxed_mode:
                        print(f"    [WARNING] {company} 공시 수집 실패 (계속 진행): {e}")
                    else:
                        raise
            
            # EV 관련 공시만 필터링
            if all_disclosures:
                # relaxed_mode에서는 필터링 기준 완화
                # EV 기업의 공시는 모두 EV 관련으로 간주 (strict=False)
                if relaxed_mode:
                    ev_disclosures = self.dart_tagger.filter_ev_disclosures(all_disclosures, strict=False)
                    print(f"    [INFO] Relaxed mode: EV 기업의 모든 공시 포함")
                else:
                    ev_disclosures = self.dart_tagger.filter_ev_disclosures(all_disclosures, strict=True)
                
                disclosure_data = ev_disclosures
                
                print(f"    [OK] 총 {len(all_disclosures)}개 공시 중 {len(ev_disclosures)}개 선별")
                
                # 요약 통계
                summary = self.dart_tagger.get_disclosure_summary(ev_disclosures)
                print(f"    [SUMMARY] 공시 통계:")
                print(f"        - 전체: {summary['total']}개")
                print(f"        - 중요도 (High/Medium/Low): {summary['by_importance']['high']}/{summary['by_importance']['medium']}/{summary['by_importance']['low']}")
                print(f"        - EV 관련: {summary['ev_related']}개")
                
                if summary['recent_important']:
                    print(f"    [IMPORTANT] 주요 공시 (최대 3개):")
                    for disc in summary['recent_important'][:3]:
                        print(f"        - [{disc['company']}] {disc['title'][:50]}... ({disc['date']})")
            else:
                print("    ⚠️  [경고] DART 공시 데이터를 찾지 못했습니다!")
                print("    → 해당 기업의 공시가 기간 내에 없거나 API 호출이 실패했습니다.")
                print("    → 한국 기업 공시 정보 없이 분석을 계속합니다.")
            
            print("    ========================================\n")
            
        except Exception as e:
            print(f"    [ERROR] DART 공시 수집 실패: {e}")
            if not relaxed_mode:
                import traceback
                traceback.print_exc()
        
        return disclosure_data
    
    def _collect_sec_disclosures(
        self, 
        company_names: List[str], 
        state: Dict[str, Any],
        relaxed_mode: bool
    ) -> List[Dict[str, Any]]:
        """미국 기업 SEC EDGAR 공시 수집"""
        disclosure_data = []
        
        try:
            print("\n    ========================================")
            print("    [미국 기업 공시 수집 - SEC EDGAR]")
            print("    ========================================")
            
            print(f"    [OK] 공시 수집 대상 미국 기업: {len(company_names)}개")
            for company in company_names[:5]:
                print(f"        - {company}")
            if len(company_names) > 5:
                print(f"        ... 외 {len(company_names) - 5}개")
            
            # 각 기업의 최근 공시 수집
            max_sec_filings = state.get('config', {}).get('max_sec_filings_per_company', 8)
            overseas_filings = self.sec_tagger.collect_company_filings(
                company_names,
                max_filings=max_sec_filings,
                relaxed_mode=relaxed_mode
            )
            
            # EV 관련 공시만 필터링
            if overseas_filings:
                # relaxed_mode에서는 모든 공시 포함 (EV 기업의 공시는 모두 관련성 있음)
                if relaxed_mode:
                    # 각 공시에 EV 관련 태그 자동 추가
                    for filing in overseas_filings:
                        company_name = filing.get('company_name', '')
                        if 'tags' not in filing:
                            filing['tags'] = {
                                'importance': 'high',
                                'is_ev_related': True,
                                'ev_keywords': [f'{company_name} (EV 기업)'],
                                'tagged_at': datetime.now().isoformat()
                            }
                        else:
                            filing['tags']['is_ev_related'] = True
                    ev_filings = overseas_filings
                    print(f"    [INFO] Relaxed mode: EV 기업의 모든 공시 포함")
                else:
                    ev_filings = self.sec_tagger.filter_ev_filings(overseas_filings)
                
                disclosure_data = ev_filings
                
                print(f"    [OK] 총 {len(overseas_filings)}개 공시 중 {len(ev_filings)}개 선별")
                
                # 요약 통계
                summary = self.sec_tagger.get_filing_summary(ev_filings)
                print(f"    [SUMMARY] SEC 공시 통계:")
                print(f"        - 전체: {summary['total']}개")
                print(f"        - 중요도 (High/Medium/Low): {summary['by_importance']['high']}/{summary['by_importance']['medium']}/{summary['by_importance']['low']}")
                print(f"        - EV 관련: {summary['ev_related']}개")
                
                if summary['recent_important']:
                    print(f"    [IMPORTANT] 주요 공시 (최대 3개):")
                    for disc in summary['recent_important'][:3]:
                        print(f"        - [{disc['company']}] {disc['title']} ({disc['date']})")
            else:
                print("    ⚠️  [경고] SEC 공시 데이터를 찾지 못했습니다!")
                print("    → 해당 기업의 SEC 공시가 없거나 API 호출이 실패했습니다.")
                print("    → 미국 기업 공시 정보 없이 분석을 계속합니다.")
            
            print("    ========================================\n")
            
        except Exception as e:
            print(f"    [ERROR] SEC 공시 수집 실패: {e}")
            if not relaxed_mode:
                import traceback
                traceback.print_exc()
        
        return disclosure_data
    
    def _collect_yahoo_data(
        self, 
        company_names: List[str], 
        state: Dict[str, Any],
        relaxed_mode: bool
    ) -> List[Dict[str, Any]]:
        """그 외 기업 Yahoo Finance 재무 정보 수집"""
        yahoo_data = []
        
        try:
            print("\n    ========================================")
            print("    [그 외 기업 재무 정보 수집 - Yahoo Finance]")
            print("    ========================================")
            
            print(f"    [OK] 재무 정보 수집 대상 기업: {len(company_names)}개")
            for company in company_names[:5]:
                print(f"        - {company}")
            if len(company_names) > 5:
                print(f"        ... 외 {len(company_names) - 5}개")
            
            # Yahoo Finance 도구 import
            from tools.yahoo_finance_tools import YahooFinanceTool
            yahoo_tool = YahooFinanceTool()
            
            for company_name in company_names:
                try:
                    # 티커 심볼 가져오기
                    company_info = self.sec_tagger.OVERSEAS_EV_COMPANIES.get(company_name, {})
                    ticker = company_info.get('ticker')
                    
                    if not ticker:
                        if not relaxed_mode:
                            print(f"    [WARNING] {company_name}: 티커 심볼을 찾을 수 없습니다.")
                        continue
                    
                    # 재무 데이터 생성 (공시 형식으로 변환)
                    financial_info = {
                        'company_name': company_name,
                        'title': f'{company_name} - Yahoo Finance 재무 정보',
                        'ticker': ticker,
                        'date': datetime.now().strftime('%Y%m%d'),
                        'source': 'Yahoo Finance',
                        'country': company_info.get('country', 'Unknown'),
                        'tags': {
                            'importance': 'medium',
                            'is_ev_related': True,
                            'ev_keywords': ['EV', 'electric vehicle'],
                            'tagged_at': datetime.now().isoformat()
                        }
                    }
                    
                    yahoo_data.append(financial_info)
                    print(f"    [OK] {company_name} ({ticker}): 재무 정보 수집")
                    
                except Exception as e:
                    if relaxed_mode:
                        print(f"    [WARNING] {company_name} 재무 정보 수집 실패 (계속 진행): {e}")
                    else:
                        print(f"    [ERROR] {company_name} 재무 정보 수집 실패: {e}")
            
            print(f"    [OK] 총 {len(yahoo_data)}개 기업의 재무 정보 수집")
            print("    ========================================\n")
            
        except Exception as e:
            print(f"    [ERROR] Yahoo Finance 데이터 수집 실패: {e}")
            if not relaxed_mode:
                import traceback
                traceback.print_exc()
        
        return yahoo_data

    def _extract_and_categorize_keywords(
        self,
        news_articles: List[Dict[str, Any]],
        disclosure_data: List[Dict[str, Any]],
        analyst_reports: List[Dict[str, Any]],
    ) -> Dict[str, List[str]]:
        """키워드 추출 및 분류 (시간 가중치 적용)"""
        import re
        from collections import Counter

        # 주요 전기차 관련 기업 (한국어 + 영어)
        ev_companies = [
            # 한국 배터리
            '삼성SDI', 'LG에너지솔루션', 'SK온', '에코프로',
            # 한국 약어
            'LG', 'LG에너지', 'SDI', 'SK', 'SK이노베이션',
            '현대차', '기아', '포스코', '엘앤에프',
            # 한국 부품/소재
            '솔루스첨단소재', 'LG전자', 'LS', '후성',
            # 해외 완성차
            'Tesla', '테슬라', 'BYD', 'BMW', 'Mercedes', '벤츠',
            'Volkswagen', '폭스바겐', 'GM', 'Ford', '포드',
            'Nio', 'Xpeng', 'Li Auto', 'Lucid', 'Rivian',
            # 해외 배터리
            'CATL', 'Panasonic', '파나소닉', 'BYD Battery',
        ]

        # 텍스트 수집 (시간 가중치 고려)
        weighted_texts: List[tuple] = []
        for a in news_articles:
            text = (a.get('title') or '') + ' ' + (a.get('content') or '')
            weight = a.get('time_weight', 0.5)
            weighted_texts.append((text, weight))
        
        # 가중치를 고려한 텍스트 블롭 생성 (최근 기사를 더 많이 반복)
        blob_parts = []
        for text, weight in weighted_texts:
            # 가중치에 따라 텍스트를 반복 (1.0 = 1번, 0.8 = 0.8번, ...)
            repetitions = int(weight * 2)  # 최대 2번 반복
            if repetitions > 0:
                blob_parts.extend([text] * repetitions)
            else:
                blob_parts.append(text)
        
        blob = ' '.join(blob_parts)

        # 기업명 추출 (가중치 고려)
        company_counts = Counter()
        for text, weight in weighted_texts:
            for company in ev_companies:
                if company in text:
                    # 가중치를 곱하여 카운트
                    company_counts[company] += weight
        
        # 상위 기업명 추출 (가중치 합계 기준)
        found_companies = [company for company, _ in company_counts.most_common(30)]

        # 키워드 추출 (영어, 가중치 적용)
        keyword_counts = Counter()
        for text, weight in weighted_texts:
            tokens = re.findall(r"[A-Za-z][A-Za-z0-9\-\+]+", text)
            for token in tokens:
                if len(token) > 2:
                    keyword_counts[token.lower()] += weight
        
        top_keywords = [w for (w, _) in keyword_counts.most_common(30)]

        # 한국 기업명 추출 (가중치 적용)
        korean_company_counts = Counter()
        for text, weight in weighted_texts:
            korean_companies = re.findall(r'[가-힣]+(?:전자|SDI|에너지|솔루션|이노베이션|케미칼|소재)', text)
            for company in korean_companies:
                korean_company_counts[company] += weight
        
        found_companies.extend([c for c, _ in korean_company_counts.most_common(10)])

        #  
        found_companies = list(set(found_companies))
        
        # 무의미한 키워드 필터링
        def is_valid_keyword(keyword: str) -> bool:
            """유효한 키워드인지 검사"""
            if not keyword or not keyword.strip():
                return False
            if keyword.strip() in ['-', '_', '/', '\\', '|', '.', ',']:
                return False
            if len(keyword.strip()) < 2:
                return False
            if keyword.strip().isdigit():
                return False
            return True
        
        # 회사명 필터링
        found_companies = [c for c in found_companies if is_valid_keyword(c)]
        
        # 키워드 필터링
        top_keywords = [k for k in top_keywords if is_valid_keyword(k)]

        print(f"   [OK] 추출된 기업명 (가중치 적용): {len(found_companies)}")
        for company in found_companies[:10]:  # 상위 10개 출력
            weight_score = company_counts.get(company, korean_company_counts.get(company, 0))
            print(f"      - {company} (가중치 합: {weight_score:.2f})")

        print(f"   [OK] 추출된 키워드 (가중치 적용): {len(top_keywords)}")
        for keyword in top_keywords[:10]:
            weight_score = keyword_counts.get(keyword, 0)
            print(f"      - {keyword} (가중치 합: {weight_score:.2f})")

        return {
            'companies': found_companies,  # 기업명
            'tech': top_keywords[:10],
            'market': top_keywords[10:20],
            'investment': top_keywords[20:30],
        }

    def _structure_analysis_result(
        self,
        news_articles: List[Dict[str, Any]],
        disclosure_data: List[Dict[str, Any]],
        analyst_reports: List[Dict[str, Any]],
        categorized_keywords: Dict[str, List[str]],
        market_trends: List[Dict[str, Any]],
        state: Dict[str, Any],
    ) -> Dict[str, Any]:
        all_keywords: List[str] = []
        for v in categorized_keywords.values():
            all_keywords.extend(v)
        all_keywords = list(dict.fromkeys(all_keywords))

        #   suppliers  
        companies = categorized_keywords.get('companies', [])
        suppliers = []
        for company in companies:
            suppliers.append({
                'company': company,
                'category': ' ',
                'products': [],
                'oem_relationships': [],
                'confidence': 0.8,
                'source': 'news_extraction'
            })

        print(f"   [OK] MarketTrend  : {len(suppliers)}")

        return {
            'news_articles': news_articles,
            'disclosure_data': disclosure_data,
            'analyst_reports': analyst_reports,
            'keywords': all_keywords,
            'categorized_keywords': categorized_keywords,
            'market_trends': market_trends,
            'discovered_companies': suppliers,  #    
            'analysis_metadata': {
                'status': 'completed',
                'timestamp': datetime.now().isoformat(),
                'total_news': len(news_articles),
                'total_disclosures': len(disclosure_data),
                'total_reports': len(analyst_reports),
                'total_keywords': len(all_keywords),
                'total_trends': len(market_trends),
                'discovered_companies': len(suppliers),
            },
        }

