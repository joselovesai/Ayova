from setuptools import setup, find_packages

setup(
    name="ayova",
    version="1.0.0",
    description="AYOVA - Secure encrypted message vault CLI with gradient aesthetics",
    author="Ayogwokhai Jose Maria",
    packages=find_packages(),
    install_requires=[
        "click>=8.0",
        "rich>=13.0",
        "cryptography>=41.0",
    ],
    entry_points={
        "console_scripts": [
            "ayova=ayova.cli:main",
        ],
    },
    python_requires=">=3.8",
)
