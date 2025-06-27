# Teams RAG Chatbot

A Microsoft Teams plugin with RAG (Retrieval-Augmented Generation) backend for task input, retrieval, and updates.

## Project Structure

```
teams-rag-chatbot/
├── app/                 # Main application code
│   ├── __init__.py     # Package initialization
│   ├── chat_engine.py  # Chat processing logic
│   ├── config.py       # Configuration settings
│   ├── document_loader.py  # Document processing
│   ├── embedding.py    # Embedding generation
│   ├── guardrails.py   # Input validation and security rules
│   ├── main.py         # FastAPI application initialization
│   └── pinecone_index.py  # Vector store operations
├── docs/               # Documentation files
├── scripts/            # Helper scripts
├── tests/              # Test files
├── .env                # Environment configuration (DO NOT COMMIT)
├── .env.example        # Template for environment variables
├── .gitignore          # Git ignore rules
├── LICENSE             # Project license
├── pyproject.toml      # Project configuration and dependencies
├── clear_index.py      # Script to clear search indexes
└── run_local.py        # Script to run the application locally
```

## Key Components

- `app/guardrails.py`: Implements security measures including:
  - Sensitive data blocking (salary, SSN, passwords, etc.)
  - General-purpose AI pattern prevention
  - Intent drift detection
  - TODO: Add LLM-based rules for prompt injection prevention

- `app/main.py`: FastAPI application initialization and configuration

- `app/chat_engine.py`: Core chat processing logic including:
  - Query processing
  - Response generation
  - Context management

- `app/document_loader.py`: Document processing utilities for:
  - PDF extraction
  - DOCX processing
  - TXT file handling
  - Excel file processing

- `app/embedding.py`: Handles text embedding generation using:
  - OpenAI embeddings
  - Vector store integration
  - Chunk processing

- `app/pinecone_index.py`: Vector store operations including:
  - Index management
  - Similarity search
  - Document storage

- `app/config.py`: Contains configuration settings for:
  - API keys
  - Model settings
  - Vector store configuration

- `run_local.py`: Interactive development script that:
  - Provides a local testing interface
  - Demonstrates query/response flow
  - Allows easy testing without Teams integration

- `clear_index.py`: Utility script for:
  - Resetting vector store
  - Clearing document embeddings
  - Maintaining clean state for development

- `scripts/utils.py`: Helper functions for:
  - Document chunking
  - File type handling
  - Text processing utilities

## Potential Improvements

1. **Security Enhancements**:
   - Implement LLM-based prompt injection detection
   - Add rate limiting
   - Improve sensitive data detection using NLP
   - Add audit logging

2. **Performance Optimization**:
   - Implement caching for frequently accessed documents
   - Add batch processing for document ingestion
   - Optimize vector store operations
   - Implement request queuing

3. **Feature Additions**:
   - Add support for more document types
   - Implement version control for documents
   - Add document metadata management
   - Implement user-specific document access control

4. **Testing Improvements**:
   - Add more integration tests
   - Implement end-to-end testing
   - Add performance benchmarks
   - Implement fuzz testing for security

5. **Documentation**:
   - Add API documentation
   - Create deployment guides
   - Add security best practices
   - Document configuration options

6. **Monitoring**:
   - Add request/response logging
   - Implement error tracking
   - Add performance metrics
   - Create health check endpoints

## Setup and Requirements

This project requires Python 3.12 or higher. The main dependencies include:
- FastAPI: Web framework
- OpenAI: Integration with OpenAI services
- LangChain: Framework for building RAG applications
- Various data processing libraries (pandas, python-docx, pypdf)

## Development

1. Create a virtual environment and activate it
2. Install dependencies using `pip install -e .`
3. Copy `.env.example` to `.env` and configure your environment variables
4. Run tests using `pytest`
5. Run the application locally using `python run_local.py`

## Security

- Never commit `.env` file
- Keep API keys and sensitive information in environment variables
- Review and update security configurations in `guardrails.py`

## License

This project is licensed under the terms specified in the LICENSE file.
