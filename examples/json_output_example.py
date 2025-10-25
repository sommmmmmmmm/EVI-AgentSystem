"""
Example: Using JSON-Only Output System

Demonstrates how to integrate the JSON-only output system
into your LLM-based agents.
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.json_parser import (
    parse_llm_json,
    extract_json,
    quick_fix_json,
    diagnose_json_error,
    JSONParseError
)

from prompts.json_output_templates import (
    get_risk_analysis_prompt,
    get_financial_analysis_prompt,
    get_market_trends_prompt,
    get_repair_prompt,
    get_json_llm_config,
    get_json_system_message,
    RISK_ANALYSIS_SCHEMA,
    FINANCIAL_ANALYSIS_SCHEMA,
    MARKET_TRENDS_SCHEMA,
    END_TOKEN
)


# =============================================================================
# Example 1: Basic Risk Analysis
# =============================================================================

def example_1_basic_risk_analysis():
    """Example: Parse a clean JSON response"""
    
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Risk Analysis (Clean JSON)")
    print("="*70)
    
    # Simulate LLM output (clean JSON with END_TOKEN)
    llm_output = '''{
  "company": "Tesla",
  "topic": "Compliance",
  "timeframe": "2023-2024",
  "incidents": [
    {
      "title": "Autopilot safety investigation",
      "date": "2023-08-15",
      "source_url": "https://nhtsa.gov/tesla-autopilot-investigation",
      "severity": "high",
      "description": "NHTSA investigating Autopilot after multiple crashes",
      "financial_impact": {
        "capex": null,
        "opex": null,
        "fines": 250000000
      },
      "probability": 0.7,
      "mitigation": "Software updates and enhanced warnings deployed"
    }
  ],
  "overall_risk_score": 68,
  "summary": "Tesla faces moderate-high regulatory risk due to ongoing Autopilot investigations"
}''' + END_TOKEN
    
    # Parse with schema validation
    try:
        result = parse_llm_json(
            llm_output,
            schema=RISK_ANALYSIS_SCHEMA,
            fallback_data={
                'company': 'Tesla',
                'topic': 'Compliance',
                'timeframe': '2023-2024'
            }
        )
        
        print(f"\n✅ SUCCESS!")
        print(f"   Company: {result['company']}")
        print(f"   Risk Score: {result['overall_risk_score']}")
        print(f"   Incidents: {len(result['incidents'])}")
        print(f"   Summary: {result['summary'][:60]}...")
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")


# =============================================================================
# Example 2: Handling Markdown Code Fences
# =============================================================================

def example_2_markdown_handling():
    """Example: Parse JSON wrapped in markdown"""
    
    print("\n" + "="*70)
    print("EXAMPLE 2: Handling Markdown Code Fences")
    print("="*70)
    
    # Simulate LLM output with markdown (common mistake)
    llm_output = '''Here's the analysis result:

```json
{
  "company": "Samsung SDI",
  "analysis_date": "2024-03-20",
  "metrics": {
    "revenue": 15000000000,
    "operating_profit": 1200000000,
    "net_income": 900000000,
    "total_assets": 25000000000,
    "total_equity": 18000000000,
    "total_debt": 3000000000
  },
  "ratios": {
    "roe": 0.05,
    "roa": 0.036,
    "operating_margin": 0.08,
    "debt_ratio": 0.167,
    "current_ratio": 2.5
  },
  "score": 75,
  "summary": "Solid financial performance with manageable debt"
}
```''' + END_TOKEN + '''

This analysis shows Samsung SDI is in good financial health.
'''
    
    # Parser automatically removes markdown
    try:
        result = parse_llm_json(
            llm_output,
            schema=FINANCIAL_ANALYSIS_SCHEMA
        )
        
        print(f"\n✅ SUCCESS (auto-cleaned markdown)!")
        print(f"   Company: {result['company']}")
        print(f"   Score: {result['score']}")
        print(f"   ROE: {result['ratios']['roe']:.1%}")
        print(f"   Debt Ratio: {result['ratios']['debt_ratio']:.1%}")
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")


# =============================================================================
# Example 3: Auto-Repair (Trailing Comma)
# =============================================================================

def example_3_auto_repair():
    """Example: Automatic repair of common JSON errors"""
    
    print("\n" + "="*70)
    print("EXAMPLE 3: Auto-Repair (Trailing Comma)")
    print("="*70)
    
    # Simulate LLM output with trailing comma
    llm_output = '''{
  "company": "LG Energy Solution",
  "analysis_date": "2024-03-20",
  "metrics": {
    "revenue": 23000000000,
    "operating_profit": 1800000000,
    "net_income": 1300000000,
    "total_assets": 35000000000,
    "total_equity": 22000000000,
    "total_debt": 5000000000,
  },
  "ratios": {
    "roe": 0.059,
    "roa": 0.037,
    "operating_margin": 0.078,
    "debt_ratio": 0.227,
    "current_ratio": 2.1,
  },
  "score": 78,
  "summary": "Strong performance in EV battery market",
}''' + END_TOKEN
    
    print("\n🔧 Input has trailing commas (line 9, 16, 19)")
    
    # Parser automatically repairs
    try:
        result = parse_llm_json(
            llm_output,
            schema=FINANCIAL_ANALYSIS_SCHEMA,
            repair_attempts=2
        )
        
        print(f"\n✅ AUTO-REPAIRED!")
        print(f"   Company: {result['company']}")
        print(f"   Score: {result['score']}")
        print(f"   Operating Margin: {result['ratios']['operating_margin']:.1%}")
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")


# =============================================================================
# Example 4: Fallback Response
# =============================================================================

def example_4_fallback():
    """Example: Using fallback when parsing completely fails"""
    
    print("\n" + "="*70)
    print("EXAMPLE 4: Fallback Response (Complete Parse Failure)")
    print("="*70)
    
    # Simulate completely broken output
    llm_output = "I couldn't generate the JSON because the data was incomplete."
    
    print(f"\n🔧 Input is not JSON at all")
    print(f"   Input: {llm_output[:50]}...")
    
    # Parser returns fallback
    result = parse_llm_json(
        llm_output,
        schema=RISK_ANALYSIS_SCHEMA,
        fallback_data={
            'company': 'Unknown Company',
            'topic': 'General Risk',
            'timeframe': '2024'
        }
    )
    
    print(f"\n⚠️  FALLBACK USED!")
    print(f"   Company: {result['company']}")
    print(f"   Topic: {result['topic']}")
    print(f"   Incidents: {len(result['incidents'])}")
    print(f"   Risk Score: {result['overall_risk_score']}")
    print(f"   Summary: {result['summary'][:80]}...")


# =============================================================================
# Example 5: Generating JSON-Only Prompt
# =============================================================================

def example_5_generate_prompt():
    """Example: Generate hard-guard JSON-only prompt"""
    
    print("\n" + "="*70)
    print("EXAMPLE 5: Generating JSON-Only Prompt")
    print("="*70)
    
    # Generate risk analysis prompt
    prompt = get_risk_analysis_prompt(
        company="Panasonic Holdings",
        topic="Sustainability",
        timeframe="2023-2024",
        analysis_text="""
        Panasonic has committed to carbon neutrality by 2030.
        They've invested $5B in renewable energy for factories.
        However, they faced criticism for slow progress on supplier sustainability.
        Environmental groups rated them 6/10 on green initiatives.
        """
    )
    
    print("\n📝 Generated Prompt Preview:")
    print(prompt[:800])
    print("\n... (truncated)")
    
    # Get recommended LLM config
    config = get_json_llm_config()
    print(f"\n⚙️  Recommended LLM Config:")
    print(f"   Temperature: {config['temperature']}")
    print(f"   Max Tokens: {config['max_tokens']}")
    print(f"   Top-P: {config['top_p']}")
    print(f"   Stop Token: {config['stop']}")


# =============================================================================
# Example 6: Two-Stage Approach
# =============================================================================

def example_6_two_stage():
    """Example: Two-stage approach (Summary → JSON)"""
    
    print("\n" + "="*70)
    print("EXAMPLE 6: Two-Stage Approach")
    print("="*70)
    
    print("\n📊 STAGE A: Natural language summary")
    print("   (Free-form LLM output)")
    
    # Stage A: Natural language summary
    stage_a_summary = """
    Tesla's compliance risk is moderate-high (68/100) due to:
    1. Ongoing NHTSA Autopilot investigation (high severity)
    2. Potential $250M fine
    3. 70% probability of regulatory action
    
    Mitigation: Software updates and enhanced driver warnings deployed.
    Timeline: Investigation ongoing since Aug 2023.
    """
    
    print(stage_a_summary)
    
    print("\n🔄 STAGE B: Convert summary to structured JSON")
    
    # Stage B: Convert to JSON using hard-guard prompt
    prompt = get_risk_analysis_prompt(
        company="Tesla",
        topic="Compliance",
        timeframe="2023-2024",
        analysis_text=stage_a_summary
    )
    
    print(f"   Generated JSON-only prompt ({len(prompt)} chars)")
    print(f"   → Send to LLM with strict config")
    print(f"   → Parse with schema validation")
    
    # In real usage:
    # llm_output = llm.generate(prompt, **get_json_llm_config())
    # result = parse_llm_json(llm_output, schema=RISK_ANALYSIS_SCHEMA)
    
    print("\n✅ Two-stage approach benefits:")
    print("   • Separates complex analysis from formatting")
    print("   • Each stage is simpler")
    print("   • Easier to debug")


# =============================================================================
# Example 7: Diagnostic Tools
# =============================================================================

def example_7_diagnostics():
    """Example: Using diagnostic tools"""
    
    print("\n" + "="*70)
    print("EXAMPLE 7: Diagnostic Tools")
    print("="*70)
    
    # Example of broken JSON
    broken_json = '''```json
{
  "company": "BYD",
  "score": NaN,
  "value": Infinity,
  "items": [1, 2, 3,],
}
```'''
    
    print("\n🔍 Input (with multiple issues):")
    print(broken_json)
    
    # Run diagnostics
    print("\n🔬 Diagnosis:")
    diagnosis = diagnose_json_error(broken_json)
    print(diagnosis)
    
    # Apply fixes
    print("\n🔧 Applying fixes...")
    
    # Step 1: Extract JSON
    extracted = extract_json(broken_json)
    print(f"   1. Extracted from markdown ({len(extracted)} chars)")
    
    # Step 2: Quick fix
    fixed = quick_fix_json(extracted)
    print(f"   2. Fixed syntax ({len(fixed)} chars)")
    
    # Step 3: Parse
    import json
    try:
        result = json.loads(fixed)
        print(f"\n✅ REPAIRED SUCCESSFULLY!")
        print(f"   {result}")
    except Exception as e:
        print(f"\n❌ Still failed: {e}")


# =============================================================================
# Example 8: Integration with Agent
# =============================================================================

def example_8_agent_integration():
    """Example: Full integration in an agent"""
    
    print("\n" + "="*70)
    print("EXAMPLE 8: Agent Integration Pattern")
    print("="*70)
    
    print("""
