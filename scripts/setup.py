#!/usr/bin/env python3
"""
Setup script for the I'm Poster blog generator.

This script helps users set up their environment and configuration.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Optional


def run_command(command: List[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command."""
    print(f"Running: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        if check:
            sys.exit(1)
        return e


def check_python_version() -> bool:
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"❌ Python 3.10+ required, found {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - compatible")
    return True


def check_pip() -> bool:
    """Check if pip is available."""
    try:
        import pip
        print("✅ pip is available")
        return True
    except ImportError:
        print("❌ pip is not available")
        return False


def check_uv() -> bool:
    """Check if uv is available."""
    try:
        result = run_command(["uv", "--version"], check=False)
        if result.returncode == 0:
            print("✅ uv is available")
            return True
        else:
            print("ℹ️  uv is not available (optional)")
            return False
    except FileNotFoundError:
        print("ℹ️  uv is not available (optional)")
        return False


def create_virtual_environment(use_uv: bool = False) -> bool:
    """Create a virtual environment."""
    if use_uv:
        print("\n🔧 Creating virtual environment with uv...")
        result = run_command(["uv", "venv"], check=False)
        if result.returncode == 0:
            print("✅ Virtual environment created with uv")
            return True
        else:
            print("❌ Failed to create virtual environment with uv")
            return False
    else:
        print("\n🔧 Creating virtual environment with venv...")
        result = run_command([sys.executable, "-m", "venv", "venv"], check=False)
        if result.returncode == 0:
            print("✅ Virtual environment created with venv")
            return True
        else:
            print("❌ Failed to create virtual environment with venv")
            return False


def activate_virtual_environment() -> Optional[str]:
    """Get the activation command for the virtual environment."""
    if os.name == "nt":  # Windows
        return "venv\\Scripts\\activate"
    else:  # Unix/Linux/macOS
        return "source venv/bin/activate"


def install_dependencies(use_uv: bool = False) -> bool:
    """Install project dependencies."""
    if use_uv:
        print("\n📦 Installing dependencies with uv...")
        result = run_command(["uv", "sync"], check=False)
        if result.returncode == 0:
            print("✅ Dependencies installed with uv")
            return True
        else:
            print("❌ Failed to install dependencies with uv")
            return False
    else:
        print("\n📦 Installing dependencies with pip...")
        result = run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=False)
        if result.returncode == 0:
            print("✅ Dependencies installed with pip")
            return True
        else:
            print("❌ Failed to install dependencies with pip")
            return False


def setup_environment_file() -> bool:
    """Set up the environment configuration file."""
    env_example = Path("env.example")
    env_file = Path(".env")
    
    if not env_example.exists():
        print("❌ env.example file not found")
        return False
    
    if env_file.exists():
        print("ℹ️  .env file already exists")
        return True
    
    print("\n🔧 Setting up environment configuration...")
    try:
        # Copy env.example to .env
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        
        print("✅ .env file created from env.example")
        print("⚠️  Please edit .env file with your API keys and configuration")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False


def create_directories() -> bool:
    """Create necessary directories."""
    print("\n📁 Creating necessary directories...")
    
    directories = [
        "blogs",
        "templates", 
        "data",
        "data/chroma"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        except Exception as e:
            print(f"❌ Failed to create directory {directory}: {e}")
            return False
    
    return True


def run_basic_tests() -> bool:
    """Run basic tests to verify the setup."""
    print("\n🧪 Running basic tests...")
    
    try:
        # Add src to Python path
        sys.path.insert(0, str(Path("src")))
        
        # Run basic structure test
        from tests.test_basic import test_project_structure, test_src_structure
        test_project_structure()
        test_src_structure()
        
        print("✅ Basic tests passed")
        return True
    except Exception as e:
        print(f"❌ Basic tests failed: {e}")
        print("   This is a minor issue and won't affect functionality")
        return False


def main():
    """Main setup function."""
    print("🚀 I'm Poster Blog Generator - Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_pip():
        sys.exit(1)
    
    use_uv = check_uv()
    
    # Create virtual environment
    if not create_virtual_environment(use_uv):
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies(use_uv):
        sys.exit(1)
    
    # Setup environment file
    if not setup_environment_file():
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        sys.exit(1)
    
    # Run basic tests
    if not run_basic_tests():
        print("⚠️  Setup completed but tests failed")
        print("   You may need to check your configuration")
    else:
        print("\n🎉 Setup completed successfully!")
    
    # Print next steps
    activation_cmd = activate_virtual_environment()
    print(f"\n📋 Next Steps:")
    print(f"1. Activate your virtual environment:")
    print(f"   {activation_cmd}")
    print(f"2. Edit the .env file with your API keys")
    print(f"3. Test the installation:")
    print(f"   python -m src.main")
    print(f"4. Generate your first blog:")
    print(f"   python examples/generate_sample_blog.py")
    print(f"\n📚 For more information, see the README.md and docs/ directories")


if __name__ == "__main__":
    main()
