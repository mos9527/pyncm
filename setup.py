from pathlib import Path
import re
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def get_version():
    """从 __init__.py 文件中读取版本号"""
    version_file = Path(__file__).parent / "pyncm_async" / "__init__.py"
    content = version_file.read_text(encoding="utf-8")

    major_match = re.search(r"__VERSION_MAJOR__\s*=\s*(\d+)", content)
    minor_match = re.search(r"__VERSION_MINOR__\s*=\s*(\d+)", content)
    patch_match = re.search(r"__VERSION_PATCH__\s*=\s*(\d+)", content)

    if not major_match or not minor_match or not patch_match:
        raise RuntimeError("Unable to find version components in pyncm_async/__init__.py")

    major = major_match.group(1)
    minor = minor_match.group(1)
    patch = patch_match.group(1)

    return f"{major}.{minor}.{patch}"


setuptools.setup(
    name="pyncm-async",
    version=get_version(),
    author="greats3an",
    author_email="greats3an@gmail.com",
    description="NeteaseCloudMusic APIs for Python 3.x 适用于 Python 3 的网易云音乐异步 API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/greats3an/pyncm/tree/async",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=["httpx"],
    python_requires=">=3.8",
)