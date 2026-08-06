# Development Guide

This guide provides comprehensive information for developers working on the I'm Poster blog generator.

## Development Environment Setup

### Prerequisites

- Python 3.10 or higher
- Git
- A code editor (VS Code, PyCharm, etc.)
- OpenAI API key (or Anthropic API key)

### Initial Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd blog-generator
   ```

2. **Create a virtual environment:**
   ```bash
   # Using venv
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Using uv (recommended)
   uv venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   # Using pip
   pip install -r requirements.txt
   
   # Using uv
   uv sync
   
   # Install development dependencies
   uv sync --extra dev
   ```

4. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your API keys and configuration
   ```

5. **Verify installation:**
   ```bash
   python -m src.main
   ```

## Project Structure

```
blog-generator/
├── src/                    # Main application source
│   ├── __init__.py        # Package initialization
│   ├── main.py            # Application entry point
│   ├── cli.py             # Command-line interface
│   ├── core/              # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py      # Configuration management
│   │   ├── models.py      # Data models
│   │   └── blog_generator.py  # Main interface
│   └── agents/            # Multi-agent system
│       ├── __init__.py
│       ├── base_agent.py  # Base agent class
│       ├── research_agent.py
│       ├── content_agent.py
│       ├── code_agent.py
│       ├── formatting_agent.py
│       ├── review_agent.py
│       └── agent_orchestrator.py
├── docs/                  # Documentation
├── examples/              # Example scripts
├── tests/                 # Test suite
├── worklog/               # Development tracking
├── blogs/                 # Generated blog posts
├── templates/             # Blog templates
├── data/                  # Application data
├── pyproject.toml         # Project configuration
├── requirements.txt       # Dependencies
└── README.md             # Project overview
```

## Development Workflow

### 1. Code Style and Quality

The project uses several tools to maintain code quality:

**Black** - Code formatting
```bash
# Format all Python files
black src/ tests/ examples/

# Check formatting without changes
black --check src/ tests/ examples/
```

**isort** - Import sorting
```bash
# Sort imports
isort src/ tests/ examples/

# Check import sorting
isort --check-only src/ tests/ examples/
```

**Ruff** - Fast linting
```bash
# Run linter
ruff check src/ tests/ examples/

# Fix auto-fixable issues
ruff check --fix src/ tests/ examples/
```

**MyPy** - Type checking
```bash
# Run type checker
mypy src/

# Run with strict mode
mypy --strict src/
```

### 2. Pre-commit Hooks

Install pre-commit hooks to automatically run quality checks:

```bash
# Install pre-commit
pip install pre-commit

# Install the git hook scripts
pre-commit install

# Run against all files
pre-commit run --all-files
```

### 3. Testing

**Run tests:**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test categories
pytest tests/test_agents/
pytest tests/test_blog_generation/

# Run with verbose output
pytest -v

# Run tests in parallel
pytest -n auto
```

**Test structure:**
```
tests/
├── conftest.py           # Test configuration and fixtures
├── test_agents/          # Agent tests
├── test_core/            # Core functionality tests
├── test_integration/     # Integration tests
└── test_cli/             # CLI tests
```

**Writing tests:**
```python
import pytest
from src.core.blog_generator import BlogGenerator

class TestBlogGenerator:
    @pytest.fixture
    def generator(self):
        return BlogGenerator()
    
    @pytest.mark.asyncio
    async def test_generate_tech_blog(self, generator):
        result = await generator.generate_tech_blog(
            topic="Test Topic",
            goals=["Test Goal"]
        )
        assert result.success
        assert result.blog_post is not None
```

### 4. Development Commands

**Development server:**
```bash
# Run with auto-reload
python -m src.main --reload

# Run with debug mode
DEBUG=true python -m src.main
```

**Code generation:**
```bash
# Generate a sample blog
python examples/generate_sample_blog.py

