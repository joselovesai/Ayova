from setuptools import setup, find_packages

setup(
    name="ayova",
    version="2.1.0",
    description="AYOVA P2P - Device-based, trust-first secure messenger with auto port forwarding by Ayogwokhai Josemaria",
    author="Ayogwokhai Josemaria",
    packages=find_packages(),
    install_requires=[
        "click>=8.0",
        "rich>=13.0",
        "pynacl>=1.5",
        "asyncssh>=2.10",
        "cryptography>=41.0",
        "miniupnpc>=2.0;platform_system!='Windows'",
    ],
    entry_points={
        "console_scripts": [
            "ayova=ayova.cli:main",
        ],
    },
    python_requires=">=3.8",
)
