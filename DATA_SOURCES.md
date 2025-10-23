# 데이터 출처 상세 문서

## 📊 기업별 데이터 출처 매핑

### 🇰🇷 한국 기업

| 기업명 | 티커 | 재무제표 | 공시 | 주가 |
|--------|------|----------|------|------|
| LG에너지솔루션 | 373220.KS | DART | DART | Yahoo Finance |
| 삼성SDI | 006400.KS | DART | DART | Yahoo Finance |
| SK온 | (비상장) | DART | DART | - |
| SK이노베이션 | 096770.KS | DART | DART | Yahoo Finance |
| 현대자동차 | 005380.KS | DART | DART | Yahoo Finance |
| 기아 | 000270.KS | DART | DART | Yahoo Finance |
| 에코프로비엠 | 247540.KS | DART | DART | Yahoo Finance |

### 🇺🇸 미국 기업 (SEC EDGAR 지원)

| 기업명 | 티커 | CIK | 재무제표 | 공시 | 주가 |
|--------|------|-----|----------|------|------|
| Tesla | TSLA | 1318605 | SEC EDGAR | SEC EDGAR | Yahoo Finance |
| General Motors | GM | 1467858 | SEC EDGAR | SEC EDGAR | Yahoo Finance |
| Ford | F | 37996 | SEC EDGAR | SEC EDGAR | Yahoo Finance |
| Rivian | RIVN | 1874178 | SEC EDGAR | SEC EDGAR | Yahoo Finance |
| Lucid | LCID | 1811210 | SEC EDGAR | SEC EDGAR | Yahoo Finance |
| Nio | NIO | 1736541 | SEC EDGAR | SEC EDGAR | Yahoo Finance |
| Xpeng | XPEV | 1806059 | SEC EDGAR | SEC EDGAR | Yahoo Finance |
| Li Auto | LI | 1799209 | SEC EDGAR | SEC EDGAR | Yahoo Finance |
| Albemarle | ALB | 915913 | SEC EDGAR | SEC EDGAR | Yahoo Finance |
| QuantumScape | QS | 1811414 | SEC EDGAR | SEC EDGAR | Yahoo Finance |

**공시 유형**:
- 10-K: 연간 보고서
- 10-Q: 분기 보고서
- 8-K: 주요 이벤트 보고서

### 🇩🇪 독일 기업

| 기업명 | 티커 | 거래소 | 재무 데이터 | 공시 | 주가 |
|--------|------|--------|-------------|------|------|
| BMW | BMW.DE | Xetra | Yahoo Finance | ❌ | Yahoo Finance |
| Mercedes-Benz | MBG.DE | Xetra | Yahoo Finance | ❌ | Yahoo Finance |
| Volkswagen | VOW3.DE | Xetra | Yahoo Finance | ❌ | Yahoo Finance |

**참고**: 유럽 공시 시스템 미연동

### 🇨🇳 중국 기업

| 기업명 | 티커 | 거래소 | 재무 데이터 | 공시 | 주가 |
|--------|------|--------|-------------|------|------|
| BYD | 1211.HK | 홍콩 | Yahoo Finance | ❌ | Yahoo Finance |

### 🇯🇵 일본 기업

| 기업명 | 티커 | 거래소 | 재무 데이터 | 공시 | 주가 |
|--------|------|--------|-------------|------|------|
| Panasonic | 6752.T | 도쿄 | Yahoo Finance | ❌ | Yahoo Finance |

---

## 🔍 데이터 신뢰도 분석

### 최상급 (Tier 1)
**SEC EDGAR + DART**
- 공식 규제 기관 공시
- 감사된 재무제표
- 법적 구속력
- 예시: Tesla, GM, LG에너지솔루션, 삼성SDI

### 상급 (Tier 2)
**Yahoo Finance (상장 기업)**
- 거래소 공식 데이터
- 실시간 주가
- 기본 재무 지표
- 예시: BMW, Mercedes, BYD, Panasonic

### 중급 (Tier 3)
**Yahoo Finance (비상장/OTC)**
- 제한된 공개 정보
- 주가 데이터 없음
- 예시: 비상장 기업

---

## 📈 수집 데이터 항목

### SEC EDGAR (미국)
**재무제표**:
- 손익계산서 (Income Statement)
- 재무상태표 (Balance Sheet)
- 현금흐름표 (Cash Flow Statement)
- 주주지분변동표 (Stockholders' Equity)

**공시**:
- 10-K: 연간 보고서 (감사 완료)
- 10-Q: 분기 보고서
- 8-K: 주요 이벤트 (M&A, CEO 변경, 계약 체결 등)
- Form 4: 내부자 거래

### DART (한국)
**재무제표**:
- 손익계산서
- 재무상태표
- 현금흐름표
- 자본변동표

**공시**:
- 사업보고서 (연간)
- 분기보고서
- 반기보고서
- 주요사항보고서 (유상증자, 투자 결정 등)
- 최대주주 변동 신고서

### Yahoo Finance (글로벌)
**주가 데이터**:
- 실시간 주가
- 거래량
- 시가총액
- 52주 고가/저가

**재무 지표**:
- P/E Ratio
- PEG Ratio
- Dividend Yield
- Beta

---

## ⚠️ 데이터 제한사항

### SEC EDGAR
- **대상**: 미국 상장 기업만
- **언어**: 영어
- **지연**: 실시간 아님 (제출 후 공개)
- **접근**: API 키 불필요 (무료)

### DART
- **대상**: 한국 상장 기업만
- **언어**: 한국어
- **지연**: 제출 후 즉시 공개
- **접근**: API 키 필요 (무료)

### Yahoo Finance
- **대상**: 전 세계 상장 기업
- **언어**: 영어
- **지연**: 15-20분 (거래소별 상이)
- **접근**: API 키 불필요 (무료)
- **제한**: 재무제표 상세도 낮음

---

## 🔄 데이터 업데이트 주기

| 출처 | 재무제표 | 공시 | 주가 |
|------|----------|------|------|
| SEC EDGAR | 분기 (10-Q), 연간 (10-K) | 실시간 (8-K) | N/A |
| DART | 분기, 연간 | 실시간 | N/A |
| Yahoo Finance | 분기 | N/A | 실시간 (15-20분 지연) |

---

**최종 업데이트**: 2025-10-23  
**문서 버전**: 1.0

