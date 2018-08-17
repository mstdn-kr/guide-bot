from setuptools import setup
from guidebot import __version__

setup(
    name="guide-bot",
    version=__version__,
    entry_points={
        'console_scripts': [
            'guidebot = guidebot.bot:main',
        ]
    }
)
