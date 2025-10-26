"""
JSON Output Templates with Hard-Guard Prompts

Forces LLM to output ONLY valid JSON with strict schema compliance.
"""

from typing import Dict, Any
import json


# End token to mark complete JSON
END_TOKEN = "<END_OF_JSON>"


# ========================================
# JSON Schemas
# ========================================

RISK_ANALYSIS_SCHEMA = {
    "type": "object",
    "required": ["company", "topic", "timeframe", "incidents", "overall_risk_score", "summary"],
    "properties": {
        "company": {"type": "string"},
        "topic": {
            "type": "string",
            "enum": ["Compliance", "Governance", "Sustainability", "Market", "Technology", "Financial"]
        },
        "timeframe": {"type": "string"},
        "incidents": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["title", "date", "severity", "description"],
                "properties": {
                    "title": {"type": "string"},
                    "date": {"type": "string"},
                    "source_url": {"type": ["string", "null"]},
                    "severity": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"]
                    },
                    "description": {"type": "string"},
                    "financial_impact": {
                        "type": ["object", "null"],
                        "properties": {
                            "capex": {"type": ["number", "null"]},
                            "opex": {"type": ["number", "null"]},
                            "fines": {"type": ["number", "null"]}
                        },
                        "additionalProperties": False
                    },
                    "probability": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
                    "mitigation": {"type": ["string", "null"]}
                },
                "additionalProperties": False
            }
        },
        "overall_risk_score": {"type": ["number", "null"], "minimum": 0, "maximum": 100},
        "summary": {"type": "string"}
    },
    "additionalProperties": False
}


FINANCIAL_ANALYSIS_SCHEMA = {
    "type": "object",
    "required": ["company", "analysis_date", "metrics", "ratios", "score"],
    "properties": {
        "company": {"type": "string"},
        "analysis_date": {"type": "string"},
        "metrics": {
            "type": "object",
            "properties": {
                "revenue": {"type": ["number", "null"]},
                "operating_profit": {"type": ["number", "null"]},
                "net_income": {"type": ["number", "null"]},
                "total_assets": {"type": ["number", "null"]},
                "total_equity": {"type": ["number", "null"]},
                "total_debt": {"type": ["number", "null"]}
            },
            "additionalProperties": False
        },
        "ratios": {
            "type": "object",
            "properties": {
                "roe": {"type": ["number", "null"]},
                "roa": {"type": ["number", "null"]},
                "operating_margin": {"type": ["number", "null"]},
                "debt_ratio": {"type": ["number", "null"]},
                "current_ratio": {"type": ["number", "null"]}
            },
            "additionalProperties": False
        },
        "score": {"type": ["number", "null"], "minimum": 0, "maximum": 100},
        "summary": {"type": "string"}
    },
    "additionalProperties": False
}


MARKET_TRENDS_SCHEMA = {
    "type": "object",
    "required": ["analysis_date", "trends", "key_insights", "investment_implications"],
    "properties": {
        "analysis_date": {"type": "string"},
        "trends": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["title", "description", "significance", "time_horizon"],
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "significance": {
                        "type": "string",
                        "enum": ["high", "medium", "low"]
                    },
                    "time_horizon": {
                        "type": "string",
                        "enum": ["short-term", "medium-term", "long-term"]
                    },
                    "evidence": {"type": "array", "items": {"type": "string"}},
                    "affected_companies": {"type": "array", "items": {"type": "string"}}
                },
                "additionalProperties": False
            }
        },
        "key_insights": {"type": "array", "items": {"type": "string"}},
        "investment_implications": {"type": "array", "items": {"type": "string"}}
    },
    "additionalProperties": False
}


# ========================================
# Hard-Guard Prompt Templates
# ========================================

