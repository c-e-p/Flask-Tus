"""
Flask-Tus
-------------

Implements the tus.io server-side file-upload protocol
visit http://tus.io for more information

"""
from setuptools import setup


setup(
    name='Flask-Tus-Fork',
    version='0.7.0',
    url='http://github.com/c-e-p/Flask-Tus',
    license='MIT',
    author='Elena Palmer',
    author_email='c.elena.palmer@gmail.com',
    description='Fork of Matt Hoskins\' TUS protocol implementation',
    long_description=__doc__,
    py_modules=['flask_tus_fork'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
