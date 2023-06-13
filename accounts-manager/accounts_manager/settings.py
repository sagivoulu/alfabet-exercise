from pydantic import BaseSettings, DirectoryPath


class Settings(BaseSettings):

    title: str = 'Accounts Manager'

    logs_dir: DirectoryPath = './logs'

    console_color_logs: bool = True

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
