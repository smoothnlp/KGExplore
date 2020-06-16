import setuptools
import os

rootdir = os.path.abspath(os.path.dirname(__file__))
long_description = open(os.path.join(rootdir, 'README.md'),encoding="utf-8").read()

setuptools.setup(
    name="kgexplore",
    version="0.1.2",
    author="SmoothNLP Organization",
    author_email="contact@smoothnlp.com",
    description="Python Package for Knowledge Exploration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/smoothnlp/kgexplore",
    packages=setuptools.find_packages(),
    package_data={'kgexplore': ['resources/simhei/*',"resources/*"]},
    install_requires=[
        'request',
      ],
    keywords=["Knowledge Graph","Business"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # test_suite = "kgexplore.unittest.testall",
)
