import requests
import time

# Set your public ngrok URL here for webhook testing
url = "https://c879e7ce17b6.ngrok-free.app//hackrx/run"
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": "Bearer 16946ba51d27b2876a0d08882d9c32b7e5faa66ae63f9f94fa85f34e3cb3c3f8"
}

print("=== Webhook Performance Test ===")
print(f"Testing URL: {url}")
print()

doc_url = input("Enter the document URL: ")
questions_input = input("Enter your questions (comma-separated): ")
questions = [q.strip() for q in questions_input.split(',') if q.strip()]

data = {
    "documents": doc_url,
    "questions": questions
}

print(f"\nSending request with {len(questions)} questions...")
print("=" * 50)

start_time = time.time()
try:
    # Set a reasonable timeout for the entire request
    response = requests.post(url, headers=headers, json=data, timeout=60)
    total_time = time.time() - start_time
    
    print(f"Status Code: {response.status_code}")
    print(f"Total Response Time: {total_time:.2f} seconds")
    print(f"Average Time per Question: {total_time/len(questions):.2f} seconds")
    print()
    
    try:
        result = response.json()
        print("Response:")
        for i, answer in enumerate(result.get('answers', []), 1):
            print(f"Q{i}: {answer[:100]}{'...' if len(answer) > 100 else ''}")
    except Exception as e:
        print("Raw Response:", response.text)
        
except requests.exceptions.Timeout:
    print("❌ Request timed out after 60 seconds")
    print("This indicates the API is too slow for the evaluation system")
except Exception as e:
    print(f"❌ Error: {e}")
    print("This indicates a connection or server issue")

print("\n" + "=" * 50)
if total_time < 30:
    print("✅ Response time is good for evaluation")
elif total_time < 60:
    print("⚠️  Response time is borderline - may need further optimization")
else:
    print("❌ Response time is too slow for evaluation")
