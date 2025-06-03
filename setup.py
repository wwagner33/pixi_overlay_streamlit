from setuptools import setup, find_packages

setup(
    name="pixi_overlay_component",
    version="0.1.0",
    author="Seu Nome",
    author_email="seuemail@example.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "streamlit>=1.34.0",
    ],
)
