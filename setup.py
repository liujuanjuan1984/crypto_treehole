import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="crypto_treehole",
    version="0.2.5",
    author="liujuanjuan1984",
    author_email="qiaoanlu@163.com",
    description="a treehole bot server for mixin messenger and rum system (both crypto products)",
    keywords=["rumsystem", "quorum", "treehole", "mixin"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/liujuanjuan1984/crypto_treehole",
    project_urls={
        "Github Repo": "https://github.com/liujuanjuan1984/crypto_treehole",
        "Bug Tracker": "https://github.com/liujuanjuan1984/crypto_treehole/issues",
        "About Quorum": "https://github.com/rumsystem/quorum",
        "About Mixin": "https://github.com/MixinNetwork/mixin",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(exclude=["example"]),
    python_requires=">=3.8",
    install_requires=[
        "requests",
        "mixinsdk==0.2.1",
        "quorum-mininode-py>=1.2.1",
        "quorum-data-py>=1.1.5",
    ],
)
