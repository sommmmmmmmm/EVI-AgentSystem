"""
Robust JSON Parser for LLM Outputs

Handles common LLM JSON output issues:
- Markdown code fences (```)
- Natural language mixed with JSON
- Trailing commas
- NaN/Infinity values
- Incomplete/truncated output
- BOM and zero-width characters
"""

import json
import re
from typing import Dict, Any, Optional, Tuple
from jsonschema import validate, ValidationError, Draft7Validator


# End token to mark complete JSON output
END_TOKEN = "<END_OF_JSON>"


class JSONParseError(Exception):
    """Custom exception for JSON parsing failures"""
    pass


def extract_json(text: str) -> str:
    """
    Extract JSON from LLM output that may contain extra text
    
    Args:
        text: Raw LLM output
        
    Returns:
        Cleaned JSON string
    """
    if not text or not text.strip():
        raise JSONParseError("Empty or whitespace-only text")
    
    # 1) Extract up to END_TOKEN if present
    if END_TOKEN in text:
        text = text.split(END_TOKEN)[0]
        print(f"   [JSON] Found END_TOKEN, extracted {len(text)} chars")
    
    # 2) Remove markdown code fences
    text = text.strip()
    
    # Remove ```json ... ``` or ``` ... ```
    if text.startswith("```"):
        # Find closing ```
        lines = text.split("\n")
        if lines[0].strip() in ["```", "```json", "```JSON"]:
            lines = lines[1:]  # Remove opening fence
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]  # Remove closing fence
        text = "\n".join(lines)
    
    text = text.strip()
    
    # 3) Remove any leading/trailing backticks
    text = text.strip("`").strip()
    
    # 4) Extract JSON object/array (outermost braces/brackets)
    # Try to find the main JSON structure
    
    # Look for JSON object {...}
    match = re.search(r'\{.*\}', text, flags=re.DOTALL)
    if match:
        json_str = match.group(0)
        print(f"   [JSON] Extracted JSON object ({len(json_str)} chars)")
        return json_str
    
    # Look for JSON array [...]
    match = re.search(r'\[.*\]', text, flags=re.DOTALL)
    if match:
        json_str = match.group(0)
        print(f"   [JSON] Extracted JSON array ({len(json_str)} chars)")
        return json_str
    
    # If no match found, return original
    print(f"   [WARNING] No JSON structure found, returning original text")
    return text


def quick_fix_json(s: str) -> str:
    """
    Apply quick fixes to common JSON issues
    
    Args:
        s: JSON string with potential issues
        
    Returns:
        Fixed JSON string
    """
    # Remove BOM (Byte Order Mark)
    s = s.replace("\ufeff", "")
    
    # Remove zero-width characters
    s = s.replace("\u200b", "")  # Zero-width space
    s = s.replace("\u200c", "")  # Zero-width non-joiner
    s = s.replace("\u200d", "")  # Zero-width joiner
    
    # Remove 'JSON:' prefix
    s = re.sub(r'^\s*JSON\s*:\s*', '', s, flags=re.IGNORECASE)
    
    # Remove trailing commas before } or ]
    # Example: {"key": "value",} -> {"key": "value"}
    s = re.sub(r',\s*([}\]])', r'\1', s)
    
    # Replace NaN, Infinity with null
    s = re.sub(r'\bNaN\b', 'null', s)
    s = re.sub(r'\bInfinity\b', 'null', s)
    s = re.sub(r'-Infinity\b', 'null', s)
    
    # Remove single-line comments (// ...)
    s = re.sub(r'//[^\n]*', '', s)
    
    # Remove multi-line comments (/* ... */)
    s = re.sub(r'/\*.*?\*/', '', s, flags=re.DOTALL)
    
    return s.strip()


