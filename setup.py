from setuptools import setup, find_packages

setup(
    name="slow_trade_detector",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.3",
        "numpy",
        "matplotlib",
        "scikit-learn",
        "jinja2",
        "pyodbc",
    ],
    python_requires=">=3.7",
)
