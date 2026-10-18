# Please install OpenAI SDK first: `pip3 install openai`
from pydantic_settings import BaseSettings,SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DEEPSEEK_",
        env_file=".env"
    )
    api_key: str
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-flash"
    reasoning_effort: str = "high"
    thinking_enabled: bool = True
    rag_top_k: int = Field(default=3, ge=1)
    rag_threshold: float = Field(default=0.5, ge=0.0, le=2.0)

settings = Settings()

