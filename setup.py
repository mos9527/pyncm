import setuptools, pyncm

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyncm",
    version=pyncm.__version__,
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
    install_requires=["requests"],
    entry_points={"console_scripts": ["pyncm=pyncm.__main__:__main__"]},
    python_requires=">=3.6",
)
