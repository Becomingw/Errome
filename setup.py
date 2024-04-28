from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fp:
    long_description = fp.read()
setup(
    name='Errome',
    version='0.3.1',
    packages=find_packages(),
    description='A program error or completion email notification tool.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='BecomingW',
    author_email='Becomingw@qq.com',
    url='https://github.com/Becomingw/Errome.git',
    include_package_data=True
)
