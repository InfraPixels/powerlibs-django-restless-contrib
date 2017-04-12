try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = '0.3.0'
requires = []

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='powerlibs-django-restless-contrib',
    version=version,
    description="Contrib moduls for Powerlibs Django Restless",
    long_description=readme,
    author='Cléber Zavadniak',
    author_email='cleberman@gmail.com',
    url='https://github.com/Dronemapp/powerlibs-django-restless-contrib',
    license=license,
    packages=['powerlibs.django.restless.contrib', 'powerlibs.django.restless.contrib.endpoints'],
    package_data={'': ['LICENSE', 'README.md']},
    include_package_data=True,
    install_requires=requires,
    zip_safe=False,
    keywords='generic libraries',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ),
)
