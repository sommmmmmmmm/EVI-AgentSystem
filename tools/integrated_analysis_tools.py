"""
 +    
-     +    
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class IntegratedAnalysisTool:
    """
     +    
    """
    
    def __init__(self):
        from tools.yahoo_finance_tools import YahooFinanceTool
        from tools.expert_opinion_tools import ExpertOpinionTool
        
        self.yahoo_tool = YahooFinanceTool()
        self.expert_tool = ExpertOpinionTool()
    
    def get_comprehensive_analysis(self, company_name: str) -> Dict[str, Any]:
        """
          ( + )
        """
        # 1.   ( )
        quantitative_analysis = self._get_quantitative_analysis(company_name)
        
        # 2.   ( )
        qualitative_analysis = self._get_qualitative_analysis(company_name)
        
        # 3.   
        integrated_score = self._calculate_integrated_score(quantitative_analysis, qualitative_analysis)
        
        # 4.   
        investment_grade = self._determine_investment_grade(integrated_score)
        
        # 5.   
        summary = self._generate_comprehensive_summary(company_name, quantitative_analysis, qualitative_analysis, integrated_score, investment_grade)
        
        return {
            'company_name': company_name,
            'analysis_date': datetime.now().isoformat(),
            'quantitative_analysis': quantitative_analysis,
            'qualitative_analysis': qualitative_analysis,
            'integrated_score': integrated_score,
            'investment_grade': investment_grade,
            'summary': summary
        }
    
    def _get_quantitative_analysis(self, company_name: str) -> Dict[str, Any]:
        """
          ( )
        """
        result = self.yahoo_tool.get_company_financial_data(company_name)
        
        if not result['data_available']:
            return {
                'data_available': False,
                'error': '   '
            }
        
        company_info = result['company_info']
        ratios = result['financial_ratios']
        
        return {
            'data_available': True,
            'company_info': company_info,
            'current_price': result['stock_price'],
            'market_cap': result['market_cap'],
            'stability_score': ratios.get('stability_score', 0),
            'growth_score': ratios.get('growth_score', 0),
            'market_interest_score': ratios.get('market_interest_score', 0),
            'overall_score': ratios.get('overall_score', 0),
            'daily_volatility': ratios.get('daily_volatility', 0),
            'yearly_position': ratios.get('yearly_position', 0),
            'volume': ratios.get('volume', 0)
        }
    
    def _get_qualitative_analysis(self, company_name: str) -> Dict[str, Any]:
        """
          ( )
        """
        return self.expert_tool.generate_qualitative_analysis(company_name)
    
    def _calculate_integrated_score(self, quantitative: Dict[str, Any], qualitative: Dict[str, Any]) -> Dict[str, float]:
        """
          
        """
        if not quantitative['data_available']:
            return {
                'integrated_score': 0,
                'quantitative_weight': 0,
                'qualitative_weight': 0,
                'confidence': 0
            }
        
        #   (30% )
        quant_score = quantitative['overall_score']
        quant_weight = 0.3
        
        #   (70% )
        qual_score = qualitative['qualitative_score']
        qual_weight = 0.7
        
        #  
        integrated_score = (quant_score * quant_weight) + (qual_score * qual_weight)
        
        #  
        quant_confidence = 1.0 if quantitative['data_available'] else 0.0
        qual_confidence = qualitative['expert_analysis']['expert_confidence']
        overall_confidence = (quant_confidence * quant_weight) + (qual_confidence * qual_weight)
        
        return {
            'integrated_score': integrated_score,
            'quantitative_score': quant_score,
            'qualitative_score': qual_score,
            'quantitative_weight': quant_weight,
            'qualitative_weight': qual_weight,
            'confidence': overall_confidence
        }
    
    def _determine_investment_grade(self, integrated_score: Dict[str, float]) -> Dict[str, str]:
        """
          
        """
        score = integrated_score['integrated_score']
        confidence = integrated_score['confidence']
        
        #   
        if score >= 90:
            grade = 'A+'
            recommendation = 'Strong Buy'
        elif score >= 80:
            grade = 'A'
            recommendation = 'Buy'
        elif score >= 70:
            grade = 'B+'
            recommendation = 'Buy'
        elif score >= 60:
            grade = 'B'
            recommendation = 'Hold'
        elif score >= 50:
            grade = 'C+'
            recommendation = 'Hold'
        elif score >= 40:
            grade = 'C'
            recommendation = 'Hold'
        elif score >= 30:
            grade = 'D+'
            recommendation = 'Sell'
        else:
            grade = 'D'
            recommendation = 'Strong Sell'
        
        #   
        if confidence < 0.5:
            grade += ' (Low Confidence)'
        elif confidence < 0.7:
            grade += ' (Medium Confidence)'
        else:
            grade += ' (High Confidence)'
        
        return {
            'grade': grade,
            'recommendation': recommendation,
            'confidence_level': self._get_confidence_level(confidence)
        }
    
    def _get_confidence_level(self, confidence: float) -> str:
        """
          
        """
        if confidence >= 0.8:
            return 'High'
        elif confidence >= 0.6:
            return 'Medium'
        elif confidence >= 0.4:
            return 'Low'
        else:
            return 'Very Low'
    
    def _generate_comprehensive_summary(self, company_name: str, quantitative: Dict, qualitative: Dict, integrated_score: Dict, investment_grade: Dict) -> str:
        """
           
        """
        if not quantitative['data_available']:
            return f"{company_name}:    "
        
        #  
        current_price = quantitative['current_price']
        quant_score = integrated_score['quantitative_score']
        qual_score = integrated_score['qualitative_score']
        total_score = integrated_score['integrated_score']
        grade = investment_grade['grade']
        recommendation = investment_grade['recommendation']
        
        #  
        expert_analysis = qualitative['expert_analysis']
        consensus_score = expert_analysis['expert_consensus_score']
        consensus_strength = expert_analysis['consensus_strength']
        
        summary = f"""
{company_name}   
{'='*50}

  : {grade}
 : {recommendation}
  : ${current_price:,.2f}

  :
