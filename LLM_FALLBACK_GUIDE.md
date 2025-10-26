# LLM API Fallback 전략

## 현재 문제

investment_strategy_agent.py 260-271행:

```python
def _generate_investment_thesis(self, company: str, company_data: Dict[str, Any]) -> str:
    """API 실패 시 에러 메시지 반환"""
    return f"[ERROR] '{company}'의 투자 논리를 생성할 수 없습니다. API 키를 확인하세요."

def _estimate_target_price(self, company: str, company_data: Dict[str, Any]) -> float:
    """API 실패 시 0 반환"""
    return 0.0
```

**문제점:**
- LLM API 실패 시 보고서에 에러 메시지가 그대로 노출
- 투자 논리, 목표가, 투자 기간 등이 모두 빈 값
- 보고서가 쓸모없어짐

---

## Fallback이란?

**Fallback = Plan A가 실패하면 자동으로 Plan B, Plan C를 시도**

### 일상 예시

#### 음식 배달:
```
Plan A: 카드 결제 → [실패] 잔액 부족
Plan B: 간편결제 → [실패] 미연동
Plan C: 현금 결제 → [성공] ✅
```

#### 네비게이션:
```
Plan A: 고속도로 (최단) → [실패] 사고로 정체
Plan B: 국도 (우회) → [성공] ✅
```

---

## 개선 방안: 3단계 Fallback

### 1. 투자 논리 생성

```python
def _generate_investment_thesis(self, company: str, company_data: Dict[str, Any]) -> str:
    """투자 논리 생성 (3단계 Fallback)"""
    
    # ========================================
    # Plan A: LLM API (최고 품질)
    # ========================================
    try:
        print(f"[Plan A] LLM API로 {company} 투자 논리 생성 중...")
        
        prompt = f"""
        기업명: {company}
        재무 데이터: {company_data.get('financial_ratios', {})}
        시장 트렌드: {company_data.get('market_trends', [])}
        
        위 정보를 바탕으로 투자 논리를 작성하세요.
        """
        
        llm_response = self.llm_tool.generate(prompt)
        print(f"[Plan A] ✅ LLM API 성공")
        return llm_response
        
    except Exception as e:
        print(f"[Plan A] ❌ LLM API 실패: {e}")
        
        # ========================================
        # Plan B: 재무 데이터 기반 자동 생성 (중간 품질)
        # ========================================
        try:
            print(f"[Plan B] 재무 데이터 기반으로 {company} 투자 논리 생성 중...")
            return self._generate_thesis_from_financial_data(company, company_data)
            
        except Exception as e2:
            print(f"[Plan B] ❌ 재무 데이터 기반 생성 실패: {e2}")
            
            # ========================================
            # Plan C: 기본 템플릿 (최소 품질)
            # ========================================
            print(f"[Plan C] 기본 템플릿으로 {company} 투자 논리 생성")
            return self._generate_basic_thesis_template(company, company_data)


def _generate_thesis_from_financial_data(self, company: str, company_data: Dict[str, Any]) -> str:
    """Plan B: 재무 데이터로 간단한 투자 논리 생성"""
    
    ratios = company_data.get('financial_ratios', {})
    roe = ratios.get('roe', 0.0) * 100
    operating_margin = ratios.get('operating_margin', 0.0) * 100
    debt_ratio = ratios.get('debt_ratio', 0.0) * 100
    
    # 재무 지표 기반 평가
    if roe > 15:
        roe_comment = "우수한 자기자본이익률(ROE)"
    elif roe > 10:
        roe_comment = "양호한 자기자본이익률(ROE)"
    else:
        roe_comment = "개선이 필요한 자기자본이익률(ROE)"
    
    if operating_margin > 10:
        margin_comment = "높은 영업이익률"
    elif operating_margin > 5:
        margin_comment = "적정 영업이익률"
    else:
        margin_comment = "낮은 영업이익률"
    
    if debt_ratio < 50:
        debt_comment = "안정적인 재무구조"
    elif debt_ratio < 100:
        debt_comment = "적정 부채 수준"
    else:
        debt_comment = "높은 부채비율로 재무 리스크 존재"
    
    thesis = f"""
{company}는 {roe_comment}({roe:.1f}%)를 기록하고 있으며, {margin_comment}({operating_margin:.1f}%)로 
수익성을 확보하고 있습니다. {debt_comment}(부채비율 {debt_ratio:.1f}%)로 전기차 시장의 성장과 함께 
투자 가치가 있는 기업으로 판단됩니다.
    """.strip()
    
    return thesis


def _generate_basic_thesis_template(self, company: str, company_data: Dict[str, Any]) -> str:
    """Plan C: 최소한의 기본 템플릿"""
    
    # OEM인지 공급업체인지 확인
    is_oem = company_data.get('company_type') == 'oem'
    
    if is_oem:
        return f"{company}는 전기차 시장의 주요 OEM 제조사로, 시장 성장에 따른 수혜가 예상됩니다."
    else:
        return f"{company}는 전기차 공급망의 핵심 기업으로, 전기차 수요 증가에 따른 성장이 기대됩니다."
```

