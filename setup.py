from setuptools import setup, find_packages

setup(
    name="ayova",
    version="2.0.0",
    description="AYOVA P2P - Device-based, trust-first secure messenger by Ayogwokhai Josemaria",
    author="Ayogwokhai Josemaria",
    packages=find_packages(),
    install_requires=[
        "click>=8.0",
        "rich>=13.0",
        "pynacl>=1.5",
        "asyncssh>=2.10",
        "cryptography>=41.0",
    ],
    entry_points={
        "console_scripts": [
            "ayova=ayova.cli:main",
        ],
    },
    python_requires=">=3.8",
)
