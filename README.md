# Online Form Filling Library

A Python library for automating online form filling using Playwright and Language Models (LLMs). This library intelligently fills out web forms by analyzing field context and generating appropriate responses using AI and resume data.

## Features

- **AI-Powered Form Filling**: Leverages LLMs to generate contextually appropriate responses
- **Resume Parsing**: Extracts content from PDF resumes to populate form fields
- **Comprehensive Element Support**:
  - Text inputs (text, email, tel, url, search, password)
  - Textareas
  - Select dropdowns
  - Radio buttons and radio groups
  - Checkboxes and checkbox containers
  - File uploads
  - LinkedIn-specific fieldsets
- **Intelligent Field Detection**: Automatically identifies field names from various attributes
- **Fuzzy Matching**: Matches provided data to form fields using fuzzy string matching
- **Multiple LLM Providers**: Supports Ollama, Google Gemini, Mistral, HuggingFace, Groq, DeepSeek, and NVIDIA AI
- **Cross-Browser Support**: Works with Chromium, Firefox, and WebKit via Playwright
- **Comprehensive Testing**: Extensive test suite with unit and integration tests

## Installation

### Standard Installation

1. Clone the repository:
```bash
git clone https://github.com/OzMaatuk/OnlineFormFilling.git
cd OnlineFormFilling
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install chromium  # or msedge, firefox, webkit
```

### Docker Installation

Build and run using Docker:
```bash
docker build -t online-form-filling .
docker run -it online-form-filling
```

### Dev Container

Open the project in VS Code with the Dev Containers extension to use the pre-configured development environment.

## Usage

### Basic Example

```python
from form_filling.form_filling import FormFilling
from langchain.chat_models import init_chat_model
from playwright.sync_api import sync_playwright

# Initialize the LLM
llm = init_chat_model(
    model="mistral",
    model_provider="ollama",
    temperature=0
)

# Initialize FormFilling with resume path
form_filling = FormFilling(
    llm=llm,
    resume="path/to/resume.pdf"
)

# Use with Playwright
with sync_playwright() as p:
    browser = p.webkit.launch(headless=False)
    page = browser.new_page()
    page.goto("https://example.com/job-application")

    # Fill form elements automatically
    input_elements = page.query_selector_all("input[type='text']")
    for element in input_elements:
        form_filling.fill_element(element, page)
    
    browser.close()
```

### Advanced Usage with Pre-defined Data

```python
# Provide specific values for known fields
details = {
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "phone": "123-456-7890",
    "experience": "5 years"
}

# Fill elements with provided details
for element in page.query_selector_all("input"):
    element_id = element.get_attribute("id")
    form_filling.fill_element(element, page, element_id, details)
```

### File Upload Handling

```python
# Handle file uploads (e.g., resume upload)
file_input = page.query_selector("input[type='file']")
form_filling.file_handler.handle_file_upload(page, file_input, "path/to/resume.pdf")
```

## Configuration

### Environment Variables

Create a `.env` file for sensitive configuration:
```
GOOGLE_API_KEY=your_api_key_here
MISTRAL_API_KEY=your_api_key_here
```

### LLM Configuration

The library supports multiple LLM providers through LangChain:

```python
# Ollama (local)
llm = init_chat_model(model="mistral", model_provider="ollama", temperature=0)

# Google Gemini
llm = init_chat_model(model="gemini-pro", model_provider="google-genai", temperature=0)

# Mistral AI
llm = init_chat_model(model="mistral-large-latest", model_provider="mistralai", temperature=0)
```

### Resume Input

The library accepts resume as a file path:
```python
form_filling = FormFilling(llm=llm, resume="data/personal/resume.pdf")
```

## Project Structure

```
OnlineFormFilling/
├── form_filling/              # Main package
│   ├── __init__.py           # Package initialization
│   ├── form_filling.py       # Core form filling logic
│   ├── element_handlers.py   # Element-specific fill methods
│   ├── element_utils.py      # Element type and name detection
│   ├── value_evaluator.py    # Value generation and evaluation
│   ├── content_utils.py      # LLM content generation
│   └── file_handler.py       # File upload handling
├── tests/                     # Test suite
│   ├── conftest.py           # Pytest fixtures
│   ├── test_basic.py         # Basic functionality tests
│   ├── test_element_types.py # Element type tests
│   ├── test_integration.py   # Integration tests
│   ├── test_content_generator.py
│   ├── test_edge_cases.py
│   └── index.html            # Test HTML form
├── data/
│   ├── personal/             # Personal data (gitignored)
│   └── prompts/              # Prompt templates
├── conda_recipe/             # Conda packaging
├── .devcontainer/            # Dev container config
├── requirements.txt          # Python dependencies
├── pyproject.toml           # Project metadata
├── pytest.ini               # Pytest configuration
├── Dockerfile               # Docker configuration
└── main.py                  # Example usage script
```

## How It Works

1. **Element Detection**: The library identifies form elements and determines their type (text, select, radio, etc.)
2. **Field Name Extraction**: Extracts field names from attributes like `name`, `id`, `aria-label`, or associated labels
3. **Value Matching**: Uses fuzzy matching to find relevant data from provided details
4. **AI Generation**: If no matching data is found, uses LLM to generate appropriate content based on the resume
5. **Element Filling**: Applies the value using the appropriate method for each element type

## Testing

Run the full test suite:
```bash
pytest
```

Run specific test files:
```bash
pytest tests/test_basic.py
pytest tests/test_integration.py
```

Run with verbose output:
```bash
pytest -v
```

The test suite includes:
- Unit tests for individual components
- Integration tests with real browser interactions
- Edge case handling
- Mock-based tests for LLM interactions

## Dependencies

Core dependencies:
- `playwright` - Browser automation
- `langchain` - LLM integration framework
- `pypdf` - PDF text extraction
- `fuzzywuzzy` - Fuzzy string matching
- `python-Levenshtein` - String similarity calculations
- `python-dotenv` - Environment variable management

LLM providers (optional, install as needed):
- `langchain-ollama` - Local LLM support
- `langchain-google-genai` - Google Gemini
- `langchain-mistralai` - Mistral AI
- `langchain-huggingface` - HuggingFace models
- `langchain-groq` - Groq API
- `langchain-deepseek` - DeepSeek models
- `langchain-nvidia-ai-endpoints` - NVIDIA AI

## Troubleshooting

**Issue**: Playwright browser not found
```bash
playwright install chromium
```

**Issue**: PDF parsing fails
- Ensure the PDF is not encrypted or password-protected
- Verify the file path is correct

**Issue**: LLM not generating content
- Check your API keys in `.env` file
- Verify the LLM provider is correctly configured
- Ensure the model name is valid for your provider

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests to ensure everything works (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

MIT License - See LICENSE file for details

## Author

Oz Levi - [ozmaatuk@gmail.com](mailto:ozmaatuk@gmail.com)

## Acknowledgments

- Built with [Playwright](https://playwright.dev/) for browser automation
- Powered by [LangChain](https://www.langchain.com/) for LLM integration
- Uses [fuzzywuzzy](https://github.com/seatgeek/fuzzywuzzy) for intelligent field matching