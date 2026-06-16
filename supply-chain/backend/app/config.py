import os


class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv('JWT_SECRET', 'change-this-in-production')
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{os.getenv('POSTGRES_USER', 'campus')}:"
        f"{os.getenv('POSTGRES_PASSWORD', 'campus_dev_2026')}@"
        f"{os.getenv('POSTGRES_HOST', 'localhost')}:"
        f"{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_DB', 'supply_chain')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

    # Elasticsearch
    ES_HOST = os.getenv('ES_HOST', 'localhost')
    ES_PORT = int(os.getenv('ES_PORT', 9200))

    # AI
    AI_PROVIDER = os.getenv('AI_PROVIDER', 'openai')
    AI_API_KEY = os.getenv('AI_API_KEY', '')
    AI_API_BASE = os.getenv('AI_API_BASE', 'https://api.openai.com/v1')
    AI_MODEL = os.getenv('AI_MODEL', 'gpt-4o')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
