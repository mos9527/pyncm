import setuptools, pyncm_async

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyncm-async",
    version=pyncm_async.__version__,
    author="greats3an",
    author_email="greats3an@gmail.com",
    description="NeteaseCloudMusic APIs for Python 3.x 适用于 Python 3 的网易云音乐异步 API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/greats3an/pyncm",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=["httpx"],    
    python_requires=">=3.8",
)
