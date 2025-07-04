"""
Setup script for LoRA the Explorer
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="lora-the-explorer",
    version="1.0.0",
    author="LoRA the Explorer",
    author_email="pneill@gmail.com",
    description="Advanced FLUX LoRA manipulation toolkit with GUI interface for layer targeting, subtraction, and compatibility fixes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/lora-the-explorer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Graphics",
        "Environment :: X11 Applications",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-cov>=5.0.0",
            "black>=24.0.0",
            "ruff>=0.1.0",
            "mypy>=1.8.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=2.0.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="lora, flux, stable-diffusion, ai, gui, layer-targeting",
    project_urls={
        "Bug Reports": "https://github.com/your-username/lora-the-explorer/issues",
        "Documentation": "https://github.com/your-username/lora-the-explorer/blob/main/README.md",
        "Source": "https://github.com/your-username/lora-the-explorer",
        "Support": "https://buymeacoffee.com/loratheexplorer",
    },
)