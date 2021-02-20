from pathlib import Path
from setuptools import setup, find_packages

readme = Path('README.md').read_text(encoding='utf-8')

setup(
    name='procemon',
    version="1.2.0",
    description='Procedurally generated trading card game',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/subalterngames/procemon',
    author='Seth Alter',
    author_email="subalterngames@gmail.com",
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    keywords='image pokemon card procgen',
    packages=find_packages(),
    include_package_data=True,
    install_requires=["requests", "markovify", "beautifulsoup4", "gensim", "numpy", "pillow", "fpdf",
                      "perlin-numpy @ git+https://github.com/pvigier/perlin-numpy"],
)
