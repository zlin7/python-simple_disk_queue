import os
from pathlib import Path

from setuptools import find_packages, setup


def create_setting_folder():
    """Create the setting folder
    """
    SETTING_PATH = os.path.join(Path.home(), '.cache', 'simple_disk_queue')
    if not os.path.isdir(SETTING_PATH):
        os.makedirs(SETTING_PATH)


with open('README.md', encoding='utf-8') as readme_file:
    README = readme_file.read()

with open('HISTORY.md', encoding='utf-8') as history_file:
    HISTORY = history_file.read()

setup_args = dict(
    name='simple_disk_queue',
    version='0.0.3',
    description='Create a disk-based queue',
    long_description_content_type="text/markdown",
    long_description=README + '\n\n' + HISTORY,
    license='MIT',
    packages=find_packages(),
    author='Zhen Lin',
    author_email='zhenlin4@illinois.edu',
    keywords=['Job Scheduler', 'Disk-based Queue', 'Disk Queue Scheduler'],
    url='https://github.com/zlin7/python-simple_disk_queue',
)

install_requires = [
    'filelock>=3.9.0'
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)
    create_setting_folder()