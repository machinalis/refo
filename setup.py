from distutils.core import setup
setup(
    name="REfO",
    version="0.12",
    description="Regular expressions for objects",
    long_description=open('README.txt').read(),
    author="Rafael Carrascosa",
    author_email="rafacarrascosa@gmail.com",
    url="https://github.com/machinalis/refo",
    keywords=["regular expressions", "regexp", "re", "objects", "classes"],
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing",
        "Topic :: Utilities",
        ],
    packages=["refo"],
)
