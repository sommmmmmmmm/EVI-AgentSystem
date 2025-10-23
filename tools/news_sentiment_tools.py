"""
      
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import requests
import json

class NewsSentimentTool:
    """
          
    """
    
    def __init__(self):
        self.sentiment_keywords = self._load_sentiment_keywords()
        self.news_sources = [
            'Reuters', 'Bloomberg', 'Wall Street Journal', 
            'Financial Times', 'Yonhap News', 'Maeil Business'
        ]
    
    def _load_sentiment_keywords(self) -> Dict[str, List[str]]:
        """
           
        """
        return {
            'positive': [
                'breakthrough', 'innovation', 'growth', 'expansion', 'partnership',
                'contract', 'award', 'achievement', 'success', 'profit',
                'revenue', 'increase', 'strong', 'robust', 'outperform',
                'upgrade', 'buy', 'bullish', 'optimistic', 'confident',
                '', '', '', '', '', '', '',
                '', '', '', '', '', '', '',
                '', '', '', ''
            ],
            'negative': [
                'decline', 'loss', 'decrease', 'weak', 'poor', 'disappointing',
                'concern', 'risk', 'challenge', 'problem', 'issue', 'crisis',
                'downgrade', 'sell', 'bearish', 'pessimistic', 'worried',
                'uncertain', 'volatile', 'unstable', 'troubled', 'struggling',
                '', '', '', '', '', '', '',
                '', '', '', '', '', '', '',
                '', '', '', ''
            ],
            'neutral': [
                'maintain', 'stable', 'steady', 'unchanged', 'consistent',
                'normal', 'average', 'moderate', 'balanced', 'mixed',
                '', '', '', '', '', '',
                '', '', '', ''
            ]
        }
    
    def analyze_news_sentiment(self, company_name: str, news_texts: List[str]) -> Dict[str, Any]:
        """
           
        """
        if not news_texts:
            return {
                'sentiment_score': 0.0,
                'sentiment_label': 'neutral',
                'confidence': 0.0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0
            }
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for text in news_texts:
            sentiment = self._analyze_text_sentiment(text)
            if sentiment == 'positive':
                positive_count += 1
            elif sentiment == 'negative':
                negative_count += 1
            else:
                neutral_count += 1
        
        total_news = len(news_texts)
        
        #    (-1 ~ 1)
        sentiment_score = (positive_count - negative_count) / total_news if total_news > 0 else 0
        
        #   
        if sentiment_score > 0.2:
            sentiment_label = 'positive'
        elif sentiment_score < -0.2:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'
        
        #  
        confidence = abs(sentiment_score)
        
        return {
            'sentiment_score': sentiment_score,
            'sentiment_label': sentiment_label,
            'confidence': confidence,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'total_news': total_news
        }
    
    def _analyze_text_sentiment(self, text: str) -> str:
        """
           
        """
        text_lower = text.lower()
        
        positive_score = 0
        negative_score = 0
        
        #   
        for keyword in self.sentiment_keywords['positive']:
            if keyword.lower() in text_lower:
                positive_score += 1
        
        #   
        for keyword in self.sentiment_keywords['negative']:
            if keyword.lower() in text_lower:
                negative_score += 1
        
        #  
        if positive_score > negative_score:
            return 'positive'
        elif negative_score > positive_score:
            return 'negative'
        else:
            return 'neutral'
    
    def get_mock_news_data(self, company_name: str) -> List[str]:
        """
        API 실패 시 빈 리스트 반환
        """
        print(f"[ERROR] '{company_name}'의 뉴스 데이터를 가져올 수 없습니다. API 키를 확인하세요.")
        return []
    
    def get_market_sentiment(self, company_name: str) -> Dict[str, Any]:
        """
           ( )
        """
        # API 실패 시 빈 데이터로 처리
        news_texts = self.get_mock_news_data(company_name)
        
        sentiment_analysis = self.analyze_news_sentiment(company_name, news_texts)
        
        #    (0-100)
        market_sentiment_score = (sentiment_analysis['sentiment_score'] + 1) * 50
        
        return {
            'market_sentiment_score': market_sentiment_score,
            'sentiment_analysis': sentiment_analysis,
            'news_summary': self._generate_news_summary(company_name, sentiment_analysis)
        }
    
    def _generate_news_summary(self, company_name: str, sentiment_analysis: Dict[str, Any]) -> str:
        """
            
        """
        sentiment_label = sentiment_analysis['sentiment_label']
        confidence = sentiment_analysis['confidence']
        positive_count = sentiment_analysis['positive_count']
        negative_count = sentiment_analysis['negative_count']
        total_news = sentiment_analysis['total_news']
        
        if sentiment_label == 'positive':
            summary = f"{company_name}    . "
        elif sentiment_label == 'negative':
            summary = f"{company_name}    . "
        else:
            summary = f"{company_name}    . "
        
        summary += f" {total_news}    {positive_count},  {negative_count} "
        summary += f" {confidence:.1%} {sentiment_label}  ."
        
        return summary


