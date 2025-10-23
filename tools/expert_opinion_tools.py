"""
      ( )
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import os
import statistics
import math

class ExpertOpinionTool:
    """
         
    """
    
    def __init__(self):
        self.expert_opinions_db = self._load_expert_opinions()
        self.industry_trends = self._load_industry_trends()
        self.risk_factors = self._load_risk_factors()
    
    def _load_expert_opinions(self) -> Dict[str, List[Dict[str, Any]]]:
        """
           
        """
        return {
            '': [
                {
                    'expert': 'Morgan Stanley',
                    'rating': 'Overweight',
                    'target_price': 500,
                    'opinion': '        ',
                    'confidence': 0.8,
                    'date': '2024-01-15',
                    'category': 'growth_potential'
                },
                {
                    'expert': 'Goldman Sachs',
                    'rating': 'Neutral',
                    'target_price': 450,
                    'opinion': '       ',
                    'confidence': 0.7,
                    'date': '2024-01-10',
                    'category': 'competition_risk'
                }
            ],
            'LG': [
                {
                    'expert': 'KB',
                    'rating': 'Buy',
                    'target_price': 500000,
                    'opinion': '        ',
                    'confidence': 0.9,
                    'date': '2024-01-20',
                    'category': 'market_leadership'
                },
                {
                    'expert': 'NH',
                    'rating': 'Hold',
                    'target_price': 450000,
                    'opinion': '       ',
                    'confidence': 0.6,
                    'date': '2024-01-18',
                    'category': 'margin_pressure'
                }
            ],
            'SDI': [
                {
                    'expert': '',
                    'rating': 'Buy',
                    'target_price': 300000,
                    'opinion': '    OEM  ',
                    'confidence': 0.8,
                    'date': '2024-01-22',
                    'category': 'technology_advantage'
                }
            ],
            '': [
                {
                    'expert': '',
                    'rating': 'Buy',
                    'target_price': 350000,
                    'opinion': '      ',
                    'confidence': 0.7,
                    'date': '2024-01-19',
                    'category': 'business_expansion'
                }
            ],
            'BYD': [
                {
                    'expert': 'JP Morgan',
                    'rating': 'Overweight',
                    'target_price': 15,
                    'opinion': '        ',
                    'confidence': 0.8,
                    'date': '2024-01-16',
                    'category': 'global_expansion'
                }
            ],
            '': [
                {
                    'expert': '',
                    'rating': 'Hold',
                    'target_price': 40000,
                    'opinion': '         ',
                    'confidence': 0.6,
                    'date': '2024-01-17',
                    'category': 'cautious_growth'
                }
            ]
        }
    
    def _load_industry_trends(self) -> Dict[str, Any]:
        """
           
        """
        return {
            'ev_battery': {
                'trend': '',
                'growth_rate': 0.25,
                'key_drivers': [
                    '  ',
                    '  (ESS)  ',
                    '  '
                ],
                'challenges': [
                    '  ',
                    '  ',
                    '  '
                ],
                'forecast_period': '2024-2026'
            },
            'autonomous_driving': {
                'trend': ' ',
                'growth_rate': 0.15,
                'key_drivers': [
                    'AI  ',
                    '  ',
                    ' '
                ],
                'challenges': [
                    ' ',
                    ' ',
                    ' '
                ],
                'forecast_period': '2024-2030'
            }
        }
    
    def _load_risk_factors(self) -> Dict[str, List[Dict[str, Any]]]:
        """
           ( )
        """
        return {
            '': [
                {'factor': '  ', 'severity': 'high'},
                {'factor': '   ', 'severity': 'medium'},
                {'factor': 'CEO  ', 'severity': 'medium'},
                {'factor': '  ', 'severity': 'high'}
            ],
            'LG': [
                {'factor': '   ', 'severity': 'high'},
                {'factor': '  ', 'severity': 'high'},
                {'factor': '  ', 'severity': 'medium'},
                {'factor': '  ', 'severity': 'low'}
            ],
            'SDI': [
                {'factor': '  ', 'severity': 'high'},
                {'factor': ' ', 'severity': 'medium'},
                {'factor': 'R&D  ', 'severity': 'medium'},
                {'factor': '  ', 'severity': 'high'}
            ],
            '': [
                {'factor': '  ', 'severity': 'medium'},
                {'factor': '  ', 'severity': 'high'},
                {'factor': '  ', 'severity': 'medium'},
                {'factor': '  ', 'severity': 'low'}
            ],
            'BYD': [
                {'factor': '   ', 'severity': 'high'},
                {'factor': '  ', 'severity': 'medium'},
                {'factor': '  ', 'severity': 'low'},
                {'factor': '  ', 'severity': 'medium'}
            ],
            '': [
                {'factor': '   ', 'severity': 'high'},
                {'factor': '  ', 'severity': 'medium'},
                {'factor': '  ', 'severity': 'high'},
                {'factor': ' ', 'severity': 'medium'}
            ]
        }
    
    def _calculate_time_weight(self, opinion_date: str, current_date: Optional[datetime] = None) -> float:
        """
             (  )
        """
        if current_date is None:
            current_date = datetime.now()
        
        opinion_datetime = datetime.strptime(opinion_date, '%Y-%m-%d')
        days_old = (current_date - opinion_datetime).days
        
        #   : 30  = 1.0, 90 = 0.7, 180 = 0.5
        # weight = e^(-days/90)
        time_weight = math.exp(-days_old / 90)
        
        return max(0.3, time_weight)  #   0.3
    
    def get_expert_opinions(self, company_name: str) -> List[Dict[str, Any]]:
        """
            
        """
        return self.expert_opinions_db.get(company_name, [])
    
    def calculate_expert_score(self, company_name: str) -> Dict[str, float]:
        """
             (    )
        """
        opinions = self.get_expert_opinions(company_name)
        
        if not opinions:
            return {
                'expert_consensus_score': 50.0,
                'expert_confidence': 0.0,
                'bullish_ratio': 0.0,
                'bearish_ratio': 0.0,
                'opinion_variance': 0.0,
                'consensus_strength': 0.0
            }
        
        #  
        rating_scores = {
            'Buy': 100,
            'Overweight': 80,
            'Neutral': 60,
            'Hold': 60,
            'Underweight': 40,
            'Sell': 20
        }
        
        weighted_scores = []
        total_weight = 0
        bullish_count = 0
        bearish_count = 0
        raw_scores = []
        
        for opinion in opinions:
            rating = opinion['rating']
            confidence = opinion['confidence']
            date = opinion['date']
            
            score = rating_scores.get(rating, 60)
            raw_scores.append(score)
            
            #   
            time_weight = self._calculate_time_weight(date)
            
            #   = confidence * time_weight
            final_weight = confidence * time_weight
            
            weighted_scores.append(score * final_weight)
            total_weight += final_weight
            
            if score >= 80:
                bullish_count += 1
            elif score <= 40:
                bearish_count += 1
        
        #   
        if total_weight > 0:
            expert_consensus_score = sum(weighted_scores) / total_weight
            expert_confidence = total_weight / len(opinions)
        else:
            expert_consensus_score = 50.0
            expert_confidence = 0.0
        
        #    ()
        if len(raw_scores) > 1:
            opinion_variance = statistics.stdev(raw_scores)
        else:
            opinion_variance = 0.0
        
        #   (   )
        #  0 = 100% ,  40 = 0% 
        consensus_strength = max(0, 1 - (opinion_variance / 40)) * 100
        
        bullish_ratio = bullish_count / len(opinions)
        bearish_ratio = bearish_count / len(opinions)
        
        return {
            'expert_consensus_score': expert_consensus_score,
            'expert_confidence': expert_confidence,
            'bullish_ratio': bullish_ratio,
            'bearish_ratio': bearish_ratio,
            'opinion_variance': opinion_variance,
            'consensus_strength': consensus_strength
        }
    
    def get_industry_outlook(self, company_name: str) -> Dict[str, Any]:
        """
           
        """
        industry_mapping = {
            '': 'ev_battery',
            'LG': 'ev_battery',
            'SDI': 'ev_battery',
            '': 'autonomous_driving',
            '': 'autonomous_driving',
            'BYD': 'ev_battery'
        }
        
        industry = industry_mapping.get(company_name, 'ev_battery')
        return self.industry_trends.get(industry, {})
    
    def get_risk_assessment(self, company_name: str) -> Dict[str, Any]:
        """
           (  )
        """
        risks = self.risk_factors.get(company_name, [])
        
        if not risks:
            return {
                'risk_factors': [],
                'risk_score': 0,
                'risk_level': 'Low'
            }
        
        #  
        severity_weights = {
            'high': 25,
            'medium': 15,
            'low': 5
        }
        
        #    
        risk_score = 0
        for risk in risks:
            severity = risk.get('severity', 'medium')
            risk_score += severity_weights.get(severity, 15)
        
        #  100 
        risk_score = min(100, risk_score)
        
        #    (  )
        risk_factors_list = [r['factor'] for r in risks]
        
        return {
            'risk_factors': risk_factors_list,
            'risk_details': risks,  #   
            'risk_score': risk_score,
            'risk_level': self._get_risk_level(risk_score)
        }
    
    def _get_risk_level(self, risk_score: float) -> str:
        """
            
        """
        if risk_score >= 80:
            return 'High'
        elif risk_score >= 60:
            return 'Medium-High'
        elif risk_score >= 40:
            return 'Medium'
        elif risk_score >= 20:
            return 'Low-Medium'
        else:
            return 'Low'
    
    def _normalize_growth_rate(self, growth_rate: float) -> float:
        """
          0-100  
        25%  = 80, 15% = 65, 5% = 40, 0% = 30, -5% = 20
        """
        if growth_rate >= 0.25:  # 25% 
            return min(100, 80 + (growth_rate - 0.25) * 100)
        elif growth_rate >= 0.15:  # 15~25%
            return 65 + (growth_rate - 0.15) * 150
        elif growth_rate >= 0.05:  # 5~15%
            return 40 + (growth_rate - 0.05) * 250
        elif growth_rate >= 0:  # 0~5%
            return 30 + growth_rate * 200
        else:  #  
            return max(10, 30 + growth_rate * 100)
    
    def generate_qualitative_analysis(self, company_name: str) -> Dict[str, Any]:
        """
           
        """
        expert_score = self.calculate_expert_score(company_name)
        industry_outlook = self.get_industry_outlook(company_name)
        risk_assessment = self.get_risk_assessment(company_name)
        
        #   
        growth_rate = industry_outlook.get('growth_rate', 0.1)
        industry_score = self._normalize_growth_rate(growth_rate)
        
        #     
        consensus_adjustment = expert_score['consensus_strength'] / 100
        
        #    
        #   40%,   35%,   25%
        base_score = (
            expert_score['expert_consensus_score'] * 0.40 +
            (100 - risk_assessment['risk_score']) * 0.35 +
            industry_score * 0.25
        )
        
        #   (50) 
        qualitative_score = base_score * consensus_adjustment + 50 * (1 - consensus_adjustment)
        
        return {
            'qualitative_score': qualitative_score,
            'expert_analysis': expert_score,
            'industry_outlook': industry_outlook,
            'industry_score': industry_score,
            'risk_assessment': risk_assessment,
            'summary': self._generate_summary(
                company_name, 
                expert_score, 
                industry_outlook, 
                risk_assessment,
                industry_score
            )
        }
    
    def _generate_summary(
        self, 
        company_name: str, 
        expert_score: Dict, 
        industry_outlook: Dict, 
        risk_assessment: Dict,
        industry_score: float
    ) -> str:
        """
           
        """
        expert_consensus = expert_score['expert_consensus_score']
        consensus_strength = expert_score['consensus_strength']
        risk_level = risk_assessment['risk_level']
        industry_growth = industry_outlook.get('growth_rate', 0.1) * 100
        
        #   
        if expert_consensus >= 80:
            expert_sentiment = " "
        elif expert_consensus >= 60:
            expert_sentiment = ""
        elif expert_consensus >= 40:
            expert_sentiment = ""
        else:
            expert_sentiment = ""
        
        #   
        if consensus_strength >= 80:
            consensus_desc = " "
        elif consensus_strength >= 60:
            consensus_desc = " "
        else:
            consensus_desc = " "
        
        return f"""
{company_name}  :
-  : {expert_sentiment} ( {expert_consensus:.1f}, {consensus_desc})
-  : {industry_growth:.1f}%   (: {industry_score:.1f})
-  : {risk_level} ({risk_assessment['risk_score']:.0f})
-  : {', '.join(risk_assessment['risk_factors'][:3])}
-  : {expert_score['expert_confidence']:.2f}
        """.strip()


#  
if __name__ == "__main__":
    tool = ExpertOpinionTool()
    
    companies = ['', 'LG', 'SDI']
    
    for company in companies:
        print(f"\n{'='*60}")
        print(f"{company} ")
        print('='*60)
        
        analysis = tool.generate_qualitative_analysis(company)
        
        print(f"\n : {analysis['qualitative_score']:.2f}")
        print(f"\n :")
        print(f"  -  : {analysis['expert_analysis']['expert_consensus_score']:.2f}")
        print(f"  - : {analysis['expert_analysis']['expert_confidence']:.2f}")
        print(f"  -  : {analysis['expert_analysis']['consensus_strength']:.2f}")
        print(f"  -  : {analysis['expert_analysis']['opinion_variance']:.2f}")
        print(f"\n  : {analysis['industry_score']:.2f}")
        print(f" : {analysis['risk_assessment']['risk_score']:.0f}")
        print(f"\n{analysis['summary']}")