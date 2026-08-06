# I'm Poster - Multi-Agent Blog Generator

A sophisticated multi-agent AI system that generates high-quality blog posts in multiple formats with rich Markdown formatting.

## 🚀 Features

- **Multi-Agent Architecture**: Powered by LangGraph and LangChain
- **Rich Blog Generation**: Creates well-structured blog posts with examples and code snippets
- **Multiple Blog Types**: Support for tech blogs, tutorials, and more
- **MCP Integration**: Uses publicly available MCP tools for enhanced functionality
- **Modern Tech Stack**: Built with Python, FastAPI, and modern validation frameworks

## 🏗️ Architecture

The application uses a multi-agent system where different agents handle specific aspects of blog generation:
- **Research Agent**: Gathers information and context
- **Content Agent**: Generates the main blog content
- **Code Agent**: Creates code examples and snippets
- **Formatting Agent**: Ensures proper Markdown formatting
- **Review Agent**: Quality checks and final review

## 📁 Project Structure

```
blog-generator/
├── src/                    # Main application source
│   ├── agents/            # Multi-agent system components
│   ├── core/              # Core functionality and models
│   ├── blog_types/        # Different blog type handlers
│   └── utils/             # Utility functions and helpers
├── blogs/                 # Generated blog posts
├── docs/                  # Component documentation
├── worklog/               # Task tracking and progress
├── tests/                 # Test suite
├── examples/              # Example usage and demos
└── scripts/               # Setup and utility scripts
```

## 🛠️ Tech Stack

- **Python 3.9+**
- **LangGraph & LangChain** - Multi-agent orchestration
- **FastAPI** - API framework
- **Pydantic** - Data validation
- **ChromaDB** - Vector database for RAG
- **FastMCP** - MCP tool integration
- **httpx** - HTTP client for API calls

## 🚀 Quick Start

> **📖 For a complete walkthrough, see our [Quickstart Guide](docs/quickstart.md)**

### Prerequisites
- Python 3.10 or higher
- pip or uv package manager

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd blog-generator
   ```

2. **Install dependencies:**
   ```bash
   # Using pip
   pip install -r requirements.txt
   
   # Using uv (recommended)
   uv sync
   ```

3. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Generate your first blog post:**
   ```bash
   # Interactive CLI (recommended for beginners)
   python -m src.cli generate-tutorial
   
   # Or run the main application
   python -m src.main
   ```

## 📚 Usage

### Interactive CLI (Recommended)

The easiest way to use I'm Poster is through the interactive command-line interface:

```bash
# Generate a blog post interactively
python -m src.cli generate-tutorial

# Or with verbose logging
python -m src.cli generate-tutorial --verbose
```

The interactive CLI will prompt you for:
- **Blog Topic**: What you want to write about
- **Blog Type**: Tech blog, tutorial, comparison, etc.
- **Goals**: What you want to achieve with the blog
- **Target Audience**: Who the blog is for
- **Tone**: Professional, casual, humorous, etc.
- **Output File**: Where to save the generated blog

### Basic Blog Generation

```python
from src.core.blog_generator import BlogGenerator

generator = BlogGenerator()
blog_post = generator.generate_tech_blog(
    topic="Building Multi-Agent Systems",
    goals=["Understand agent communication", "Implement workflow orchestration"]
)
```

### Custom Blog Types

```python
# Generate a tutorial blog
tutorial = generator.generate_tutorial_blog(
    topic="LangGraph Basics",
    difficulty="Intermediate"
)

# Generate a comparison blog
comparison = generator.generate_comparison_blog(
    topic="LangChain vs LangGraph",
    items=["LangChain", "LangGraph", "Custom Solution"]
)
```

### CLI Commands

```bash
# Generate a tutorial blog interactively
python -m src.cli generate-tutorial

# Generate with specific parameters
python -m src.cli generate-tutorial \
  --topic "Building MCP Servers" \
  --goal "Learn MCP basics" --goal "Implement file operations" \
  --audience developers \
  --tone professional \
  --backend openai \
  --output my_blog.md --verbose

# Use verbose mode for debugging
python -m src.cli generate-tutorial --verbose

# Use local LM Studio backend
python -m src.cli generate-tutorial --backend lm-studio --lm-studio-model local-model --verbose

# Use local Ollama backend
python -m src.cli generate-tutorial --backend ollama --ollama-model gemma3:4b --verbose
```

### Session Management

The blog generator automatically saves session parameters to `blogs/works/` directory, allowing you to resume interrupted generations:

```bash
# Resume from a saved session
python -m src.cli generate-tutorial --resume blogs/works/my_topic_1234567890.json

# List all available sessions
python -m src.cli list-sessions

# Resume using the dedicated command
python -m src.cli resume-generation blogs/works/my_topic_1234567890.json

# Delete a session file
python -m src.cli delete-session my_topic_1234567890.json --force
```

**Session files contain all generation parameters** including topic, goals, audience, tone, length, code settings, and LLM configuration (Ollama/LM Studio settings).

### Backend Selection

You can select the LLM backend explicitly with `--backend` on both generation and resume commands:

- `--backend openai` (default if neither local backend is selected)
- `--backend lm-studio`
- `--backend ollama`

Examples:

```bash
# Force OpenAI on resume (ignores LM Studio/Ollama saved in the session file)
python -m src.cli resume-generation blogs/works/my_topic_1234567890.json --backend openai --verbose

# Use LM Studio explicitly
python -m src.cli generate-tutorial --topic "Docker Basics" --goal "Containerize" --backend lm-studio --lm-studio-model local-model --verbose

# Use Ollama explicitly
python -m src.cli generate-tutorial --topic "Agents" --goal "Implement" --backend ollama --ollama-model gemma3:4b --verbose
```

Note: Streaming visualization panels appear when `--verbose` is enabled. Without verbose mode, the CLI runs quietly and prints a summary on completion.

## 🔧 Configuration

The application can be configured through environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `ANTHROPIC_API_KEY`: Your Anthropic API key (optional)
- `CHROMA_HOST`: ChromaDB host (default: localhost)
- `CHROMA_PORT`: ChromaDB port (default: 8000)
- `LOG_LEVEL`: Logging level (default: INFO)
- `DEFAULT_OLLAMA_MODEL`: Default Ollama model for local LLM (default: gemma3:4b)
- `OLLAMA_BASE_URL`: Ollama server URL (default: http://localhost:11434)

## 🚀 MCP Integration

I'm Poster includes a powerful **Integrated MCP (Model Context Protocol) Service** that provides:

### **Internal MCP Server**
- Runs within the same process for maximum performance
- Comprehensive filesystem operations (create, read, write, delete, move)
- Real MCP tools using FastMCP library
- No external dependencies or network overhead

### **External MCP Server Support**
- Connect to external MCP servers over HTTP/SSE
- Distributed deployments and microservices
- Network-based operations for production environments
- Graceful fallback to internal mode if connection fails

### **Available MCP Tools**
- `file_create`, `file_read`, `file_append`, `file_delete`, `file_move`
- `folder_create`, `folder_contents`, `folder_delete`
- `file_exists`, `call_tool_bulk`
- All tools return structured results with proper error handling

## 📖 Documentation

- [Component Documentation](docs/components.md)
- [Agent Architecture](docs/agents.md)
- [Blog Types](docs/blog_types.md)
- [API Reference](docs/api.md)
- [Development Guide](docs/development.md)

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test categories
pytest tests/test_agents/
pytest tests/test_blog_generation/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Documentation**: [Project Wiki](https://github.com/your-repo/wiki)

---

**Built with ❤️ using LangGraph and modern AI technologies**
