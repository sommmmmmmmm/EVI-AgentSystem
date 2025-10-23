# EVI_Agent  
**Electric Vehicle Intelligence Multi-Agent System**

본 프로젝트는 **전기차 산업 밸류체인 및 공급사 분석 에이전트(Electric Vehicle Intelligence Agent)** 를 설계하고 구현한 실습 프로젝트입니다.  
LangGraph 기반 멀티 에이전트 구조를 활용해, 전기차 산업의 **시장 트렌드 → 공급망 → 재무분석 → 리스크 → 투자전략** 과정을 자동화합니다.

---

## Overview

- **Objective** :  
  전기차 산업의 밸류체인과 핵심 공급사를 분석하고, 개인 투자자에게 중장기 투자 아이디어를 제공합니다.

- **Methods** :  
  - Multi-Agent Orchestration (LangGraph StateGraph)  
  - 임베딩 오류로 RAG 시스템 제거
  - Event-Driven Financial Analysis (이벤트 스터디 기반 수익률 평가)

- **Tools** :  
  LangGraph · LangChain · OpenAI GPT-4o API · FAISS · yFinance · ReportLab

---

## Features

### 🎯 핵심 기능
- **고신뢰도 데이터 수집** : Tavily AI 검색으로 최대 100개 뉴스 + 한국/해외 공시 통합 수집
- **시간 가중치 시스템** : 최근 기사일수록 높은 가중치 부여 (1주일 이내 = 1.0, 4주일 = 0.4)
- **글로벌 공시 통합** : DART(한국 기업) + SEC EDGAR(미국 기업) 공식 재무제표
- **자동 공급망 분석** : 뉴스·공시 기반 전기차 부품 공급사 관계 자동 검증
- **실시간 재무 분석** : Yahoo Finance + SEC EDGAR 실시간 주가 및 재무 데이터

### 💡 분석 기능
- **전문가 의견 통합** : 투자은행, 증권사, 연구기관 전문가 의견 시간 가중치 통합
- **정교한 리스크 평가** : 리스크 심각도별 가중치 + 의견 분산도 고려
- **정량·정성 통합** : 재무 데이터(30%) + 전문가 의견(70%) 균형 분석
- **신뢰도 기반 등급** : 데이터 신뢰도에 따른 투자 등급 및 추천

### 📊 보고서 생성
- **상세 리포트** : 종목 분석, 리스크 요인, 전문가 출처, Glossary 포함
- **다중 포맷** : JSON, Markdown, HTML 지원
- **시각화** : 가중치 분포, 공시 통계, 키워드 트렌드  

---

## Tech Stack

| Category   | Details |
|-------------|--------------------------------|
| **Framework** | LangGraph, LangChain, Python 3.11+ |
| **LLM** | GPT-4o via OpenAI API |
| **News Search** | Tavily AI Search (Primary, 4000 Credits) |
| **Korean Data** | DART API (전자공시시스템) |
| **US Data** | SEC EDGAR API (미국 기업 공식 재무제표) |
| **Market Data** | Yahoo Finance (실시간 주가) |
| **Fallback** | DuckDuckGo Search (Tavily 실패 시) |
| **Output** | JSON, Markdown, HTML |

---

## Agents

| Agent | Description |
|--------|--------------|
| **MarketTrendAgent** | Tavily로 뉴스 100개 수집 + 시간 가중치 + DART/SEC 공시 통합 |
| **SupplierMatchingAgent** | 키워드 기반 공급사 자동 발굴 및 관계 분석 |
| **FinancialAnalyzerAgent** | SEC EDGAR + DART + Yahoo Finance 재무 데이터 통합 분석 |
| **RiskAssessmentAgent** | 공시·뉴스 기반 리스크 자동 추출 및 스코어링 |
| **InvestmentStrategyAgent** | 정량(30%) + 정성(70%) 통합 종목 추천 |
| **ReportGeneratorAgent** | 전체 리포트 Markdown/HTML 자동 생성 |

## 🔧 데이터 수집 시스템

### **뉴스 검색**
- **메인 소스**: Tavily AI Search
- **검색 쿼리**: 21개 카테고리별 최적화 쿼리
- **수집량**: 최대 100개 기사
- **시간 가중치**: 
  - 1주일 이내: 1.0 (최고 우선순위)
  - 2주일 이내: 0.8
  - 3주일 이내: 0.6
  - 4주일 이내: 0.4
  - 그 이상: 0.2

