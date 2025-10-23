"""
Clean MarketTrendAgent implementation.
Collects EV-related news via a bootstrap search and returns a structured result
expected by the workflow graph.
"""

from typing import Dict, Any, List
from datetime import datetime
from tools.gnews_tool import GNewsTool


class MarketTrendAgent:
    def __init__(self, web_search_tool, llm_tool, dart_tool=None):
        self.web_search_tool = web_search_tool
        self.llm_tool = llm_tool
        self.dart_tool = dart_tool
        self.gnews_tool = GNewsTool()  # GNews 도구 추가

    def analyze_market_trends(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            print("\n============================")
            print("[MarketTrendAgent] Start")
            print("============================")

            news_articles = self._collect_news_articles_bootstrap(state)

            # Optionally collect disclosures if DART is available and companies are known
            disclosure_data: List[Dict[str, Any]] = []

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
        
        print("    GNews를 사용한 최근 전기차 뉴스 수집 중...")
        
        try:
            # 1. GNews로 전기차 관련 뉴스 검색 (최대 10개)
            ev_articles = self.gnews_tool.search_ev_news(max_results=max_articles)
            articles.extend(ev_articles)
            print(f"    [OK] GNews에서 {len(ev_articles)}개 EV 뉴스 수집")
            
        except Exception as e:
            print(f"    [WARNING] GNews 검색 실패: {e}")
        
        # 2. GNews가 실패하거나 결과가 부족한 경우 웹 검색 사용 (영어 검색어로 변경, 쿼리 수 감소)
        if len(articles) < 5:
            print("    웹 검색으로 추가 뉴스 수집 중...")
            # 쿼리 수를 5개에서 3개로 줄여서 속도 개선
            seed_queries = [
                "EV market trends 2024",
                "electric vehicle battery news", 
                "Tesla stock news latest"
            ]
            
            for i, q in enumerate(seed_queries):
                if len(articles) >= max_articles:
                    break
                    
                try:
                    remaining = max_articles - len(articles)
                    results_needed = min(3, remaining)  # 2개에서 3개로 증가하여 효율성 개선
                    
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
        최근 N일 이내 뉴스만 필터링
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
                        recent_articles.append(article)
                except:
                    # 날짜 파싱 실패 시 포함
                    recent_articles.append(article)
            else:
                # 날짜 정보가 없으면 포함
                recent_articles.append(article)
        
        print(f"    [FILTER] 최근 {days}일 이내 기사: {len(recent_articles)}개")
        return recent_articles

    def _extract_and_categorize_keywords(
        self,
        news_articles: List[Dict[str, Any]],
        disclosure_data: List[Dict[str, Any]],
        analyst_reports: List[Dict[str, Any]],
    ) -> Dict[str, List[str]]:
        """   ( )"""
        import re
        from collections import Counter

        #      ( + )
        ev_companies = [
            #  
            '', '', '', '',
            #  
            'LG', 'LG', 'SDI', 'SK', 'SK',
            '', '', '', '',
            #  /
            '', 'LG', 'LS', '',
            #  
            'Tesla', '', 'BYD', 'BMW', 'Mercedes', '',
            'Volkswagen', '', 'GM', 'Ford', '',
            'Nio', 'Xpeng', 'Li Auto', 'Lucid', 'Rivian',
            #  
            'CATL', 'Panasonic', '', 'BYD Battery',
        ]

        #   
        texts: List[str] = []
        for a in news_articles:
            texts.append((a.get('title') or '') + ' ' + (a.get('content') or ''))
        blob = ' '.join(texts)

        #  
        found_companies = []
        for company in ev_companies:
            if company in blob:
                found_companies.append(company)

        #    ( )
        tokens = re.findall(r"[A-Za-z][A-Za-z0-9\-\+]+|[-]{2,}", blob)
        counts = Counter([t.lower() for t in tokens if len(t) > 2])
        top_keywords = [w for (w, _) in counts.most_common(20)]

        #    ( )
        korean_companies = re.findall(r'[-]+(?:|||||||SDI|)', blob)
        found_companies.extend(set(korean_companies))

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

        print(f"   [OK]   : {len(found_companies)}")
        for company in found_companies[:10]:  #  10 
            print(f"      - {company}")

        return {
            'companies': found_companies,  #  
            'tech': top_keywords[:7],
            'market': top_keywords[7:14],
            'investment': top_keywords[14:20],
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

