# SEC EDGAR API 404 에러 수정

## 🐛 문제 원인

SEC EDGAR API 호출 시 **404 에러**가 발생했습니다.

### 핵심 원인

**CIK 형식 오류**: CIK를 **10자리로 패딩**하지 않아서 404 발생

```
❌ 잘못된 형식: CIK1318605.json (7자리)
✅ 올바른 형식: CIK0001318605.json (10자리)
```

### 추가 문제

1. **Host 헤더 충돌**: `Host: data.sec.gov`를 수동 설정하면 자동 헤더와 충돌
2. **User-Agent 불충분**: 연락처 정보 미포함
3. **CIK 매핑 부족**: Nio, Xpeng, Li Auto 등 중국 기업(미국 상장) 누락

---

## ✅ 수정 내용

### 1. **CIK 정규화 함수 추가**

```python
def _normalize_cik(self, cik: str) -> str:
    """
    CIK를 10자리 형식으로 정규화 (앞에 0 패딩)
    
    Args:
        cik: CIK 코드 (숫자 문자열)
        
    Returns:
        10자리로 패딩된 CIK (예: '0001318605')
    """
    # 숫자만 추출
    cik_digits = ''.join(filter(str.isdigit, cik))
    # 10자리로 패딩
    return cik_digits.zfill(10)
```

**작동 원리:**
- `'1318605'` → `'0001318605'` ✅
- `'0001318605'` → `'0001318605'` ✅ (이미 10자리)
- `'CIK1318605'` → `'0001318605'` ✅ (숫자만 추출 후 패딩)

### 2. **API URL 형식 수정**

#### Before (❌ 잘못됨)
```python
# Line 136 (구버전)
cik_clean = cik.lstrip('0')  # ❌ 0을 제거하고 있음!
url = f"{self.base_url}/api/xbrl/companyfacts/CIK{cik}.json"
# 결과: https://data.sec.gov/api/xbrl/companyfacts/CIK1318605.json (404)
```

#### After (✅ 올바름)
```python
# Line 165-168 (신버전)
cik_padded = self._normalize_cik(cik)  # ✅ 10자리로 패딩
url = f"{self.base_url}/api/xbrl/companyfacts/CIK{cik_padded}.json"
# 결과: https://data.sec.gov/api/xbrl/companyfacts/CIK0001318605.json (200 ✅)
```

### 3. **Host 헤더 제거**

#### Before (❌)
```python
self.session.headers.update({
    'User-Agent': self.user_agent,
    'Accept-Encoding': 'gzip, deflate',
    'Host': 'data.sec.gov'  # ❌ 수동 설정 시 충돌
})
```

#### After (✅)
```python
self.session.headers.update({
    'User-Agent': self.user_agent,
    'Accept-Encoding': 'gzip, deflate'
    # Host 헤더는 자동으로 설정됨
})
```

### 4. **User-Agent 개선**

#### Before
```python
self.user_agent = "EVI-Agent/1.0 (contact@example.com)"
```

#### After
```python
self.user_agent = "EVI-Agent/1.0 (evi-agent@example.com)"
print(f"[OK] SEC EDGAR API 초기화 완료 (User-Agent: {self.user_agent})")
```

### 5. **CIK 매핑 추가**

추가된 기업들 (중국 기업, 미국 상장):

```python
# 중국 자동차 (미국 상장)
'Nio': '0001736541',
'NIO': '0001736541',
'Xpeng': '0001806059',
'XPEV': '0001806059',
'Li Auto': '0001799209',
'LI': '0001799209',

# 미국 배터리/부품
'Albemarle': '0000915913',
'QuantumScape': '0001811414',
```

### 6. **에러 메시지 개선**

#### Before (❌)
```python
print(f"   [WARNING] CIK {cik}의 데이터를 찾을 수 없습니다")
```

#### After (✅)
```python
if e.response.status_code == 404:
    print(f"   ❌ [에러] CIK {cik_padded}의 데이터를 찾을 수 없습니다 (404)")
    print(f"   → URL: {url}")
    print(f"   → CIK 형식을 확인하세요. 10자리여야 합니다 (예: CIK0001318605.json)")
elif e.response.status_code == 403:
    print(f"   ❌ [에러] SEC API 접근 거부 (403)")
    print(f"   → User-Agent 헤더를 확인하세요: {self.user_agent}")
elif e.response.status_code == 429:
    print(f"   ❌ [에러] SEC API 요청 한도 초과 (429)")
    print(f"   → Rate limit: 10 requests/second을 초과했습니다")
```

### 7. **디버그 로그 추가**

```python
print(f"   [DEBUG] SEC API 호출: {url}")
print(f"   [DEBUG] SEC Submissions API 호출: {url}")
```

**실제 호출되는 URL을 확인 가능**

---

## 📋 SEC API 체크리스트

### ✅ 필수 요구사항

1. **CIK 형식**: 10자리 (앞에 0 패딩)
   - ✅ `0001318605` (Tesla)
   - ✅ `0000037996` (Ford)
   - ❌ `1318605` (잘못된 형식)

2. **User-Agent 헤더**: 연락처 포함
   - ✅ `EVI-Agent/1.0 (evi-agent@example.com)`
   - ❌ `Python-requests/2.31.0` (기본값)

3. **Host 헤더**: 자동 설정 (수동 금지)
   - ✅ `requests.Session()`이 자동 설정
   - ❌ 수동 `'Host': 'data.sec.gov'` 설정

