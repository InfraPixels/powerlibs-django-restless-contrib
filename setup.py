import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = '0.28.1'


def pip_git_to_setuptools_git(url):
    match = re.match(r'git\+https://github.com/(?P<organization>[^/]+)/(?P<repository>[^/]+).git@(?P<tag>.+)', url.strip())
    if match:
        url = 'http://github.com/{organization}/{repository}/tarball/master#egg={tag}'.format(
            **match.groupdict()
        )
    return url


requires = []
dependency_links = []
with open('requirements/production.txt') as requirements_file:
    for line in requirements_file:
        if 'git+http' in line:
            dependency_links.append(pip_git_to_setuptools_git(line))
        else:
            requires.append(line)

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
    packages=['powerlibs.django.restless.contrib.endpoints'],
    package_data={'': ['LICENSE', 'README.md']},
    include_package_data=True,
    install_requires=requires,
    dependency_links=dependency_links,
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
