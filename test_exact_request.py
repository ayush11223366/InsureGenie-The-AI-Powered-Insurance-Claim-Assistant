import requests
import time
import json

# Your webhook URL
url = "https://712ab720d661.ngrok-free.app/hackrx/run"

# Headers exactly as the hackathon system will send
headers = {
  "Content-Type": "application/json",
  "Accept": "application/json",
  "Authorization": "Bearer 16946ba51d27b2876a0d08882d9c32b7e5faa66ae63f9f94fa85f34e3cb3c3f8",
  "X-Answer-Mode": "compose"
}

# Request body exactly as the hackathon system will send
data = {
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
       
       
        "Who are considered insured persons under this policy?",
        "What is the definition of 'Hospitalisation' in this policy?",
        "What is the coverage for Day Care Treatment?",
        "How does the policy define 'Domiciliary Hospitalisation'?",
        "What is the process for claim intimation and documentation?",
        "Are pre and post-hospitalisation expenses covered? If yes, for how long?",
        "What is the policy's stance on coverage for HIV/AIDS?",
        "What are the exclusions related to maternity benefits?",
        "How is the Sum Insured determined for a family floater plan?",
        "What is the grievance redressal mechanism provided in the policy?"
    ]
}

print("=== Testing Exact Hackathon Request Format ===")
print(f"URL: {url}")
print(f"Questions: {len(data['questions'])}")
print("=" * 60)

start_time = time.time()
total_time = 0

try:
    print("Sending request...")
    response = requests.post(url, headers=headers, json=data, timeout=60)
    total_time = time.time() - start_time
    
    print(f"Status Code: {response.status_code}")
    print(f"Total Response Time: {total_time:.2f} seconds")
    print(f"Average Time per Question: {total_time/len(data['questions']):.2f} seconds")
    print()
    
    if response.status_code == 200:
        try:
            result = response.json()
            print("✅ SUCCESS: Received valid JSON response")
            print(f"Number of answers: {len(result.get('answers', []))}")
            print()
            
            # Display first few answers
            for i, answer in enumerate(result.get('answers', [])[:3], 1):
                print(f"Answer {i}: {answer[:150]}{'...' if len(answer) > 150 else ''}")
            
            if len(result.get('answers', [])) > 3:
                print(f"... and {len(result.get('answers', [])) - 3} more answers")
                
        except json.JSONDecodeError:
            print("❌ ERROR: Response is not valid JSON")
            print("Raw response:", response.text[:500])
    else:
        print(f"❌ ERROR: HTTP {response.status_code}")
        print("Response:", response.text)
        
except requests.exceptions.Timeout:
    total_time = time.time() - start_time
    print("❌ TIMEOUT: Request took longer than 60 seconds")
    print(f"Time elapsed: {total_time:.2f} seconds")
    print("This indicates the API is too slow for evaluation")
except Exception as e:
    total_time = time.time() - start_time
    print(f"❌ ERROR: {e}")
    print(f"Time elapsed: {total_time:.2f} seconds")

print("\n" + "=" * 60)
if total_time < 30:
    print("✅ EXCELLENT: Response time is good for evaluation")
elif total_time < 60:
    print("⚠️  WARNING: Response time is borderline")
else:
    print("❌ CRITICAL: Response time is too slow for evaluation")

print("\nYour webhook is ready for submission if all tests pass!")
