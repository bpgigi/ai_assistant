# Please install OpenAI SDK first: `pip3 install openai`
from pydantic_settings import BaseSettings,SettingsConfigDict

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

settings = Settings()

