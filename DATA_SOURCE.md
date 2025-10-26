# 공시 자료 수집 로직 개선 문서

## 📋 개요

공시 자료 수집 로직을 **미국(SEC) / 한국(DART) / 그 외(Yahoo Finance)**로 명확히 분리하고, 웹 서치 실패 시에도 안정적으로 동작하도록 개선했습니다.

---

## 🎯 주요 변경사항

### 1. **데이터 소스 분류 체계 확립**

기업을 국가/지역별로 분류하여 적절한 데이터 소스를 사용합니다:

| 국가/지역 | 데이터 소스 | 설명 |
|----------|------------|------|
| 🇰🇷 **한국** | **DART** | 금융감독원 전자공시시스템 - 한국 상장 기업 공시 |
| 🇺🇸 **미국** | **SEC EDGAR** | 미국 증권거래위원회 - 미국 상장 기업 공시 (10-K, 10-Q, 8-K 등) |
| 🌍 **그 외** | **Yahoo Finance** | 유럽, 중국, 일본 등 - 재무 정보 (공시는 없음) |

#### 지원 기업 예시

```python
# 한국 기업 (DART)
- LG에너지솔루션, 삼성SDI, SK온
- 현대자동차, 기아
- 에코프로비엠, 포스코케미칼

# 미국 기업 (SEC EDGAR)
- Tesla, GM, Ford
- Rivian, Lucid
- Nio, Xpeng, Li Auto (미국 상장 중국 기업)
- Albemarle, QuantumScape

# 그 외 기업 (Yahoo Finance)
- BMW, Mercedes-Benz, Volkswagen (독일)
- BYD, CATL (중국)
- Panasonic (일본)
- Northvolt (스웨덴)
```

---

### 2. **Relaxed Mode 도입**

웹 서치나 API 호출이 실패해도 시스템이 중단되지 않고 계속 진행됩니다.

#### 주요 특징:
- ✅ **에러 허용**: 개별 기업 데이터 수집 실패 시에도 다음 기업으로 진행
- ✅ **필터링 기준 완화**: EV 관련 필터링을 완화하여 더 많은 데이터 수집
- ✅ **다양한 공시 유형 포함**: SEC에서 10-K/A, 10-Q/A 등 추가 유형도 수집
- ✅ **기본 기업 리스트 활용**: 뉴스에서 기업을 찾지 못하면 기본 리스트 사용

```python
# config 설정 예시
config = {
    'relaxed_mode': True,  # 에러 시에도 계속 진행
    'fallback_enabled': True,  # fallback 전략 사용
    'default_companies_enabled': True  # 기본 기업 리스트 사용
}
```

---

### 3. **Fallback 전략**

데이터 수집 실패 시 대체 방법을 사용합니다:

```python
# 한국 기업
Primary: DART 공시 → Fallback: Yahoo Finance

# 미국 기업  
Primary: SEC EDGAR 공시 → Fallback: Yahoo Finance

# 그 외 기업
Primary: Yahoo Finance (fallback 없음)
```

#### 기본 기업 리스트

뉴스에서 기업을 찾지 못하면 자동으로 주요 기업의 공시를 수집합니다:

```python
# 한국 기업 (기본)
['LG에너지솔루션', '삼성SDI', 'SK온', '현대자동차', '기아']

# 미국 기업 (기본)
['Tesla', 'GM', 'Ford']

# 그 외 기업 (기본)
['BMW', 'Mercedes', 'Volkswagen', 'BYD', 'Panasonic']
```

---

## 📁 수정된 파일

### 1. `tools/sec_tagger.py`

```python
# 주요 변경사항:
- 기업별 'source'와 'country' 필드 추가
- classify_companies_by_source() 메서드 추가
- collect_company_filings()에 relaxed_mode 파라미터 추가
- CATL, Northvolt 등 추가 기업 지원
```

**새로운 메서드:**
```python
def classify_companies_by_source(company_names: List[str]) -> Dict[str, List[str]]:
    """
    기업들을 데이터 소스별로 분류
    Returns: {'SEC': [...], 'DART': [...], 'Yahoo': [...]}
    """
```

### 2. `agents/market_trend_agent.py`

```python
# 주요 변경사항:
- _collect_disclosures() 메서드를 3개의 함수로 분리
  * _collect_dart_disclosures() - 한국 기업
  * _collect_sec_disclosures() - 미국 기업
  * _collect_yahoo_data() - 그 외 기업
- 뉴스가 없어도 기본 기업 리스트로 동작
- relaxed_mode 지원
```

**새로운 워크플로우:**
```
1. 뉴스에서 기업명 추출 (실패 시 기본 리스트)
   ↓
2. 기업을 소스별로 분류 (SEC/DART/Yahoo)
   ↓
3. 각 소스에서 병렬로 데이터 수집
   ↓
4. 데이터 병합 및 반환
```

