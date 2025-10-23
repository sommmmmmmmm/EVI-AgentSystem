"""
OpenAI LLM
"""

import openai
import time
from typing import Optional


class OpenAILLM:
    """
    OpenAI API 
    """
    
    def __init__(self, api_key: str):
        try:
            self.client = openai.OpenAI(
                api_key=api_key,
                timeout=30.0,  # 30초 타임아웃
                max_retries=2   # 최대 2번 재시도
            )
            self.model = "gpt-4o"
        except Exception as e:
            print(f"[경고] OpenAI 클라이언트 초기화 실패: {e}")
            self.client = None
            self.model = "gpt-4o"
    
    def call(self, prompt: str,
             system: str = None,
             max_tokens: int = 4000,
             temperature: float = 0.7) -> str:
        """
        OpenAI API 호출 (재시도 로직 포함)

        Args:
            prompt: 사용자 프롬프트
            system: 시스템 프롬프트
            max_tokens: 최대 토큰 수
            temperature: 온도

        Returns:
            API 응답
        """
        if self.client is None:
            print("[ERROR] OpenAI API 키가 설정되지 않았습니다.")
            return self._fallback_response(prompt)

        # 재시도 로직: 최대 3번 시도
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
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

            except openai.RateLimitError as e:
                wait_time = (attempt + 1) * 5  # 5초, 10초, 15초
                print(f"[경고] Rate limit 도달, {wait_time}초 대기 후 재시도... (시도 {attempt + 1}/{max_attempts})")
                if attempt < max_attempts - 1:
                    time.sleep(wait_time)
                else:
                    print(f"[오류] Rate limit 초과: {e}")
                    return self._fallback_response(prompt)

            except openai.APITimeoutError as e:
                wait_time = (attempt + 1) * 3  # 3초, 6초, 9초
                print(f"[경고] API 타임아웃, {wait_time}초 대기 후 재시도... (시도 {attempt + 1}/{max_attempts})")
                if attempt < max_attempts - 1:
                    time.sleep(wait_time)
                else:
                    print(f"[오류] API 타임아웃: {e}")
                    return self._fallback_response(prompt)

            except openai.APIConnectionError as e:
                wait_time = (attempt + 1) * 2  # 2초, 4초, 6초
                print(f"[경고] 네트워크 연결 오류, {wait_time}초 대기 후 재시도... (시도 {attempt + 1}/{max_attempts})")
                if attempt < max_attempts - 1:
                    time.sleep(wait_time)
                else:
                    print(f"[오류] 연결 실패: {e}")
                    return self._fallback_response(prompt)

            except Exception as e:
                print(f"[오류] {e}")
                print(f"[오류] OpenAI API 호출 실패 (시도 {attempt + 1}/{max_attempts}): {e}")
                if attempt < max_attempts - 1:
                    time.sleep(2)
                else:
                    return self._fallback_response(prompt)

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