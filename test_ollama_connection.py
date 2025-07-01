#!/usr/bin/env python3
"""
Test script to verify Ollama connection functionality
"""

import litellm


def test_ollama_connection():
    """Test Ollama connection with the improved format"""

    # Enable debugging
    litellm.set_verbose = True

    # Test parameters matching what the admin form would send
    base_url = "https://ollama.serveur.au"
    model_id = "llama3"

    print(f"Testing Ollama connection to {base_url} with model {model_id}")

    # Use the same format as the fixed admin route
    kwargs = {
        "model": f"ollama/{model_id}",  # LiteLLM requires provider prefix
        "messages": [
            {
                "role": "user",
                "content": "Say 'Connection successful' in exactly 3 words.",
            }
        ],
        "max_tokens": 10,
        "temperature": 0.2,
        "api_base": base_url,  # Use api_base for Ollama
    }

    try:
        print("Making LiteLLM completion request...")
        response = litellm.completion(**kwargs)

        if response and response.choices:
            content = response.choices[0].message.content
            print(f"✅ Success! Response: {content}")
            return True
        else:
            print("❌ No response received")
            return False

    except Exception as e:
        print(f"❌ Connection failed: {e!s}")
        return False


if __name__ == "__main__":
    test_ollama_connection()
