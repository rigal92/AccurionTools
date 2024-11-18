import setuptools

setuptools.setup(
    name="pycurrion",
    version="1.0.0",
    author="Riccardo Galafassi",
    author_email="rigal@live.it",
    description="Package to manage accurion conversions",
    long_description="long_description missing",
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=['numpy','pandas','scimate', 'scipy'],
)
