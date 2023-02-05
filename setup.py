from setuptools import setup

setup(
    name="troubadour",
    version="0.1",
    description=(
        "A simple framework to write client-side web text-based games with python"
    ),
    url="https://github.com/vlanore/troubadour",
    author="Vincent Lanore",
    author_email="vincent.lanore@gmail.com",
    license="MIT",
    packages=["troubadour"],
    install_requires=[
        "docopt",
        "termcolor",
    ],
    scripts=["bin/troubadour"],
)
