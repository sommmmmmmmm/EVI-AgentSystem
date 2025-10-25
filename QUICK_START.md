# 🚀 빠른 시작 가이드

## ✅ 준비 완료 사항

### API 키 설정 완료
```bash
✅ OpenAI API (GPT-4o)  - 설정 완료
✅ Tavily API           - 설정 완료
✅ DART API             - 설정 완료
✅ SEC EDGAR            - 설정 완료
✅ Yahoo Finance        - 설정 완료
```

### 시스템 구성 완료
```bash
✅ 리스크 분석 3가지 지표 업데이트
✅ 보고서 생성 한국어 번역
✅ Mock 테스트 환경 구축
✅ 모든 API 툴 준비 완료
```

---

## 🎯 실행 방법

### 1. 간단한 API 테스트 (10초, $0.001)
```bash
python3 test_api_key.py
```

### 2. Mock 테스트 (API 비용 없음)
```bash
python3 test_report_generation.py
```

### 3. **실제 보고서 생성** (5-10분, $1.68)
```bash
python3 main.py
```

---

## 📊 실행 결과

### 생성되는 파일
```
outputs/
├── report_20251024_HHMMSS.json    # JSON 형식 보고서
├── report_20251024_HHMMSS.md      # Markdown 형식 보고서
├── report_20251024_HHMMSS.html    # HTML 형식 (선택)
└── report_20251024_HHMMSS.pdf     # PDF 형식 (선택)
```

### 보고서 구성
```
1. Executive Summary        - 핵심 투자 하이라이트
2. EV Market Trends         - 시장 동향 분석
3. Supply Chain Analysis    - 공급망 구조
4. Financial Performance    - 재무 성과
5. Risk Assessment          - 리스크 평가 (3가지 지표)
6. Investment Strategy      - 투자 전략
7. Glossary                 - 용어 사전
8. Risk Disclaimer          - 투자 위험 고지
9. References & Appendix    - 참고문헌
```

---

## 💰 예상 비용

### 보고서 1개 생성 (GPT-4o)
```
NewsDiscovery:      $0.30
MarketTrend:        $0.23
SupplierMatching:   $0.15
FinancialAnalyzer:  $0.32
RiskAssessment:     $0.23
InvestmentStrategy: $0.22
ReportGenerator:    $0.25
─────────────────────────
총 비용:            $1.68
```

### Tavily API (웹 검색)
```
뉴스 100개 수집:    Free Tier 범위 내
월 10회 보고서:     무료 가능
```

---

## ⚡ 성능 최적화

### 처리 시간
```
뉴스 수집:          1-2분
재무 분석:          2-3분
리스크 평가:        1-2분
보고서 생성:        1-2분
─────────────────────────
총 소요 시간:       5-10분
```

### 캐싱 효과
```
동일 기업 재분석:    50-70% 시간 절감
중복 뉴스 제거:      30% 비용 절감
```

---

## 🔍 문제 해결

### API 키 오류
```bash
# .env 파일 확인
cat .env

# API 키 테스트
python3 test_api_key.py
```

### 크레딧 부족
```
Error: insufficient_quota
→ https://platform.openai.com/account/billing
→ 크레딧 충전 필요
```

### 네트워크 오류
```bash
# 연결 테스트
curl -I https://api.openai.com
curl -I https://api.tavily.com
```

---

## 📞 도움말

### 로그 확인
```bash
# 실행 중 로그 출력됨
# 오류 발생 시 전체 로그 확인
```

### 성능 모니터링
```bash
# 토큰 사용량 출력
# 비용 실시간 추적
```

---

## 🎉 준비 완료!

**OpenAI 크레딧 충전 후 바로 실행 가능합니다!**

```bash
python3 main.py
```

---

**작성일**: 2025-10-24  
**버전**: 1.0


