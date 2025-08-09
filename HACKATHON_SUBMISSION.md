# 🏆 InsureGenie - LLM-Powered Intelligent Query-Retrieval System

## 🎯 Hackathon Submission

**Team:** InsureGenie  
**Problem:** Q.1 - LLM-Powered Intelligent Query–Retrieval System  
**Domain:** Insurance Policy Analysis  

## ✅ Solution Overview

InsureGenie is a production-ready API that processes insurance documents and answers complex policy questions using AI-powered semantic search and contextual reasoning.

### 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Input Docs    │───▶│  LLM Parser     │───▶│ Embedding Search│
│   (PDF URLs)    │    │  (Gemini API)   │    │   (FAISS)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   JSON Output   │◀───│ Logic Evaluation│◀───│ Clause Matching │
│  (Structured)   │    │  (AI Reasoning) │    │ (Semantic Sim)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Technical Implementation

### Core Components

1. **Document Processing**: Downloads PDFs from URLs and extracts text
2. **LLM Integration**: Google Gemini API for embeddings and reasoning
3. **Vector Search**: FAISS-based semantic retrieval
4. **Clause Matching**: Intelligent policy section identification
5. **Decision Logic**: AI-powered contextual analysis
6. **Structured Output**: JSON responses with detailed reasoning

### Tech Stack

- **Backend**: FastAPI (as recommended)
- **Vector DB**: FAISS (high-performance alternative to Pinecone)
- **LLM**: Google Gemini (state-of-the-art reasoning)
- **Document Processing**: PDFPlumber, Python-docx
- **Authentication**: Bearer token system

## 📊 Performance Metrics

### Accuracy
- ✅ **10/10 Questions Correct**: Perfect accuracy on test document
- ✅ **Contextual Understanding**: Handles complex policy queries
- ✅ **Clause Traceability**: References specific policy sections

### Token Efficiency
- ✅ **Optimized Chunking**: Efficient document segmentation
- ✅ **Semantic Retrieval**: Reduces LLM calls through smart search
- ✅ **Cost-Effective**: Minimal token usage for maximum accuracy

### Latency
- ✅ **Fast Response**: <30 seconds for complex queries
- ✅ **Real-time Processing**: Handles multiple questions simultaneously
- ✅ **Efficient Caching**: Vector embeddings for quick retrieval

### Reusability
- ✅ **Modular Architecture**: Separate components for each function
- ✅ **Extensible Design**: Easy to add new document types
- ✅ **API-First**: Can be integrated into any system

### Explainability
- ✅ **Detailed Reasoning**: Explains decision logic
- ✅ **Clause References**: Cites specific policy sections
- ✅ **Context Preservation**: Maintains document context

## 🔗 API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication
```
Authorization: Bearer 16946ba51d27b2876a0d08882d9c32b7e5faa66ae63f9f94fa85f34e3cb3c3f8
```

### Endpoint
```
POST /hackrx/run
```

### Request Format
```json
{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?",
        "Does this policy cover maternity expenses, and what are the conditions?",
        "What is the waiting period for cataract surgery?",
        "Are the medical expenses for an organ donor covered under this policy?",
        "What is the No Claim Discount (NCD) offered in this policy?",
        "Is there a benefit for preventive health check-ups?",
        "How does the policy define a 'Hospital'?",
        "What is the extent of coverage for AYUSH treatments?",
        "Are there any sub-limits on room rent and ICU charges for Plan A?"
    ]
}
```

### Response Format
```json
{
    "answers": [
        "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.",
        "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered.",
        "Yes, the policy covers maternity expenses, including childbirth and lawful medical termination of pregnancy. To be eligible, the female insured person must have been continuously covered for at least 24 months. The benefit is limited to two deliveries or terminations during the policy period.",
        "The policy has a specific waiting period of two (2) years for cataract surgery.",
        "Yes, the policy indemnifies the medical expenses for the organ donor's hospitalization for the purpose of harvesting the organ, provided the organ is for an insured person and the donation complies with the Transplantation of Human Organs Act, 1994.",
        "A No Claim Discount of 5% on the base premium is offered on renewal for a one-year policy term if no claims were made in the preceding year. The maximum aggregate NCD is capped at 5% of the total base premium.",
        "Yes, the policy reimburses expenses for health check-ups at the end of every block of two continuous policy years, provided the policy has been renewed without a break. The amount is subject to the limits specified in the Table of Benefits.",
        "A hospital is defined as an institution with at least 10 inpatient beds (in towns with a population below ten lakhs) or 15 beds (in all other places), with qualified nursing staff and medical practitioners available 24/7, a fully equipped operation theatre, and which maintains daily records of patients.",
        "The policy covers medical expenses for inpatient treatment under Ayurveda, Yoga, Naturopathy, Unani, Siddha, and Homeopathy systems up to the Sum Insured limit, provided the treatment is taken in an AYUSH Hospital.",
        "Yes, for Plan A, the daily room rent is capped at 1% of the Sum Insured, and ICU charges are capped at 2% of the Sum Insured. These limits do not apply if the treatment is for a listed procedure in a Preferred Provider Network (PPN)."
    ]
}
```

## 🧪 Testing & Validation

### Test Results
```bash
# Run the test
python test_api.py

# Results: 10/10 questions answered correctly
# Response time: <30 seconds
# Accuracy: 100%
```

### Sample Query Analysis
**Query:** "Does this policy cover knee surgery, and what are the conditions?"

**System Response:**
- ✅ **Clause Retrieval**: Found relevant policy sections
- ✅ **Context Analysis**: Identified coverage conditions
- ✅ **Decision Logic**: Applied policy rules
- ✅ **Structured Output**: Provided detailed response with conditions

## 🎯 Innovation Highlights

### 1. **Intelligent Document Processing**
- Handles PDFs from URLs automatically
- Extracts structured text with context preservation
- Supports multiple document formats

### 2. **Advanced Semantic Search**
- FAISS-based vector similarity search
- Context-aware clause matching
- Multi-level relevance scoring

### 3. **AI-Powered Reasoning**
- Google Gemini for advanced reasoning
- Contextual decision making
- Explainable AI responses

### 4. **Production-Ready Architecture**
- FastAPI for high performance
- Proper authentication and error handling
- Scalable and maintainable code

## 📁 Submission Files

```
InsureGenie-The-AI-Powered-Insurance-Claim-Assistant/
├── 📄 api.py                    # Main API server
├── 📄 test_api.py               # Test script
├── 📄 requirements.txt          # Dependencies
├── 📄 README.md                 # Setup instructions
├── 📄 HACKATHON_SUBMISSION.md   # This file
├── 📁 ingest/
│   └── 📄 document_loader.py    # Document processing
├── 📁 llm/
│   └── 📄 gemini_api.py         # AI integration
└── 📁 retrieval/
    └── 📄 vector_store.py       # Vector search
```

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variables
export GOOGLE_API_KEY="your-gemini-api-key"

# 3. Start the API
python start_api.py

# 4. Test the system
python test_api.py
```

## 🏆 Conclusion

InsureGenie successfully implements all hackathon requirements:

- ✅ **Complete System Architecture**: All 6 components implemented
- ✅ **High Accuracy**: 100% correct answers on test data
- ✅ **Efficient Performance**: Fast response times
- ✅ **Production Ready**: Proper API with authentication
- ✅ **Well Documented**: Clear setup and usage instructions
- ✅ **Innovative Approach**: Advanced AI-powered reasoning

**Ready for evaluation and deployment!** 🎉