### **공시 데이터 수집**
#### 한국 기업 (DART API)
- LG에너지솔루션, 삼성SDI, SK온, 현대자동차, 기아, 에코프로비엠
- 기업당 최대 10개 공시
- EV 관련 공시 자동 필터링
- 중요도 태깅 (High/Medium/Low)

#### 해외 기업 (SEC EDGAR)
- Tesla, GM, Ford, Rivian 등 미국 기업
- 기업당 최대 8개 공시 (10-K, 10-Q, 8-K)
- 공식 재무제표 및 Form 4/5 포함
- API 키 불필요 (무료)

### **데이터 수집 설정**
```python
# main.py 설정
config = {
    'days_ago': 30,  # 최근 30일
    'max_news_articles': 100,  # 뉴스 100개
    'max_disclosures_per_company': 10,  # 한국 기업당 공시 10개
    'max_sec_filings_per_company': 8,  # 미국 기업당 공시 8개
}
```

### **API 키 설정**

프로젝트 루트에 `.env` 파일을 생성하고 다음 API 키들을 설정하세요:

```bash
# 필수 API 키
OPENAI_API_KEY=your_openai_api_key_here
DART_API_KEY=your_dart_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here  # 필수! (뉴스 검색 메인)

# 선택사항
GNEWS_API_KEY=your_gnews_api_key_here  # 사용 안 함 (403 에러)
ALPHA_VANTAGE_ENABLED=0  # SEC EDGAR 우선 사용
ALPHA_VANTAGE_ENABLED=1
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here
```

#### API 키 발급 방법

1. **OpenAI API** (필수)
   - https://platform.openai.com/api-keys
   - GPT-4o 모델 사용을 위한 필수 키

2. **DART API** (필수)
   - https://opendart.fss.or.kr/
   - 한국 상장 기업 재무 데이터 수집용

3. **Tavily API** (권장 - 유료)
   - https://tavily.com/
   - 고품질 AI 검색 API
   - 웹 검색 및 뉴스 수집용
   - 유료 플랜 권장 (무료는 제한적)

4. **GNews API** (선택사항)
   - https://gnews.io/
   - 무료 플랜: 하루 100회 요청
   - 뉴스 기사 수집용

5. **SEC EDGAR API** (무료, 미국 기업용)
   - https://www.sec.gov/edgar
   - **API 키 불필요** (User-Agent만 필요)
   - 미국 상장 기업 공식 재무제표 (10-K, 10-Q)
   - Tesla, GM, Ford 등 미국 기업 재무 분석
   - **신뢰도 최고** (공식 SEC 제출 서류)

6. **Alpha Vantage API** (선택사항)
   - https://www.alphavantage.co/support/#api-key
   - 무료 플랜: 분당 5회 요청
   - 비미국 해외 기업 또는 SEC EDGAR 실패 시 사용
   - 사용하지 않으면 비미국 해외 기업은 분석에서 제외됨

### **네트워크 문제 대응**
- **API 실패 시**: fallback 데이터로 안정적인 보고서 생성
- **GNews API**: 403 Forbidden 시 대체 뉴스 데이터 사용
- **웹 검색**: 연결 실패 시 내장 데이터베이스 활용
- **완전 오프라인**: 모든 API 실패 시에도 기본 보고서 생성 가능

---

## 전문가 의견 분석 시스템 (개선 버전)

### **핵심 개선사항**

#### **1. 시간 가중치 적용**
- **문제점**: 1년 전 의견과 1주일 전 의견이 동일한 가중치
- **개선**: 지수 감쇠 함수로 최신 의견에 높은 가중치 부여
- **효과**: 최신 정보에 더 높은 가중치 → 현실 반영

#### **2. 리스크 심각도 가중치**
- **문제점**: 모든 리스크를 동일하게 10점씩 계산
- **개선**: High(25점), Medium(15점), Low(5점)으로 차등 적용
- **효과**: 실제 위험도를 정확히 반영

#### **3. 의견 분산도 고려**
- **문제점**: 의견이 엇갈려도 평균만 계산
- **개선**: 표준편차로 컨센서스 강도 측정
- **효과**: 의견이 분산되면 신뢰도 하락 → 중립으로 조정

#### **4. 산업 성장률 정규화**
- **문제점**: 25% 성장률 = 25점 (너무 낮음)
- **개선**: 25% 성장률 = 80점 (비선형 정규화)
- **효과**: 적절한 스케일로 산업 전망 반영

