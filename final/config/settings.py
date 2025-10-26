# -*- coding: utf-8 -*-
"""
     
"""

import os
from typing import Dict, List, Any
from dataclasses import dataclass
from dotenv import load_dotenv

#   
load_dotenv()

@dataclass
class EVMarketConfig:
    """   """
    #   
    analysis_days: int = 30  #  30

    #   
    news_sources: List[str] = None

    #  
    securities_firms: List[str] = None

    #    
    ev_oems: List[str] = None

    #   
    keyword_categories: Dict[str, List[str]] = None

    #    
    financial_analysis_weights: Dict[str, float] = None

    #    
    risk_analysis_weights: Dict[str, float] = None
    
    # 데이터 수집 설정
    max_news_articles: int = 50  # 최대 뉴스 기사 수
    max_disclosures_per_company: int = 10  # 기업당 최대 공시 수
    max_sec_filings_per_company: int = 8  # 기업당 최대 SEC 공시 수
    days_ago: int = 30  # 최근 N일 이내 데이터
    
    # 웹 서치 및 에러 핸들링 설정
    relaxed_mode: bool = True  # 에러 시에도 계속 진행 (기준 완화)
    fallback_enabled: bool = True  # 웹 서치 실패 시 fallback 전략 사용
    default_companies_enabled: bool = True  # 기본 기업 리스트 사용 여부

    def __post_init__(self):
        if self.news_sources is None:
            self.news_sources = [
                '',
                '',
                ''
            ]

        if self.securities_firms is None:
            self.securities_firms = [
                '',
                '',
                ''
            ]

        if self.ev_oems is None:
            self.ev_oems = [
                'Tesla', 'Ford', 'GM', 'Rivian', 'Lucid',  # 미국
                'BYD', 'Nio', 'Xpeng', 'Li Auto',  # 중국
                'BMW', 'Mercedes', 'Volkswagen', 'Audi', 'Porsche',  # 독일
                'Hyundai', 'Kia', 'Genesis',  # 한국
                '현대자동차', '기아', '제네시스',  # 한국 (한글)
                'Toyota', 'Nissan', 'Honda',  # 일본
                'Volvo', 'Polestar'  # 스웨덴
            ]

        if self.keyword_categories is None:
            self.keyword_categories = {
                '_': [
                    'LFP', 'NCM', 'NCA', '4680', '21700', '2170',
                    '', '', '', 'BMS',
                    '', 'DC', 'AC', '',
                    '', 'ADAS', 'V2G', 'V2L'
                ],
                '_': [
                    '', '', '', '',
                    '', '', '', 'ESG',
                    '', '', '', ''
                ],
                '_': [
                    '', '', '', 'OBC',
                    'BMS', '', '', 'DC-DC',
                    '', 'PTC', '', ''
                ],
                '_': [
                    '', '', '', '', '',
                    '', 'LFP', 'NCM', 'NCA', 'LCO',
                    '', '', '', '',
                    '', '', '', ''
                ],
                '_': [
                    '', '', '', '',
                    '', '', '',
                    '', '', ''
                ],
                '_': [
                    '', 'R&D', '', '',
                    '', 'M&A', '', '',
                    '', '', ''
                ]
            }

        if self.financial_analysis_weights is None:
            self.financial_analysis_weights = {
                'qualitative': 0.7,  #   70%
                'quantitative': 0.3   #   30%
            }

        if self.risk_analysis_weights is None:
            self.risk_analysis_weights = {
                'quantitative': 0.8,  #   80%
                'qualitative': 0.2    #   20%
            }

#   
config = EVMarketConfig()

# OEM 기업 리스트 (영문, 대소문자 구분 없이 매칭하기 위한 소문자 버전)
OEM_COMPANIES_LOWER = [oem.lower() for oem in config.ev_oems]

def is_oem_company(company_name: str) -> bool:
    """기업명이 OEM인지 확인"""
    return company_name.lower() in OEM_COMPANIES_LOWER

