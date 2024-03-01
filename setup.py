from setuptools import setup

setup(
    name='tradermade',
    version='0.8.0',    
    description='A package that helps you get Forex data from TraderMade data API',
    url='https://github.com/tradermade',
    author='TraderMade',
    author_email='support@tradermade.com',
    license='MIT',
    long_description=open('README.rst', 'r').read(),
    packages=['tradermade'],
    install_requires=['numpy>=1.16.4',
                      'pandas>=0.24.2',
                      'requests>=2.25.1',  
                      'websockets==8.1',                 
                      ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ],
)