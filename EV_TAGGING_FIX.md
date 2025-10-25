# EV 관련 공시 태깅 로직 수정

## 🐛 문제 상황

웹 서치에서 전기차 관련 회사들을 찾았는데, 공시 통계에서 **"EV 관련: 0개"**로 표시되는 문제

```
[SUMMARY] 공시 통계:
    - 전체: 46개
    - 중요도 (High/Medium/Low): 9/4/33
    - EV 관련: 0개  ← ❌ 말이 안 됨!
```

---

## 🎯 문제 원인

### 기존 로직의 문제점

1. **키워드 기반 필터링만 사용**
   - 공시 제목/내용에 "전기차", "배터리", "EV" 등의 키워드가 있어야만 EV 관련으로 태깅
   - 하지만 대부분의 일반 공시(사업보고서, 재무제표 등)에는 이런 키워드가 없음

2. **회사 정보 무시**
   - 웹 서치에서 이미 **"LG에너지솔루션", "삼성SDI", "Tesla"** 등을 EV 기업으로 확인
   - 하지만 공시 태깅 시 이 정보를 활용하지 않음

3. **논리적 모순**
   ```
   웹 서치: "LG에너지솔루션은 EV 배터리 기업이다" ✅
   공시 수집: LG에너지솔루션의 공시 46개 수집 ✅
   필터링: "EV" 키워드가 없어서 0개로 필터링 ❌ (말이 안 됨!)
   ```

---

## ✅ 해결 방법

### 1. **회사 기반 자동 태깅**

EV 관련 기업 리스트에 있는 회사의 공시는 **자동으로 EV 관련으로 태깅**

#### DART Tagger (`dart_tagger.py`)

```python
def tag_disclosure(self, disclosure: Dict[str, Any]) -> Dict[str, Any]:
    company_name = disclosure.get('company_name', '')
    
    # 1. 회사가 EV 관련 기업 리스트에 있으면 자동으로 EV 관련으로 태깅
    if company_name in self.KOREAN_EV_COMPANIES:
        is_ev_related = True
        ev_keywords_found.append(f'{company_name} (EV 기업)')
        print(f"   [AUTO-TAG] {company_name}는 EV 관련 기업으로 자동 태깅")
    
    # 2. 제목/내용에 EV 키워드가 있는지 추가 체크
    # (기존 키워드 기반 로직도 유지)
```

**EV 기업 리스트:**
- 한국: LG에너지솔루션, 삼성SDI, SK온, 현대자동차, 기아, 에코프로비엠 등
- 미국: Tesla, GM, Ford, Rivian, Lucid 등

#### SEC Tagger (`sec_tagger.py`)

```python
def tag_filing(self, filing: Dict[str, Any]) -> Dict[str, Any]:
    company_name = filing.get('company_name', '')
    
    # 1. 회사가 EV 관련 기업 리스트에 있으면 자동으로 태깅
    if company_name in self.OVERSEAS_EV_COMPANIES:
        company_info = self.OVERSEAS_EV_COMPANIES[company_name]
        if company_info.get('source') == 'SEC':  # SEC 기업만
            is_ev_related = True
            ev_keywords_found.append(f'{company_name} (EV 기업)')
```

### 2. **Strict/Relaxed 필터링 모드**

#### Strict Mode (엄격)
- 키워드가 있거나 중요도가 높은 공시만 포함
- 데이터 양이 적을 때 사용

#### Relaxed Mode (완화) ← **기본값**
- **EV 기업의 모든 공시를 포함**
- 키워드 없어도 OK
- 웹 서치로 찾은 기업들의 공시는 모두 관련성 있음

```python
def filter_ev_disclosures(self, disclosures: List[Dict[str, Any]], strict: bool = True):
    if not strict:
        # 회사가 EV 관련 기업이면 모든 공시 포함
        if company_name in self.KOREAN_EV_COMPANIES:
            disclosure['tags']['is_ev_related'] = True
            ev_disclosures.append(disclosure)
```

### 3. **MarketTrendAgent 개선**

