from distutils.core import setup

setup(
    name='pyACH',
    version='1.0',
    packages=['pyach'],
    url='https://github.com/morganthrapp/pyACH',
    license='MIT',
    author='Morgan Thrapp',
    author_email='mpthrapp@gmail.com',
    description='A package to create NACHA files with Python.',
    requires=['holidays']
)
