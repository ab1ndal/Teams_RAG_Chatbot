# Teams RAG Chatbot

A Microsoft Teams plugin with RAG (Retrieval-Augmented Generation) backend for task input, retrieval, and updates.

## Project Structure

```
teams-rag-chatbot/
├── app/                 # Main application code
│   ├── __init__.py     # Package initialization
│   ├── clear_index.py  # Script to clear search indexes
│   ├── config.py       # Configuration settings
│   ├── document_loader.py  # Document processing utilities
│   ├── graph/          # Graph-based processing framework
│   │   ├── __init__.py     # Package initialization
│   │   ├── assistant.py    # Main assistant logic using LangGraph
│   │   ├── state.py       # State management class (AssistantState)
│   │   └── nodes/         # Processing nodes
│   │       ├── classify.py # Query classification and intent detection
│   │       ├── excel_insight.py # Excel code generation and execution
│   │       ├── generate.py     # Answer generation
│   │       ├── guardrails.py   # Security and validation rules
│   │       ├── rag.py         # RAG implementation
│   │       ├── respond.py     # Response formatting
│   │       └── rfi_lookup.py  # RFI lookup and context combination
│   ├── clients/           # API client implementations
│   │   └── openAI_client.py # OpenAI API client
│   ├── services/         # Service implementations
│   │   ├── embedding.py  # Text embedding generation
│   │   ├── excel_cache.py # Excel data caching
│   │   └── pinecone_index.py # Vector store operations
│   ├── smart_indexer.py  # Smart indexing implementation
│   ├── utils.py         # Utility functions
│   └── outdated/        # Legacy files (to be removed)
│       ├── chat_engine.py  # Legacy chat processing
│       ├── main.py        # Legacy FastAPI app
│       └── read_excel.py  # Legacy Excel processing
```

## Key Components

- `app/graph/assistant.py`: Implements the main assistant logic using LangGraph framework, including:
  - Query classification
  - Excel insights generation and execution
  - RFI lookup and context combination
  - Answer generation

- `app/graph/state.py`: Manages the assistant's state through the `AssistantState` class

- `app/graph/nodes/`: Contains specialized processing nodes:
  - `classify.py`: Handles query classification and intent detection
  - `excel_insight.py`: Generates and executes Excel code
  - `generate.py`: Implements answer generation
  - `guardrails.py`: Security and validation rules
  - `rag.py`: Contains RAG implementation
  - `respond.py`: Formats responses
  - `rfi_lookup.py`: Handles RFI lookups and context combination

- `app/clients/openAI_client.py`: Implements OpenAI API client for LLM interactions

- `app/services/`: Contains service implementations:
  - `embedding.py`: Handles text embedding generation
  - `excel_cache.py`: Manages Excel data caching
  - `pinecone_index.py`: Handles vector store operations

- `app/config.py`: Contains configuration settings for:
  - API integrations
  - Model settings
  - Vector store configuration

- `app/document_loader.py`: Provides utilities for:
  - Document processing
  - File handling
  - Text extraction

- `app/smart_indexer.py`: Implements smart indexing functionality

- `app/utils.py`: Contains general utility functions

- `app/clear_index.py`: Utility script for:
  - Resetting vector store
  - Clearing document embeddings

- `app/outdated/`: Contains legacy files that should be removed:
  - `chat_engine.py`: Legacy chat processing
  - `main.py`: Legacy FastAPI app
  - `read_excel.py`: Legacy Excel processing

## Key Components

- `app/graph/assistant.py`: Implements the main assistant logic using LangGraph framework, including:
  - Query classification
  - Excel insights generation and execution
  - RFI lookup and context combination
  - Answer generation

- `app/graph/state.py`: Manages the assistant's state through the `AssistantState` class

- `app/graph/nodes/`: Contains specialized processing nodes:
  - `classify.py`: Handles query classification and intent detection
  - `excel_insight.py`: Generates and executes Excel code
  - `generate.py`: Implements answer generation
  - `guardrails.py`: Security and validation rules
  - `rag.py`: Contains RAG implementation
  - `respond.py`: Formats responses
  - `rfi_lookup.py`: Handles RFI lookups and context combination

- `app/clients/openAI_client.py`: Implements OpenAI API client for LLM interactions

- `app/services/`: Contains service implementations:
  - `embedding.py`: Handles text embedding generation
  - `excel_cache.py`: Manages Excel data caching
  - `pinecone_index.py`: Handles vector store operations

- `app/config.py`: Contains configuration settings for:
  - API integrations
  - Model settings
  - Vector store configuration

- `app/document_loader.py`: Provides utilities for:
  - Document processing
  - File handling
  - Text extraction

- `app/smart_indexer.py`: Implements smart indexing functionality

- `app/utils.py`: Contains general utility functions

- `app/clear_index.py`: Utility script for:
  - Resetting vector store
  - Clearing document embeddings

- `app/outdated/`: Contains legacy files that should be removed:
  - `chat_engine.py`: Legacy chat processing
  - `main.py`: Legacy FastAPI app
  - `read_excel.py`: Legacy Excel processing

## Potential Improvements

1. **Performance Optimization**:
   - Implement caching for frequently accessed documents
   - Add batch processing for document ingestion
   - Optimize vector store operations
   - Implement request queuing

2. **Feature Additions**:
   - Add support for more document types
   - Implement version control for documents
   - Add document metadata management
   - Implement user-specific document access control

3. **Testing Improvements**:
   - Add more integration tests
   - Implement end-to-end testing
   - Add performance benchmarks

4. **Documentation**:
   - Add API documentation
   - Create deployment guides
   - Document configuration options

5. **Monitoring**:
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
