# 🧪 Mock 테스트 가이드

API 키 없이 보고서 생성 시스템을 테스트할 수 있는 가이드입니다.

## 📋 목차

1. [개요](#개요)
2. [준비사항](#준비사항)
3. [실행 방법](#실행-방법)
4. [Mock 데이터 설명](#mock-데이터-설명)
5. [결과 확인](#결과-확인)
6. [문제 해결](#문제-해결)

---

## 개요

### Mock 테스트란?

- **실제 API를 호출하지 않고** 시스템을 테스트할 수 있습니다
- **샘플 데이터**로 전체 프로세스를 확인할 수 있습니다
- **API 키가 없어도** 집에서 테스트 가능합니다

### 제공되는 Mock Tools

| Tool | 실제 Tool | Mock Tool | 설명 |
|------|----------|-----------|------|
| Web Search | Tavily/DuckDuckGo | `MockWebSearchTool` | 가짜 뉴스 기사 반환 |
| LLM | OpenAI GPT-4 | `MockLLMTool` | 미리 정의된 분석 결과 반환 |
| DART | 금융감독원 DART | `MockDARTTool` | 가짜 재무제표 생성 |

---

## 준비사항

### 1. Python 환경 확인

```bash
python --version  # Python 3.8 이상 필요
```

### 2. 의존성 설치

```bash
cd /Users/jangsomin/workspace/EVI-AgentSystem
pip install -r requirements.txt
```

### 3. 파일 확인

다음 파일들이 있는지 확인:
- ✅ `mock_tools.py` - Mock 툴 정의
- ✅ `test_report_generation.py` - 테스트 스크립트
- ✅ `MOCK_TEST_README.md` - 이 파일

---

## 실행 방법

### 방법 1: 직접 실행

```bash
cd /Users/jangsomin/workspace/EVI-AgentSystem
python test_report_generation.py
```

### 방법 2: Mock Tools만 테스트

```bash
python mock_tools.py
```

### 예상 출력

```
======================================================================
🧪 보고서 생성 테스트 (Mock Mode)
======================================================================

⚠️  주의: 실제 API를 호출하지 않고 Mock 데이터를 사용합니다.
   실제 데이터가 아닌 테스트용 샘플 데이터입니다.

[설정 정보]
   - 보고서 월: 2025-10
   - 모드: Mock Testing Mode
   - 키워드: EV, electric vehicle, battery, charging

[Mock 툴 초기화...]
   [OK] Mock Web Search Tool ✓
   [OK] Mock LLM Tool ✓
   [OK] Mock DART Tool ✓

[초기 State 생성...]
   [OK] 분석 대상 기업: 3개
       - LG에너지솔루션 (Battery)
       - Samsung SDI (Battery)
       - SK온 (Battery)

[워크플로우 실행 시작!]
======================================================================
...
```

---

## Mock 데이터 설명

### 1. 재무제표 데이터 (`MockDARTTool`)

각 기업마다 **랜덤하지만 현실적인** 재무 데이터 생성:

```python
# 예시 데이터 구조
{
    'income_statement': {
        'revenue': 5000000000000,      # 5조원
        'rnd_expense': 750000000000,   # R&D 15% (랜덤 8-18%)
        'net_income': 400000000000,    # 순이익 8%
        'depreciation': 250000000000    # 감가상각 5%
    },
    'balance_sheet': {
        'total_assets': 12500000000000,        # 총자산
        'intangible_assets': 1500000000000,    # 무형자산 (랜덤 20-40%)
        'current_assets': 6000000000000,
        'inventory': 750000000000
    },
    'cash_flow_statement': {
        'capex': 1250000000000,        # CapEx (랜덤 10-25%)
        'operating_cash_flow': 750000000000
    }
}
```

### 2. 웹 검색 결과 (`MockWebSearchTool`)

쿼리 타입에 따라 다른 Mock 컨텐츠 반환:

- **Governance 검색**: "Strong corporate governance practices..."
- **Legal 검색**: "No significant legal issues..."
- **Management 검색**: "Strong leadership demonstrated..."

### 3. LLM 응답 (`MockLLMTool`)

프롬프트 분석하여 적절한 응답 생성:

- **리스크 분석**: JSON 형식의 리스크 평가
- **정성적 분석**: 시장 포지셔닝, 기술 리더십 등
- **시장 트렌드**: 성장 전망, 주요 동인 등

---

## 결과 확인

### 1. 출력 파일 위치

```
outputs/mock_test/
├── mock_report_20251023_143022.json      # JSON 형식 보고서
└── mock_report_20251023_143022.md        # Markdown 형식 보고서
```

### 2. JSON 보고서 구조

```json
{
  "metadata": {
    "generated_at": "20251023_143022",
    "mode": "mock_test",
    "config": { ... }
  },
  "report": {
    "executive_summary": "...",
    "market_analysis": "...",
    "financial_analysis": "...",
    "risk_assessment": "...",
    "investment_strategy": "..."
  },
  "statistics": {
    "companies_analyzed": 3,
    "news_articles": 15,
    "errors": 0
  }
}
```

### 3. Markdown 보고서 예시

```markdown
# Investment Analysis Report (Mock Test)

**Generated**: 2025-10-23 14:30:22
**Mode**: Mock Testing (샘플 데이터 사용)

---

## Executive Summary

This analysis provides comprehensive evaluation...

---

## Financial Analysis

### LG에너지솔루션

**리스크 평가:**
- 종합 등급: MEDIUM (0.45)
- 정량적 리스크: 0.52 (기술투자: 0.48, 운전자본: 0.35, 성장단계: 0.62)
- 정성적 리스크: 0.20 (리스크 이슈: 2건)

...
```

---

## 리스크 분석 검증

### 새로운 3가지 지표 확인

Mock 데이터로 다음 지표들이 제대로 계산되는지 확인:

#### 1. 기술투자 리스크
```
R&D 비용 비중 = rnd_expense / revenue
무형자산 비중 = intangible_assets / total_assets
```

#### 2. 운전자본 리스크
```
운전자본/매출 = (current_assets - current_liabilities) / revenue
CCC = 재고회전일수 + 매출채권회전일수 - 매입채무회전일수
```

#### 3. 성장단계 리스크
```
CapEx/매출 = capex / revenue
감가상각 증가율 = (current_depreciation - previous_depreciation) / previous_depreciation
```

### 확인 방법

1. JSON 파일에서 각 기업의 `risk_analysis` 섹션 확인
2. 계산된 리스크 점수가 0.0~1.0 범위 내인지 확인
3. 로그 출력에서 각 지표별 계산 과정 확인

---

## 문제 해결

### 문제 1: ImportError 발생

**증상:**
```
ImportError: No module named 'workflow'
```

**해결:**
```bash
# 올바른 디렉토리에서 실행했는지 확인
cd /Users/jangsomin/workspace/EVI-AgentSystem
python test_report_generation.py
```

### 문제 2: 파일이 생성되지 않음

**원인:** 워크플로우 실행 중 오류 발생

**해결:**
1. 콘솔 출력에서 오류 메시지 확인
2. `final_state['errors']` 확인
3. 각 에이전트별 로그 확인

### 문제 3: 인코딩 오류 (Windows)

**증상:**
```
UnicodeEncodeError: 'cp949' codec can't encode character
```

**해결:**
- 이미 `test_report_generation.py`에 UTF-8 인코딩 설정 포함됨
- 그래도 문제 시:
```bash
set PYTHONIOENCODING=utf-8
python test_report_generation.py
```

---

## 실제 API로 전환하기

Mock 테스트가 성공하면 실제 API로 전환:

### 1. API 키 설정

`.env` 파일 생성:
```bash
OPENAI_API_KEY=sk-proj-your-actual-key
DART_API_KEY=your-dart-key
TAVILY_API_KEY=your-tavily-key
```

### 2. 실제 실행

```bash
python main.py
```

### 3. 결과 비교

Mock 테스트 결과와 실제 API 결과를 비교하여 검증

---

## 추가 정보

### Mock 데이터 커스터마이징

`mock_tools.py`를 수정하여 원하는 데이터 생성:

```python
# 특정 기업에 대한 커스텀 데이터
def get_financial_statements(self, company_name: str, year: int = 2024):
    if company_name == "LG에너지솔루션":
        # 커스텀 데이터
        return {
            'income_statement': {
                'revenue': 25000000000000,  # 25조원
                'rnd_expense': 3000000000000,  # R&D 12%
                ...
            }
        }
    # 기본 랜덤 데이터
    return self._generate_default_financials()
```

### 로깅 레벨 조정

더 자세한 로그를 보려면:

```python
# test_report_generation.py 상단에 추가
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📞 도움이 필요하신가요?

- 이슈 발생 시: 콘솔 출력 전체를 공유해주세요
- 기능 개선 제안: `mock_tools.py`에 주석으로 남겨주세요

---

**Last Updated**: 2025-10-23
**Version**: 1.0

