from setuptools import setup

CLASSIFIERS = [
    "Development Status :: Beta",
    "Environment :: Web Environment",
    "Framework :: Django",
    "Framework :: Django :: 1.11",
    "Framework :: Django :: 2.0",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: BSD License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Topic :: Software Development",
    "Topic :: Software Development :: Libraries :: Application Frameworks",
]

setup(
    name="db_saver",
    version='0.0.1',
    author="Noors Ergesh",
    author_email="jackmovies01@gmail.com",
    description="Django plug for backups and load it into DROPBOX",
    url="https://github.com/NursErgesh/django_backup.git",
    packages=("django_backup",),
    include_package_data=True,
    install_requires=open('requirements/requirements.txt').read().splitlines(),
    tests_require=open('requirements/test.txt').read().splitlines(),
    classifiers=CLASSIFIERS,
    zip_safe=False,
)
