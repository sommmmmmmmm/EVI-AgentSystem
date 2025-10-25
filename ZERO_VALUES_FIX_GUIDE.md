# 보고서 0값 문제 해결 가이드

## 📋 문제 진단

보고서에서 다음과 같은 0값들이 발견되었습니다:

| 문제 | 증상 | 원인 |
|------|------|------|
| **트렌드 분석** | "주요 트렌드 0개" | 불용어 제거 안됨, 군집화 임계치 과도 |
| **키워드** | "the, and, that" 상위 노출 | 언어별 불용어 처리 미흡 |
| **공급망** | "13개 중 0개 신규 발견" | 검증 임계치(0.7) 너무 높음 |
| **리스크** | "0개 저위험 기업" | 리스크 필터링 과도, JSON 파싱 실패 |
| **공시** | "공시 데이터 없음" | CIK 패딩 오류, 국가별 API 라우팅 문제 |

---

## ✅ 해결 방법

### 1. 트렌드 분석 개선 (`trend_analysis_tools.py`)

**문제**: 불용어 제거 안됨, 군집화 실패 시 빈 결과

**해결**:
- ✅ 언어 감지 (한국어/영어) + 언어별 불용어 제거
- ✅ 군집화 임계치 하향 (10→3개, 유사도 0.8→0.6)
- ✅ **Fallback 규칙**: 군집화 실패 시 키워드 기반 트렌드 3-5개 자동 생성

**사용법**:
```python
from tools.trend_analysis_tools import TrendAnalyzer

analyzer = TrendAnalyzer()

# 키워드 추출 (불용어 제거 포함)
keywords = analyzer.extract_keywords(news_articles, top_n=20)

# 트렌드 분석 (Fallback 포함)
trends = analyzer.analyze_trends_with_fallback(
    news_articles,
    clustering_result=[]  # 군집화 실패 시
)
# → 최소 3개 트렌드 보장
```

**통합 방법**:
```python
# agents/market_trend_agent.py
from tools.trend_analysis_tools import TrendAnalyzer

class MarketTrendAgent:
    def __init__(self):
        self.trend_analyzer = TrendAnalyzer()
    
    def analyze_market_trends(self, state):
        news_articles = state.get('news_articles', [])
        
        # 기존 군집화 시도
        clustering_result = self._cluster_news(news_articles)
        
        # Fallback 포함 트렌드 분석
        trends = self.trend_analyzer.analyze_trends_with_fallback(
            news_articles,
            clustering_result=clustering_result
        )
        
        # 키워드 추출 (불용어 제거됨)
        keywords = self.trend_analyzer.extract_keywords(news_articles, top_n=20)
        
        state['trends'] = trends
        state['keywords'] = keywords
        return state
```

---

### 2. 공급망 스코어링 개선 (`supplier_scoring_tools.py`)

**문제**: 검증 임계치(0.7) 너무 높아서 대부분 필터링됨

**해결**:
- ✅ **2단계 버킷**: Verified(≥0.7) / Discovery(0.4-0.69) 분리
- ✅ 최근성 보너스 (+0.0 ~ +0.2)
- ✅ 다중 출처 보너스 (+0.05 ~ +0.15)
- ✅ 출처별 가중치 (공식 발표 1.0, 뉴스 0.7, SNS 0.4)

**사용법**:
```python
from tools.supplier_scoring_tools import SupplierScorer

scorer = SupplierScorer()

# 관계 스코어링
result = scorer.score_relationship(
    supplier_name='LG Energy Solution',
    oem_name='Tesla',
    relationship_type='battery_supplier',
    evidence=[
        {
            'source_type': 'official_announcement',
            'date': '2024-10-01',
            'text': 'LG signed battery supply agreement with Tesla',
            'url': 'https://example.com/news1'
        },
        {
            'source_type': 'news_article',
            'date': '2024-10-05',
            'text': 'Tesla confirms LG as battery partner',
            'url': 'https://example.com/news2'
        }
    ]
)

print(f"Confidence: {result['confidence']}")  # 0.95 (다중 출처 + 최근)
print(f"Tier: {result['tier']}")  # 'verified'

# 발견 단계(Discovery)도 포함
summary = scorer.generate_summary(all_relationships)
print(f"Verified: {summary['verified']}")  # 검증된 관계
print(f"Discovery: {summary['discovery']}")  # 발견 단계 관계
```

**통합 방법**:
```python
# agents/supplier_matching_agent.py
from tools.supplier_scoring_tools import SupplierScorer

class SupplierMatchingAgent:
    def __init__(self):
        self.scorer = SupplierScorer()
    
    def match_suppliers(self, state):
        # 공급업체-OEM 관계 추출
        relationships = self._extract_relationships(state)
        
        # 각 관계 스코어링
        scored_relationships = []
        for rel in relationships:
            score_result = self.scorer.score_relationship(
                supplier_name=rel['supplier'],
                oem_name=rel['oem'],
                relationship_type=rel['type'],
                evidence=rel['evidence']
            )
            scored_relationships.append(score_result)
        
        # Discovery(0.4+) 이상만 포함
        filtered = self.scorer.filter_by_tier(
            scored_relationships,
            min_tier='discovery'
        )
        
        # 요약 통계
        summary = self.scorer.generate_summary(scored_relationships)
        
        state['suppliers_verified'] = filtered
        state['supplier_summary'] = summary
        return state
```