---

### 2. 목표가 추정

```python
def _estimate_target_price(self, company: str, company_data: Dict[str, Any]) -> float:
    """목표가 추정 (3단계 Fallback)"""
    
    # Plan A: LLM API로 추정
    try:
        prompt = f"{company}의 적정 목표가를 추정하세요..."
        response = self.llm_tool.generate(prompt)
        price = self._extract_price_from_llm_response(response)
        if price > 0:
            return price
    except Exception as e:
        print(f"[WARNING] LLM 목표가 추정 실패: {e}")
    
    # Plan B: PER 기반 계산
    try:
        return self._calculate_target_price_by_per(company, company_data)
    except Exception as e:
        print(f"[WARNING] PER 기반 계산 실패: {e}")
    
    # Plan C: 현재가 기준 +20%
    try:
        current_price = company_data.get('stock_price', 0)
        if current_price > 0:
            return current_price * 1.2  # 20% 상승 가정
    except:
        pass
    
    # Plan D: 없음 표시
    return None  # "N/A"로 표시


def _calculate_target_price_by_per(self, company: str, company_data: Dict[str, Any]) -> float:
    """Plan B: PER 기반 목표가 계산"""
    
    # 현재 주가 정보
    current_price = company_data.get('stock_price', 0)
    current_per = company_data.get('financial_ratios', {}).get('per', 0)
    
    # 산업 평균 PER (전기차/배터리)
    industry_avg_per = 25  # 성장주 평균
    
    if current_per > 0 and current_price > 0:
        # 현재가 × (산업 평균 PER / 현재 PER)
        target_price = current_price * (industry_avg_per / current_per)
        return round(target_price, 2)
    
    raise ValueError("PER 데이터 부족")
```

---

### 3. 투자 기간 추정

```python
def _estimate_time_horizon(self, company: str, company_data: Dict[str, Any]) -> str:
    """투자 기간 추정 (3단계 Fallback)"""
    
    # Plan A: LLM API
    try:
        prompt = f"{company}의 적정 투자 기간을 추정하세요..."
        return self.llm_tool.generate(prompt)
    except:
        pass
    
    # Plan B: 재무 안정성 기반
    try:
        debt_ratio = company_data.get('financial_ratios', {}).get('debt_ratio', 0)
        roe = company_data.get('financial_ratios', {}).get('roe', 0)
        
        # 안정적 (부채 낮음, ROE 높음) → 장기
        if debt_ratio < 0.5 and roe > 0.15:
            return "장기 투자 (12개월 이상)"
        
        # 보통 → 중기
        elif debt_ratio < 1.0 and roe > 0.1:
            return "중기 투자 (6-12개월)"
        
        # 불안정 → 단기
        else:
            return "단기 투자 (3-6개월)"
            
    except:
        pass
    
    # Plan C: 기본값
    return "중기 투자 (6-12개월)"  # 기본 권장 기간
```

---

## 실행 결과 비교

### ❌ Fallback 없이 (현재)

```
Tesla 분석:
- 투자 논리: [ERROR] API 키를 확인하세요.
- 목표가: 0.0
- 투자 기간: [ERROR] API 키를 확인하세요.
```

**보고서가 쓸모없음!**

---

### ✅ Fallback 적용 후

```
Tesla 분석:

[Plan A] LLM API 시도... ❌ 실패 (API 키 없음)
[Plan B] 재무 데이터 기반 생성... ✅ 성공!

- 투자 논리: 
  "Tesla는 우수한 자기자본이익률(ROE 18.5%)를 기록하고 있으며, 
   높은 영업이익률(12.3%)로 수익성을 확보하고 있습니다. 
   안정적인 재무구조(부채비율 42%)로 전기차 시장의 성장과 함께 
   투자 가치가 있는 기업으로 판단됩니다."
   
- 목표가: $285.60 (현재가 $238 × 1.2)

- 투자 기간: 장기 투자 (12개월 이상)
```

**의미 있는 보고서!** 🎉

---

## 장점

### 1. 안정성
- LLM API 없어도 보고서 생성 가능
- 에러 메시지 대신 실용적인 정보 제공

### 2. 품질 보장
- Plan A (LLM): 최고 품질
- Plan B (재무): 중간 품질
- Plan C (템플릿): 최소 품질

### 3. 사용자 경험
- 보고서가 항상 완성됨
- API 크레딧 소진 시에도 작동

---

## 구현 우선순위

### 🔥 긴급 (Must Have):
1. `_generate_investment_thesis()` - 투자 논리
2. `_estimate_target_price()` - 목표가

### ⚠️ 중요 (Should Have):
3. `_estimate_time_horizon()` - 투자 기간

### 💡 선택 (Nice to Have):
4. 리스크 분석 fallback
5. 시장 트렌드 분석 fallback

---

## 구현할까요?

어떤 fallback을 먼저 구현하시겠습니까?

1. 투자 논리 fallback (가장 중요)
2. 목표가 fallback
3. 모두 구현
4. 일단 설명만 듣고 나중에

