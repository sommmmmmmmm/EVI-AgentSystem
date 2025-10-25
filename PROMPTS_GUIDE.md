# CoT (Chain of Thought) 프롬프트 가이드

## 🧠 CoT란?

**CoT (Chain of Thought)** = **사고의 연쇄**

AI가 복잡한 문제를 풀 때 **단계별로 생각하도록** 유도하는 프롬프트 기법입니다.

### 왜 중요한가?

| 일반 프롬프트 | CoT 프롬프트 |
|--------------|-------------|
| "분석해줘" | "1단계: 데이터 수집, 2단계: 패턴 파악, 3단계: 결론 도출" |
| 결과만 제시 | 사고 과정 + 결과 |
| 정확도 낮음 | 정확도 높음 |
| 근거 불명확 | 근거 명확 |

---

## 📋 제공되는 CoT 프롬프트

### 1. **Market Trend Analysis** (시장 트렌드 분석)

```python
CoTPromptTemplates.get_market_trend_analysis_prompt()
```

**사고 과정:**
1. **Data Collection**: 뉴스, 리포트, 통계 수집 및 정리
2. **Pattern Identification**: 기술/시장/정책 트렌드 파악
3. **Trend Analysis**: 단기/중기/장기 영향 분석

**결과물:**
- 5-10개 주요 트렌드 (증거 + 중요도 + 시간대)
- 3-5개 전략적 인사이트
- 투자 시사점

**예시:**
```
<step1: 데이터 수집>
- 뉴스 50개 수집 (최근 30일)
- 전기차 배터리 관련 15개
- 충전 인프라 관련 10개
</step1>

<step2: 패턴 파악>
트렌드 1: 고체전지 기술 발전 가속
- Tesla, Samsung SDI 투자 확대
- 2026년 상용화 목표
- 영향: 배터리 밀도 2배 향상
</step2>

<step3: 분석>
투자 시사점:
- 고체전지 관련 기업 주목 (QuantumScape, Samsung SDI)
- 기존 리튬이온 배터리 기업 리스크 증가
</step3>
```

---

### 2. **Supply Chain Analysis** (공급망 분석)

```python
CoTPromptTemplates.get_supplier_matching_prompt()
```

**사고 과정:**
1. **Structure Analysis**: OEM/Tier 1/Tier 2 구조 매핑
2. **Relationship Verification**: 공식 발표, 재무 공시로 검증
3. **Confidence Scoring**: 신뢰도 점수 부여 (0.0-1.0)

**결과물:**
- 공급망 구조도
- 검증된 공급 관계 (신뢰도 ≥ 0.7)
- 투자 추천

**예시:**
```
<verified_suppliers>
LG에너지솔루션 → Tesla
- 제품: 2170 원통형 배터리
- 관계: Primary Supplier
- 신뢰도: 0.95
- 증거: [Tesla 2023 10-K, LG에너지솔루션 사업보고서]

삼성SDI → BMW
- 제품: Gen 5 배터리 셀
- 관계: Exclusive Supplier (5년 계약)
- 신뢰도: 0.98
- 증거: [BMW 공식 발표 2023.03, 삼성SDI IR 자료]
</verified_suppliers>
```

---

### 3. **Financial Analysis** (재무 분석)

```python
CoTPromptTemplates.get_financial_analysis_prompt()
```

**사고 과정:**
1. **Data Collection**: 재무제표 수집 (손익계산서, 재무상태표, 현금흐름표)
2. **Ratio Analysis**: 주요 비율 계산 (ROE, P/E, 부채비율 등)
3. **Comparative Analysis**: 동종업계 비교 + 과거 추세

**결과물:**
- 주요 재무 지표
- 밸류에이션 분석
- 투자 점수 (0-100점)

**예시:**
```
<financial_metrics>
LG에너지솔루션 (2023 FY)
- 매출: 25.4조원 (YoY +26%)
- 영업이익률: 8.2% (전년 5.1%)
- ROE: 12.5%
- 부채비율: 45%
- 출처: DART 사업보고서 2024.03.15
</financial_metrics>

<investment_scores>
재무 건전성 (40점): 35/40 (양호)
성장 잠재력 (30점): 27/30 (우수)
밸류에이션 (30점): 18/30 (보통)
---
총점: 80/100 (투자 매력적)
</investment_scores>
```

---

### 4. **Risk Assessment** (리스크 평가)

```python
CoTPromptTemplates.get_risk_assessment_prompt()
```

