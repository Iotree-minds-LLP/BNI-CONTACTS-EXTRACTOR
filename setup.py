from setuptools import setup
import sys
sys.setrecursionlimit(10000)  # Set a higher value for recursion limit

setup(
    app=['main.py'],
    setup_requires=['py2app'],
    install_requires=[
        'selenium',
        'beautifulsoup4',
        'pandas',
    ]
)