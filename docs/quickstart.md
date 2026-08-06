# 🚀 Quickstart Guide - I'm Poster

Get up and running with I'm Poster in minutes! This guide will walk you through setting up and using the interactive CLI to generate your first blog post.

## ⚡ Quick Start (5 minutes)

### 1. Install Dependencies

```bash
# Clone the repository
git clone <repository-url>
cd blog-generator

# Install dependencies (choose one)
pip install -r requirements.txt
# OR
uv sync
```

### 2. Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

**Required Environment Variables:**
```bash
# OpenAI API Key (required)
OPENAI_API_KEY=sk-your-openai-key-here

# Optional: Anthropic API Key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Optional: Ollama for local LLM usage
DEFAULT_OLLAMA_MODEL=gemma3:4b
OLLAMA_BASE_URL=http://localhost:11434
```

### 3. Generate Your First Blog Post

```bash
# Start the interactive CLI
python -m src.cli generate-tutorial
```

That's it! The CLI will guide you through the rest.

## 💾 Session Management

I'm Poster automatically saves all generation parameters to session files in the `blogs/works/` directory. This is incredibly useful for:

### **Resuming Interrupted Generations**
If your blog generation fails (network issues, API limits, etc.), you can resume exactly where you left off:

```bash
# List available sessions
python -m src.cli list-sessions

# Resume from a specific session
python -m src.cli generate-tutorial --resume blogs/works/my_topic_1234567890.json

# Or use the dedicated resume command
python -m src.cli resume-generation blogs/works/my_topic_1234567890.json
```

### **Session File Contents**
Each session file contains:
- **Blog parameters**: Topic, goals, audience, tone, length
- **Code settings**: Whether to include code examples, diagrams
- **LLM configuration**: Ollama/LM Studio settings, streaming options
- **Custom instructions**: Any additional requirements
- **Timestamp**: When the session was created

### **Managing Sessions**
```bash
# Delete a session file
python -m src.cli delete-session my_topic_1234567890.json --force

# View session details
cat blogs/works/my_topic_1234567890.json
```

## 🎯 Interactive CLI Walkthrough

### Basic Usage

```bash
python -m src.cli generate-tutorial
```

The CLI will interactively prompt you for:

#### **Blog Topic** 📝
```
What topic would you like to write about? 
> Building MCP Servers with FastMCP
```

#### **Blog Type** 🏷️
```
What type of blog post would you like to create?
1. Tech Blog - Technical deep-dive with code examples
2. Tutorial - Step-by-step guide
3. Comparison - Compare different technologies
4. Case Study - Real-world implementation
> 1
```

#### **Goals** 🎯
```
What are the main goals of this blog post? (comma-separated)
> Learn MCP basics, Implement file operations, Deploy to production
```

#### **Target Audience** 👥
```
Who is the target audience for this blog post?
1. Beginners - New to the topic
2. Intermediate - Some experience
3. Advanced - Experienced developers
4. Mixed - All skill levels
> 2
```

#### **Tone** 🎭
```
What tone would you like for this blog post?
1. Professional - Formal and business-like
2. Casual - Friendly and conversational
3. Humorous - Light-hearted with jokes
4. Academic - Research-focused
> 2
```

#### **Output File** 💾
```
Where would you like to save the blog post?
> my_mcp_blog.md
```

### Advanced CLI Options

#### **Verbose Mode** 🔍
```bash
# Enable detailed logging for debugging
python -m src.cli generate-tutorial --verbose
```

#### **Local LLM with Ollama** 🏠
```bash
# Use local Ollama model instead of OpenAI
python -m src.cli generate-tutorial --use-ollama --model "gemma3:4b"
```

#### **List Available Models** 📋
```bash
# See what Ollama models you have installed
python -m src.cli generate-tutorial --list-models
```

#### **Pre-filled Parameters** ⚙️
```bash
# Skip interactive prompts with pre-filled values
python -m src.cli generate-tutorial \
  --topic "Building MCP Servers" \
  --blog-type "tech" \
  --goals "Learn MCP basics,Implement file operations" \
  --audience "developers" \
  --tone "professional" \
  --output "my_blog.md"
```

## 🎨 Blog Post Examples

### Tech Blog Example
```markdown
# Building MCP Servers with FastMCP

## Goal
- Learn MCP basics and architecture
- Implement file operations server
- Deploy to production environment

## Approach
This blog post will guide you through building a complete MCP server...

## Topic Breakup
1. Understanding MCP Protocol
2. Setting up FastMCP
3. Implementing File Operations
4. Testing and Deployment

## Understanding MCP Protocol
The Model Context Protocol (MCP) is a standardized way for AI models...

## Wrapup
- MCP provides standardized tool interfaces
- FastMCP simplifies server development
- File operations are essential for most applications

## References
- [MCP Specification](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
```

### Tutorial Example
```markdown
# Step-by-Step MCP Server Tutorial

## Prerequisites
- Python 3.10+
- Basic understanding of async programming

## Step 1: Install Dependencies
```bash
pip install fastmcp
```

## Step 2: Create Basic Server
```python
from fastmcp import FastMCP

mcp = FastMCP("MyFirstServer")

@mcp.tool
def hello(name: str) -> str:
    return f"Hello, {name}!"
```

## Step 3: Run the Server
```bash
python server.py
```
```

## 🔧 Troubleshooting

### Common Issues

#### **"No module named 'src'" Error**
```bash
# Make sure you're in the project root directory
cd blog-generator
python -m src.cli generate-tutorial
```

#### **API Key Errors**
```bash
# Check your .env file
cat .env

# Make sure OPENAI_API_KEY is set
export OPENAI_API_KEY="sk-your-key-here"
```

#### **Ollama Connection Issues**
```bash
# Check if Ollama is running
ollama list

# Start Ollama if needed
ollama serve

# Pull the model
ollama pull gemma3:4b
```

#### **Verbose Mode for Debugging**
```bash
# Enable verbose logging to see what's happening
python -m src.cli generate-tutorial --verbose
```

### Performance Tips

#### **For Faster Generation**
- Use local Ollama models (`--use-ollama`)
- Choose smaller models (e.g., `gemma3:4b` instead of `llama3:70b`)
- Use `--verbose` only when debugging

#### **For Better Quality**
- Use OpenAI GPT-4 or Claude 3.5 Sonnet
- Provide detailed goals and context
- Choose appropriate audience level

## 🚀 Next Steps

After generating your first blog post:

1. **Explore Blog Types**: Try different blog types and tones
2. **Customize Content**: Modify the generated content to match your style
3. **Add Code Examples**: Enhance with your own code snippets
4. **Deploy MCP Servers**: Set up external MCP servers for production
5. **Contribute**: Add new blog types or improve the system

## 📚 Additional Resources

- [Component Documentation](components.md)
- [Agent Architecture](agents.md)
- [Blog Types](blog_types.md)
- [API Reference](api.md)
- [Development Guide](development.md)

## 🆘 Need Help?

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Documentation**: [Project Wiki](https://github.com/your-repo/wiki)

---

**Happy Blogging! 🎉**

Start with `python -m src.cli generate-tutorial` and let the AI agents do the heavy lifting!
