# 공급망 관계 검색 개선 옵션

## 현재 문제
- 12개 OEM 중 상위 3개(Tesla, BYD, BMW)만 검색
- Ford, GM, Hyundai 등과의 관계 놓침
- API 크레딧 절약을 위한 제한

---

## 옵션 1: 검색 개수 늘리기 (단순하지만 비용 증가)

### 변경 사항
```python
# 현재: major_oems[:3] (3개)
# 변경: major_oems[:6] (6개)
for oem in major_oems[:6]:  # Tesla, BYD, BMW, Mercedes, VW, Ford
```

### 장점
- 간단하고 효과적
- 더 많은 OEM 관계 발견

### 단점
- API 호출 2배 증가 (90 → 180회)
- Tavily 크레딧 빠르게 소진

### 추천도: ⭐⭐⭐ (3/5)
비용이 허용된다면 가장 간단한 방법

---

## 옵션 2: 스마트 OEM 선택 (효율적)

### 아이디어
공급업체 이름이나 카테고리 기반으로 관련성 높은 OEM만 선택

### 변경 사항
```python
def _select_relevant_oems(self, supplier_name: str, category: str) -> List[str]:
    """공급업체에 가장 관련성 높은 OEM 선택 (최대 5개)"""
    
    # 한국 공급업체 → 한국 OEM 우선
    korean_suppliers = ['LG', 'Samsung', 'SK', 'Hyundai', 'Posco']
    if any(k in supplier_name for k in korean_suppliers):
        priority_oems = ['Hyundai', 'Kia', 'Tesla', 'Ford', 'GM']
    
    # 배터리 공급업체 → 주요 EV 제조사
    elif 'battery' in category.lower() or 'CATL' in supplier_name or 'Panasonic' in supplier_name:
        priority_oems = ['Tesla', 'Ford', 'GM', 'BMW', 'Volkswagen']
    
    # 중국 공급업체 → 중국+글로벌 OEM
    elif 'CATL' in supplier_name or 'BYD' in supplier_name:
        priority_oems = ['BYD', 'Nio', 'Tesla', 'Ford', 'BMW']
    
    # 기본: 시장 점유율 상위 5개
    else:
        priority_oems = ['Tesla', 'BYD', 'Volkswagen', 'Ford', 'GM']
    
    return priority_oems[:5]
```

### 장점
- API 호출 효율적 (관련성 높은 OEM만 검색)
- 더 정확한 관계 발견 가능

### 단점
- 구현 복잡도 증가
- 휴리스틱 규칙 필요

### 추천도: ⭐⭐⭐⭐⭐ (5/5)
**가장 추천!** 효율성과 정확도 균형

---

## 옵션 3: 배치 검색 (1번 호출로 여러 OEM 확인)

### 아이디어
하나의 쿼리로 여러 OEM 관계를 한 번에 검색

### 변경 사항
```python
# 현재: 각 OEM별로 개별 검색
query = f"{supplier_name} supplier {oem} partnership"

# 변경: 모든 OEM을 포함한 1개 쿼리
query = f"{supplier_name} supplier electric vehicle partnership Tesla Ford GM BMW"
```

그런 다음 결과 텍스트에서 여러 OEM 이름을 추출

### 장점
- API 호출 최소화 (공급업체당 1~2회)
- 비용 효율적

### 단점
- 검색 정확도 떨어질 수 있음
- 모든 OEM 관계를 놓칠 위험

### 추천도: ⭐⭐⭐ (3/5)
API 크레딧이 매우 제한적일 때

---

## 옵션 4: 하이브리드 (추천!)

### 전략
1. **1단계**: 배치 검색으로 빠른 스캔 (공급업체당 1회)
2. **2단계**: 발견된 관계에 대해서만 상세 검색 (최대 3회)

### 예시
```python
# 1단계: 빠른 스캔
query = f"{supplier_name} EV battery supplier customers OEM partnership"
results = self.web_search_tool.search(query, num_results=3)

# 텍스트에서 언급된 OEM 추출
mentioned_oems = []
for oem in major_oems:
    if oem.lower() in combined_text.lower():
        mentioned_oems.append(oem)

# 2단계: 언급된 OEM에 대해서만 상세 검색 (최대 3개)
for oem in mentioned_oems[:3]:
    query = f"{supplier_name} {oem} supply contract partnership"
    # 상세 검색...
```

### 장점
- API 호출 최소화 (공급업체당 1~4회)
- 관련성 높은 OEM에 집중
- 정확도와 효율성 균형

### 단점
- 구현이 가장 복잡

### 추천도: ⭐⭐⭐⭐⭐ (5/5)
**최적 솔루션!** 정확도 + 효율성

---

## 비용 비교

| 옵션 | 공급업체당 API 호출 | 30개 공급업체 총 호출 | Tavily 크레딧 |
|------|-------------------|---------------------|---------------|
| 현재 (3개) | 3 | 90 | ~90 |
| 옵션1 (6개) | 6 | 180 | ~180 |
| 옵션2 (스마트 5개) | 5 | 150 | ~150 |
| 옵션3 (배치) | 1 | 30 | ~30 |
| 옵션4 (하이브리드) | 1~4 | 60~90 | ~60 |

---

## 추천 순위

1. **옵션4 (하이브리드)** ⭐⭐⭐⭐⭐
   - 정확도 ✅ / 비용 ✅
   - 구현: 중간

2. **옵션2 (스마트 선택)** ⭐⭐⭐⭐⭐
   - 정확도 ✅ / 비용 ✅
   - 구현: 중간

3. **옵션1 (개수 증가)** ⭐⭐⭐
   - 정확도 ✅ / 비용 ❌
   - 구현: 쉬움 (1줄 수정)

4. **옵션3 (배치)** ⭐⭐⭐
   - 정확도 ⚠️ / 비용 ✅
   - 구현: 중간

---

## 어떤 것을 선택할까요?

**빠른 개선이 필요하다면**: 옵션1 ([:3] → [:6])
**장기적으로 최적화하려면**: 옵션2 또는 옵션4

