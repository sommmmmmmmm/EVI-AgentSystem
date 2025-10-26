# 🎯 상장사 필터링 전략 (투자 보고서 최적화)

## 핵심 아이디어
**투자 보고서는 일반 투자자가 실제로 투자할 수 있는 기업만 분석해야 한다!**

---

## 📊 현재 vs 개선

### ❌ **이전 (비효율적)**
```
웹에서 발견된 30개 기업 전부 분석:
├─ 상장사 12개 (투자 가능) ✅
├─ 비상장사 15개 (투자 불가) ❌  ← 불필요!
└─ 불명확 3개 ❓

→ 30개 × 12 OEM × 1 검색 = 360번 API 호출
→ 비상장사 분석에 API 크레딧 낭비
```

### ✅ **개선 후 (효율적)**
```
상장사 12개 + 참고용 비상장 5개 = 17개 분석:
├─ 상장사 12개 (우선 분석) ✅
└─ 비상장사 5개 (참고용) ⚠️

→ 17개 × 12 OEM × 1 검색 = 204번 API 호출

절감: 360 → 204 (43% 감소!)
```

---

## 🚀 구현 내용

### 1. 상장사 확인 함수 추가

`supplier_matching_agent.py` 518-570행:

```python
def _is_listed_company(self, company_name: str) -> tuple[bool, str]:
    """
    기업이 상장사인지 확인
    
    Returns:
        (is_listed, ticker_symbol)
    """
    LISTED_COMPANIES = {
        # 한국
        'LG에너지솔루션': '373220.KS',
        '삼성SDI': '006400.KS',
        'SK이노베이션': '096770.KS',
        '현대자동차': '005380.KS',
        
        # 미국
        'Tesla': 'TSLA',
        'Ford': 'F',
        'GM': 'GM',
        'Rivian': 'RIVN',
        
        # 중국
        'BYD': '002594.SZ',
        'CATL': '300750.SZ',
        'Nio': 'NIO',
        
        # 유럽
        'BMW': 'BMW.DE',
        'Volkswagen': 'VOW.DE',
        'Mercedes': 'MBG.DE',
        
        # 일본
        'Panasonic': '6752.T',
        'Toyota': '7203.T',
    }
    
    # 정확한 매칭 + 부분 매칭
    ...
```

### 2. 상장사 우선 필터링

`supplier_matching_agent.py` 572-600행:

```python
def _structure_supplier_result(...):
    # 상장사 필터링
    for supplier in suppliers:
        is_listed, ticker = self._is_listed_company(company_name)
        
        if is_listed:
            listed_suppliers.append(supplier)
        else:
            unlisted_suppliers.append(supplier)
    
    print(f"[FILTER] 상장사: {len(listed_suppliers)}개 / 비상장사: {len(unlisted_suppliers)}개")
    print(f"[STRATEGY] 투자 보고서 → 상장사 우선 분석")
    
    # 상장사 먼저 + 비상장 최대 5개
    priority_suppliers = listed_suppliers + unlisted_suppliers[:5]
```

### 3. 신뢰도 증가 (상장사 +0.2)

`supplier_matching_agent.py` 618-624행:

```python
# 상장사 정보 추가
is_listed = supplier.get('is_listed', False)
ticker = supplier.get('ticker', '')

# 상장사는 신뢰도 증가 (투자 가능성)
if is_listed:
    confidence = min(confidence + 0.2, 1.0)
```

### 4. 투자 가능 태그 추가

`supplier_matching_agent.py` 646-663행:

```python
# 상장사 태그 추가
investable_tag = '📈 투자가능' if is_listed else ''

structured_supplier = {
    'name': name,
    'is_listed': is_listed,  # 상장 여부
    'ticker': ticker,  # 티커 심볼
    'investable': is_listed,  # 투자 가능 여부
    'investable_tag': investable_tag,  # 표시용 태그
    'confidence_score': confidence,  # 상장사는 +0.2
    ...
}
```

---

## 📈 효과

### 1. API 크레딧 절감 (43%)
- **이전**: 360번 검색 (30개 × 12 OEM)
- **개선**: 204번 검색 (17개 × 12 OEM)
- **절감**: 156번 (43%)

### 2. 보고서 실용성 증가
- **투자 가능 기업**에 집중
- 티커 심볼 제공 → 바로 매수 가능
- 비상장사는 참고용으로만 최소 포함

### 3. 신뢰도 차등화
```
상장사 (투자 가능):
- 기본 신뢰도 0.6 + 상장 보너스 0.2 = 0.8+

비상장사 (투자 불가):
- 기본 신뢰도 0.6 유지
```

### 4. 분석 효율 증가
- 상위 12개 상장사에 분석 리소스 집중
- 비상장사는 5개만 참고용으로 포함

---

## 🎯 주요 상장사 리스트 (포함된 기업)

### **한국 (KOSPI/KOSDAQ)**
- LG에너지솔루션 `373220.KS`
- 삼성SDI `006400.KS`
- SK이노베이션 `096770.KS`
- 현대자동차 `005380.KS`
- 기아 `000270.KS`
- 에코프로비엠 `247540.KQ`
- 포스코퓨처엠 `003670.KS`
- LG화학 `051910.KS`

### **미국 (NYSE/NASDAQ)**
- Tesla `TSLA`
- Ford `F`
- GM `GM`
- Rivian `RIVN`
- Lucid `LCID`
- Albemarle `ALB`

### **중국 (Shenzhen/NYSE)**
- BYD `002594.SZ`
- CATL `300750.SZ`
- Nio `NIO`
- Xpeng `XPEV`
- Li Auto `LI`

### **유럽 (Frankfurt)**
- BMW `BMW.DE`
- Volkswagen `VOW.DE`
- Mercedes-Benz `MBG.DE`
- Porsche `P911.DE`

### **일본 (Tokyo)**
- Panasonic `6752.T`
- Toyota `7203.T`

---

## ❌ 제외되는 비상장사 예시

### 자동 필터링:
- **SK On** (SK이노베이션 자회사, 분리 전)
- **Bosch** (독일 비상장 대기업)
- **Continental** (복잡한 지배구조)
- **Denso** (소액 투자 어려움)
- 대부분의 중소 부품업체

### 참고용으로만 포함 (최대 5개):
- 시장 영향력이 큰 비상장사
- 주요 OEM의 핵심 공급업체

---

## 🔍 추가 개선 가능성

### 1. yfinance 동적 확인
현재는 하드코딩된 리스트, 향후 yfinance로 실시간 확인 가능:

```python
import yfinance as yf

def is_listed_dynamic(company_name: str) -> tuple[bool, str]:
    """yfinance로 상장 여부 동적 확인"""
    try:
        ticker = yf.Ticker(company_name)
        info = ticker.info
        if 'marketCap' in info and info['marketCap'] > 0:
            return True, company_name
    except:
        pass
    return False, ''
```

### 2. 시가총액 기준 필터
```python
# 시가총액 1조원 이상만 분석
if market_cap > 1_000_000_000_000:
    analyze()
```

### 3. 거래량 기준 필터
```python
# 일평균 거래량 10억원 이상만 분석
if avg_daily_volume > 1_000_000_000:
    analyze()
```

---

## 💡 결론

**투자 보고서는 투자 가능한 기업에 집중해야 한다!**

✅ API 크레딧 43% 절감  
✅ 보고서 실용성 증가  
✅ 신뢰도 차등화  
✅ 분석 효율 증가  

**이 전략으로 비용은 절감하고 품질은 향상됩니다!**