### 3. `config/settings.py`

```python
# 추가된 설정:
@dataclass
class EVMarketConfig:
    # 데이터 수집 설정
    max_news_articles: int = 50
    max_disclosures_per_company: int = 10
    max_sec_filings_per_company: int = 8
    days_ago: int = 30
    
    # 웹 서치 및 에러 핸들링 설정
    relaxed_mode: bool = True
    fallback_enabled: bool = True
    default_companies_enabled: bool = True

# 새로운 상수:
DATA_SOURCE_FALLBACK = {
    'korea': {...},
    'us': {...},
    'others': {...}
}
```

### 4. `main.py`

```python
# 추가된 config 설정:
config = {
    ...
    'relaxed_mode': True,
    'fallback_enabled': True,
    'default_companies_enabled': True
}
```

---

## 🚀 사용 방법

### 기본 실행

```bash
python main.py
```

### 설정 커스터마이징

```python
# main.py에서 수정
config = {
    'days_ago': 30,  # 최근 30일
    'max_news_articles': 100,  # 뉴스 100개
    'max_disclosures_per_company': 10,  # 기업당 공시 10개
    'relaxed_mode': True,  # 에러 허용 모드
}
```

---

## 📊 실행 결과 예시

```
========================================
[공시 데이터 수집 전략]
========================================
- 한국 기업 (DART): 5개
- 미국 기업 (SEC): 3개
- 그 외 기업 (Yahoo Finance): 4개
- Relaxed Mode: 활성화
========================================

========================================
[한국 기업 공시 수집 - DART]
========================================
[OK] 공시 수집 대상 한국 기업: 5개
    - LG에너지솔루션
    - 삼성SDI
    - SK온
    - 현대자동차
    - 기아
[OK] 총 45개 공시 중 35개 선별
[SUMMARY] 공시 통계:
    - 전체: 35개
    - 중요도 (High/Medium/Low): 12/15/8
    - EV 관련: 28개

========================================
[미국 기업 공시 수집 - SEC EDGAR]
========================================
[OK] 공시 수집 대상 미국 기업: 3개
    - Tesla
    - GM
    - Ford
[OK] 총 18개 공시 중 15개 선별
[SUMMARY] SEC 공시 통계:
    - 전체: 15개
    - 중요도 (High/Medium/Low): 9/4/2
    - EV 관련: 12개

========================================
[그 외 기업 재무 정보 수집 - Yahoo Finance]
========================================
[OK] 재무 정보 수집 대상 기업: 4개
    - BMW
    - BYD
    - Panasonic
    - CATL
[OK] 총 4개 기업의 재무 정보 수집

[총계] 수집된 공시/재무 데이터: 54개
```

---

## 🔧 주요 개선 효과

### 1. **안정성 향상**
- ✅ 웹 서치 실패 시에도 시스템 중단 없음
- ✅ 개별 API 호출 실패 시 다른 데이터 소스로 fallback
- ✅ 뉴스가 없어도 기본 기업 리스트로 데이터 수집

### 2. **커버리지 확대**
- ✅ 한국, 미국 외 유럽/중국/일본 기업도 지원
- ✅ Yahoo Finance 통합으로 글로벌 기업 재무 정보 수집
- ✅ 더 많은 공시 유형 포함 (relaxed mode)

### 3. **명확한 데이터 소스 관리**
- ✅ 국가별로 최적의 데이터 소스 사용
- ✅ 공시 vs 재무 정보 명확히 구분
- ✅ 데이터 신뢰도 및 출처 추적 가능

### 4. **유연한 설정**
- ✅ relaxed_mode로 수집 기준 조정
- ✅ 기업당 수집 개수 제한 가능
- ✅ 기본 기업 리스트 커스터마이징 가능

---

## 🎯 향후 개선 계획

1. **더 많은 국가 지원**
   - 영국 (London Stock Exchange API)
   - 일본 (EDINET API)
   - 유럽 (ESEF/XBRL)

2. **캐싱 기능**
   - 동일 기업 중복 조회 방지
   - API 호출 최적화

3. **병렬 처리**
   - 여러 기업 동시 수집
   - 성능 향상

4. **데이터 품질 검증**
   - 공시 데이터 검증 로직
   - 이상치 탐지

---

## 📝 참고 문서

- [DART Open API](https://opendart.fss.or.kr/)
- [SEC EDGAR API](https://www.sec.gov/edgar/sec-api-documentation)
- [Yahoo Finance API](https://pypi.org/project/yfinance/)

---

## 🤝 기여

버그 리포트나 기능 제안은 이슈로 등록해주세요.

---

**마지막 업데이트:** 2025-10-24
**버전:** 2.0.0

