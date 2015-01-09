from distutils.core import setup

setup(
    name='ACHFileCreatorV4',
    version='0.0.1',
    packages=['argparse', 'pymssql', 'datetime', 'unittest'],
    url='',
    license='',
    author='Morgan Thrapp',
    author_email='mpthrapp@gmail.com',
    description='This script was written to create ACH Files for our Tax and Utility billing systems.',
    requires=['pymssql']
)