# Use CLI
im-poster generate-tech-blog "Test Topic" --goal "Test Goal"
```

## Adding New Features

### 1. New Blog Types

To add a new blog type:

1. **Update the BlogType enum:**
   ```python
   # In src/core/models.py
   class BlogType(str, Enum):
       TECH_BLOG = "tech_blog"
       TUTORIAL = "tutorial"
       COMPARISON = "comparison"
       CASE_STUDY = "case_study"
       NEWS_ANALYSIS = "news_analysis"
       OPINION = "opinion"
       YOUR_NEW_TYPE = "your_new_type"  # Add this
   ```

2. **Add generation method to BlogGenerator:**
   ```python
   # In src/core/blog_generator.py
   async def generate_your_new_type_blog(
       self,
       topic: str,
       goals: List[str],
       # ... other parameters
   ) -> BlogGenerationResult:
       # Implementation
       pass
   ```

3. **Add CLI command:**
   ```python
   # In src/cli.py
   @app.command()
   def generate_your_new_type(
       topic: str = typer.Argument(..., help="Main topic"),
       # ... other options
   ):
       """Generate a your-new-type blog post."""
       # Implementation
       pass
   ```

### 2. New Agents

To add a new agent:

1. **Create the agent class:**
   ```python
   # In src/agents/your_agent.py
   from .base_agent import BaseAgent
   
   class YourAgent(BaseAgent):
       def __init__(self, **kwargs):
           super().__init__(
               name="Your Agent",
               description="Description of what this agent does",
               **kwargs
           )
       
       async def process(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
           # Implementation
           pass
   ```

2. **Update the orchestrator:**
   ```python
   # In src/agents/agent_orchestrator.py
   from .your_agent import YourAgent
   
   class AgentOrchestrator:
       def __init__(self, **kwargs):
           # ... existing agents
           self.your_agent = YourAgent(**kwargs)
       
       def _create_workflow(self) -> StateGraph:
           # Add your agent to the workflow
           workflow.add_node("your_agent", self._your_agent_node)
           # ... workflow edges
   ```

### 3. New Output Formats

To add new output formats:

1. **Create a formatter class:**
   ```python
   class YourFormatFormatter:
       def format_blog(self, blog_post: BlogPost) -> str:
           # Convert blog post to your format
           pass
   ```

2. **Add to BlogGenerator:**
   ```python
   # In src/core/blog_generator.py
   def save_blog_to_your_format(self, blog_post: BlogPost, filename: str) -> str:
       formatter = YourFormatFormatter()
       content = formatter.format_blog(blog_post)
       # Save content
       return saved_file_path
   ```

## Debugging

### 1. Logging

The application uses structured logging:

```python
import logging

# Set log level
logging.basicConfig(level=logging.DEBUG)

# In your code
logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### 2. Debug Mode

Enable debug mode for detailed output:

```bash
# Set environment variable
export DEBUG=true

# Or in .env file
DEBUG=true
```

### 3. Agent Debugging

Debug individual agents:

```python
# Enable agent debugging
agent = ResearchAgent(debug=True)

# Check agent state
print(agent.get_system_prompt())
print(agent.model_name)
```

### 4. Workflow Debugging

Debug the LangGraph workflow:

```python
# Enable workflow debugging
orchestrator = AgentOrchestrator(debug=True)

# Check workflow status
status = orchestrator.get_workflow_status()
print(status)
```

## Performance Optimization

### 1. Async Operations

Ensure all I/O operations are async:

```python
# Good
async def process_data(self):
    result = await self.llm.ainvoke(messages)
    return result

# Avoid
def process_data(self):
    result = self.llm.invoke(messages)  # Blocking
    return result
```

### 2. Caching

Implement caching for expensive operations:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_operation(self, key: str):
    # Expensive computation
    pass
```

### 3. Batch Processing

Process multiple items in batches:

```python
async def process_batch(self, items: List[Any]):
    tasks = [self.process_item(item) for item in items]
    results = await asyncio.gather(*tasks)
    return results
```

## Security Considerations

### 1. API Key Management

Never commit API keys to version control:

```python
# Good - use environment variables
api_key = os.getenv("OPENAI_API_KEY")

# Bad - hardcoded
api_key = "sk-1234567890abcdef"
```

### 2. Input Validation

Always validate user inputs:

```python
from pydantic import BaseModel, validator

class BlogRequest(BaseModel):
    topic: str
    
    @validator('topic')
    def validate_topic(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Topic must be at least 3 characters')
        return v.strip()
```

### 3. Output Sanitization

Sanitize generated content:

```python
import html

def sanitize_content(content: str) -> str:
    # Escape HTML characters
    return html.escape(content)
```

## Deployment

### 1. Production Configuration

Update configuration for production:

```env
# Production settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
HOST=0.0.0.0
PORT=8000
```

### 2. Docker Deployment

Create a Dockerfile:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "-m", "src.main"]
```

### 3. Environment Management

Use different configurations for different environments:

```bash
# Development
cp env.example .env.dev

# Production
cp env.example .env.prod

# Staging
cp env.example .env.staging
```

## Contributing

### 1. Code Review Process

1. Create a feature branch
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### 2. Commit Message Format

Use conventional commit messages:

```
feat: add new blog type support
fix: resolve agent initialization issue
docs: update API documentation
test: add integration tests for new agent
refactor: improve error handling
```

### 3. Testing Requirements

- All new code must have tests
- Maintain test coverage above 80%
- Include integration tests for new features
- Test error conditions and edge cases

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated
2. **API Key Issues**: Check environment variables and .env file
3. **Memory Issues**: Reduce max_tokens or use smaller models
4. **Performance Issues**: Check async operations and caching

### Getting Help

- Check the logs for error messages
- Review the configuration settings
- Test with minimal examples
- Check GitHub issues for similar problems

## Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Python AsyncIO Documentation](https://docs.python.org/3/library/asyncio.html)
