# Online Form Filling Library

A Python library for automating online form filling using Playwright and Language Models (LLMs). This library intelligently fills out web forms using resume data and AI-powered content generation.

## Features

- Automated form filling with AI assistance
- Support for various input types:
  - Text inputs
  - Select dropdowns
  - Radio buttons
  - Checkboxes
  - File uploads
- Resume parsing and content extraction
- Intelligent field value generation using LLMs
- Cross-browser compatibility via Playwright
- Extensive testing suite

## Installation

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
playwright install msedge
```

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

# Initialize FormFilling with resume
form_filling = FormFilling(
    llm=llm,
    resume_path="path/to/resume.pdf"
)

# Use with Playwright
with sync_playwright() as p:
    browser = p.webkit.launch(headless=False)
    page = browser.new_page()
    page.goto("https://example.com/job-application")

    # Fill form elements
    input_elements = page.query_selector_all("input[type='text']")
    for element in input_elements:
        form_filling.fill_element(element, page)
```

## Project Structure

```
OnlineFormFilling/
├── form_filling/          # Main package directory
│   ├── __init__.py
│   ├── content_utils.py   # Content generation utilities
│   ├── element_handlers.py # Form element handling
│   ├── element_utils.py   # Element type detection
│   ├── file_handler.py   # File upload handling
│   ├── form_filling.py   # Main form filling logic
│   └── value_evaluator.py # Value evaluation and generation
├── tests/                # Test suite
├── conda_recipe/        # Conda build recipes
├── requirements.txt     # Python dependencies
├── pyproject.toml      # Project metadata
└── Dockerfile          # Container configuration
```

## Configuration

The library supports various configuration options through environment variables or direct initialization:

- LLM configuration (model, provider, temperature)
- Resume content or file path
- Browser settings (headless mode, etc.)

## Testing

Run the test suite using pytest:

```bash
pytest
```

Tests include:
- Unit tests for individual components
- Integration tests for form filling
- Edge case handling
- Content generation validation

## Docker Support

Build and run using Docker:

```bash
docker build -t online-form-filling .
docker run -it online-form-filling
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Make your changes
4. Run tests to ensure functionality
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Author

Oz Levi - [ozmaatuk@gmail.com](mailto:ozmaatuk@gmail.com)