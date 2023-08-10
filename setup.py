from setuptools import setup, find_packages

from web3_reactor import version

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="web3-reactor",
    version=version,
    author="Majoson Chen",
    author_email="Majoson@qq.com",
    description="Asyncio Base Reactor for Web3，used to collect, process and react the data from blockchain.",
    long_description=long_description,
    keywords="web3, asyncio",
    long_description_content_type="text/markdown",
    url="https://github.com/web3-reactor/web3-reactor",
    packages=find_packages(exclude=["*.test", "*.test.*", "test"]),
    classifiers=[
        'Development Status :: 3 - Alpha',
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    license="MIT",
    # extras_require={
    #     'test': ["pytest"],
    # },
    # entry_points={
    #     'console_scripts': [
    #         'web3-reactor = cmd_tools:main'  # 格式为'命令名 = 模块名:函数名'
    #     ]
    # },
    python_requires='>=3.9',
)