# Pseudo-code for agent integration

class RiskAnalysisAgent:
    
    def analyze_risk(self, company: str, topic: str) -> dict:
        '''Analyze risk and return structured JSON'''
        
        # 1. Generate JSON-only prompt
        prompt = get_risk_analysis_prompt(
            company=company,
            topic=topic,
            timeframe="2023-2024",
            analysis_text=self._gather_data(company, topic)
        )
        
        # 2. Call LLM with strict config
        config = get_json_llm_config()
        system_msg = get_json_system_message()
        
        llm_output = self.llm.generate(
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            **config
        )
        
        # 3. Parse with fallback
        try:
            result = parse_llm_json(
                llm_output,
                schema=RISK_ANALYSIS_SCHEMA,
                fallback_data={
                    'company': company,
                    'topic': topic,
                    'timeframe': '2023-2024'
                },
                repair_attempts=2
            )
            
            return result
            
        except Exception as e:
            # Last resort: manual repair
            repair_prompt = get_repair_prompt(
                broken_json=llm_output,
                schema=RISK_ANALYSIS_SCHEMA,
                error_message=str(e)
            )
            
            repaired_output = self.llm.generate(repair_prompt)
            return parse_llm_json(repaired_output, schema=RISK_ANALYSIS_SCHEMA)
    """)
    
    print("\n✅ Key integration points:")
    print("   1. Use JSON-only prompts (json_output_templates)")
    print("   2. Apply strict LLM config (low temp, stop token)")
    print("   3. Parse with schema validation (json_parser)")
    print("   4. Provide fallback data for safety")
    print("   5. Log parsing process for monitoring")


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("JSON-Only Output System - Complete Examples")
    print("="*70)
    
    # Run all examples
    example_1_basic_risk_analysis()
    example_2_markdown_handling()
    example_3_auto_repair()
    example_4_fallback()
    example_5_generate_prompt()
    example_6_two_stage()
    example_7_diagnostics()
    example_8_agent_integration()
    
    print("\n" + "="*70)
    print("All examples completed!")
    print("="*70)
    print("\nNext steps:")
    print("  1. Review JSON_OUTPUT_GUIDE.md for detailed documentation")
    print("  2. Integrate json_parser.py into your agents")
    print("  3. Use json_output_templates.py for LLM prompts")
    print("  4. Monitor parsing success rate and adjust as needed")
    print("="*70 + "\n")

