from pathlib import Path
from setuptools import setup, find_packages

"""
readme = Path('README.md').read_text(encoding='utf-8')
readme = readme.replace('"https://raw.githubusercontent.com/alters-mit/magnebot/main/doc/images/reach_high.gif"',
                        '"https://github.com/alters-mit/magnebot/raw/main/social.jpg"')
"""

setup(
    name='procemon',
    version="0.0.1",
    description='Procedurally generated monsters',
    long_description="Procedurally generated monsters",
    long_description_content_type='text/markdown',
    url='???',
    author='Seth Alter',
    author_email="subalterngames@gmail.com",
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    keywords='image pokemon card procgen',
    packages=find_packages(),
    install_requires=["requests", "markovify", "beautifulsoup4"],
)