def parse_and_validate(
    json_str: str, 
    schema: Optional[Dict[str, Any]] = None,
    repair_attempts: int = 2
) -> Tuple[Dict[str, Any], bool]:
    """
    Parse JSON and validate against schema with automatic repair
    
    Args:
        json_str: JSON string to parse
        schema: JSON schema for validation (optional)
        repair_attempts: Number of repair attempts (default: 2)
        
    Returns:
        Tuple of (parsed_object, was_repaired)
        
    Raises:
        JSONParseError: If parsing fails after all repair attempts
    """
    original_str = json_str
    was_repaired = False
    
    # First attempt: Parse as-is
    try:
        obj = json.loads(json_str)
        
        # Validate against schema if provided
        if schema:
            validate(obj, schema)
        
        print(f"   [JSON] ✓ Parsed successfully ({len(json_str)} chars)")
        return obj, False
        
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"   [JSON] ⚠ Initial parse failed: {type(e).__name__}: {str(e)[:100]}")
        
        # Attempt quick fixes
        for attempt in range(repair_attempts):
            try:
                print(f"   [JSON] Repair attempt {attempt + 1}/{repair_attempts}...")
                
                # Apply quick fixes
                fixed_str = quick_fix_json(json_str)
                
                # Try parsing fixed string
                obj = json.loads(fixed_str)
                
                # Validate against schema if provided
                if schema:
                    validate(obj, schema)
                
                print(f"   [JSON] ✓ Repaired and parsed successfully")
                was_repaired = True
                return obj, was_repaired
                
            except (json.JSONDecodeError, ValidationError) as repair_error:
                print(f"   [JSON] Repair attempt {attempt + 1} failed: {type(repair_error).__name__}")
                
                # On last attempt, raise the error
                if attempt == repair_attempts - 1:
                    error_msg = f"JSON parsing failed after {repair_attempts} repair attempts"
                    error_detail = f"{type(e).__name__}: {str(e)}"
                    print(f"   [JSON] ❌ {error_msg}")
                    print(f"   [JSON] Original error: {error_detail}")
                    print(f"   [JSON] String length: {len(original_str)}")
                    print(f"   [JSON] First 200 chars: {original_str[:200]}")
                    raise JSONParseError(f"{error_msg}\n{error_detail}")


def create_fallback_response(
    company: str,
    topic: str,
    timeframe: str,
    raw_text: str,
    error_msg: str
) -> Dict[str, Any]:
    """
    Create fallback response when JSON parsing completely fails
    
    Args:
        company: Company name
        topic: Analysis topic
        timeframe: Time period
        raw_text: Original raw text
        error_msg: Error message
        
    Returns:
        Minimal valid response structure
    """
    print(f"   [JSON] Creating fallback response for {company}")
    
    return {
        "company": company,
        "topic": topic,
        "timeframe": timeframe,
        "incidents": [],
        "overall_risk_score": None,
        "summary": f"JSON parsing failed: {error_msg}. Raw text length: {len(raw_text)}"
    }


def get_json_repair_prompt(
    broken_json: str,
    schema: Dict[str, Any],
    error_message: str
) -> str:
    """
    Generate prompt to ask LLM to repair broken JSON
    
    Args:
        broken_json: The broken JSON string
        schema: Expected JSON schema
        error_message: The error message from parsing
        
    Returns:
        Repair prompt for LLM
    """
    return f"""
You are a JSON repair tool. Fix the following JSON string to make it valid.

CRITICAL RULES:
- Output ONLY valid JSON (no markdown, no explanations, no comments)
- Remove any keys that violate the schema
- Add missing required keys with null values
- Fix syntax errors (trailing commas, quotes, etc.)
- End output with: {END_TOKEN}

[Expected Schema]
{json.dumps(schema, indent=2)}

[Error Message]
{error_message}

[Broken JSON to Fix]
{broken_json}

[Output]
(Valid JSON only) + {END_TOKEN}
"""


