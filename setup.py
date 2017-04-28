from setuptools import setup
from setuptools.command.install import install
from chromedriver_binary.utils import get_chromedriver_filename, get_chromedriver_url, find_binary_in_path

import sys
import os
import zipfile
import shutil
import subprocess
try:
    from io import BytesIO
    from urllib.request import urlopen, URLError
except ImportError:
    from StringIO import StringIO as BytesIO
    from urllib2 import urlopen, URLError

__author__ = 'Daniel Kaiser <d.kasier@fz-juelich.de>'


def create_required_files():
    """
    Creates the files required for building a package.
    """
    # Manifest
    if not os.path.isfile('MANIFEST.in'):
        with open('MANIFEST.in', 'w') as manifest_in:
            manifest_in.write('include *.txt')
    # License
    if not os.path.isfile('LICENSE.txt'):
        shutil.copyfile('LICENSE', 'LICENSE.txt')
    # Readme in reST format
    if not os.path.isfile('README.txt'):
        subprocess.call(['pandoc', 'README.md', '-t', 'rst', '-o', 'README.txt'])

create_required_files()
with open('README.txt') as readme_file:
    long_description = readme_file.read()


class DownloadChromedriver(install):
    def run(self):
        """
        Downloads, unzips and installs chromedriver. 
        If a chromedriver binary is found in PATH it will be copied, otherwise downloaded.
        """
        chromedriver_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'chromedriver_binary')
        chromedriver_filename = find_binary_in_path(get_chromedriver_filename())
        if chromedriver_filename:
            print("\nChromedriver already installed at {}...\n".format(chromedriver_filename))
            new_filename = os.path.join(chromedriver_dir, get_chromedriver_filename())
            self.copy_file(chromedriver_filename, new_filename)
        else:
            chromedriver_bin = get_chromedriver_filename()
            chromedriver_filename = os.path.join(chromedriver_dir, chromedriver_bin)
            if not os.path.isfile(chromedriver_filename):
                print("\nDownloading Chromedriver...\n")
                if not os.path.isdir(chromedriver_dir):
                    os.mkdir(chromedriver_dir)
                url = get_chromedriver_url()
                try:
                    response = urlopen(url)
                    if response.getcode() != 200:
                        raise URLError('Not Found')
                except URLError:
                    raise RuntimeError('Failed to download chromedriver archive: {}'.format(url))
                archive = BytesIO(response.read())
                with zipfile.ZipFile(archive) as zip_file:
                    zip_file.extract(chromedriver_bin, chromedriver_dir)
            else:
                print("\nChromedriver already installed at {}...\n".format(chromedriver_filename))
            if not os.access(chromedriver_filename, os.X_OK):
                os.chmod(chromedriver_filename, 0o744)
        install.run(self)


setup(
    name="chromedriver-binary",
    version="2.29.2",
    author="Daniel Kaiser",
    author_email="daniel.kaiser94@gmail.com",
    description="Installer for chromedriver.",
    license="MIT",
    keywords="chromedriver chrome browser selenium splinter",
    url="https://github.com/danielkaiser/python-chromedriver-binary",
    packages=['chromedriver_binary'],
    package_data={
        'chromedriver_binary': ['chromedriver*']
    },
    long_description=long_description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Installation/Setup",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
    ],
    cmdclass={'install': DownloadChromedriver}
)