"""
    (  )
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class DetailedReportGenerator:
    """
        (  )
    """
    
    def __init__(self):
        from tools.integrated_analysis_tools import IntegratedAnalysisTool
        self.integrated_tool = IntegratedAnalysisTool()
    
    def generate_comprehensive_report(self, company_names: List[str]) -> Dict[str, Any]:
        """
            (  )
        """
        #   
        individual_analyses = {}
        for company in company_names:
            individual_analyses[company] = self.integrated_tool.get_comprehensive_analysis(company)
        
        #    
        comparison = self.integrated_tool.compare_companies(company_names)
        
        #  
        insights = self._analyze_insights(individual_analyses, comparison)
        
        #   
        detailed_report = self._generate_detailed_report(individual_analyses, comparison, insights)
        
        return {
            'report_date': datetime.now().isoformat(),
            'individual_analyses': individual_analyses,
            'comparison_analysis': comparison,
            'insights_analysis': insights,
            'detailed_report': detailed_report
        }
    
    def _analyze_insights(self, individual_analyses: Dict, comparison: Dict) -> Dict[str, Any]:
        """
          (  )
        """
        insights = {
            'top_performers': [],
            'key_findings': [],
            'expert_consensus_analysis': {},
            'quantitative_vs_qualitative': {},
            'risk_analysis': {},
            'growth_drivers': {}
        }
        
        #   
        ranking = comparison['ranking']
        insights['top_performers'] = self._analyze_top_performers(ranking[:3])
        
        #  
        insights['key_findings'] = self._analyze_key_findings(individual_analyses, ranking)
        
        #   
        insights['expert_consensus_analysis'] = self._analyze_expert_consensus(individual_analyses)
        
        #  vs  
        insights['quantitative_vs_qualitative'] = self._analyze_quantitative_vs_qualitative(individual_analyses)
        
        #  
        insights['risk_analysis'] = self._analyze_risks(individual_analyses)
        
        #   
        insights['growth_drivers'] = self._analyze_growth_drivers(individual_analyses)
        
        return insights
    
    def _analyze_top_performers(self, top_3: List[tuple]) -> List[Dict[str, Any]]:
        """
          
        """
        top_performers = []
        
        for i, (company, analysis) in enumerate(top_3, 1):
            integrated_score = analysis['integrated_score']
            investment_grade = analysis['investment_grade']
            qualitative = analysis['qualitative_analysis']
            
            #   
            expert_consensus = qualitative['consensus_analysis']
            top_growth_drivers = qualitative['top_growth_drivers']
            top_risks = qualitative['top_risks']
            
            performer = {
                'rank': i,
                'company': company,
                'score': integrated_score['integrated_score'],
                'grade': investment_grade['grade'],
                'recommendation': investment_grade['recommendation'],
                'evidence': {
                    'expert_consensus': {
                        'rating': expert_consensus['consensus_rating'],
                        'target_price': expert_consensus['consensus_target_price'],
                        'upside': expert_consensus['consensus_upside'],
                        'analyst_count': expert_consensus['analyst_count'],
                        'confidence': expert_consensus['confidence_score']
                    },
                    'quantitative_score': integrated_score['quantitative_score'],
                    'qualitative_score': integrated_score['qualitative_score'],
                    'top_growth_drivers': top_growth_drivers[:3],
                    'top_risks': top_risks[:3]
                },
                'sources': self._get_sources_for_company(company, analysis)
            }
            
            top_performers.append(performer)
        
        return top_performers
    
    def _analyze_key_findings(self, individual_analyses: Dict, ranking: List[tuple]) -> List[Dict[str, Any]]:
        """
          
        """
        findings = []
        
        # 1. GM 1 
        gm_analysis = individual_analyses.get('GM')
        if gm_analysis and ranking[0][0] == 'GM':
            findings.append({
                'finding': 'GM 1:       ',
                'evidence': {
                    'score': gm_analysis['integrated_score']['integrated_score'],
                    'qualitative_score': gm_analysis['integrated_score']['qualitative_score'],
                    'expert_consensus': gm_analysis['qualitative_analysis']['consensus_analysis']['consensus_rating'],
                    'expert_confidence': gm_analysis['qualitative_analysis']['consensus_analysis']['confidence_score']
                },
                'sources': self._get_sources_for_company('GM', gm_analysis),
                'explanation': 'GM   100       '
            })
        
        # 2.   
        korean_companies = ['SDI', '', 'LG']
        korean_performances = []
        
        for company in korean_companies:
            if company in individual_analyses:
                analysis = individual_analyses[company]
                korean_performances.append({
                    'company': company,
                    'score': analysis['integrated_score']['integrated_score'],
                    'grade': analysis['investment_grade']['grade'],
                    'qualitative_score': analysis['integrated_score']['qualitative_score']
                })
        
        if korean_performances:
            findings.append({
                'finding': '  : SDI,  A   ',
                'evidence': {
                    'korean_companies': korean_performances,
                    'a_grade_count': len([p for p in korean_performances if 'A' in p['grade']])
                },
                'sources': self._get_korean_companies_sources(korean_companies, individual_analyses),
                'explanation': '          '
            })
        
        # 3.  
        tesla_analysis = individual_analyses.get('')
        if tesla_analysis:
            findings.append({
                'finding': ' :       ',
                'evidence': {
                    'quantitative_score': tesla_analysis['integrated_score']['quantitative_score'],
                    'qualitative_score': tesla_analysis['integrated_score']['qualitative_score'],
                    'expert_consensus': tesla_analysis['qualitative_analysis']['consensus_analysis']['consensus_rating'],
                    'rank': next(i for i, (company, _) in enumerate(ranking, 1) if company == '')
                },
                'sources': self._get_sources_for_company('', tesla_analysis),
                'explanation': '     ,        '
            })
        
        # 4.   
        findings.append({
            'finding': '  : 70%       ',
            'evidence': {
                'qualitative_weight': 0.7,
                'quantitative_weight': 0.3,
                'correlation_analysis': self._analyze_qualitative_impact(individual_analyses)
            },
            'sources': '    ',
            'explanation': '  70%         '
        })
        
        return findings
    
    def _analyze_expert_consensus(self, individual_analyses: Dict) -> Dict[str, Any]:
        """
          
        """
        consensus_data = {}
        
        for company, analysis in individual_analyses.items():
            if analysis['quantitative_analysis']['data_available']:
                expert_consensus = analysis['qualitative_analysis']['consensus_analysis']
                consensus_data[company] = {
                    'rating': expert_consensus['consensus_rating'],
                    'target_price': expert_consensus['consensus_target_price'],
                    'upside': expert_consensus['consensus_upside'],
                    'analyst_count': expert_consensus['analyst_count'],
                    'confidence': expert_consensus['confidence_score']
                }
        
        return consensus_data
    
    def _analyze_quantitative_vs_qualitative(self, individual_analyses: Dict) -> Dict[str, Any]:
        """
         vs  
        """
        comparison_data = []
        
        for company, analysis in individual_analyses.items():
            if analysis['quantitative_analysis']['data_available']:
                integrated_score = analysis['integrated_score']
                comparison_data.append({
                    'company': company,
                    'quantitative_score': integrated_score['quantitative_score'],
                    'qualitative_score': integrated_score['qualitative_score'],
                    'difference': integrated_score['qualitative_score'] - integrated_score['quantitative_score']
                })
        
        return {
            'comparison_data': comparison_data,
            'average_quantitative': sum(c['quantitative_score'] for c in comparison_data) / len(comparison_data),
            'average_qualitative': sum(c['qualitative_score'] for c in comparison_data) / len(comparison_data)
        }
    
    def _analyze_risks(self, individual_analyses: Dict) -> Dict[str, Any]:
        """
         
        """
        all_risks = []
        
        for company, analysis in individual_analyses.items():
            if analysis['quantitative_analysis']['data_available']:
                risks = analysis['qualitative_analysis']['top_risks']
                for risk in risks:
                    if isinstance(risk, dict):
                        all_risks.append({
                            'company': company,
                            'risk': risk['risk'],
                            'frequency': risk['frequency']
                        })
                    else:
                        all_risks.append({
                            'company': company,
                            'risk': risk[0],
                            'frequency': risk[1]
                        })
        
        #   
        risk_frequency = {}
        for risk_item in all_risks:
            risk_text = risk_item['risk']
            if risk_text not in risk_frequency:
                risk_frequency[risk_text] = {'count': 0, 'companies': []}
            risk_frequency[risk_text]['count'] += risk_item['frequency']
            risk_frequency[risk_text]['companies'].append(risk_item['company'])
        
        return {
            'all_risks': all_risks,
            'risk_frequency': risk_frequency,
            'top_risks': sorted(risk_frequency.items(), key=lambda x: x[1]['count'], reverse=True)[:5]
        }
    
    def _analyze_growth_drivers(self, individual_analyses: Dict) -> Dict[str, Any]:
        """
          
        """
        all_drivers = []
        
        for company, analysis in individual_analyses.items():
            if analysis['quantitative_analysis']['data_available']:
                drivers = analysis['qualitative_analysis']['top_growth_drivers']
                for driver in drivers:
                    if isinstance(driver, dict):
                        all_drivers.append({
                            'company': company,
                            'driver': driver['driver'],
                            'frequency': driver['frequency']
                        })
                    else:
                        all_drivers.append({
                            'company': company,
                            'driver': driver[0],
                            'frequency': driver[1]
                        })
        
        #    
        driver_frequency = {}
        for driver_item in all_drivers:
            driver_text = driver_item['driver']
            if driver_text not in driver_frequency:
                driver_frequency[driver_text] = {'count': 0, 'companies': []}
            driver_frequency[driver_text]['count'] += driver_item['frequency']
            driver_frequency[driver_text]['companies'].append(driver_item['company'])
        
        return {
            'all_drivers': all_drivers,
            'driver_frequency': driver_frequency,
            'top_drivers': sorted(driver_frequency.items(), key=lambda x: x[1]['count'], reverse=True)[:5]
        }
    
    def _analyze_qualitative_impact(self, individual_analyses: Dict) -> Dict[str, Any]:
        """
           
        """
        impact_data = []
        
        for company, analysis in individual_analyses.items():
            if analysis['quantitative_analysis']['data_available']:
                integrated_score = analysis['integrated_score']
                quant_score = integrated_score['quantitative_score']
                qual_score = integrated_score['qualitative_score']
                final_score = integrated_score['integrated_score']
                
                #      
                qualitative_impact = (qual_score * 0.7) / final_score if final_score > 0 else 0
                
                impact_data.append({
                    'company': company,
                    'qualitative_impact_ratio': qualitative_impact,
                    'score_difference': qual_score - quant_score
                })
        
        return {
            'impact_data': impact_data,
            'average_impact': sum(d['qualitative_impact_ratio'] for d in impact_data) / len(impact_data)
        }
    
    def _get_sources_for_company(self, company: str, analysis: Dict) -> List[str]:
        """
           
        """
        sources = []
        
        if 'qualitative_analysis' in analysis:
            expert_analyses = analysis['qualitative_analysis'].get('consensus_analysis', {})
            if 'analyst_count' in expert_analyses:
                #       
                sources.append(f"{company}   {expert_analyses['analyst_count']}")
        
        return sources
    
    def _get_korean_companies_sources(self, korean_companies: List[str], individual_analyses: Dict) -> List[str]:
        """
           
        """
        sources = []
        
        for company in korean_companies:
            if company in individual_analyses:
                analysis = individual_analyses[company]
                expert_consensus = analysis['qualitative_analysis']['consensus_analysis']
                sources.append(f"{company}: {expert_consensus['analyst_count']}  ")
        
        return sources
    
    def _generate_detailed_report(self, individual_analyses: Dict, comparison: Dict, insights: Dict) -> str:
        """
          
        """
        report = f"""
