from pydantic import BaseSettings, DirectoryPath


class Settings(BaseSettings):

    title: str = 'Demo'

    long_request_sleep_seconds: int = 3

    logs_dir: DirectoryPath = './logs'

    console_color_logs: bool = True

    remote_debugger: bool = False

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
