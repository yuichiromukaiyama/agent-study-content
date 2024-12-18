from pydantic_settings import BaseSettings, SettingsConfigDict


class Configs(BaseSettings):
    model_config = SettingsConfigDict(
        validate_default=True,
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    AZURE_OPENAI_COMPLETION_DEPLOYMENT_NAME: str
    AZURE_OPENAI_COMPLETION_ENDPOINT: str
    AZURE_OPENAI_COMPLETION_API_KEY: str
    AZURE_OPENAI_COMPLETION_API_VERSION: str


configs = Configs()  # type: ignore