def get_json_only_prompt(
    task_description: str,
    schema: Dict[str, Any],
    input_data: Dict[str, Any],
    examples: str = ""
) -> str:
    """
    Generate hard-guard prompt that forces JSON-only output
    
    Args:
        task_description: Brief description of the task
        schema: JSON schema to enforce
        input_data: Input data for the task
        examples: Optional examples (default: "")
        
    Returns:
        Complete prompt with hard guards
    """
    
    schema_str = json.dumps(schema, indent=2)
    input_str = json.dumps(input_data, indent=2, ensure_ascii=False)
    
    prompt = f"""
You are a JSON compiler. Output EXACTLY ONE JSON object that matches the required schema.

CRITICAL RULES (VIOLATION = FAILURE):
1. Output ONLY valid JSON (NO markdown, NO natural language, NO comments)
2. NO code fences (``` is FORBIDDEN)
3. NO keys outside the schema (additionalProperties: false)
4. Missing values MUST be null (not empty string, not undefined)
5. End output with token: {END_TOKEN}
6. NO explanations before or after JSON
7. Follow data types exactly (string, number, array, object, null)

[TASK]
{task_description}

[REQUIRED SCHEMA]
{schema_str}

[INPUT DATA]
{input_str}

{examples}

[OUTPUT]
(ONLY ONE JSON OBJECT) + {END_TOKEN}
"""
    
    return prompt


def get_risk_analysis_prompt(
    company: str,
    topic: str,
    timeframe: str,
    analysis_text: str
) -> str:
    """
    Generate risk analysis JSON-only prompt
    
    Args:
        company: Company name
        topic: Risk topic (Compliance/Governance/Sustainability/etc)
        timeframe: Analysis period
        analysis_text: Raw analysis text to convert to JSON
        
    Returns:
        JSON-only prompt
    """
    
    task = f"""
Analyze the risk incidents for {company} regarding {topic} over {timeframe}.
Extract incidents with severity levels and calculate overall risk score (0-100).
"""
    
    input_data = {
        "company": company,
        "topic": topic,
        "timeframe": timeframe,
        "analysis_text": analysis_text[:1000]  # Truncate if too long
    }
    
    examples = """
[EXAMPLE OUTPUT]
{
  "company": "Panasonic Holdings",
  "topic": "Compliance",
  "timeframe": "2023-2024",
  "incidents": [
    {
      "title": "Battery safety recall",
      "date": "2023-06-15",
      "source_url": "https://example.com/news",
      "severity": "high",
      "description": "Recall of 100k battery units due to fire risk",
      "financial_impact": {
        "capex": null,
        "opex": 50000000,
        "fines": 5000000
      },
      "probability": 0.8,
      "mitigation": "Enhanced quality control implemented"
    }
  ],
  "overall_risk_score": 65,
  "summary": "Moderate risk level with recent compliance issues"
}""" + f"{END_TOKEN}"
    
    return get_json_only_prompt(
        task_description=task,
        schema=RISK_ANALYSIS_SCHEMA,
        input_data=input_data,
        examples=examples
    )


def get_financial_analysis_prompt(
    company: str,
    financial_data: Dict[str, Any]
) -> str:
    """
    Generate financial analysis JSON-only prompt
    
    Args:
        company: Company name
        financial_data: Raw financial data
        
    Returns:
        JSON-only prompt
    """
    
    task = f"""
Analyze the financial performance of {company}.
Calculate key metrics and ratios, assign investment score (0-100).
"""
    
    input_data = {
        "company": company,
        "financial_data": financial_data
    }
    
    examples = """
[EXAMPLE OUTPUT]
{
  "company": "Tesla",
  "analysis_date": "2024-03-20",
  "metrics": {
    "revenue": 96773000000,
    "operating_profit": 8891000000,
    "net_income": 14997000000,
    "total_assets": 106618000000,
    "total_equity": 62634000000,
    "total_debt": 13408000000
  },
  "ratios": {
    "roe": 0.239,
    "roa": 0.141,
    "operating_margin": 0.092,
    "debt_ratio": 0.214,
    "current_ratio": 1.73
  },
  "score": 85,
  "summary": "Strong financial performance with high profitability and manageable debt"
}""" + f"{END_TOKEN}"
    
    return get_json_only_prompt(
        task_description=task,
        schema=FINANCIAL_ANALYSIS_SCHEMA,
        input_data=input_data,
        examples=examples
    )