---

### 3. 공시 데이터 라우팅 개선 (`disclosure_routing_tools.py`)

**문제**: CIK 제로패딩 누락, 국가별 API 라우팅 실패

**해결**:
- ✅ **CIK 10자리 제로패딩** (1318605 → 0001318605)
- ✅ 국가별 API 라우팅 (US=SEC EDGAR, KR=DART, CN/HK=거래소)
- ✅ Fallback skeleton (None 사용, 0으로 대체 안함)
- ✅ SEC 헤더 준수 (User-Agent에 연락처 포함)

**사용법**:
```python
from tools.disclosure_routing_tools import DisclosureRouter

router = DisclosureRouter()

# CIK 정규화
cik = router.normalize_cik('1318605')  # → '0001318605'

# 국가 감지 및 라우팅
route = router.route_disclosure_request(
    company_name='Tesla',
    ticker='TSLA',
    cik='1318605'
)

print(f"Country: {route['country']}")  # US
print(f"API: {route['api']}")  # SEC_EDGAR
print(f"CIK: {route['cik']}")  # 0001318605
print(f"URL: {route['api_url']}")  # https://data.sec.gov/submissions/CIK0001318605.json

# SEC 헤더
headers = router.get_sec_request_headers(
    user_agent_name='EVI-AgentSystem',
    contact_email='admin@example.com'
)

# 실패 시 Fallback
if not route['success']:
    fallback = router.create_fallback_skeleton(
        company_name='Tesla',
        error_message=route['error']
    )
    # fallback['financial_data']['revenue'] = None (0이 아님!)
```

**통합 방법**:
```python
# agents/financial_analyzer_agent.py
from tools.disclosure_routing_tools import DisclosureRouter
import requests

class FinancialAnalyzerAgent:
    def __init__(self):
        self.router = DisclosureRouter()
    
    def analyze_financials(self, state):
        companies = state.get('suppliers_verified', [])
        
        financial_data = []
        for company in companies:
            # 라우팅 결정
            route = self.router.route_disclosure_request(
                company_name=company['name'],
                ticker=company.get('ticker'),
                cik=company.get('cik')
            )
            
            if not route['success']:
                # Fallback skeleton
                data = self.router.create_fallback_skeleton(
                    company_name=company['name'],
                    error_message=route['error']
                )
                financial_data.append(data)
                continue
            
            # API 호출
            if route['api'] == 'SEC_EDGAR':
                headers = self.router.get_sec_request_headers(
                    user_agent_name='EVI-AgentSystem',
                    contact_email='your_email@example.com'
                )
                response = requests.get(route['api_url'], headers=headers)
                
                if response.status_code == 200:
                    data = self._parse_sec_data(response.json())
                else:
                    data = self.router.create_fallback_skeleton(
                        company_name=company['name'],
                        error_message=f'SEC API {response.status_code}'
                    )
                
                financial_data.append(data)
            
            # 다른 API들도 유사하게...
        
        state['financials'] = financial_data
        return state
```

---

### 4. 스코어링 결측값 처리 (`scoring_missing_data_tools.py`)

**문제**: 결측값을 0으로 대체 → 점수 하락

**해결**:
- ✅ **결측값 = 섹터 중앙값** (0이 아님)
- ✅ 신뢰도 페널티 (결측 1개당 -5%)
- ✅ Z-score 가드 (분산=0 → Rank 기반)
- ✅ Top-N 랭킹 (엄격한 임계치 대신)

**사용법**:
```python
from tools.scoring_missing_data_tools import ScoringWithMissingData

scorer = ScoringWithMissingData()

# 결측값 있는 데이터
company_data = {
    'company_name': 'BYD',
    'roe': 0.14,
    'roa': None,  # 결측
    'operating_margin': 0.09,
    'debt_ratio': None,  # 결측
    'current_ratio': 1.5
}

# 스코어링 (결측값 자동 채움)
result = scorer.score_with_confidence(company_data, sector='OEM')

print(f"Score: {result['total_score']}")  # 74.7 (0이 아님!)
print(f"Confidence: {result['confidence']:.2f}")  # 0.90 (페널티 반영)
print(f"Missing: {result['missing_count']}")  # 2
print(f"Filled: {result['filled_fields']}")  # ['roa', 'debt_ratio']

# 여러 회사 랭킹
companies = [result1, result2, result3]
ranked = scorer.rank_companies(companies, top_n=5)

for company in ranked:
    print(f"{company['rank']}. {company['company_name']}: {company['total_score']} "
          f"(Confidence: {company['confidence']:.2f}, Tier: {company['tier']})")
```

