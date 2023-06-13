from pydantic import BaseSettings, DirectoryPath, SecretStr


class Settings(BaseSettings):
    title: str = 'Advances service'
    logs_dir: DirectoryPath = './logs'
    console_color_logs: bool = True

    db_connection_string: SecretStr

    redis_url: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
