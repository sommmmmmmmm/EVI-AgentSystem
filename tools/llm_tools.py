"""
OpenAI LLM 
"""

import openai
from typing import Optional


class OpenAILLM:
    """
    OpenAI API 
    """
    
    def __init__(self, api_key: str):
        try:
            self.client = openai.OpenAI(api_key=api_key)
            self.model = "gpt-4o"
        except Exception as e:
            print(f"[] OpenAI   : {e}")
            self.client = None
            self.model = "gpt-4o"
    
    def call(self, prompt: str, 
             system: str = None,
             max_tokens: int = 4000,
             temperature: float = 0.7) -> str:
        """
        OpenAI API 
        
        Args:
            prompt: 
            system:  
            max_tokens:  
            temperature: 
        
        Returns:
            API  
        """
        try:
            if self.client is None:
                print("[ERROR] OpenAI API 키가 설정되지 않았습니다.")
                return self._fallback_response(prompt)

            messages = []

            if system:
                messages.append({"role": "system", "content": system})

            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"[] OpenAI API  : {e}")
            # API     
            return self._fallback_response(prompt)
    
    def _fallback_response(self, prompt: str) -> str:
        """API 실패 시 에러 메시지 반환"""
        return f"[ERROR] OpenAI API 키가 설정되지 않았습니다. '{prompt[:50]}...' 요청을 처리할 수 없습니다."
    
    def generate(self, prompt: str) -> str:
        """
        generate   (Risk Assessment Agent )
        """
        return self.call(prompt)
    
    def generate_analysis(self, data: str, analysis_type: str = "general") -> str:
        """
            
        
        Args:
            data:  
            analysis_type:  
        
        Returns:
             
        """
        system_prompts = {
            "market_trend": "    .        .",
            "financial": "   .       .",
            "risk": "   .      .",
            "supplier": "   .      .",
            "general": "   .     ."
        }
        
        system = system_prompts.get(analysis_type, system_prompts["general"])
        
        prompt = f"""
  :

{data}

    .
"""
        
        return self.call(prompt, system=system, max_tokens=3000)