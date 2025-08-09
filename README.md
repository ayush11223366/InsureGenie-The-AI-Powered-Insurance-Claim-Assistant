# InsureGenie - AI-Powered Insurance Claim Assistant

InsureGenie is an intelligent document analysis system that helps users understand insurance policies and answer questions about coverage, terms, and conditions using AI-powered natural language processing.

## Features

- **Document Processing**: Upload and analyze PDF insurance documents
- **AI-Powered Q&A**: Ask questions about policy terms, coverage, and conditions
- **Vector Search**: Intelligent document retrieval using embeddings
- **Web Interface**: User-friendly Streamlit application
- **REST API**: Programmatic access via FastAPI endpoints
- **Multi-format Support**: PDF, DOCX, and EML file support

## Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd InsureGenie-The-AI-Powered-Insurance-Claim-Assistant
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   - Copy `env_template.txt` to `.env`
   - Add your Google Gemini API key:
```env
GOOGLE_API_KEY=your-google-gemini-api-key-here
API_KEY=your-secret-api-key-here
```

## Usage

### Web Application (Streamlit)

Run the interactive web interface:

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

### API Server

Start the REST API server:

```bash
python start_api.py
```

Or directly:

```bash
python api.py
```

The API will be available at `http://localhost:8000`

## Deploying to Heroku

1. Make sure you have a `requirements.txt` and a `Procfile` in your project root.
2. Install the Heroku CLI and log in:
   ```sh
   heroku login
   ```
3. Create a new Heroku app:
   ```sh
   heroku create your-app-name
   ```
4. Set the Python buildpack (optional):
   ```sh
   heroku buildpacks:set heroku/python
   ```
5. Push your code to Heroku:
   ```sh
   git push heroku main
   ```
   (or `git push heroku master` if your branch is named master)
6. Scale the web process:
   ```sh
   heroku ps:scale web=1
   ```
7. Set environment variables (if needed):
   ```sh
   heroku config:set API_KEY=your_api_key GOOGLE_API_KEY=your_gemini_api_key
   ```
8. Open your deployed app:
   ```sh
   heroku open
   ```
   Or visit the URL shown in your terminal (e.g., `https://your-app-name.herokuapp.com/hackrx/run`).

## API Documentation

### POST /hackrx/run

Process insurance policy documents and answer questions.

**Authentication:**
- Bearer token required in Authorization header

**Request Format:**
```json
{
    "documents": "https://example.com/policy.pdf",
    "questions": [
        "What is the grace period for premium payment?",
        "What is the waiting period for pre-existing diseases?"
    ]
}
```

**Response Format:**
```json
{
    "answers": [
        "A grace period of thirty days is provided...",
        "There is a waiting period of thirty-six months..."
    ]
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/hackrx/run" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer your-secret-api-key-here" \
  -d '{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?"
    ]
}'
```

### GET /health

Health check endpoint.

**Response:**
```json
{
    "status": "healthy",
    "service": "InsureGenie API"
}
```

## Testing

Test the API with the provided test script:

```bash
python test_api.py
```

## Project Structure

```
InsureGenie-The-AI-Powered-Insurance-Claim-Assistant/
├── app.py                 # Streamlit web application
├── api.py                 # FastAPI REST server
├── main.py                # Command-line interface
├── start_api.py           # API startup script
├── test_api.py            # API testing script
├── requirements.txt       # Python dependencies
├── env_template.txt       # Environment variables template
├── API_README.md          # Detailed API documentation
├── ingest/
│   └── document_loader.py # Document processing utilities
├── llm/
│   └── gemini_api.py      # Google Gemini API integration
├── retrieval/
│   └── vector_store.py    # Vector search implementation
└── docs/
    └── ICIHLIP22012V012223.pdf  # Sample insurance document
```

## Architecture

The system uses a modular architecture:

1. **Document Loader**: Extracts text from various document formats
2. **Vector Store**: Stores document embeddings for semantic search
3. **LLM Integration**: Uses Google's Gemini API for embeddings and Q&A
4. **Web Interface**: Streamlit-based user interface
5. **REST API**: FastAPI-based programmatic interface

## Security

- API key authentication for REST endpoints
- Environment variable configuration
- Temporary file cleanup
- Input validation and sanitization

## Error Handling

The system provides comprehensive error handling:

- Invalid document URLs
- Unsupported file formats
- API key validation
- Network connectivity issues
- Document processing errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed information