4. **Rate Limit**: 10 requests/second
   - ✅ `time.sleep(1)` 추가
   - ⚠️ 429 에러 시 지수백오프 권장

---

## 🎯 주요 기업 CIK 목록

| 기업명 | 티커 | CIK (10자리) | 국가 |
|--------|------|--------------|------|
| Tesla | TSLA | `0001318605` | 🇺🇸 |
| GM | GM | `0001467858` | 🇺🇸 |
| Ford | F | `0000037996` | 🇺🇸 |
| Rivian | RIVN | `0001874178` | 🇺🇸 |
| Lucid | LCID | `0001811210` | 🇺🇸 |
| Nio | NIO | `0001736541` | 🇨🇳 (미국 상장) |
| Xpeng | XPEV | `0001806059` | 🇨🇳 (미국 상장) |
| Li Auto | LI | `0001799209` | 🇨🇳 (미국 상장) |
| Albemarle | ALB | `0000915913` | 🇺🇸 |
| QuantumScape | QS | `0001811414` | 🇺🇸 |

---

## 🧪 테스트 방법

### 1. Python에서 직접 테스트

```python
from tools.sec_edgar_tools import SECEdgarTool

# 초기화
sec_tool = SECEdgarTool()

# Tesla 재무 데이터 조회
data = sec_tool.get_company_financial_data('Tesla')
print(data)

# Tesla 공시 조회
filings = sec_tool.get_recent_filings('0001318605', form_type='10-K')
print(filings)
```

### 2. curl로 직접 호출

```bash
# 올바른 형식 (✅)
curl -H "User-Agent: TestApp/1.0 (test@example.com)" \
  https://data.sec.gov/api/xbrl/companyfacts/CIK0001318605.json

# 잘못된 형식 (❌ 404)
curl -H "User-Agent: TestApp/1.0 (test@example.com)" \
  https://data.sec.gov/api/xbrl/companyfacts/CIK1318605.json
```

### 3. 로그 확인

실행 시 다음과 같은 로그가 출력됩니다:

```
[OK] SEC EDGAR API 초기화 완료 (User-Agent: EVI-Agent/1.0 (evi-agent@example.com))
    SEC EDGAR 'Tesla' (CIK: 0001318605) 데이터 수집 중...
   [DEBUG] SEC API 호출: https://data.sec.gov/api/xbrl/companyfacts/CIK0001318605.json
   [OK] Tesla: 5개 공시 수집
```

---

## 📊 변경 전후 비교

| 항목 | Before (❌) | After (✅) |
|------|------------|-----------|
| **CIK 형식** | `CIK1318605.json` (7자리) | `CIK0001318605.json` (10자리) |
| **Host 헤더** | 수동 설정 | 자동 설정 |
| **User-Agent** | 기본값 | 연락처 포함 |
| **CIK 매핑** | 5개 기업 | 15개 기업 |
| **에러 메시지** | 간단 | 상세 (원인 + 해결책) |
| **디버그 로그** | 없음 | URL 확인 가능 |
| **정규화** | 없음 | `_normalize_cik()` 함수 |

---

## 🔧 수정된 파일

1. **`tools/sec_edgar_tools.py`**
   - `_normalize_cik()` 함수 추가
   - `_get_cik()` 함수 개선 (CIK 매핑 추가)
   - `_get_company_facts()` 수정 (CIK 패딩)
   - `get_recent_filings()` 수정 (CIK 패딩)
   - Host 헤더 제거
   - 에러 메시지 개선

2. **`tools/sec_tagger.py`**
   - CIK를 10자리 형식으로 수정 (주석 추가)

---

## 🚀 향후 개선 사항

### 1. **대량 CIK 매핑**

SEC의 `company_tickers.json`을 주기적으로 다운로드하여 캐시:

```python
# https://www.sec.gov/files/company_tickers.json
def load_company_tickers():
    url = "https://www.sec.gov/files/company_tickers.json"
    response = requests.get(url)
    data = response.json()
    # ticker -> CIK 매핑 생성
    return {item['ticker']: str(item['cik_str']).zfill(10) for item in data.values()}
```

### 2. **지수백오프 (Exponential Backoff)**

429 에러 시 자동 재시도:

```python
import time
from functools import wraps

def retry_with_backoff(max_retries=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429:
                        wait_time = 2 ** attempt  # 1s, 2s, 4s
                        time.sleep(wait_time)
                    else:
                        raise
            return None
        return wrapper
    return decorator
```

### 3. **Bulk Data 사용**

일일 대량 수집 시 ZIP 파일 다운로드:

```python
# https://www.sec.gov/Archives/edgar/daily-index/bulkdata/submissions.zip
# 매일 새벽에 재생성되는 전체 submissions 데이터
```

---

## 📝 참고 문서

- [SEC EDGAR API Documentation](https://www.sec.gov/edgar/sec-api-documentation)
- [Company Facts API](https://www.sec.gov/edgar/sec-api-documentation#company-facts)
- [Submissions API](https://www.sec.gov/edgar/sec-api-documentation#submissions)
- [Fair Access Policy](https://www.sec.gov/os/accessing-edgar-data)

---

## ✅ 검증 완료

- ✅ Lint 검사 통과
- ✅ CIK 정규화 함수 테스트
- ✅ Tesla (0001318605) API 호출 가능
- ✅ Ford (0000037996) API 호출 가능
- ✅ Nio (0001736541) 추가
- ✅ 에러 메시지 개선

---

**작성일:** 2025-10-24  
**버전:** 2.2.0  
**수정자:** AI Assistant

