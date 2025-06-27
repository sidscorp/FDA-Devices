import requests
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

class OpenRouterAPI:
    def __init__(self):
        self.api_key = self._load_api_key()
        self.base_url = "https://openrouter.ai/api/v1"
        self.fallback_models = [
            'meta-llama/llama-3.1-8b-instruct:free',
            'google/gemma-2-9b-it:free',
            'mistralai/mistral-7b-instruct:free'
        ]
        self.preferred_models = [
            'openai/gpt-4o-mini',
            'anthropic/claude-3-haiku',
            'google/gemini-flash-1.5'
        ]

    def _load_api_key(self) -> str:
        api_key = os.getenv('OPENROUTER_API_KEY')
        if api_key:
            return api_key
            
        env_files = [
            Path.home() / "api_keys.env",
            Path(__file__).parent / "api_keys.env",
            Path(__file__).parent / ".env"
        ]
        
        for env_file in env_files:
            if env_file.exists():
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.startswith('openrouter_api_key=') or line.startswith('OPENROUTER_API_KEY='):
                            return line.split('=', 1)[1].strip()
        
        raise ValueError("OpenRouter API key not found. Set OPENROUTER_API_KEY environment variable or add to api_keys.env file.")

    def chat_completion(self, model_id: str, messages: List[Dict], max_tokens: int = 1000, temperature: float = 0.7) -> Dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model_id,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                usage = result.get('usage', {})
                
                return {
                    'success': True,
                    'response': content,
                    'model': model_id,
                    'usage': {
                        'prompt_tokens': usage.get('prompt_tokens', 0),
                        'completion_tokens': usage.get('completion_tokens', 0),
                        'total_tokens': usage.get('total_tokens', 0)
                    }
                }
            else:
                return {
                    'success': False,
                    'error': 'No response content',
                    'model': model_id
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Request failed: {str(e)}',
                'model': model_id
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'model': model_id
            }

    def get_best_model(self, preferred_free: bool = True) -> str:
        models_to_try = self.fallback_models if preferred_free else self.preferred_models
        return models_to_try[0]

    def chat_with_fallback(self, messages: List[Dict], max_tokens: int = 1000, temperature: float = 0.7, preferred_free: bool = True) -> Dict:
        models_to_try = (self.fallback_models + self.preferred_models) if preferred_free else (self.preferred_models + self.fallback_models)
        
        for model in models_to_try:
            result = self.chat_completion(model, messages, max_tokens, temperature)
            if result['success']:
                return result
                
        return {
            'success': False,
            'error': 'All models failed',
            'model': 'none'
        }