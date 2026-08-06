# 📚 I'm Poster Documentation

Welcome to the comprehensive documentation for I'm Poster, the multi-agent blog generator powered by LangGraph and MCP integration.

## 🚀 Getting Started

### [Quickstart Guide](quickstart.md) ⭐ **NEW!**
**Start here if you're new to I'm Poster!** This guide will get you up and running in 5 minutes with the interactive CLI.

- Interactive CLI walkthrough
- Step-by-step setup instructions
- Common troubleshooting
- Performance tips

## 🏗️ Architecture & Components

### [Component Documentation](components.md)
Learn about the core components that make I'm Poster work:

- **Blog Generator**: Main orchestration engine
- **Agent System**: Multi-agent architecture overview
- **MCP Integration**: Model Context Protocol services
- **Data Models**: Pydantic models and schemas

### [Development Guide](development.md)
For developers who want to contribute or extend I'm Poster:

- Development environment setup
- Code structure and patterns
- Testing and debugging
- Contributing guidelines

## 🎯 Key Features

### **Interactive CLI** 🖥️
The easiest way to use I'm Poster is through the interactive command-line interface:

```bash
# Generate a blog post interactively
python -m src.cli generate-tutorial

# Use local Ollama models
python -m src.cli generate-tutorial --use-ollama --model "gemma3:4b"

# Verbose mode for debugging
python -m src.cli generate-tutorial --verbose
```

### **Multi-Agent System** 🤖
- **Research Agent**: Gathers information and context
- **Content Agent**: Generates the main blog content
- **Code Agent**: Creates code examples and snippets
- **Formatting Agent**: Ensures proper Markdown formatting
- **Review Agent**: Quality checks and final review

### **MCP Integration** 🔧
- **Internal MCP Server**: Fast, in-process filesystem operations
- **External MCP Server**: Network-based distributed operations
- **Comprehensive Tools**: File create, read, write, delete, move
- **Graceful Fallback**: Automatic fallback to internal mode

### **Blog Types** 📝
- **Tech Blogs**: Technical deep-dives with code examples
- **Tutorials**: Step-by-step guides
- **Comparisons**: Technology comparisons
- **Case Studies**: Real-world implementations

## 🛠️ Quick Commands

### **Basic Usage**
```bash
# Interactive blog generation
python -m src.cli generate-tutorial

# List available Ollama models
python -m src.cli generate-tutorial --list-models

# Generate with specific parameters
python -m src.cli generate-tutorial \
  --topic "Building MCP Servers" \
  --blog-type "tech" \
  --goals "Learn MCP basics,Implement file operations"
```

### **Testing**
```bash
# Run all tests
pytest

# Test MCP integration
python examples/test_integrated_mcp_service.py

# Test with coverage
pytest --cov=src
```

### **Development**
```bash
# Install dependencies
uv sync

# Run development server
python -m src.main

# Format code
black src/
```

## 🔧 Configuration

### **Environment Variables**
```bash
# Required
OPENAI_API_KEY=sk-your-openai-key-here

# Optional
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
DEFAULT_OLLAMA_MODEL=gemma3:4b
OLLAMA_BASE_URL=http://localhost:11434
CHROMA_HOST=localhost
CHROMA_PORT=8000
LOG_LEVEL=INFO
```

### **MCP Server Configuration**
```bash
# Start external MCP server
python src/core/mcp_file_server.py --http --host localhost --port 8000

# Test MCP integration
python examples/test_integrated_mcp_service.py
```

## 📖 Additional Resources

### **External Documentation**
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [MCP Specification](https://modelcontextprotocol.io/)

### **Examples & Demos**
- [MCP Integration Test](examples/test_integrated_mcp_service.py)
- [Blog Generation Examples](examples/)
- [Component Tests](tests/)

## 🆘 Support & Contributing

### **Getting Help**
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Documentation**: [Project Wiki](https://github.com/your-repo/wiki)

### **Contributing**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 🎉 What's New

### **Latest Features**
- ✅ **Interactive CLI**: User-friendly command-line interface
- ✅ **MCP Integration**: Real Model Context Protocol tools
- ✅ **Ollama Support**: Local LLM integration
- ✅ **Verbose Logging**: Enhanced debugging capabilities
- ✅ **Performance Optimization**: Fast internal MCP server

### **Coming Soon**
- 🔄 **More Blog Types**: Additional blog post formats
- 🔄 **Advanced MCP Tools**: Database, HTTP, and cloud operations
- 🔄 **Web Interface**: Browser-based blog generation
- 🔄 **Template System**: Customizable blog templates

---

**Start your journey with [Quickstart Guide](quickstart.md) and generate your first AI-powered blog post! 🚀**
