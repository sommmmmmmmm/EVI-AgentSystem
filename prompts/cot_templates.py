"""
Chain of Thought (CoT)   
 Agent     
"""

from typing import Dict, Any, List
from models.citation import SourceType


class CoTPromptTemplates:
    """
    CoT   
    """
    
    @staticmethod
    def get_market_trend_analysis_prompt() -> str:
        """   CoT """
        return """
      . 
      :

<thinking_process>
<step1>
         .
-     
-     
-   /  
</step1>

<step2>
  , ,    .
-     (, ,  )
-      (, ,  )
-    (OEM, ,   )
</step2>

<step3>
       .
- //  
-     
-     
</step3>
</thinking_process>

     :

<analysis_result>
<market_trends>
[  -    ]
</market_trends>

<key_insights>
[  -  ]
</key_insights>

<investment_implications>
[ ]
</investment_implications>
</analysis_result>

:       .
"""
    
    @staticmethod
    def get_supplier_matching_prompt() -> str:
        """  CoT """
        return """
        .
      :

<thinking_process>
<step1>
     .
-      
-      
-      
</step1>

<step2>
        .
-     
-  ,  ,   
- OEM      
</step2>

<step3>
     .
- , ,   
-     
-     
</step3>
</thinking_process>

     :

<analysis_result>
<supply_chain_structure>
[  ]
</supply_chain_structure>

<verified_suppliers>
[   -     ]
</verified_suppliers>

<investment_recommendations>
[   ]
</investment_recommendations>
</analysis_result>

:        .
"""
    
    @staticmethod
    def get_financial_analysis_prompt() -> str:
        """  CoT """
        return """
       .
      :

<thinking_process>
<step1>
      .
- , ,   
-    (,  ) 
-   (,  ) 
</step1>

<step2>
      .
- PER, PBR, PSR    
-      
-        
</step2>

<step3>
       .
-      
-    
-      
</step3>
</thinking_process>

     :

<analysis_result>
<financial_metrics>
[   ]
</financial_metrics>

<valuation_analysis>
[  ]
</valuation_analysis>

<investment_scores>
[    ]
</investment_scores>
</analysis_result>

:         .
"""
    
    @staticmethod
    def get_risk_assessment_prompt() -> str:
        """  CoT """
        return """
      .
      :

<thinking_process>
<step1>
     .
-   (IRA,    )
-   (, ,    )
-   (  ,   )
-   ( ,   )
-   ( ,   )
</step1>

<step2>
        .
-     
-      
-       
</step2>

<step3>
       .
-      
-      
-      
</step3>
</thinking_process>

     :

<analysis_result>
<risk_factors>
[  ]
</risk_factors>

<risk_assessment>
[    ]
</risk_assessment>

<risk_mitigation>
[  ]
</risk_mitigation>
</analysis_result>

:         .
"""
    
    @staticmethod
    def get_investment_strategy_prompt() -> str:
        """  CoT """
        return """
      .
      :

<thinking_process>
<step1>
      .
-      
-     
-     
</step1>

<step2>
        .
-  ,  ,  ,    
-        
- //    
</step2>

<step3>
     .
-       
-    /  
-      
</step3>
</thinking_process>

     :

<analysis_result>
<market_analysis>
[  ]
</market_analysis>

<investment_opportunities>
[  ]
</investment_opportunities>

<portfolio_strategy>
[    ]
</portfolio_strategy>
</analysis_result>

:         .
"""
    
    @staticmethod
    def get_report_generation_prompt() -> str:
        """  CoT """
        return """
    .
      :

<thinking_process>
<step1>
        .
-       
-      
-      
</step1>

<step2>
        .
-     
-     
-    
</step2>

<step3>
     .
-      
-     
-        
</step3>
</thinking_process>

    :

<report_structure>
<executive_summary>
[ ]
</executive_summary>

<market_analysis>
[ ]
</market_analysis>

<investment_recommendations>
[ ]
</investment_recommendations>

<risk_analysis>
[ ]
</risk_analysis>

<glossary>
[ ]
</glossary>

<references>
[ -   ]
</references>
</report_structure>

:       ,       .
"""
    
    @staticmethod
    def get_cot_prompt_for_agent(agent_type: str, context: Dict[str, Any]) -> str:
        """  CoT  """
        
        base_prompts = {
            "market_trend": CoTPromptTemplates.get_market_trend_analysis_prompt(),
            "supplier_matching": CoTPromptTemplates.get_supplier_matching_prompt(),
            "financial_analysis": CoTPromptTemplates.get_financial_analysis_prompt(),
            "risk_assessment": CoTPromptTemplates.get_risk_assessment_prompt(),
            "investment_strategy": CoTPromptTemplates.get_investment_strategy_prompt(),
            "report_generation": CoTPromptTemplates.get_report_generation_prompt()
        }
        
        base_prompt = base_prompts.get(agent_type, "")
        
        #   
        context_info = f"""
<context>
{context.get('description', '')}
</context>

<data_sources>
   : {', '.join(context.get('data_sources', []))}
</data_sources>

<previous_results>
  : {context.get('previous_results', '')}
</previous_results>
"""
        
        return base_prompt + context_info
