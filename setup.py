import setuptools

pkg_name = "spikeforest2"

setuptools.setup(
    name=pkg_name,
    version="0.1.0",
    author="Jeremy Magland",
    author_email="jmagland@flatironinstitute.org",
    description="SpikeForest -- spike sorting analysis for website -- version 2",
    packages=setuptools.find_packages() + setuptools.find_namespace_packages(include=['spikeforest2.*']),
    scripts=[
        'bin/sf-sort'
    ],
    install_requires=[
        'python-frontmatter',
        'spikeextractors',
        'scipy', 'pandas', 'pymongo'
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    )
)
