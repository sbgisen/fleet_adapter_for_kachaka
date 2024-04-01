import os  # noqa: C101
from glob import glob

from setuptools import setup

package_name = 'fleet_adapter_for_kachaka'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name, glob('config*.yaml')),
        (
            os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.xml'),
        ),

    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Yadunund',
    maintainer_email='yadunund@openrobotics.org',
    description='A RMF fleet adapter for kachaka',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'fleet_adapter=fleet_adapter_for_kachaka.fleet_adapter:main',
            'delivery_node=fleet_adapter_for_kachaka.delivery_node:main',
        ],
    },
)
