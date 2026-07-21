from setuptools import setup, find_packages

setup(
    name="mcp-sap-gui",
    version="0.1.3",
    description="MCP server for SAP GUI automation",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "mcp>=1.2.1",
        "pywin32>=306",
        "pillow>=10.2.0",
        "pyautogui>=0.9.54",
        "python-dotenv>=1.0.0",
        "psutil>=5.9.0",
        "mss>=9.0.1"
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.4",
            "black>=23.12.1",
            "isort>=5.13.2",
            "mypy>=1.8.0"
        ]
    }
)
