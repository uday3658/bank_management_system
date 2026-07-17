from setuptools import find_packages, setup

setup(
    name="bank_analytics",
    version="0.1.0",
    author="Uday Patel",
    description="Bank Transaction Analytics System — Streamlit + MySQL + Pandas analytics dashboard",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9",
)
