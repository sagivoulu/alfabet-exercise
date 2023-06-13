from pydantic import BaseSettings, DirectoryPath, SecretStr


class Settings(BaseSettings):
    title: str = 'Accounts Manager'
    logs_dir: DirectoryPath = './logs'
    console_color_logs: bool = True

    db_connection_string: SecretStr

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
