from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    jaeger_url: str = "http://jaeger:16686"
    prom_url: str = "http://prometheus:9090"
    loki_url: str = "http://loki:3100"
    ollama_url: str = "http://host.docker.internal:11434"
    model: str = "qwen3:8b"
    embed_model: str = "nomic-embed-text"
    chroma_path: str = "/data/chroma"
    agent_mode: str = "fixed"


settings = Settings()
