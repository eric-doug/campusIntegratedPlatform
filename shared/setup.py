from setuptools import setup, find_packages

setup(
    name='campus-shared',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'flask>=3.0',
        'sqlalchemy>=2.0',
        'psycopg2-binary>=2.9',
        'redis>=5.0',
        'elasticsearch>=8.0',
        'pyjwt>=2.8',
        'bcrypt>=4.1',
        'openai>=1.0',
        'python-dotenv>=1.0',
    ],
)
