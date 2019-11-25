from setuptools import setup

setup(
    name='biblioapp',
    packages=['biblioapp'],
    include_package_data=True,
    install_requires=[
        'flask',
        'requests',
	'flask_bootstrap',
        'flask-mysql'
    ],
)