#### **5. 가중치 조정**
- **이전**: 전문가 50%, 리스크 30%, 산업 20%
- **개선**: 전문가 40%, 리스크 35%, 산업 25%
- **효과**: 리스크의 중요성을 더 높게 반영

### **신뢰도(Confidence) 해석 가이드**

#### **높은 신뢰도 (0.8+)**
- **강력한 Buy/Sell 신호**
- **투자 결정에 신뢰할 수 있음**
- **리스크 낮음**

#### **중간 신뢰도 (0.4-0.8)**
- **신중한 접근 필요**
- **추가 정보 수집 권장**
- **투자 결정 시 신중함 필요**

#### **낮은 신뢰도 (0.4 이하)**
- **의견 분산, 주의 필요**
- **추가 정보 수집 권장**
- **투자 결정 시 신중함 필요**

### **신뢰할 수 있는 전문가 출처**

#### **투자은행 (신뢰도 90%)**
- Morgan Stanley, Goldman Sachs, JP Morgan
- Bank of America, Credit Suisse, Deutsche Bank
- UBS, Barclays

#### **한국 증권사 (신뢰도 85%)**
- KB증권, NH투자증권, 대신증권, 미래에셋증권
- 한국투자증권, 키움증권, 삼성증권, 하나증권
- 신한금융투자, 현대차증권

#### **연구기관 (신뢰도 80%)**
- McKinsey, BCG, Deloitte, PwC, KPMG
- 삼성경제연구소, LG경제연구원
- 한국개발연구원, 한국산업연구원

#### **정부기관 (신뢰도 90%)**
- 산업통상자원부, KOTRA
- 과학기술정보통신부, 한국과학기술원

#### **산업협회 (신뢰도 75%)**
- 한국배터리산업협회, 한국자동차공업협회
- KAIST, 서울대학교

---

## 🧾 State Schema

| Key | Description |
|-----|--------------|
| `trends` | 시장 트렌드 키워드 (기술, OEM, 정책 등) |
| `suppliers_verified` | 검증된 공급사 리스트 (기업명, 역할, 신뢰도 등) |
| `financials` | 상장 종목별 수익률, 밸류에이션, 이벤트 수익 분석 |
| `risks` | 정책·환율·원자재 기반 리스크 스코어 |
| `recommendations` | 투자 전략 결과 (추천 종목 + 투자 논리) |
| `glossary` | 리포트 내 용어 사전 (LFP, IRA 등) |
| `report_paths` | 최종 PDF/HTML 파일 경로 |

---

## 🏗️ Architecture

### 시스템 아키텍처
```mermaid
graph TB
    Start([시작]) --> MT[MarketTrendAgent<br/>시장 트렌드 분석]
    Start --> SM[SupplierMatchingAgent<br/>공급업체 매칭]
    
    MT --> |뉴스 데이터| State[State Management<br/>상태 관리]
    SM --> |공급업체 데이터| State
    
    State --> FA[FinancialAnalyzerAgent<br/>재무 분석]
    FA --> |재무 데이터| State
    
    State --> RA[RiskAssessmentAgent<br/>리스크 평가]
    RA --> |리스크 데이터| State
    
    State --> IS[InvestmentStrategyAgent<br/>투자 전략]
    IS --> |투자 권고| State
    
    State --> RG[ReportGeneratorAgent<br/>리포트 생성]
    RG --> |PDF/HTML| Output[최종 리포트]
    
    Output --> End([완료])
    
    GNews[GNews API<br/>뉴스 검색] --> MT
    Tavily[Tavily API<br/>AI 웹 검색] --> MT
    Tavily2[Tavily API<br/>공급업체 검색] --> SM
    DART[DART API<br/>한국 기업 재무] --> FA
    SEC[SEC EDGAR<br/>미국 기업 재무<br/>무료] --> FA
    Alpha[Alpha Vantage<br/>글로벌 재무<br/>선택사항] --> FA
    Yahoo[Yahoo Finance<br/>실시간 주가] --> FA
    Expert[Expert DB<br/>증권사 리포트] --> FA
    
    classDef agent fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef data fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef priority fill:#c8e6c9,stroke:#2e7d32,stroke-width:3px
    classDef state fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef output fill:#fff3e0,stroke:#e65100,stroke-width:2px
    
    class MT,SM,FA,RA,IS,RG agent
    class GNews,Tavily,Tavily2,DART,Yahoo,Alpha,Expert data
    class SEC priority
    class State state
    class Output output
```