**통합 방법**:
```python
# agents/investment_strategy_agent.py
from tools.scoring_missing_data_tools import ScoringWithMissingData

class InvestmentStrategyAgent:
    def __init__(self):
        self.scorer = ScoringWithMissingData()
    
    def generate_strategy(self, state):
        financials = state.get('financials', [])
        
        # 각 회사 스코어링 (결측값 처리됨)
        scored_companies = []
        for company in financials:
            score_result = self.scorer.score_with_confidence(
                company_data=company,
                sector=company.get('sector', 'Unknown')
            )
            scored_companies.append(score_result)
        
        # Top-N 랭킹 (엄격한 임계치 없음)
        top_companies = self.scorer.rank_companies(
            scored_companies,
            top_n=10  # 상위 10개
        )
        
        # 신뢰도별 그룹핑
        high_confidence = [c for c in top_companies if c['confidence'] >= 0.8]
        medium_confidence = [c for c in top_companies if 0.5 <= c['confidence'] < 0.8]
        low_confidence = [c for c in top_companies if c['confidence'] < 0.5]
        
        state['recommendations'] = {
            'high_confidence': high_confidence,
            'medium_confidence': medium_confidence,
            'low_confidence': low_confidence,
            'all_scored': scored_companies
        }
        return state
```

---

## 🔧 통합 체크리스트

### 단계별 적용

#### 1️⃣ **MarketTrendAgent**
- [ ] `TrendAnalyzer` 임포트 및 초기화
- [ ] `analyze_trends_with_fallback()` 사용
- [ ] `extract_keywords()` 로 불용어 제거된 키워드 사용

#### 2️⃣ **SupplierMatchingAgent**
- [ ] `SupplierScorer` 임포트 및 초기화
- [ ] 관계마다 `score_relationship()` 호출
- [ ] `filter_by_tier(min_tier='discovery')` 로 Discovery 포함
- [ ] `generate_summary()` 로 통계 생성

#### 3️⃣ **FinancialAnalyzerAgent**
- [ ] `DisclosureRouter` 임포트 및 초기화
- [ ] `route_disclosure_request()` 로 API 결정
- [ ] CIK는 `normalize_cik()` 로 10자리 패딩
- [ ] SEC 헤더는 `get_sec_request_headers()` 사용
- [ ] 실패 시 `create_fallback_skeleton()` (0 대신 None)

#### 4️⃣ **InvestmentStrategyAgent**
- [ ] `ScoringWithMissingData` 임포트 및 초기화
- [ ] `score_with_confidence()` 로 결측값 처리
- [ ] `rank_companies(top_n=N)` 로 Top-N 추출
- [ ] 신뢰도 레벨별로 그룹핑

#### 5️⃣ **RiskAssessmentAgent**
- [ ] JSON 파서 (`json_parser.py`) 사용
- [ ] JSON-only 프롬프트 (`json_output_templates.py`) 사용
- [ ] 스키마 검증 + Fallback

---

## 📊 예상 개선 결과

| 지표 | Before | After | 개선 |
|------|--------|-------|------|
| 트렌드 식별 | 0개 | 3-7개 | **∞** |
| 공급망 관계 | 0개 신규 | 5-10개 | **∞** |
| 리스크 기업 | 0개 | 5-8개 | **∞** |
| 공시 데이터 | 없음 | 수집됨 | **100%** |
| 추천 종목 | 없음 | Top-N | **100%** |
| 키워드 품질 | 불용어 포함 | 불용어 제거 | **80%↑** |

---

## 🧪 테스트

모든 도구는 단독 테스트가 가능합니다:

```bash
# 트렌드 분석
python tools/trend_analysis_tools.py

# 공급망 스코어링
python tools/supplier_scoring_tools.py

# 공시 라우팅
python tools/disclosure_routing_tools.py

# 스코어링 결측값 처리
python tools/scoring_missing_data_tools.py
```

---

## 💡 핵심 원칙

1. **결측값 ≠ 0**: 결측값은 섹터 중앙값으로 대체, 신뢰도 페널티 부여
2. **Fallback 규칙**: 모든 단계에서 최소 결과 보장 (빈 결과 방지)
3. **2단계 필터링**: Verified / Discovery 분리 (단일 임계치 지양)
4. **Top-N 랭킹**: 엄격한 임계치 대신 상대적 순위 사용
5. **국가별 라우팅**: 미국(SEC), 한국(DART), 중국/홍콩(거래소) 자동 라우팅
6. **CIK 정규화**: SEC API는 반드시 10자리 제로패딩
7. **JSON 강제**: LLM 출력은 JSON-only + 자동 수정 + Fallback

---

## 📚 관련 문서

- **JSON 출력 시스템**: `JSON_OUTPUT_GUIDE.md`
- **빠른 참조**: `JSON_QUICK_REFERENCE.md`
- **구현 요약**: `JSON_OUTPUT_IMPLEMENTATION_SUMMARY.md`
- **메인 README**: `README.md`

---

**작성일**: 2025-10-24  
**버전**: 1.0.0  
**작성자**: AI Assistant

