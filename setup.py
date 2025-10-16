from pathlib import Path
import re
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def get_version():
    """从 __init__.py 文件中读取版本号"""
    version_file = Path(__file__).parent / "pyncm" / "__init__.py"
    content = version_file.read_text(encoding="utf-8")

    major_match = re.search(r"__VERSION_MAJOR__\s*=\s*(\d+)", content)
    minor_match = re.search(r"__VERSION_MINOR__\s*=\s*(\d+)", content)
    patch_match = re.search(r"__VERSION_PATCH__\s*=\s*(\d+)", content)

    major = major_match.group(1)
    minor = minor_match.group(1)
    patch = patch_match.group(1)

    return f"{major}.{minor}.{patch}"


setuptools.setup(
    name="pyncm",
    version=get_version(),
    author="greats3an",
    author_email="greats3an@gmail.com",
    description="NeteaseCloudMusic APIs for Python 3.x 适用于 Python 3 的网易云音乐 API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/greats3an/pyncm",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=["requests", "httpx"],
    entry_points={"console_scripts": ["pyncm=pyncm.__main__:__main__"]},
    python_requires=">=3.8",
)
