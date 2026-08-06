# Component Documentation

This document provides detailed information about the core components of the I'm Poster blog generator.

## Core Components

### 1. Configuration Management (`src/core/config.py`)

The configuration system uses Pydantic Settings for environment-based configuration management.

**Key Features:**
- Environment variable support with `.env` file
- Type-safe configuration with validation
- Default values for all settings
- Support for both OpenAI and Anthropic APIs

**Configuration Options:**
- **API Keys**: OpenAI and Anthropic API keys
- **Database**: ChromaDB connection settings
- **Server**: Host, port, and reload settings
- **MCP**: Model Context Protocol configuration
- **Blog Generation**: Model settings and output directories

**Usage:**
```python
from src.core.config import settings

# Access configuration
api_key = settings.openai_api_key
output_dir = settings.blog_output_dir
```

### 2. Data Models (`src/core/models.py`)

Pydantic models for structured data handling throughout the application.

**Key Models:**

#### BlogRequest
Represents a request for blog generation with all necessary parameters.

```python
from src.core.models import BlogRequest, BlogType

request = BlogRequest(
    topic="Building Multi-Agent Systems",
    blog_type=BlogType.TECH_BLOG,
    goals=["Understand agents", "Implement workflows"],
    target_audience="developers",
    tone="friendly"
)
```

#### BlogPost
Complete blog post structure with all content sections.

```python
from src.core.models import BlogPost

blog_post = BlogPost(
    title="Your Blog Title",
    goals=["Goal 1", "Goal 2"],
    approach="Step-by-step guide",
    # ... other fields
)
```

#### CodeExample
Represents code examples within blog sections.

```python
from src.core.models import CodeExample

example = CodeExample(
    language="python",
    code="print('Hello, World!')",
    description="Simple greeting example",
    filename="hello.py"
)
```

### 3. Blog Generator (`src/core/blog_generator.py`)

Main interface for blog generation, providing high-level methods for different blog types.

**Key Methods:**

#### generate_tech_blog()
Generate technology-focused blog posts with code examples.

```python
from src.core.blog_generator import BlogGenerator

generator = BlogGenerator()
result = await generator.generate_tech_blog(
    topic="Python Async Programming",
    goals=["Understand async/await", "Build concurrent applications"],
    include_code_examples=True
)
```

#### generate_tutorial_blog()
Generate step-by-step tutorial content.

```python
result = await generator.generate_tutorial_blog(
    topic="Docker Basics",
    goals=["Containerize applications", "Deploy with Docker"],
    difficulty="beginner"
)
```

#### generate_comparison_blog()
Generate comparison analysis between different technologies or approaches.

```python
result = await generator.generate_comparison_blog(
    topic="Python vs JavaScript for Backend",
    items=["Python", "JavaScript"],
    goals=["Understand differences", "Choose the right tool"]
)
```

### 4. Multi-Agent System

The core of the application uses a sophisticated multi-agent architecture powered by LangGraph.

#### Agent Orchestrator (`src/agents/agent_orchestrator.py`)

Coordinates the workflow between different specialized agents.

**Workflow:**
1. **Research Agent** → Gathers information and context
2. **Content Agent** → Generates main blog content
3. **Code Agent** → Adds code examples and snippets
4. **Formatting Agent** → Ensures proper Markdown formatting
5. **Review Agent** → Performs quality checks and review

**Usage:**
```python
from src.agents.agent_orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator()
result = await orchestrator.generate_blog(blog_request)
```

#### Individual Agents

Each agent specializes in a specific aspect of blog generation:

- **Research Agent**: Topic research, context gathering, reference collection
- **Content Agent**: Content creation, structure, flow, and engagement
- **Code Agent**: Code example generation, technical accuracy
- **Formatting Agent**: Markdown formatting, visual structure, readability
- **Review Agent**: Quality assurance, content validation, improvement suggestions

### 5. Command Line Interface (`src/cli.py`)

Rich CLI interface built with Typer and Rich for user interaction.

**Commands:**

#### Generate Tech Blog
```bash
im-poster generate-tech-blog "Building APIs with FastAPI" \
    --goal "Understand FastAPI basics" \
    --goal "Build RESTful endpoints" \
    --tone "friendly" \
    --length "medium"
```

#### Generate Tutorial
```bash
im-poster generate-tutorial "Machine Learning Basics" \
    --goal "Understand ML concepts" \
    --goal "Build first ML model" \
    --difficulty "beginner" \
    --include-code
```

#### List Generated Blogs
```bash
im-poster list-blogs
```

#### Show Blog Content
```bash
im-poster show-blog "my-blog-post.md"
```

#### Check Status
```bash
im-poster status
```

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Interface │    │  Blog Generator │    │ Agent Orchestrator │
│                 │◄──►│                 │◄──►│                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   File Output   │    │  Multi-Agent   │
                       │                 │    │   Workflow     │
                       └─────────────────┘    └─────────────────┘
```

## Data Flow

1. **User Input**: CLI or programmatic interface
2. **Request Processing**: BlogRequest creation and validation
3. **Agent Workflow**: Sequential processing through specialized agents
4. **Content Generation**: Structured blog post creation
5. **Quality Review**: Multi-dimensional quality assessment
6. **Output**: Markdown file generation and metadata

## Configuration Management

### Environment Variables

Create a `.env` file in your project root:

```env
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Database
CHROMA_HOST=localhost
CHROMA_PORT=8000

# Application
LOG_LEVEL=INFO
DEBUG=false
HOST=0.0.0.0
PORT=8000

# Blog Generation
DEFAULT_MODEL=gpt-4
DEFAULT_TEMPERATURE=0.7
MAX_TOKENS=4000

# Output
BLOG_OUTPUT_DIR=./blogs
TEMPLATE_DIR=./templates
```

### Configuration Validation

The system automatically validates configuration on startup:

```python
from src.core.config import settings

# This will raise an error if required settings are missing
print(f"Using model: {settings.default_model}")
```

## Error Handling

The system implements comprehensive error handling:

- **Configuration Errors**: Validation failures during startup
- **API Errors**: Network and authentication issues
- **Generation Errors**: Content generation failures
- **File System Errors**: Output directory and file issues

## Performance Considerations

- **Async Operations**: All agent operations are asynchronous
- **Caching**: Research results can be cached for efficiency
- **Parallel Processing**: Some operations can run in parallel
- **Resource Management**: Proper cleanup of LLM connections

## Security Features

- **API Key Management**: Secure handling of sensitive credentials
- **Input Validation**: Comprehensive validation of all user inputs
- **Output Sanitization**: Safe handling of generated content
- **Access Control**: Configurable access to different features

## Extensibility

The system is designed for easy extension:

- **New Blog Types**: Add new blog type handlers
- **Custom Agents**: Implement specialized agents for specific domains
- **Output Formats**: Support for different output formats
- **Integration**: Easy integration with external systems
