# EV 투자 분석 시스템 (Final Release)

**버전:** 1.0 Final  
**릴리스 날짜:** 2025년 10월 26일

---

## 개요

EV(전기차) 산업 공급망을 분석하여 투자 인사이트를 제공하는 AI 기반 분석 시스템입니다.

### 주요 기능
- 시장 트렌드 분석 (뉴스, 공시 데이터)
- 공급망 관계 분석 (OEM-공급업체)
- 재무 분석 (DART, SEC, Yahoo Finance)
- 리스크 평가 (정량적 + 정성적)
- 투자 전략 생성 (Dynamic Fallback)
- 전문 투자 보고서 생성 (HTML)

---

## 주요 개선사항

### 1. 상장사 우선순위 필터링
- 상장 기업 우선 분석
- 비상장 기업 최대 5개로 제한
- API 비용 최적화

### 2. 3-Tier Dynamic Fallback
- Plan A: LLM API (고품질)
- Plan B: 재무 데이터 기반 동적 생성 (중간 품질)
- Plan C: 차별화된 템플릿 (기본 품질)

### 3. 24시간 캐시 시스템
- Tavily 웹 검색 결과 캐싱
- API 비용 30-70% 절감
- 부분 오프라인 작업 가능

### 4. 수동 에이전트 오케스트레이션
- LangGraph 버그 우회
- 안정적인 순차 실행
- 상태 관리 최적화

---

## 설치 방법

### 요구사항
- Python 3.8+
- API Keys (OpenAI, Tavily, DART)

### 설치
```bash
pip install -r requirements.txt
```

### 환경 변수 설정
```bash
# .env 파일 생성
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
DART_API_KEY=your_dart_api_key
```

---

## 사용 방법

### 보고서 생성
```bash
python main.py
```

### 출력 파일
- `outputs/report_YYYYMMDD_HHMMSS.html` - 투자 보고서
- `outputs/report_YYYYMMDD_HHMMSS.json` - JSON 데이터
- `outputs/report_YYYYMMDD_HHMMSS.md` - 마크다운

---

## 시스템 구조

```
EVI-AgentSystem/
├── main.py                  # 메인 실행 파일
├── agents/                  # 6개 분석 에이전트
│   ├── market_trend_agent.py
│   ├── supplier_matching_agent.py
│   ├── financial_analyzer_agent.py
│   ├── risk_assessment_agent_improved.py
│   ├── investment_strategy_agent.py
│   └── report_generator_agent.py
├── tools/                   # 분석 도구
│   ├── cache_manager.py
│   ├── llm_tools.py
│   ├── dart_tools.py
│   ├── sec_edgar_tools.py
│   └── ... (기타 도구)
├── config/                  # 설정
│   └── settings.py
└── reports/                 # 생성된 보고서
    ├── report_20251026_171840.html
    └── report_limitations.html
```

---

## 한계사항

**본 시스템은 금융투자업 인가를 보유하지 않으며, 투자 자문을 제공할 수 없습니다.**

자세한 한계사항은 `reports/report_limitations.html`을 참조하십시오.

### 주요 한계
1. 데이터 지연 (1-90일)
2. 소형주 커버리지 부족
3. 밸류에이션 분석 미흡
4. 실시간 데이터 부재
5. AI 환각(Hallucination) 위험

---

## 라이선스

본 프로젝트는 교육 및 연구 목적으로 제공됩니다.

**면책사항:** 본 시스템의 사용으로 인한 투자 손실에 대해 개발자는 책임을 지지 않습니다.

---

## 문의

GitHub: https://github.com/sommmmmmmmm/EVI-AgentSystem

---

**Last Updated:** 2025-10-26
