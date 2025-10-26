# Final Release - 파일 목록

**릴리스 날짜:** 2025년 10월 26일  
**버전:** 1.0 Final

---

## 디렉토리 구조

```
final/
├── README.md                          # 프로젝트 설명서
├── FILE_LIST.md                       # 이 파일
├── .env.example                       # 환경 변수 템플릿
├── .gitignore                         # Git 제외 파일
├── requirements.txt                   # Python 패키지 의존성
├── main.py                            # 메인 실행 파일
│
├── agents/                            # 6개 분석 에이전트
│   ├── __init__.py
│   ├── market_trend_agent.py          # 시장 트렌드 분석
│   ├── supplier_matching_agent.py     # 공급업체 매칭 (상장사 필터링)
│   ├── financial_analyzer_agent.py    # 재무 분석
│   ├── risk_assessment_agent_improved.py  # 리스크 평가
│   ├── investment_strategy_agent.py   # 투자 전략 (Dynamic Fallback)
│   └── report_generator_agent.py      # 보고서 생성
│
├── tools/                             # 분석 도구 (20개)
│   ├── __init__.py
│   ├── cache_manager.py               # 24시간 캐시 시스템
│   ├── llm_tools.py                   # OpenAI LLM
│   ├── dart_tools.py                  # DART API
│   ├── sec_edgar_tools.py             # SEC EDGAR API
│   ├── yahoo_finance_tools.py         # Yahoo Finance
│   ├── tavily_search_tools.py         # Tavily 웹 검색
│   ├── gnews_tool.py                  # GNews API
│   ├── web_tools.py                   # 웹 도구
│   ├── trend_analysis_tools.py        # 트렌드 분석
│   ├── supplier_scoring_tools.py      # 공급업체 점수화
│   ├── disclosure_routing_tools.py    # 공시 라우팅
│   ├── llm_qualitative_analysis_tools.py  # 정성 분석
│   ├── real_expert_analysis_tools.py  # 전문가 분석
│   ├── scoring_missing_data_tools.py  # 결측 데이터 처리
│   ├── json_parser.py                 # JSON 파서
│   ├── report_converter.py            # 보고서 변환 (HTML)
│   ├── dart_tagger.py                 # DART 태거
│   ├── sec_tagger.py                  # SEC 태거
│   ├── alpha_vantage_tools.py         # Alpha Vantage
│   └── duckduckgo_tools.py            # DuckDuckGo 검색
│
├── config/                            # 설정
│   └── settings.py                    # 시스템 설정
│
├── workflow/                          # 워크플로우
│   ├── __init__.py
│   ├── state.py                       # 상태 관리
│   └── graph.py                       # 그래프 (사용 안 함)
│
├── models/                            # 데이터 모델
│   ├── __init__.py
│   └── citation.py                    # 출처 관리
│
├── prompts/                           # 프롬프트 템플릿
│   ├── __init__.py
│   ├── cot_templates.py               # Chain-of-Thought
│   └── json_output_templates.py       # JSON 출력
│
└── reports/                           # 보고서 및 문서
    ├── report_20251026_171840.html   # 최신 투자 보고서
    ├── report_20251026_171840_limitations.md  # 보고서 한계사항
    ├── REPORT_LIMITATIONS.html        # 시스템 한계사항 (HTML)
    ├── REPORT_LIMITATIONS.md          # 시스템 한계사항 (MD)
    ├── ARCHITECTURE_FINAL.md          # 최종 아키텍처
    ├── LISTED_COMPANY_FILTER.md       # 상장사 필터링 가이드
    ├── LLM_FALLBACK_GUIDE.md          # Fallback 가이드
    └── DYNAMIC_FALLBACK_COMPARISON.md # Fallback 비교
```

---

## 핵심 파일

### 실행 파일
- **`main.py`** - 메인 실행 파일 (에이전트 순차 실행)

### 필수 설정
- **`requirements.txt`** - Python 패키지
- **`.env.example`** - API 키 템플릿

### 보고서
- **`reports/report_20251026_171840.html`** - 최신 투자 보고서
- **`reports/REPORT_LIMITATIONS.html`** - 시스템 한계사항

### 문서
- **`README.md`** - 프로젝트 설명
- **`ARCHITECTURE_FINAL.md`** - 시스템 아키텍처
- **`LISTED_COMPANY_FILTER.md`** - 상장사 필터링
- **`LLM_FALLBACK_GUIDE.md`** - Fallback 전략
- **`DYNAMIC_FALLBACK_COMPARISON.md`** - 품질 비교

---

## 에이전트 설명

| 에이전트 | 파일명 | 기능 |
|---------|-------|------|
| **Market Trend** | `market_trend_agent.py` | 뉴스/공시 수집, 트렌드 분석 |
| **Supplier Matching** | `supplier_matching_agent.py` | 공급업체 매칭, 상장사 필터링 ✨ |
| **Financial Analyzer** | `financial_analyzer_agent.py` | 재무 분석 (3-tier fallback) |
| **Risk Assessment** | `risk_assessment_agent_improved.py` | 리스크 평가 (정량+정성) |
| **Investment Strategy** | `investment_strategy_agent.py` | 투자 전략, Dynamic Fallback ✨ |
| **Report Generator** | `report_generator_agent.py` | 보고서 생성 (HTML) |

---

## 주요 도구 설명

| 도구 | 파일명 | 기능 |
|-----|-------|------|
| **Cache Manager** | `cache_manager.py` | 24시간 캐시 (414+ files) ✨ |
| **LLM Tools** | `llm_tools.py` | OpenAI GPT-4o-mini |
| **DART Tools** | `dart_tools.py` | 한국 기업 공시 |
| **SEC Tools** | `sec_edgar_tools.py` | 미국 기업 공시 |
| **Yahoo Finance** | `yahoo_finance_tools.py` | 글로벌 재무 데이터 |
| **Tavily Search** | `tavily_search_tools.py` | 웹 검색 (캐시됨) |
| **Supplier Scorer** | `supplier_scoring_tools.py` | 공급업체 점수화 |
| **JSON Parser** | `json_parser.py` | LLM 출력 안정화 |
| **Report Converter** | `report_converter.py` | MD → HTML 변환 |

---

## 파일 통계

| 카테고리 | 파일 수 |
|---------|--------|
| **에이전트** | 6개 |
| **도구** | 20개 |
| **설정** | 1개 |
| **워크플로우** | 2개 |
| **모델** | 1개 |
| **프롬프트** | 2개 |
| **보고서** | 4개 (HTML 2개, MD 2개) |
| **문서** | 4개 |
| **총계** | 40개 파일 |

---

## 크기 정보

- **총 코드 라인**: 약 15,000 라인
- **Python 파일**: 36개
- **문서**: 8개 (MD 6개, HTML 2개)
- **압축 크기**: 약 500KB

---

## 버전 정보

| 항목 | 값 |
|-----|---|
| **버전** | 1.0 Final |
| **릴리스 날짜** | 2025-10-26 |
| **Python 버전** | 3.8+ |
| **주요 개선** | 상장사 필터링, Dynamic Fallback, 24h 캐시 |
| **상태** | Production Ready ✅ |

---

**문서 끝**

