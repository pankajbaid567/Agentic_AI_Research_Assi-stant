import os
import json
import re
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from langchain_community.llms import Ollama

# Load environment variables
load_dotenv()

def call_hf_inference(prompt: str, model: str = "mistralai/Mistral-7B-Instructv0.2", max_tokens: int = 512) -> str:
    try:
        hf_token = os.environ.get("HF_API_TOKEN")
        client = InferenceClient(model=model, token=hf_token, timeout=30)
        
        response = client.text_generation(
            prompt,
            max_new_tokens=max_tokens
        )
        return response
    except Exception as e:
        print(f"Error in call_hf_inference: {e}")
        raise

def call_ollama(prompt: str, model: str = "llama3.2") -> str:
    try:
        llm = Ollama(model=model)
        response = llm.invoke(prompt)
        return response
    except Exception as e:
        print(f"Error in call_ollama: {e}")
        raise

def call_llm_with_fallback(prompt: str) -> tuple[str, str]:
    try:
        response_text = call_hf_inference(prompt)
        return response_text, "hf_inference"
    except Exception as e:
        print(f"HF Inference failed: {e}. Falling back to Ollama.")
        try:
            response_text = call_ollama(prompt)
            return response_text, "ollama"
        except Exception as e2:
            print(f"Ollama fallback failed: {e2}")
            return "", "extractive_fallback"

def safe_parse_json(text: str) -> dict | None:
    try:
        # Strip markdown code fences (```json ... ```)
        pattern = r"```(?:json)?\s*(.*?)\s*```"
        match = re.search(pattern, text, re.DOTALL)
        
        if match:
            text_to_parse = match.group(1)
        else:
            text_to_parse = text.strip()
            
        return json.loads(text_to_parse)
    except Exception as e:
        print(f"Error in safe_parse_json: {e}")
        return None
