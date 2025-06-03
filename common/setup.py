from setuptools import setup, find_packages

setup(
    name="common",
    version="0.1.0",
    packages=find_packages(),
   install_requires=[
        "pydantic>=2.0",
        "python-dotenv",
    ],
    include_package_data=True,
    zip_safe=False,
)