```python
# DART 공시
if relaxed_mode:
    ev_disclosures = self.dart_tagger.filter_ev_disclosures(all_disclosures, strict=False)
    print(f"    [INFO] Relaxed mode: EV 기업의 모든 공시 포함")
else:
    ev_disclosures = self.dart_tagger.filter_ev_disclosures(all_disclosures, strict=True)

# SEC 공시
if relaxed_mode:
    # 각 공시에 EV 관련 태그 자동 추가
    for filing in overseas_filings:
        filing['tags']['is_ev_related'] = True
    ev_filings = overseas_filings
    print(f"    [INFO] Relaxed mode: EV 기업의 모든 공시 포함")
```

---

## 📊 변경 전후 비교

### Before (❌)

```
웹 서치 → LG에너지솔루션 발견 (EV 기업)
공시 수집 → 46개 공시 수집
필터링 → "전기차", "배터리" 키워드 검색
결과 → EV 관련: 0개 ❌

왜? 일반 사업보고서, 재무제표에는 키워드가 없음
```

### After (✅)

```
웹 서치 → LG에너지솔루션 발견 (EV 기업)
공시 수집 → 46개 공시 수집
자동 태깅 → "LG에너지솔루션는 EV 관련 기업으로 자동 태깅"
필터링 (Relaxed Mode) → 모든 공시 포함
결과 → EV 관련: 46개 ✅

논리: EV 기업의 모든 공시는 EV 관련성이 있음
```

---

## 🎯 실행 결과 예시

### 기대되는 출력

```bash
========================================
[한국 기업 공시 수집 - DART]
========================================
[OK] 공시 수집 대상 한국 기업: 5개
    - LG에너지솔루션
    - 삼성SDI
    - SK온
    - 현대자동차
    - 기아

   [AUTO-TAG] LG에너지솔루션는 EV 관련 기업으로 자동 태깅
   [AUTO-TAG] 삼성SDI는 EV 관련 기업으로 자동 태깅
   [AUTO-TAG] SK온는 EV 관련 기업으로 자동 태깅
   [AUTO-TAG] 현대자동차는 EV 관련 기업으로 자동 태깅
   [AUTO-TAG] 기아는 EV 관련 기업으로 자동 태깅

    [INFO] Relaxed mode: EV 기업의 모든 공시 포함
    [OK] 총 46개 공시 중 46개 선별

    [SUMMARY] 공시 통계:
        - 전체: 46개
        - 중요도 (High/Medium/Low): 9/4/33
        - EV 관련: 46개  ✅ (모든 공시가 EV 관련!)
========================================

========================================
[미국 기업 공시 수집 - SEC EDGAR]
========================================
[OK] 공시 수집 대상 미국 기업: 3개
    - Tesla
    - GM
    - Ford

   [AUTO-TAG] Tesla는 EV 관련 기업으로 자동 태깅
   [AUTO-TAG] GM는 EV 관련 기업으로 자동 태깅
   [AUTO-TAG] Ford는 EV 관련 기업으로 자동 태깅

    [INFO] Relaxed mode: EV 기업의 모든 공시 포함
    [OK] 총 15개 공시 중 15개 선별

    [SUMMARY] SEC 공시 통계:
        - 전체: 15개
        - 중요도 (High/Medium/Low): 12/2/1
        - EV 관련: 15개  ✅ (모든 공시가 EV 관련!)
========================================
```

---

## 🔧 수정된 파일

### 1. `tools/dart_tagger.py`

**변경사항:**
- ✅ `tag_disclosure()`: 회사명 기반 자동 태깅 추가
- ✅ `filter_ev_disclosures()`: `strict` 파라미터 추가
- ✅ Relaxed mode에서 EV 기업의 모든 공시 포함

**핵심 로직:**
```python
# 1. 회사가 EV 기업 리스트에 있으면 자동 태깅
if company_name in self.KOREAN_EV_COMPANIES:
    is_ev_related = True
    ev_keywords_found.append(f'{company_name} (EV 기업)')

# 2. Relaxed mode에서 모든 공시 포함
if not strict and company_name in self.KOREAN_EV_COMPANIES:
    disclosure['tags']['is_ev_related'] = True
    ev_disclosures.append(disclosure)
```

### 2. `tools/sec_tagger.py`

**변경사항:**
- ✅ `tag_filing()`: 회사명 기반 자동 태깅 추가
- ✅ SEC 소스 기업만 자동 태깅 (Yahoo는 제외)