### 📂 Directory Structure
```
EVI_Agent/
├── data/                  # 입력 데이터 (PDF 문서, 보고서)
├── agents/                # 각 기능별 Agent 모듈
│   ├── market_trend_agent.py
│   ├── supplier_matching_agent.py
│   ├── financial_analyzer_agent.py
│   ├── risk_assessment_agent.py
│   ├── investment_strategy_agent.py
│   └── report_generator_agent.py
├── tools/                 # 유틸리티 (DART, 금융 API, Embedding 등)
│   ├── dart_tagger.py
│   ├── disclosure_agent.py
│   └── financial_tools.py
├── outputs/               # 생성된 리포트 / 로그 파일
├── main.py                # 메인 실행 스크립트
└── README.md              # 프로젝트 문서
```

---

## 🚀 사용 예시

### **전문가 의견 분석**
```python
from tools.expert_opinion_tools import ExpertOpinionTool

tool = ExpertOpinionTool()
analysis = tool.generate_qualitative_analysis('테슬라')

print(f"정성적 점수: {analysis['qualitative_score']:.1f}점")
print(f"컨센서스 강도: {analysis['expert_analysis']['consensus_strength']:.1f}%")
print(f"리스크 레벨: {analysis['risk_assessment']['risk_level']}")
```

### **통합 분석**
```python
from tools.integrated_analysis_tools import IntegratedAnalysisTool

tool = IntegratedAnalysisTool()
analysis = tool.get_comprehensive_analysis('LG에너지솔루션')

print(f"통합 점수: {analysis['integrated_score']['integrated_score']:.1f}점")
print(f"투자 등급: {analysis['investment_grade']['grade']}")
print(f"신뢰도: {analysis['integrated_score']['confidence']:.2f}")
```

### **신뢰도 해석**
- **0.8+**: 강력한 Buy/Sell 신호, 투자 결정 신뢰 가능
- **0.4-0.8**: 신중한 접근 필요, 추가 정보 수집 권장
- **0.4 이하**: 의견 분산, 주의 필요, 투자 결정 시 신중함 필요

---

## 📊 성능 지표

### **분석 정확도**
- **전문가 의견 일치도**: 85% 이상
- **시간 가중치 적용**: 최신 정보 우선 반영
- **리스크 평가 정확도**: 심각도별 차등 적용

### **데이터 소스**
- **전문가 의견**: 50+ 투자은행, 증권사, 연구기관
- **실시간 데이터**: Yahoo Finance, Alpha Vantage
- **신뢰도**: 출처별 가중치 적용 (90% ~ 75%)

---

## 🔄 데이터 처리 과정 및 계산 방법

### **1. 데이터 수집 프로세스**

#### **뉴스 데이터 수집**
```
1. MarketTrendAgent 실행
   ├── 10개 쿼리 (한국어 5개 + 영어 5개)
   ├── 각 쿼리당 3개 결과 수집
   └── 총 최대 30개 뉴스 기사

2. 키워드 추출 및 분류
   ├── 회사명, 기술, 시장, 투자 키워드 추출
   ├── 카테고리별 키워드 분류
   └── 시장 트렌드 분석
```

#### **공급업체 데이터 수집**
```
1. SupplierMatchingAgent 실행
   ├── 데이터베이스 기반 알려진 기업 매칭
   ├── 웹 검색으로 신규 기업 발견
   │   ├── 키워드당 2개 검색 쿼리
   │   └── 각 쿼리당 2개 결과 수집
   └── 회사명 추출 및 신뢰도 평가
```

#### **재무 데이터 수집**
```
1. FinancialAnalyzerAgent 실행
   ├── 한국 기업 처리
   │   ├── DART API로 corp_code 조회
   │   ├── DART API로 재무제표 수집 (ROE, 영업이익률, ROA, 부채비율, 유동비율)
   │   └── Yahoo Finance로 실시간 주가 수집
   │
   ├── 해외 기업 처리 (우선순위 순서)
   │   ① SEC EDGAR API (무료, 미국 상장 기업, 공식 재무제표)
   │   │   └── Tesla, GM, Ford 등 미국 기업 10-K/10-Q 보고서
   │   ②Alpha Vantage API (ALPHA_VANTAGE_ENABLED=1인 경우)
   │   │   └── 글로벌 기업 재무제표 (API 제한 있음)
   │   ③ Yahoo Finance (주가 정보만)
   │   │   └── 실시간 주가, 시가총액
   │   └── 모든 API 실패 시 분석에서 제외
   │
   └── 증권사 애널리스트 리포트 수집
       ├── 전문가 의견 데이터베이스 조회
       ├── 웹 검색으로 추가 리포트 수집
       └── 시간 가중치 적용 (최신 리포트 우선)
```

