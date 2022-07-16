#!/usr/bin/env python

from setuptools import find_packages, setup


def main():
    return setup(
        author="Sijin Zhang",
        author_email="zsjzyhzp@gmail.com",
        version="1.0",
        description="MATSim visualization",
        maintainer="Sijin Zhang",
        maintainer_email="zsjzyhzp@gmail.com",
        name="MATSim-VIS",
        packages=find_packages(),
        data_files=[],
        zip_safe=False,
    )


if __name__ == "__main__":
    main()
