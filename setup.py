from setuptools import setup, find_packages

setup(
    name='Errome',
    version='0.2.1',
    packages=find_packages(),
    description='一个程序报错或运行完成时的邮件通知工具',
    long_description='未来补充，目前仅支持网易邮箱',
    author='BecomingW',
    author_email='Becomingw@qq.com',
    url='https://github.com/Becomingw/Errome.git',
    include_package_data=True,
    data_files=[('Errome', ['ok.html', 'erro.html'])], 
)