def parse_llm_json(
    llm_output: str,
    schema: Optional[Dict[str, Any]] = None,
    fallback_data: Optional[Dict[str, Any]] = None,
    repair_attempts: int = 2
) -> Dict[str, Any]:
    """
    Main function to parse JSON from LLM output with full error handling
    
    Args:
        llm_output: Raw output from LLM
        schema: JSON schema for validation (optional)
        fallback_data: Data to use for fallback response (optional)
        repair_attempts: Number of automatic repair attempts
        
    Returns:
        Parsed JSON object (or fallback if parsing fails)
    """
    try:
        # Step 1: Extract JSON from mixed content
        json_str = extract_json(llm_output)
        
        # Step 2: Parse and validate with automatic repair
        obj, was_repaired = parse_and_validate(
            json_str, 
            schema=schema,
            repair_attempts=repair_attempts
        )
        
        if was_repaired:
            print(f"   [JSON] ⚠ Output was repaired (may have data loss)")
        
        return obj
        
    except (JSONParseError, Exception) as e:
        error_msg = str(e)
        print(f"   [JSON] ❌ Complete parsing failure: {error_msg}")
        
        # Return fallback if provided
        if fallback_data:
            return create_fallback_response(
                company=fallback_data.get('company', 'Unknown'),
                topic=fallback_data.get('topic', 'Unknown'),
                timeframe=fallback_data.get('timeframe', 'Unknown'),
                raw_text=llm_output,
                error_msg=error_msg
            )
        else:
            # Re-raise if no fallback
            raise


def validate_json_schema(obj: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate JSON object against schema and return detailed error
    
    Args:
        obj: JSON object to validate
        schema: JSON schema
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        validate(obj, schema)
        return True, None
    except ValidationError as e:
        error_path = " -> ".join(str(p) for p in e.path) if e.path else "root"
        error_msg = f"Validation error at {error_path}: {e.message}"
        return False, error_msg


# Diagnostic helper
def diagnose_json_error(text: str) -> str:
    """
    Diagnose common JSON parsing issues
    
    Args:
        text: String that failed to parse
        
    Returns:
        Diagnostic message
    """
    issues = []
    
    if not text or not text.strip():
        issues.append("⚠ Empty or whitespace-only input")
    
    if text.startswith("\ufeff"):
        issues.append("⚠ BOM (Byte Order Mark) detected")
    
    if "```" in text:
        issues.append("⚠ Markdown code fences detected")
    
    if re.search(r',\s*[}\]]', text):
        issues.append("⚠ Trailing commas detected")
    
    if re.search(r'\bNaN\b|\bInfinity\b', text):
        issues.append("⚠ NaN/Infinity values detected")
    
    if re.search(r'//|/\*', text):
        issues.append("⚠ Comments detected")
    
    # Check for unmatched braces
    open_braces = text.count('{')
    close_braces = text.count('}')
    if open_braces != close_braces:
        issues.append(f"⚠ Unmatched braces: {open_braces} {{ vs {close_braces} }}")
    
    if not issues:
        issues.append("✓ No obvious issues detected (may be complex syntax error)")
    
    return "\n".join(issues)


if __name__ == "__main__":
    # Test cases
    print("=" * 60)
    print("JSON Parser Test Cases")
    print("=" * 60)
    
    # Test 1: Clean JSON
    test1 = '{"name": "Tesla", "score": 85}'
    print("\n[Test 1] Clean JSON")
    result = parse_llm_json(test1)
    print(f"Result: {result}")
    
    # Test 2: JSON with markdown
    test2 = '''```json
{
    "name": "Tesla",
    "score": 85
}
```'''
    print("\n[Test 2] JSON with markdown")
    result = parse_llm_json(test2)
    print(f"Result: {result}")
    
    # Test 3: JSON with trailing comma
    test3 = '{"name": "Tesla", "score": 85,}'
    print("\n[Test 3] JSON with trailing comma")
    result = parse_llm_json(test3)
    print(f"Result: {result}")
    
    # Test 4: JSON with NaN
    test4 = '{"name": "Tesla", "score": NaN}'
    print("\n[Test 4] JSON with NaN")
    result = parse_llm_json(test4)
    print(f"Result: {result}")
    
    # Test 5: JSON with END_TOKEN
    test5 = '{"name": "Tesla", "score": 85}<END_OF_JSON>Extra text here'
    print("\n[Test 5] JSON with END_TOKEN")
    result = parse_llm_json(test5)
    print(f"Result: {result}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