-  : {quant_score:.1f}/100 ( )
-  : {qual_score:.1f}/100 ( )
-  : {total_score:.1f}/100

  :
-  : {consensus_score:.1f}/100
-  : {consensus_strength:.1f}%
- : {expert_analysis['expert_confidence']:.2f}

   :
"""
        
        #    
        industry_outlook = qualitative['industry_outlook']
        if industry_outlook:
            summary += f"1.  : {industry_outlook.get('growth_rate', 0)*100:.1f}%\n"
            summary += f"2.  : {', '.join(industry_outlook.get('key_drivers', [])[:2])}\n"
        
        summary += "\n[WARNING]  :\n"
        
        #   
        risk_assessment = qualitative['risk_assessment']
        for i, risk in enumerate(risk_assessment['risk_factors'][:3], 1):
            summary += f"{i}. {risk}\n"
        
        return summary.strip()
    
    def compare_companies(self, company_names: List[str]) -> Dict[str, Any]:
        """
           
        """
        analyses = {}
        
        for company in company_names:
            analyses[company] = self.get_comprehensive_analysis(company)
        
        #   
        sorted_companies = sorted(
            analyses.items(),
            key=lambda x: x[1]['integrated_score']['integrated_score'],
            reverse=True
        )
        
        #   
        comparison_summary = self._generate_comparison_summary(sorted_companies)
        
        return {
            'analyses': analyses,
            'ranking': sorted_companies,
            'comparison_summary': comparison_summary
        }
    
    def _generate_comparison_summary(self, sorted_companies: List[tuple]) -> str:
        """
           
        """
        summary = "   \n"
        summary += "="*50 + "\n\n"
        
        for i, (company, analysis) in enumerate(sorted_companies, 1):
            integrated_score = analysis['integrated_score']
            investment_grade = analysis['investment_grade']
            
            summary += f"{i}. {company}\n"
            summary += f"   : {investment_grade['grade']}\n"
            summary += f"   : {integrated_score['integrated_score']:.1f}/100\n"
            summary += f"   : {investment_grade['recommendation']}\n\n"
        
        return summary.strip()
