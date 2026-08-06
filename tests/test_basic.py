"""
Basic tests to verify the application structure and imports.
"""

import pytest
from pathlib import Path


def test_project_structure():
    """Test that the project has the expected structure."""
    project_root = Path(__file__).parent.parent
    
    # Check that key directories exist
    assert (project_root / "src").exists(), "src directory should exist"
    assert (project_root / "docs").exists(), "docs directory should exist"
    assert (project_root / "examples").exists(), "examples directory should exist"
    assert (project_root / "tests").exists(), "tests directory should exist"
    assert (project_root / "worklog").exists(), "worklog directory should exist"
    
    # Check that key files exist
    assert (project_root / "README.md").exists(), "README.md should exist"
    assert (project_root / "pyproject.toml").exists(), "pyproject.toml should exist"
    assert (project_root / "requirements.txt").exists(), "requirements.txt should exist"
    assert (project_root / "env.example").exists(), "env.example should exist"


def test_src_structure():
    """Test that the src directory has the expected structure."""
    src_dir = Path(__file__).parent.parent / "src"
    
    # Check core modules
    assert (src_dir / "core").exists(), "src/core directory should exist"
    assert (src_dir / "agents").exists(), "src/agents directory should exist"
    
    # Check key files
    assert (src_dir / "__init__.py").exists(), "src/__init__.py should exist"
    assert (src_dir / "main.py").exists(), "src/main.py should exist"
    assert (src_dir / "cli.py").exists(), "src/cli.py should exist"


def test_core_modules():
    """Test that core modules can be imported."""
    try:
        from src.core.config import Settings
        from src.core.models import BlogRequest, BlogPost, BlogType
        assert True, "Core modules should import successfully"
    except ImportError as e:
        pytest.fail(f"Failed to import core modules: {e}")


def test_agent_modules():
    """Test that agent modules can be imported."""
    try:
        from src.agents.base_agent import BaseAgent
        from src.agents.research_agent import ResearchAgent
        from src.agents.content_agent import ContentAgent
        from src.agents.code_agent import CodeAgent
        from src.agents.formatting_agent import FormattingAgent
        from src.agents.review_agent import ReviewAgent
        from src.agents.agent_orchestrator import AgentOrchestrator
        assert True, "Agent modules should import successfully"
    except ImportError as e:
        pytest.fail(f"Failed to import agent modules: {e}")


def test_blog_generator():
    """Test that the blog generator can be imported."""
    try:
        from src.core.blog_generator import BlogGenerator
        assert True, "BlogGenerator should import successfully"
    except ImportError as e:
        pytest.fail(f"Failed to import BlogGenerator: {e}")


def test_cli_import():
    """Test that the CLI module can be imported."""
    try:
        from src.cli import app
        assert True, "CLI app should import successfully"
    except ImportError as e:
        pytest.fail(f"Failed to import CLI app: {e}")


if __name__ == "__main__":
    # Run basic tests
    test_project_structure()
    test_src_structure()
    print("✅ Basic structure tests passed!")
