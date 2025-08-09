import requests
import time
import json

# Test locally first
url = "http://localhost:8000/hackrx/run"

headers = {
  "Content-Type": "application/json",
  "Accept": "application/json",
  "Authorization": "Bearer 16946ba51d27b2876a0d08882d9c32b7e5faa66ae63f9f94fa85f34e3cb3c3f8",
  "X-Answer-Mode": "compose"
}

# Use a non-sample question to exercise retrieval+LLM path
data = {
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        
        "Who is eligible to be covered under this policy?",
        "What is the process for policy renewal?",
        "How does the policy define 'Reasonable and Customary Charges'?",
        "What is the waiting period for specific diseases or treatments?",
        "Are ambulance charges covered under this policy?",
        "What is the process for claim settlement?",
        "Are there any co-payment requirements in this policy?",
        "What is the definition of 'Network Provider'?",
        "How are sub-limits applied to different treatments?",
        "What is the policy's stance on coverage for alternative treatments like Ayurveda or Homeopathy?"
    ]
}

print("=== Testing Local API ===")
print(f"URL: {url}")
print("=" * 40)

start_time = time.time()

try:
    print("Sending request...")
    response = requests.post(url, headers=headers, json=data, timeout=45)
    total_time = time.time() - start_time
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Time: {total_time:.2f} seconds")
    
    try:
        result = response.json()
        print("Full JSON Response:")
        print(json.dumps(result, indent=2))
        if result.get('answers'):
            print("\nAnswer:")
            print(result['answers'][0])
    except Exception:
        print("Raw Response:")
        print(response.text)
        
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\nIf local test works, the issue is with ngrok connection.")
