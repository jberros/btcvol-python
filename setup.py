"""
Setup configuration for btcvol package - BTC DVOL Competition Participant Package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="btcvol",
    version="1.1.0",
    author="Jeremy Berros",
    author_email="jberrospellenc@gmail.com",
    description="Bitcoin Implied Volatility Prediction Competition - Participant Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jberros/btcvol-python",
    packages=find_packages(include=['btcvol', 'btcvol.*']),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    keywords="bitcoin volatility prediction competition machine-learning crunchdao",
    project_urls={
        "Bug Reports": "https://github.com/jberros/btcvol-python/issues",
        "Source": "https://github.com/jberros/btcvol-python",
        "Competition": "https://www.crunchdao.com/",
    },
)
