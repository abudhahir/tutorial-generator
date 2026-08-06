"""
Configuration management for the I'm Poster blog generator.
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # API Keys
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    
    # Database Configuration
    chroma_host: str = Field("localhost", env="CHROMA_HOST")
    chroma_port: int = Field(8000, env="CHROMA_PORT")
    chroma_persist_directory: str = Field("./data/chroma", env="CHROMA_PERSIST_DIRECTORY")
    
    # Application Settings
    log_level: str = Field("INFO", env="LOG_LEVEL")
    debug: bool = Field(False, env="DEBUG")
    environment: str = Field("development", env="ENVIRONMENT")
    
    # Server Configuration
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8000, env="PORT")
    reload: bool = Field(True, env="RELOAD")
    
    # MCP Configuration
    mcp_server_url: str = Field("http://localhost:8001", env="MCP_SERVER_URL")
    mcp_enabled: bool = Field(True, env="MCP_ENABLED")
    
    # Ollama Configuration
    ollama_base_url: str = Field("http://localhost:11434", env="OLLAMA_BASE_URL")
    default_ollama_model: str = Field("gemma3:4b", env="DEFAULT_OLLAMA_MODEL")
    
    # LM Studio Configuration
    lm_studio_base_url: str = Field("http://localhost:1234", env="LM_STUDIO_BASE_URL")
    default_lm_studio_model: str = Field("local-model", env="DEFAULT_LM_STUDIO_MODEL")
    
    # Blog Generation Settings
    default_model: str = Field("gpt-4", env="DEFAULT_MODEL")
    default_temperature: float = Field(0.7, env="DEFAULT_TEMPERATURE")
    max_tokens: int = Field(4000, env="MAX_TOKENS")
    
    # LangChain Verbose Settings
    langchain_verbose: bool = Field(False, env="LANGCHAIN_VERBOSE")
    langchain_tracing: bool = Field(False, env="LANGCHAIN_TRACING")
    
    # LangSmith Configuration (for observability - optional)
    langsmith_api_key: Optional[str] = Field(None, env="LANGCHAIN_API_KEY")
    langsmith_endpoint: Optional[str] = Field(None, env="LANGCHAIN_ENDPOINT")
    langsmith_project: Optional[str] = Field(None, env="LANGCHAIN_PROJECT")
    
    # Output Settings
    blog_output_dir: str = Field("./blogs", env="BLOG_OUTPUT_DIR")
    template_dir: str = Field("./templates", env="TEMPLATE_DIR")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
