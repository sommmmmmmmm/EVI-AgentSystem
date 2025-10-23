# 🚀 데이터 기반 자동화 시스템 개선 계획

## 📋 개요

하드코딩을 제거하고 실제 API 기반 데이터 수집으로 전환

---

## 🔄 현재 시스템 vs 개선 시스템

### 현재 (하드코딩)
```python
# config/settings.py
ev_oems = ['Tesla', 'BYD', 'GM', ...]  # 하드코딩
battery_suppliers = ['LG에너지솔루션', 'Samsung SDI', ...]  # 하드코딩
```

### 개선 후 (데이터 기반)
```python
# 1. Tavily로 100개 뉴스 수집
# 2. LLM으로 기업명 추출
# 3. 국가별 API 자동 선택
# 4. 재무 데이터 수집
```

---

## 🏗️ 새로운 아키텍처

### Phase 1: 뉴스 수집 및 기업 발견 (News Discovery Agent)

```
Tavily API (100 articles)
    ↓
LLM 키워드 추출 (EV, battery, charging 관련)
    ↓
LLM 기업명 추출
    ↓
기업 리스트 생성 + 국가 분류
```

**구현 파일**: `agents/news_discovery_agent.py` (신규 생성)

### Phase 2: 기업 분류 및 데이터 수집 (Data Collection Agent)

```
기업 리스트
    ↓
국가/지역 판별 (LLM 또는 규칙 기반)
    ↓
    ├─ 한국 기업 → DART API
    │   └─ 고유번호(corp_code) 검색
    │   └─ 재무제표 수집 (income_statement, balance_sheet, cash_flow)
    │
    ├─ 미국 기업 → SEC EDGAR API
    │   └─ CIK(Central Index Key) 검색
    │   └─ 10-K, 10-Q 파일 파싱
    │
    └─ 기타 기업 → Yahoo Finance API
        └─ Ticker 심볼 검색
        └─ 재무 데이터 수집
```

**구현 파일**: `agents/data_collection_agent.py` (신규 생성)

### Phase 3: 데이터 통합 및 표준화 (Data Normalization)

```
DART 데이터 + SEC 데이터 + Yahoo 데이터
    ↓
표준화된 재무제표 형식으로 변환
    ↓
{
    'company': 'LG에너지솔루션',
    'country': 'KR',
    'income_statement': {...},
    'balance_sheet': {...},
    'cash_flow_statement': {...},
    'data_source': 'DART',
    'confidence': 0.95
}
```

---

## 📊 상세 구현 로직

### 1. News Discovery Agent

```python
class NewsDiscoveryAgent:
    def __init__(self, tavily_tool, llm_tool):
        self.tavily = tavily_tool
        self.llm = llm_tool
    
    def discover_companies(self, keywords=['EV', 'electric vehicle', 'battery']):
        # Step 1: Tavily로 100개 뉴스 수집
        news_articles = self.tavily.search(
            query=" OR ".join(keywords),
            num_results=100,
            days_ago=30
        )
        
        # Step 2: LLM으로 기업명 추출
        companies = self._extract_companies_with_llm(news_articles)
        
        # Step 3: 국가 분류
        classified_companies = self._classify_by_country(companies)
        
        return classified_companies
    
    def _extract_companies_with_llm(self, articles):
        prompt = f"""
        다음 뉴스 기사들에서 전기차 관련 기업명을 추출하세요.
        
        기사 내용:
        {articles}
        
        JSON 형식으로 반환:
        {{
            "companies": [
                {{"name": "Tesla", "country": "US", "category": "OEM"}},
                {{"name": "LG에너지솔루션", "country": "KR", "category": "Battery"}}
            ]
        }}
        """
        return self.llm.generate(prompt)
```

### 2. Data Collection Agent

