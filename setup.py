from setuptools import setup, find_packages

setup(
    name="timelapse-creator",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'opencv-python>=4.5.0',
        'pillow>=8.0.0',
        'rawpy>=0.17.0',
        'numpy>=1.19.0',
    ],
    entry_points={
        'console_scripts': [
            'timelapse-creator=src.timelapse_creator:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple application to create timelapses from photos",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/timelapse-creator",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
) 