#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from openrouter_api import OpenRouterAPI

def test_openrouter():
    try:
        api = OpenRouterAPI()
        print(f"✓ OpenRouter API initialized successfully")
        print(f"✓ Using API key: {api.api_key[:8]}...")
        
        messages = [{"role": "user", "content": "Say 'Hello from OpenRouter!' in exactly 5 words."}]
        
        result = api.chat_with_fallback(messages, max_tokens=50, temperature=0.1)
        
        if result['success']:
            print(f"✓ API call successful!")
            print(f"✓ Model used: {result['model']}")
            print(f"✓ Response: {result['response']}")
            print(f"✓ Tokens used: {result['usage']['total_tokens']}")
            return True
        else:
            print(f"✗ API call failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing OpenRouter API integration...")
    success = test_openrouter()
    sys.exit(0 if success else 1)