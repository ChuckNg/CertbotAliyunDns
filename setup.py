from setuptools import setup
from setuptools import find_packages

VERSION = "0.0.1.dev0"

INSTALL_REQUIRES = [
    "zope.interface==4.6.0",
    "certbot",
    "aliyun-python-sdk-alidns",
    "aliyun-python-sdk-core-v3"
]

setup(
    name="certbot-dns-aliyun",
    version=VERSION,
    description="Aliyun DNS Authenticator plugin for Certbot",
    python_requires="==3.6.*",
    author_email="554574099@qq.com",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Security",
        "Topic :: System :: Installation/Setup",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],

    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,

    entry_points={
        'certbot.plugins': [
            'dns-aliyun = certbot_dns_aliyun.dns_aliyun:Authenticator',
        ],
    }, 
)