```python
class DataCollectionAgent:
    def __init__(self, dart_tool, sec_tool, yahoo_tool):
        self.dart = dart_tool
        self.sec = sec_tool
        self.yahoo = yahoo_tool
    
    def collect_financial_data(self, company_info):
        country = company_info['country']
        company_name = company_info['name']
        
        if country == 'KR':
            return self._collect_from_dart(company_name)
        elif country == 'US':
            return self._collect_from_sec(company_name)
        else:
            return self._collect_from_yahoo(company_name)
    
    def _collect_from_dart(self, company_name):
        # Step 1: 고유번호(corp_code) 검색
        corp_code = self.dart.get_corp_code(company_name)
        
        if not corp_code:
            print(f"[WARNING] {company_name} DART 고유번호 없음")
            return None
        
        # Step 2: 재무제표 수집
        financials = self.dart.get_financial_statements(
            corp_code=corp_code,
            year=2024
        )
        
        return {
            'company': company_name,
            'country': 'KR',
            'data_source': 'DART',
            'corp_code': corp_code,
            'income_statement': financials['income_statement'],
            'balance_sheet': financials['balance_sheet'],
            'cash_flow_statement': financials['cash_flow'],
            'confidence': 0.95  # DART는 공식 데이터이므로 높은 신뢰도
        }
    
    def _collect_from_sec(self, company_name):
        # Step 1: CIK 검색
        cik = self.sec.get_cik(company_name)
        
        if not cik:
            print(f"[WARNING] {company_name} SEC CIK 없음")
            return None
        
        # Step 2: 10-K 최신 파일 파싱
        financials = self.sec.get_latest_10k(cik)
        
        return {
            'company': company_name,
            'country': 'US',
            'data_source': 'SEC',
            'cik': cik,
            'income_statement': financials['income_statement'],
            'balance_sheet': financials['balance_sheet'],
            'cash_flow_statement': financials['cash_flow'],
            'confidence': 0.90
        }
    
    def _collect_from_yahoo(self, company_name):
        # Step 1: Ticker 심볼 검색
        ticker = self.yahoo.search_ticker(company_name)
        
        if not ticker:
            print(f"[WARNING] {company_name} Yahoo Ticker 없음")
            return None
        
        # Step 2: 재무 데이터 수집
        financials = self.yahoo.get_financials(ticker)
        
        return {
            'company': company_name,
            'country': 'OTHER',
            'data_source': 'Yahoo',
            'ticker': ticker,
            'income_statement': financials['income_statement'],
            'balance_sheet': financials['balance_sheet'],
            'cash_flow_statement': financials['cash_flow'],
            'confidence': 0.75  # Yahoo는 신뢰도가 상대적으로 낮음
        }
```

### 3. Data Normalization (표준화)

```python
class DataNormalizer:
    """다양한 소스의 재무 데이터를 표준 형식으로 변환"""
    
    def normalize(self, raw_data):
        source = raw_data['data_source']
        
        if source == 'DART':
            return self._normalize_dart(raw_data)
        elif source == 'SEC':
            return self._normalize_sec(raw_data)
        elif source == 'Yahoo':
            return self._normalize_yahoo(raw_data)
    
    def _normalize_dart(self, data):
        """DART 데이터 → 표준 형식"""
        return {
            'company': data['company'],
            'income_statement': {
                'revenue': data['income_statement']['매출액'],
                'rnd_expense': data['income_statement']['연구개발비'],
                'cogs': data['income_statement']['매출원가'],
                'depreciation': data['income_statement']['감가상각비'],
                ...
            },
            'balance_sheet': {
                'total_assets': data['balance_sheet']['자산총계'],
                'intangible_assets': data['balance_sheet']['무형자산'],
                'current_assets': data['balance_sheet']['유동자산'],
                ...
            },
            'cash_flow_statement': {
                'capex': data['cash_flow']['투자활동현금흐름'],
                ...
            }
        }
```

---

## 🎯 구현 우선순위

### Priority 1: 핵심 데이터 수집 (1일)
- [ ] `NewsDiscoveryAgent` 구현
- [ ] Tavily API 통합 (100 articles)
- [ ] LLM 기업명 추출

### Priority 2: 데이터 소스 연동 (1-2일)
- [ ] `DataCollectionAgent` 구현
- [ ] DART API 연동 (한국 기업)
- [ ] SEC API 연동 (미국 기업)
- [ ] Yahoo Finance API 연동 (기타 기업)

### Priority 3: 데이터 표준화 (0.5일)
- [ ] `DataNormalizer` 구현
- [ ] 3가지 소스 데이터 표준 형식 정의
- [ ] 변환 로직 구현

