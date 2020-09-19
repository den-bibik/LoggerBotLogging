from setuptools import find_packages, setup

setup(
    name='LoggerBotLogging',
    version='0.1',
    packages=find_packages('.', include=['bot_logging', 'bot_logging.*']),
    url='',
    author='mc-wesban',
    author_email='wesban1@gmail.com',
    description='Logger package that can work with LoggerBotLoggingServer',
    classifiers=[
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: Implementation :: CPython",
    ]
)