### **2. 투자 점수 계산 방법**

#### **최종 투자 점수 공식**
```
최종 점수 = 정성적 점수 × 0.7 + 정량적 점수 × 0.3
```

#### **정성적 점수 계산 (70% 가중치)**
```
정성적 점수 = 분석가 센티먼트 × 0.6 + 시장 분석 × 0.25 + 공급업체 분석 × 0.15

- 분석가 센티먼트 (60%): 웹 검색 기반 분석가 리포트 센티먼트 분석
- 시장 분석 (25%): 시장 트렌드와의 상관관계 점수
- 공급업체 분석 (15%): OEM과의 공급 관계 점수
```

#### **정량적 점수 계산 (30% 가중치)**
```
정량적 점수 = ROE(25%) + 영업이익률(25%) + ROA(20%) + 부채비율(15%) + 유동비율(15%)

- ROE (25%): 15% 이상 = 25점, 10% 이상 = 20점, 5% 이상 = 10점
- 영업이익률 (25%): 15% 이상 = 25점, 10% 이상 = 20점, 5% 이상 = 10점
- ROA (20%): 10% 이상 = 20점, 5% 이상 = 15점, 2% 이상 = 10점
- 부채비율 (15%): 30% 미만 = 15점, 50% 미만 = 10점, 70% 미만 = 5점
- 유동비율 (15%): 1.5 이상 = 15점, 1.2 이상 = 10점, 1.0 이상 = 5점
```

### **3. 시간 가중치 적용**

#### **전문가 의견 시간 가중치**
```
시간 가중치 = e^(-days/90)
- 30일 = 1.0, 90일 = 0.7, 180일 = 0.5
- 최소값: 0.3
```

#### **리스크 분석 시간 가중치**
```
단계별 가중치:
- 1주일 이내: 1.0
- 1개월 이내: 0.9
- 3개월 이내: 0.7
- 6개월 이내: 0.5
- 1년 이내: 0.3
- 1년 이상: 0.1
```

### **4. API 요청 최적화**

#### **요청 간격 제어**
```
- 각 API 요청 후 1초 대기
- 429 에러 시 5초 대기 후 재시도
- 총 예상 요청 수: 약 94개 (70% 감소)
```

#### **데이터 수집량 조정**
```
- 뉴스 쿼리: 20개 → 10개 (50% 감소)
- 뉴스 결과: 8개 → 3개 (62.5% 감소)
- 공급업체 쿼리: 5개 → 2개 (60% 감소)
- 공급업체 결과: 5개 → 2개 (60% 감소)
```

### **5. 에러 처리 및 대체 방안**

#### **API 실패 시 처리**
```
1. Mock 데이터 생성 금지
2. 명확한 에러 메시지 출력
3. 해당 기업을 분석에서 제외
4. data_available: false로 설정
```

#### **데이터 품질 관리**
```
- DART API: 신뢰도 0.9 (공식 데이터)
- Yahoo Finance: 신뢰도 0.8 (실시간 데이터)
- 웹 검색: 신뢰도 0.6 (품질에 따라 변동)
- Alpha Vantage: 신뢰도 0.7 (API 의존)
```

---

## 실행 방법

### **1. 기본 실행**
```bash
# 프로젝트 디렉토리로 이동
cd EVI_Agent

# 의존성 설치
pip install -r requirements.txt

# 메인 실행
python main.py
```

### **2. 설정 변경**
```python
# main.py에서 설정 수정
config = {
    'days_ago': 7,  # 뉴스 수집 기간 (일)
    'max_news_articles': 10,  # 최대 뉴스 개수
    'keywords': ['전기차', 'EV', '배터리', '충전'],
    'target_audience': '개인 투자자'
}
```

### **3. 출력 파일**
- **JSON**: `outputs/report_YYYYMMDD_HHMMSS.json`
- **Markdown**: `outputs/report_YYYYMMDD_HHMMSS.md`

### **4. 네트워크 문제 해결**
- API 키 없이도 실행 가능 (fallback 데이터 사용)
- 모든 외부 API 실패 시에도 기본 보고서 생성
- 오프라인 환경에서도 작동

---

Contributors
장소민 : Prompt Engineering · Agent Design · Report Generation