### Priority 4: 통합 및 테스트 (0.5일)
- [ ] 기존 워크플로우에 통합
- [ ] End-to-End 테스트
- [ ] 에러 핸들링 강화

---

## 💡 핵심 개선 포인트

### 1. 하드코딩 제거
```python
# Before
ev_oems = ['Tesla', 'BYD', 'GM', ...]

# After
ev_oems = NewsDiscoveryAgent.discover_companies()
```

### 2. 자동 국가 분류
```python
def classify_company_country(company_name, llm_tool):
    prompt = f"{company_name}의 본사 국가를 판별하세요 (KR/US/CN/JP/DE/OTHER)"
    return llm_tool.generate(prompt)
```

### 3. API 자동 선택
```python
def get_financial_data(company, country):
    api_selector = {
        'KR': dart_api,
        'US': sec_api,
        'CN': None,  # Yahoo fallback
        'JP': None,  # Yahoo fallback
        'OTHER': yahoo_api
    }
    return api_selector.get(country, yahoo_api).fetch(company)
```

---

## 🔍 예상 데이터 플로우

```
[Tavily 100 articles]
    ↓
[LLM 기업명 추출]
Tesla, LG에너지솔루션, BYD, CATL, Samsung SDI, ...
    ↓
[국가 분류]
{
    'Tesla': 'US',
    'LG에너지솔루션': 'KR',
    'BYD': 'CN',
    'CATL': 'CN',
    'Samsung SDI': 'KR'
}
    ↓
[API 자동 선택]
Tesla → SEC API
LG에너지솔루션 → DART API (corp_code: 00126380)
BYD → Yahoo Finance (ticker: 1211.HK)
    ↓
[재무 데이터 수집]
{
    'Tesla': {재무제표 from SEC},
    'LG에너지솔루션': {재무제표 from DART},
    'BYD': {재무제표 from Yahoo}
}
    ↓
[데이터 표준화]
모든 데이터를 동일한 형식으로 변환
    ↓
[리스크 분석]
3가지 리스크 지표 계산
```

---

## 🚨 주의사항 및 고려사항

### API 제한
- **Tavily**: 월 1,000 requests (유료 플랜)
- **DART**: 무제한 (공개 API)
- **SEC**: Rate limit 10 requests/second
- **Yahoo Finance**: 비공식 API, 안정성 낮음

### 에러 핸들링
```python
def safe_api_call(api_func, *args, **kwargs):
    try:
        return api_func(*args, **kwargs)
    except RateLimitError:
        time.sleep(60)
        return api_func(*args, **kwargs)
    except DataNotFoundError:
        print(f"[WARNING] {args[0]} 데이터 없음")
        return None
    except Exception as e:
        print(f"[ERROR] API 호출 실패: {e}")
        return None
```

### 데이터 캐싱
```python
# 동일한 기업의 재무 데이터는 캐싱
@cache(ttl=24*60*60)  # 24시간
def get_financial_data(company, country):
    ...
```

---

## 📈 기대 효과

### Before (하드코딩)
- ❌ 수동으로 기업 리스트 관리
- ❌ 새로운 기업 발견 불가
- ❌ 데이터 업데이트 어려움

### After (자동화)
- ✅ 실시간 뉴스 기반 기업 발견
- ✅ 자동 재무 데이터 수집
- ✅ 다양한 국가 기업 지원
- ✅ 데이터 신뢰도 점수 자동 계산

---

## 🔧 다음 단계

1. **내일 사내 API 키 확보**
   - Tavily API 키
   - DART API 키 (이미 있음)
   - SEC API 접근 권한

2. **NewsDiscoveryAgent 구현 시작**
   - `agents/news_discovery_agent.py` 생성
   - Tavily 통합

3. **DataCollectionAgent 구현**
   - `agents/data_collection_agent.py` 생성
   - 3가지 API 통합

4. **기존 시스템과 통합**
   - `workflow/graph.py` 업데이트
   - 새 에이전트 추가

---

**작성일**: 2025-10-24
**목표 완료일**: 2025-10-26 (3일 이내)

