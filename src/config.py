"""
Configuration settings for Enterprise Knowledge Graph Platform
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    APP_NAME: str = "Enterprise Knowledge Graph Platform"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Base URIs (IMPORTANT: Configure for your organization)
    BASE_URI: str = os.getenv("BASE_URI", "https://enterprise-kg.local/")
    ONTOLOGY_NAMESPACE: str = os.getenv("ONTOLOGY_NAMESPACE", f"{BASE_URI}ontology/")
    DATA_NAMESPACE: str = os.getenv("DATA_NAMESPACE", f"{BASE_URI}data/")
    
    # Triple Store Configuration
    FUSEKI_URL: str = os.getenv("FUSEKI_URL", "http://localhost:3030")
    FUSEKI_DATASET: str = os.getenv("FUSEKI_DATASET", "enterprise_kg")
    FUSEKI_USERNAME: str = os.getenv("FUSEKI_USERNAME", "admin")
    FUSEKI_PASSWORD: str = os.getenv("FUSEKI_PASSWORD", "admin123")
    
    GRAPHDB_URL: str = os.getenv("GRAPHDB_URL", "http://localhost:7200")
    GRAPHDB_REPOSITORY: str = os.getenv("GRAPHDB_REPOSITORY", "enterprise_kg")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://ontology_user:ontology_pass@localhost:5432/ontology_db"
    )
    
    # Redis Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_WORKERS: int = int(os.getenv("API_WORKERS", "4"))
    
    # CORS
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # SPARQL Query Settings
    SPARQL_DEFAULT_TIMEOUT: int = int(os.getenv("SPARQL_DEFAULT_TIMEOUT", "30"))
    SPARQL_MAX_RESULTS: int = int(os.getenv("SPARQL_MAX_RESULTS", "10000"))
    SPARQL_ENABLE_CACHE: bool = os.getenv("SPARQL_ENABLE_CACHE", "True").lower() == "true"
    SPARQL_CACHE_TTL: int = int(os.getenv("SPARQL_CACHE_TTL", "300"))  # seconds
    
    # SHACL Validation Settings
    SHACL_INFERENCE: str = os.getenv("SHACL_INFERENCE", "rdfs")  # rdfs, owlrl, both, none
    SHACL_ADVANCED: bool = os.getenv("SHACL_ADVANCED", "True").lower() == "true"
    
    # Data Harmonization
    HARMONIZATION_NAMESPACE: str = os.getenv("HARMONIZATION_NAMESPACE", f"{BASE_URI}harmonized/")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")  # json or text
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))
    
    # Monitoring
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "True").lower() == "true"
    METRICS_PORT: int = int(os.getenv("METRICS_PORT", "9090"))
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


# Validation function
def validate_settings():
    """Validate critical settings."""
    errors = []
    
    if settings.ENVIRONMENT == "production":
        if settings.SECRET_KEY == "change-this-secret-key-in-production":
            errors.append("SECRET_KEY must be changed in production")
        
        if "example.com" in settings.BASE_URI:
            errors.append("BASE_URI should be configured with your domain in production")
        
        if settings.FUSEKI_PASSWORD == "admin123":
            errors.append("FUSEKI_PASSWORD should be changed in production")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    return True


# Print configuration summary (for debugging)
def print_config_summary():
    """Print configuration summary (excluding sensitive data)."""
    print("=" * 60)
    print(f"Application: {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Base URI: {settings.BASE_URI}")
    print(f"Fuseki URL: {settings.FUSEKI_URL}")
    print(f"GraphDB URL: {settings.GRAPHDB_URL}")
    print(f"Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'Not configured'}")
    print(f"Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
    print(f"API: {settings.API_HOST}:{settings.API_PORT}")
    print(f"SPARQL Cache: {'Enabled' if settings.SPARQL_ENABLE_CACHE else 'Disabled'}")
    print(f"Rate Limiting: {'Enabled' if settings.RATE_LIMIT_ENABLED else 'Disabled'}")
    print("=" * 60)


if __name__ == "__main__":
    validate_settings()
    print_config_summary()
