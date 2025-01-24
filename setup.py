from setuptools import find_packages, setup

setup(
    name="fame",
    version="3.1.2",
    maintainer="Johannes Kirchmair",
    maintainer_email="johannes.kirchmair@univie.ac.at",
    packages=find_packages(),
    url="https://github.com/molinfo-vienna/fame.git",
    description="FAME 3: Prediction of Phase 1 and Phase 2 Sites of Metabolism (SoMs)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="GNU General Public License v3.0",
    include_package_data=True,
    install_requires=[
        "rdkit==2020.09.1",
        "pandas~=1.2.1",
        "sh~=1.14.3",
        "nerdd-module>=0.3.4",
        "platformdirs>=4",
        # install importlib-resources and importlib_metadata for old Python versions
        "importlib-resources>=5; python_version<'3.9'",
        "importlib_metadata>=4.6; python_version<'3.10'",
    ],
    extras_require={
        "dev": ["mypy", "ruff"],
        "test": [
            "pytest",
            "pytest-watch",
            "pytest-cov",
            "pytest-bdd==7.3.0",
            "hypothesis",
            "hypothesis-rdkit",
        ],
    },
    entry_points={
        "console_scripts": [
            "fame3=fame.__main__:main",
        ],
    },
)
