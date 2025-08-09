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
        
        "What is the definition of 'Accident' as per the National Parivar Mediclaim Plus Policy?",
        "How does the policy define an 'AYUSH Hospital'?",
        "What is the procedure if there is a break in policy due to non-payment of premium?",
        "Are congenital anomalies covered under this policy? If yes, what types?",
        "What is the meaning of 'Co-payment' in this policy?",
        "Does the policy provide a cashless facility, and how is it availed?",
        "What are the minimum requirements for a Day Care Centre under this policy?",
        "Who is eligible to be an AYUSH Medical Practitioner as per the policy?",
        "What is the process for altering the contract or policy schedule?",
        "Are there any exclusions listed in the policy, and where can they be found?"
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