def get_market_trends_prompt(
    analysis_date: str,
    news_articles: list,
    market_data: Dict[str, Any]
) -> str:
    """
    Generate market trends JSON-only prompt
    
    Args:
        analysis_date: Date of analysis
        news_articles: List of news articles
        market_data: Market data dictionary
        
    Returns:
        JSON-only prompt
    """
    
    task = """
Identify 5-10 key market trends in the EV industry.
Assess significance level and time horizon for each trend.
Provide actionable investment implications.
"""
    
    input_data = {
        "analysis_date": analysis_date,
        "news_count": len(news_articles),
        "market_data_keys": list(market_data.keys()) if market_data else []
    }
    
    examples = """
[EXAMPLE OUTPUT]
{
  "analysis_date": "2024-03-20",
  "trends": [
    {
      "title": "Solid-state battery commercialization accelerating",
      "description": "Multiple manufacturers targeting 2026 production start",
      "significance": "high",
      "time_horizon": "medium-term",
      "evidence": [
        "Toyota announces $10B investment",
        "Samsung SDI pilot line operational"
      ],
      "affected_companies": ["Toyota", "Samsung SDI", "QuantumScape"]
    }
  ],
  "key_insights": [
    "Solid-state batteries could double range by 2027",
    "Current lithium-ion suppliers face disruption risk"
  ],
  "investment_implications": [
    "Accumulate solid-state battery pioneers (QuantumScape, Samsung SDI)",
    "Reduce exposure to legacy lithium-ion pure-plays"
  ]
}""" + f"{END_TOKEN}"
    
    return get_json_only_prompt(
        task_description=task,
        schema=MARKET_TRENDS_SCHEMA,
        input_data=input_data,
        examples=examples
    )


def get_repair_prompt(
    broken_json: str,
    schema: Dict[str, Any],
    error_message: str
) -> str:
    """
    Generate repair prompt for broken JSON
    
    Args:
        broken_json: The broken JSON string
        schema: Expected schema
        error_message: Error from parsing
        
    Returns:
        Repair prompt
    """
    
    schema_str = json.dumps(schema, indent=2)
    
    return f"""
You are a JSON repair tool. Fix the invalid JSON below.

CRITICAL RULES:
1. Output ONLY valid JSON (NO markdown, NO explanations)
2. Remove keys that violate the schema
3. Add missing required keys with null values
4. Fix syntax errors (trailing commas, quotes, braces)
5. Replace NaN/Infinity with null
6. End with: {END_TOKEN}

[EXPECTED SCHEMA]
{schema_str}

[ERROR MESSAGE]
{error_message}

[BROKEN JSON]
{broken_json}

[FIXED JSON]
(Valid JSON only) + {END_TOKEN}
"""


# ========================================
# LLM Configuration Helpers
# ========================================

def get_json_llm_config() -> Dict[str, Any]:
    """
    Get recommended LLM configuration for JSON output
    
    Returns:
        Configuration dict for LLM
    """
    return {
        "temperature": 0.1,  # Low temperature for deterministic output
        "top_p": 0.9,        # Reduce randomness
        "max_tokens": 4000,  # Ensure enough space for complete JSON
        "stop": [END_TOKEN], # Stop at end token
        "presence_penalty": 0.0,
        "frequency_penalty": 0.0
    }


def get_json_system_message() -> str:
    """
    Get system message for JSON-only mode
    
    Returns:
        System message string
    """
    return f"""You are a JSON-only response system. 
You MUST output valid JSON and nothing else.
NO markdown, NO explanations, NO comments.
End all outputs with: {END_TOKEN}"""


if __name__ == "__main__":
    # Test prompt generation
    print("=" * 60)
    print("JSON-Only Prompt Templates Test")
    print("=" * 60)
    
    # Test 1: Risk Analysis
    print("\n[Test 1] Risk Analysis Prompt")
    prompt = get_risk_analysis_prompt(
        company="Tesla",
        topic="Compliance",
        timeframe="2023-2024",
        analysis_text="Tesla faced battery recall in June 2023..."
    )
    print(prompt[:500] + "...")
    
    # Test 2: Financial Analysis
    print("\n[Test 2] Financial Analysis Prompt")
    prompt = get_financial_analysis_prompt(
        company="Samsung SDI",
        financial_data={"revenue": 15000000000, "profit": 1200000000}
    )
    print(prompt[:500] + "...")
    
    # Test 3: LLM Config
    print("\n[Test 3] LLM Configuration")
    config = get_json_llm_config()
    print(json.dumps(config, indent=2))
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

