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


class MarketTrendAgent:
    def __init__(self, web_search_tool, llm_tool, dart_tool=None):
        self.web_search_tool = web_search_tool
        self.llm_tool = llm_tool
        self.dart_tool = dart_tool
        self.gnews_tool = GNewsTool()  # GNews 도구 추가
        self.dart_tagger = DARTTagger(dart_tool=dart_tool) if dart_tool else None  # DART Tagger 추가
        self.sec_tool = SECEdgarTool()  # SEC EDGAR 도구 추가
        self.sec_tagger = SECTagger(sec_tool=self.sec_tool)  # SEC Tagger 추가

    def analyze_market_trends(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            print("\n============================")
            print("[MarketTrendAgent] Start")
            print("============================")

            news_articles = self._collect_news_articles_bootstrap(state)

            # DART 공시 데이터 수집
            disclosure_data = self._collect_disclosures(news_articles, state)

            categorized_keywords = self._extract_and_categorize_keywords(news_articles, disclosure_data, [])
            market_trends: List[Dict[str, Any]] = []

            result = self._structure_analysis_result(
                news_articles, disclosure_data, [], categorized_keywords, market_trends, state
            )

            print(f"MarketTrend: news={len(news_articles)} disclosures={len(disclosure_data)}")
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
        
        print("    Tavily를 사용한 최근 전기차 뉴스 수집 중... (GNews 건너뛰기)")
        
        # GNews 건너뛰고 바로 Tavily 웹 검색 사용 (4000 크레딧)
        if True:  # 항상 웹 검색 사용
            print("    Tavily 뉴스 검색 시작... (고용량 모드 - 4000 크레딧)")
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
                    print(f"    [WARNING] '{q}' 웹 검색 실패: {e}")
                    continue
        
        # 3. 최근 N일 이내 필터링 (config에서 설정)
        days_ago = state.get('config', {}).get('days_ago', 7)
        articles = self._filter_recent_articles(articles, days=days_ago)
        
        # 4. 최대 개수 제한
        articles = articles[:max_articles]
        
        print(f"    [OK] 총 {len(articles)}개 뉴스 기사 수집 완료 (최근 {days_ago}일 이내)")
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
        뉴스 기사에서 기업명을 추출하여 DART 공시 데이터 수집
        """
        disclosure_data = []
        
        # DART가 없으면 빈 리스트 반환
        if not self.dart_tool or not self.dart_tagger:
            print("    [INFO] DART API가 설정되지 않았습니다. 공시 데이터를 건너뜁니다.")
            return disclosure_data
        
        try:
            print("\n    ========================================")
            print("    [공시 데이터 수집 시작]")
            print("    ========================================")
            
            # 1. 뉴스 기사에서 기업명 추출
            all_text = ' '.join([
                f"{article.get('title', '')} {article.get('content', '')}" 
                for article in news_articles
            ])
            
            company_names = self.dart_tagger.extract_company_names(all_text)
            
            if not company_names:
                print("    [INFO] 뉴스에서 한국 EV 기업을 찾지 못했습니다.")
                print("    [INFO] 주요 한국 EV 기업의 공시를 자동으로 수집합니다...")
                # 주요 기업 리스트 사용
                company_names = [
                    'LG에너지솔루션', '삼성SDI', 'SK온', 
                    '현대자동차', '기아', '에코프로비엠'
                ]
            
            print(f"    [OK] 공시 수집 대상 기업: {len(company_names)}개")
            for company in company_names[:5]:  # 상위 5개만 출력
                print(f"        - {company}")
            if len(company_names) > 5:
                print(f"        ... 외 {len(company_names) - 5}개")
            
            # 2. 각 기업의 최근 공시 수집
            days_ago = state.get('config', {}).get('days_ago', 30)
            max_disclosures = state.get('config', {}).get('max_disclosures_per_company', 10)
            
            # 기업별로 더 많은 공시 수집
            all_disclosures = []
            for company in company_names:
                company_disclosures = self.dart_tagger.collect_company_disclosures(
                    [company], 
                    days=days_ago
                )
                # 기업당 최대 개수 제한
                all_disclosures.extend(company_disclosures[:max_disclosures])
            
            # 3. EV 관련 공시만 필터링
            if all_disclosures:
                ev_disclosures = self.dart_tagger.filter_ev_disclosures(all_disclosures)
                disclosure_data = ev_disclosures
                
                print(f"    [OK] 총 {len(all_disclosures)}개 공시 중 {len(ev_disclosures)}개 EV 관련 공시 선별")
                
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
                print("    [WARNING] 공시 데이터를 찾지 못했습니다.")
            
            print("    ========================================\n")
            
        except Exception as e:
            print(f"    [ERROR] 한국 기업 공시 수집 실패: {e}")
            import traceback
            traceback.print_exc()
        
        # 해외 기업 공시 수집 (SEC EDGAR)
        try:
            print("\n    ========================================")
            print("    [해외 기업 공시 데이터 수집 시작 - SEC EDGAR]")
            print("    ========================================")
            
            # 1. 뉴스 기사에서 해외 기업명 추출
            overseas_companies = self.sec_tagger.extract_company_names(all_text)
            
            if not overseas_companies:
                print("    [INFO] 뉴스에서 해외 EV 기업을 찾지 못했습니다.")
                print("    [INFO] 주요 해외 EV 기업의 공시를 자동으로 수집합니다...")
                # 주요 미국 기업 리스트 사용
                overseas_companies = ['Tesla', 'GM', 'Ford']
            
            print(f"    [OK] 공시 수집 대상 해외 기업: {len(overseas_companies)}개")
            for company in overseas_companies[:5]:
                print(f"        - {company}")
            if len(overseas_companies) > 5:
                print(f"        ... 외 {len(overseas_companies) - 5}개")
            
            # 2. 각 기업의 최근 공시 수집
            max_sec_filings = state.get('config', {}).get('max_sec_filings_per_company', 8)
            overseas_filings = self.sec_tagger.collect_company_filings(
                overseas_companies,
                max_filings=max_sec_filings
            )
            
            # 3. EV 관련 공시만 필터링
            if overseas_filings:
                ev_filings = self.sec_tagger.filter_ev_filings(overseas_filings)
                disclosure_data.extend(ev_filings)  # 한국 공시와 합치기
                
                print(f"    [OK] 총 {len(overseas_filings)}개 공시 중 {len(ev_filings)}개 EV 관련 공시 선별")
                
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
                        if disc.get('description'):
                            print(f"          {disc['description']}")
            else:
                print("    [WARNING] 해외 기업 공시 데이터를 찾지 못했습니다.")
            
            print("    ========================================\n")
            
        except Exception as e:
            print(f"    [ERROR] 해외 기업 공시 수집 실패: {e}")
            import traceback
            traceback.print_exc()
        
        return disclosure_data

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