**사고 과정:**
1. **Risk Identification**: 정책/기술/시장/공급망/재무/ESG 리스크 식별
2. **Risk Quantification**: 확률 x 영향도 계산
3. **Mitigation Strategies**: 완화 전략 제시

**결과물:**
- 8-12개 주요 리스크 (확률 x 영향도)
- 리스크 프로파일 (High/Medium/Low)
- 완화 전략

**예시:**
```
<risk_factors>
리스크 1: IRA 보조금 축소 가능성
- 확률: 중간 (30%)
- 영향: 높음 (매출 20% 감소 가능)
- 대상: 미국 시장 의존 기업 (Tesla, GM)
- 시간: 2025-2026

리스크 2: 원자재 가격 급등
- 확률: 높음 (60%)
- 영향: 중간 (마진 5-10%p 하락)
- 대상: 배터리 제조사 전체
- 증거: [리튬 가격 2배 상승 Bloomberg 2024.01]
</risk_factors>

<risk_mitigation>
전략 1: 포트폴리오 다각화
- 미국 의존 기업 50% 이하 유지
- 한국/유럽 기업 포함

전략 2: 수직 통합 기업 선호
- 원자재 확보한 기업 (Albemarle, Ganfeng)
</risk_mitigation>
```

---

### 5. **Investment Strategy** (투자 전략)

```python
CoTPromptTemplates.get_investment_strategy_prompt()
```

**사고 과정:**
1. **Opportunity Assessment**: 시장 규모, 성장률, 경쟁 구도
2. **Portfolio Construction**: 시가총액/지역/밸류체인별 분산
3. **Entry Strategy**: 진입 시점, 가격대, 비중

**결과물:**
- 시장 분석
- 투자 기회 (Core/Satellite/Emerging)
- 포트폴리오 전략 (비중, 리밸런싱, 모니터링)

**예시:**
```
<investment_opportunities>
Core Holdings (50-60%):
1. LG에너지솔루션 (20%)
   - 논거: 글로벌 2위, Tesla/GM 공급
   - 목표수익: 30-40%
   - 진입가: 40-42만원
   - 리스크: 원자재 가격 변동

2. Samsung SDI (20%)
   - 논거: 프리미엄 OEM 고객, 고수익
   - 목표수익: 25-35%
   - 진입가: 35-37만원

Satellite Positions (20-30%):
3. QuantumScape (10%)
   - 논거: 고체전지 선도, 고위험·고수익
   - 목표수익: 100%+
   - 진입가: $5-6
   - 리스크: 기술 상용화 실패

<portfolio_strategy>
전체 배분:
- 배터리: 60%
- OEM: 20%
- 소재/부품: 20%

리밸런싱:
- 분기별 검토
- 비중 ±5%p 벗어나면 조정

모니터링:
- 주간: 주가, 거래량
- 월간: 공시, 뉴스
- 분기: 실적, 가이던스
</portfolio_strategy>
```

---

### 6. **Report Generation** (보고서 생성)

```python
CoTPromptTemplates.get_report_generation_prompt()
```

**사고 과정:**
1. **Content Organization**: 모든 분석 결과 통합 및 우선순위
2. **Narrative Development**: 일관된 스토리 구성
3. **Quality Assurance**: 인용 확인, 일관성 검증

**결과물:**
- Executive Summary (2-3 문단)
- Market Analysis (상세)
- Investment Recommendations (구체적)
- Risk Analysis (완화 전략)
- Glossary (용어 설명)
- References (출처 목록)

**구조:**
```markdown
# EV 산업 투자 리포트 (2024년 3월)

## Executive Summary
현재 전기차 시장은 연평균 25% 성장 중이며, 배터리 공급망이 
핵심 투자 기회입니다. 특히 한국 배터리 3사(LG/Samsung/SK)가 
글로벌 시장점유율 30%를 차지하며 유리한 위치에 있습니다...

## Market Analysis
### 1. 산업 트렌드
- 고체전지 기술 개발 가속...
- 충전 인프라 확대 (전년 대비 40% 증가)...

### 2. 공급망 분석
- Tesla: LG/Panasonic 의존...
- BMW: Samsung SDI 독점 공급...

## Investment Recommendations
### Top Picks
1. **LG에너지솔루션** (목표가: 52만원, +30%)
   - 투자 논거: 글로벌 2위, Tesla/GM 공급...
   - 리스크: 원자재 가격 변동, IRA 정책 불확실성...

## Risk Analysis
주요 리스크:
1. 정책 리스크: IRA 보조금 축소 (확률 30%, 영향 높음)
2. 원자재 리스크: 리튬 가격 급등 (확률 60%, 영향 중간)

## Glossary
- **NCM**: Nickel-Cobalt-Manganese (삼원계 양극재)
- **LFP**: Lithium Iron Phosphate (인산철 배터리)

## References
1. DART - LG에너지솔루션 사업보고서 (2024.03.15)
2. SEC EDGAR - Tesla 10-K (2024.02.01)
3. Bloomberg - Lithium Price Index (2024.03.20)
```

