from setuptools import setup

setup(
    name='biblioapp',
    packages=['biblioapp'],
    include_package_data=True,
    install_requires=[
        'flask',
        'requests',
	    'bootstrap-flask',
        'flask-mysql',
        'flask-login',
        'flask-mail',
        'pyjwt',
        'flask-session',
        'flask-cors',
        'pytest'
    ],
)