#     
** **: {datetime.now().strftime('%Y %m %d %H:%M')}
** **: {', '.join(individual_analyses.keys())}

##    

"""
        
        #  
        for i, (company, analysis) in enumerate(comparison['ranking'], 1):
            integrated_score = analysis['integrated_score']
            investment_grade = analysis['investment_grade']
            report += f"{i}. **{company}** - {investment_grade['grade']} ({integrated_score['integrated_score']:.1f})\n"
        
        report += "\n##     \n\n"
        
        #  
        for finding in insights['key_findings']:
            report += f"### {finding['finding']}\n\n"
            report += f"****:\n"
            
            if 'evidence' in finding:
                for key, value in finding['evidence'].items():
                    if isinstance(value, (int, float)):
                        report += f"- {key}: {value}\n"
                    elif isinstance(value, list):
                        report += f"- {key}: {len(value)} \n"
                    else:
                        report += f"- {key}: {value}\n"
            
            report += f"\n****: {finding['sources']}\n"
            report += f"****: {finding['explanation']}\n\n"
        
        #   
        report += "##    \n\n"
        for company, consensus in insights['expert_consensus_analysis'].items():
            report += f"**{company}**:\n"
            report += f"- : {consensus['rating']}\n"
            report += f"- : ${consensus['target_price']:,.0f}\n"
            report += f"- : {consensus['upside']:+.1f}%\n"
            report += f"-  : {consensus['analyst_count']}\n"
            report += f"- : {consensus['confidence']:.1%}\n\n"
        
        #  vs  
        report += "##   vs  \n\n"
        quant_qual = insights['quantitative_vs_qualitative']
        report += f"-   : {quant_qual['average_quantitative']:.1f}\n"
        report += f"-   : {quant_qual['average_qualitative']:.1f}\n"
        report += f"-  : 70%\n"
        report += f"-  : 30%\n\n"
        
        #  
        report += "## [WARNING]   \n\n"
        for i, (risk, data) in enumerate(insights['risk_analysis']['top_risks'], 1):
            report += f"{i}. **{risk}** ( {data['count']})\n"
            report += f"   -  : {', '.join(data['companies'])}\n\n"
        
        #   
        report += "##    \n\n"
        for i, (driver, data) in enumerate(insights['growth_drivers']['top_drivers'], 1):
            report += f"{i}. **{driver}** ( {data['count']})\n"
            report += f"   -  : {', '.join(data['companies'])}\n\n"
        
        return report.strip()