**핵심 로직:**
```python
if company_name in self.OVERSEAS_EV_COMPANIES:
    company_info = self.OVERSEAS_EV_COMPANIES[company_name]
    if company_info.get('source') == 'SEC':
        is_ev_related = True
        ev_keywords_found.append(f'{company_name} (EV 기업)')
```

### 3. `agents/market_trend_agent.py`

**변경사항:**
- ✅ DART 공시: `strict=False`로 호출
- ✅ SEC 공시: Relaxed mode에서 자동 태그 추가
- ✅ 정보 메시지 추가

**핵심 로직:**
```python
# DART
if relaxed_mode:
    ev_disclosures = self.dart_tagger.filter_ev_disclosures(all_disclosures, strict=False)
    print(f"    [INFO] Relaxed mode: EV 기업의 모든 공시 포함")

# SEC
if relaxed_mode:
    for filing in overseas_filings:
        filing['tags']['is_ev_related'] = True
    ev_filings = overseas_filings
```

---

## 💡 핵심 개선 사항

### 1. **논리적 일관성**

```
웹 서치에서 찾은 기업 = EV 기업
→ 그 기업의 모든 공시 = EV 관련 공시 ✅

기존: 키워드가 없으면 무조건 필터링 ❌
개선: 회사가 EV 기업이면 모든 공시 포함 ✅
```

### 2. **데이터 손실 방지**

```
기존: 46개 공시 → 0개로 필터링 (100% 손실!)
개선: 46개 공시 → 46개 모두 포함 (0% 손실!)
```

### 3. **유연한 필터링**

```
Strict Mode: 키워드 기반 엄격한 필터링
Relaxed Mode: 회사 기반 완화된 필터링 (기본값)
```

### 4. **명확한 메시지**

```
[AUTO-TAG] LG에너지솔루션는 EV 관련 기업으로 자동 태깅
[INFO] Relaxed mode: EV 기업의 모든 공시 포함
```

---

## 🧪 테스트 방법

### 1. Python으로 직접 테스트

```python
from tools.dart_tagger import DARTTagger
from tools.dart_tools import DARTTool

# 초기화
dart_tool = DARTTool(api_key='your-api-key')
dart_tagger = DARTTagger(dart_tool=dart_tool)

# 공시 수집 및 태깅
disclosures = dart_tagger.collect_company_disclosures(['LG에너지솔루션'], days=30)
print(f"수집된 공시: {len(disclosures)}개")

# 필터링 (Relaxed Mode)
ev_disclosures = dart_tagger.filter_ev_disclosures(disclosures, strict=False)
print(f"EV 관련 공시: {len(ev_disclosures)}개")

# 통계
summary = dart_tagger.get_disclosure_summary(ev_disclosures)
print(f"EV 관련: {summary['ev_related']}개")
```

### 2. 전체 시스템 테스트

```bash
python main.py
```

**확인 사항:**
- ✅ `[AUTO-TAG]` 메시지가 출력되는지
- ✅ `[INFO] Relaxed mode: EV 기업의 모든 공시 포함` 메시지
- ✅ `EV 관련: 46개` (0이 아님)

---

## 📈 예상 효과

| 항목 | Before | After | 개선율 |
|------|--------|-------|--------|
| **EV 관련 공시 수** | 0개 | 46개 | ∞% |
| **데이터 손실** | 100% | 0% | 100% 개선 |
| **논리적 일관성** | ❌ | ✅ | - |
| **사용자 경험** | 혼란 | 명확 | - |

---

## 🎯 향후 개선 계획

1. **동적 기업 리스트**
   - 웹 서치에서 찾은 기업을 동적으로 EV 기업 리스트에 추가
   - DB 또는 캐시에 저장

2. **신뢰도 점수**
   - 자동 태깅: 신뢰도 0.9 (회사 기반)
   - 키워드 태깅: 신뢰도 1.0 (명시적 언급)

3. **학습 기반 필터링**
   - 과거 데이터 학습
   - ML 모델로 관련성 예측

---

## ✅ 검증 완료

- ✅ Lint 검사 통과
- ✅ 회사 기반 자동 태깅 구현
- ✅ Strict/Relaxed 모드 구현
- ✅ 한국 기업 (DART) 적용
- ✅ 미국 기업 (SEC) 적용
- ✅ 논리적 일관성 확보

---

**작성일:** 2025-10-24  
**버전:** 2.3.0  
**수정자:** AI Assistant