def calculate_company_confidence(
    company_name: str,
    is_listed: bool = False,
    has_financial_data: bool = False,
    data_source: str = 'unknown',
    is_discovered_from_news: bool = False
) -> float:
    """
    기업 신뢰도 계산
    
    Args:
        company_name: 기업명
        is_listed: 상장 여부
        has_financial_data: 재무 데이터 존재 여부
        data_source: 데이터 출처 (DART, SEC, Yahoo Finance)
        is_discovered_from_news: 뉴스에서 발견된 기업인지
    
    Returns:
        신뢰도 점수 (0.0 ~ 1.0)
    """
    base_confidence = 0.4  # 기본 신뢰도
    
    # OEM 여부 (+0.1)
    if is_oem_company(company_name):
        base_confidence += 0.1
    
    # 상장 여부 (+0.2)
    if is_listed:
        base_confidence += 0.2
    
    # 재무 데이터 존재 여부 (+0.3)
    if has_financial_data:
        base_confidence += 0.3
        
        # 데이터 소스별 추가 보너스
        if data_source == 'DART':
            base_confidence += 0.05  # 공식 공시
        elif data_source == 'SEC':
            base_confidence += 0.05  # 공식 공시
        elif data_source == 'Yahoo Finance':
            base_confidence += 0.02  # 시장 데이터
    
    # 뉴스에서 발견 (+0.1)
    if is_discovered_from_news:
        base_confidence += 0.1
    
    # 최대 1.0으로 제한
    return min(base_confidence, 1.0)

# Ensure sodium-related materials are included in the materials keyword category
try:
    kc = config.keyword_categories or {}
    sodium_terms = ['', '', '', '', 'Na-ion', 'SIB', ' ']
    target_key = None
    for k, v in kc.items():
        if isinstance(v, list) and any(x in v for x in ['LFP', 'NCM', 'NCA', 'LCO']):
            target_key = k
            break
    if target_key:
        for t in sodium_terms:
            if t not in kc[target_key]:
                kc[target_key].append(t)
except Exception:
    pass

#    
SUPPLIER_RELATIONSHIP_MAPPING = {
    '': {
        'keywords': ['', '', '', '', ''],
        'confidence_threshold': 0.7
    },
    '': {
        'keywords': ['', '', '', '', ''],
        'confidence_threshold': 0.6
    },
    '': {
        'keywords': ['', '', '', ''],
        'confidence_threshold': 0.8
    },
    '': {
        'keywords': [],
        'confidence_threshold': 0.0
    }
}

#    
RISK_ANALYSIS_CRITERIA = {
    'quantitative': {
        'financial_ratios': {
            'debt_ratio': {'threshold': 0.5, 'weight': 0.2},
            'current_ratio': {'threshold': 1.0, 'weight': 0.15},
            'roe': {'threshold': 0.1, 'weight': 0.15},
            'operating_margin': {'threshold': 0.05, 'weight': 0.15}
        },
        'market_metrics': {
            'beta': {'threshold': 1.2, 'weight': 0.1},
            'volatility': {'threshold': 0.3, 'weight': 0.1},
            'market_cap': {'threshold': 1000, 'weight': 0.15}  # 
        }
    },
    'qualitative': {
        'governance': {
            'management_stability': {'weight': 0.3},
            'board_composition': {'weight': 0.2},
            'audit_quality': {'weight': 0.2}
        },
        'legal': {
            'litigation_risk': {'weight': 0.15},
            'regulatory_compliance': {'weight': 0.15}
        }
    }
}

#   
INVESTMENT_STRATEGY_CONFIG = {
    'target_audience': '',
    'investment_horizon': '',  # 3-12
    'risk_tolerance': '',
    'focus_areas': [
        '  ',
        ' ',
        '   ',
        ' '
    ]
}

# 데이터 소스별 fallback 전략
DATA_SOURCE_FALLBACK = {
    'korea': {
        'primary': 'DART',  # 한국 기업: DART 공시
        'fallback': 'Yahoo Finance',  # DART 실패 시 Yahoo Finance
        'default_companies': [
            'LG에너지솔루션', '삼성SDI', 'SK온', 
            '현대자동차', '기아', '에코프로비엠',
            '포스코케미칼', 'LG화학'
        ]
    },
    'us': {
        'primary': 'SEC EDGAR',  # 미국 기업: SEC 공시
        'fallback': 'Yahoo Finance',  # SEC 실패 시 Yahoo Finance
        'default_companies': [
            'Tesla', 'GM', 'Ford', 
            'Rivian', 'Lucid', 'Albemarle'
        ]
    },
    'others': {
        'primary': 'Yahoo Finance',  # 그 외 국가: Yahoo Finance
        'fallback': None,  # fallback 없음
        'default_companies': [
            'BMW', 'Mercedes', 'Volkswagen',
            'BYD', 'Panasonic', 'CATL'
        ]
    }
}