---

## 🎯 사용 방법

### 기본 사용

```python
from prompts.cot_templates import CoTPromptTemplates

# 시장 트렌드 분석 프롬프트 가져오기
prompt = CoTPromptTemplates.get_market_trend_analysis_prompt()

# LLM에 전달
response = llm.generate(prompt)
```

### 컨텍스트 추가

```python
# 추가 컨텍스트와 함께 사용
context = {
    'description': 'Q1 2024 EV market analysis focusing on battery sector',
    'data_sources': ['DART', 'SEC EDGAR', 'Tavily News'],
    'previous_results': 'Previous analysis showed 25% market growth'
}

prompt = CoTPromptTemplates.get_cot_prompt_for_agent(
    agent_type='market_trend',
    context=context
)
```

### 사용 가능한 프롬프트 타입

```python
from prompts.cot_templates import get_available_prompt_types

types = get_available_prompt_types()
# ['market_trend', 'supplier_matching', 'financial_analysis', 
#  'risk_assessment', 'investment_strategy', 'report_generation']
```

---

## 💡 프롬프트 작성 원칙

### 1. **구조화된 사고 과정**

```xml
<thinking_process>
<step1: 제목>
설명 및 체크리스트
</step1>

<step2: 제목>
설명 및 체크리스트
</step2>

<step3: 제목>
설명 및 체크리스트
</step3>
</thinking_process>
```

### 2. **명확한 결과 형식**

```xml
<analysis_result>
<section1>
내용...
</section1>

<section2>
내용...
</section2>
</analysis_result>
```

### 3. **항상 출처 표시**

```
- Tesla announced partnership with LG [Source: Tesla Press Release 2024.01.15]
- Market share increased 30% [Source: Bloomberg EV Report 2024.02]
```

### 4. **구체적인 수치**

```
❌ "많이 증가했다"
✅ "30% 증가 (전년 대비)"

❌ "비싸다"
✅ "P/E 35배 (업계 평균 25배 대비 40% 프리미엄)"
```

---

## 🧪 테스트 예시

```python
# 1. 프롬프트 로드
from prompts.cot_templates import CoTPromptTemplates

prompt = CoTPromptTemplates.get_financial_analysis_prompt()

# 2. 데이터 추가
company_data = """
LG에너지솔루션 재무 데이터:
- 매출: 25.4조원
- 영업이익: 2.1조원
- 당기순이익: 1.6조원
"""

full_prompt = prompt + f"\n\n<company_data>\n{company_data}\n</company_data>"

# 3. LLM 호출
response = llm.generate(full_prompt)

# 4. 결과 확인
print(response)
```

**기대 출력:**
```
<thinking_process>
<step1: Data Collection>
재무 데이터 확인:
- 매출: 25.4조원 ✓
- 영업이익: 2.1조원 ✓
- 영업이익률: 8.27% 계산
</step1>

<step2: Ratio Analysis>
수익성 지표:
- ROE: (데이터 부족으로 계산 불가)
- 영업이익률: 8.27% (양호)
...
</step2>
...
</thinking_process>

<analysis_result>
<financial_metrics>
LG에너지솔루션:
- 매출: 25.4조원
- 영업이익: 2.1조원 (마진 8.27%)
- 당기순이익: 1.6조원 (마진 6.30%)
</financial_metrics>
...
</analysis_result>
```

---

## 📚 참고 자료

- [Chain of Thought Prompting Paper (Google, 2022)](https://arxiv.org/abs/2201.11903)
- [OpenAI Best Practices](https://platform.openai.com/docs/guides/prompt-engineering)
- [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/claude/docs/prompt-engineering)

---

## ✅ 체크리스트

프롬프트 작성 시 확인사항:

- [ ] 사고 과정이 단계별로 명확한가?
- [ ] 각 단계에 구체적인 지침이 있는가?
- [ ] 결과 형식이 명확히 정의되었는가?
- [ ] 출처 표시 요구사항이 있는가?
- [ ] 구체적인 수치/예시가 포함되었는가?
- [ ] 대상 독자가 명확한가?

---

**작성일:** 2025-10-24  
**버전:** 3.0.0  
**작성자:** AI Assistant

