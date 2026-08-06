# Quick Start Guide - I'm Poster Blog Generator

Get up and running with the I'm Poster blog generator in minutes!

## 🚀 Quick Setup

### 1. Prerequisites
- Python 3.10 or higher
- OpenAI API key (or Anthropic API key)

### 2. Automated Setup (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd blog-generator

# Run the automated setup script
python scripts/setup.py

# Activate your virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Edit your API keys
nano .env  # or use your preferred editor
```

### 3. Manual Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp env.example .env
# Edit .env with your API keys
```

## 🎯 Generate Your First Blog

### Using the CLI (Easiest)
```bash
# Generate a tech blog
im-poster generate-tech-blog "Building APIs with FastAPI" \
    --goal "Understand FastAPI basics" \
    --goal "Build RESTful endpoints" \
    --tone "friendly" \
    --length "medium"

# Generate a tutorial
im-poster generate-tutorial "Docker Basics" \
    --goal "Containerize applications" \
    --goal "Deploy with Docker" \
    --difficulty "beginner" \
    --backend openai --verbose

# List generated blogs
im-poster list-blogs

# Show blog content
im-poster show-blog "your-blog-post.md"
```

### Using Python Code
```python
from src.core.blog_generator import BlogGenerator

# Initialize the generator
generator = BlogGenerator()

# Generate a tech blog
result = await generator.generate_tech_blog(
    topic="Building Multi-Agent Systems",
    goals=[
        "Understand agent communication",
        "Implement workflow orchestration"
    ],
    include_code_examples=True
)

# Save to file
if result.success:
    saved_file = generator.save_blog_to_file(result.blog_post)
    print(f"Blog saved to: {saved_file}")
```

### Using the Example Script
```bash
# Run the sample blog generation
python examples/generate_sample_blog.py
```

## 📚 Available Blog Types

### 1. Tech Blog
- Technology-focused content
- Code examples and technical details
- Professional but accessible tone

### 2. Tutorial
- Step-by-step learning content
- Beginner to advanced difficulty levels
- Practical examples and exercises

### 3. Comparison
- Technology or approach comparisons
- Pros and cons analysis
- Decision-making guidance

### 4. Case Study
- Real-world examples and scenarios
- Problem-solution analysis
- Professional insights

## ⚙️ Configuration

### Environment Variables
```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DEFAULT_MODEL=gpt-4
DEFAULT_TEMPERATURE=0.7
MAX_TOKENS=4000
```

### Blog Generation Options
- **Topic**: Main subject of the blog
- **Goals**: What readers should learn
- **Target Audience**: Developers, beginners, experts, etc.
- **Tone**: Friendly, professional, humorous
- **Length**: Short, medium, long
- **Code Examples**: Include/exclude code snippets
- **Custom Instructions**: Additional requirements

## 🔍 CLI Commands

```bash
# Generate blogs
im-poster generate-tech-blog <topic> [options]
im-poster generate-tutorial <topic> [options]
im-poster generate-comparison <topic> [options]

# Manage blogs
im-poster list-blogs
im-poster show-blog <filename>
im-poster status

# Get help
im-poster --help
im-poster generate-tech-blog --help
```

## 📁 Output Structure

Generated blogs are saved in the `blogs/` directory with:
- Rich Markdown formatting
- Code examples with syntax highlighting
- Proper structure (introduction, sections, conclusion)
- Metadata and quality scores
- References and further reading

## 🧪 Testing

```bash
# Run basic tests
pytest tests/test_basic.py

# Run all tests
pytest

# Run with coverage
pytest --cov=src
```

## 🆘 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure virtual environment is activated
   - Check Python path includes `src/`

2. **API Key Issues**
   - Verify `.env` file exists and has correct API keys
   - Check API key permissions and quotas

3. **Memory Issues**
   - Reduce `MAX_TOKENS` in configuration
   - Use smaller models (e.g., `gpt-3.5-turbo`)

4. **Performance Issues**
   - Check network connectivity
   - Monitor API rate limits

### Getting Help

- Check the logs for detailed error messages
- Review the comprehensive documentation in `docs/`
- Check the examples in `examples/`
- Verify your configuration settings

## 🚀 Next Steps

1. **Explore Features**: Try different blog types and options
2. **Customize**: Modify agent prompts and workflows
3. **Extend**: Add new blog types or agents
4. **Integrate**: Use the API in your own applications
5. **Deploy**: Set up for production use

## 📖 Documentation

- **Components**: `docs/components.md` - Detailed component documentation
- **Development**: `docs/development.md` - Development guide and API reference
- **Examples**: `examples/` - Sample scripts and usage examples

## 🎉 You're Ready!

The I'm Poster blog generator is now fully set up and ready to create amazing blog posts. Start with a simple tech blog and explore the advanced features as you become more comfortable with the system.

Happy blogging! 🚀
# Use local Ollama model
im-poster generate-tutorial --backend ollama --ollama-model "gemma3:4b" --verbose

# Use local LM Studio model
im-poster generate-tutorial --backend lm-studio --lm-studio-model "local-model" --verbose
