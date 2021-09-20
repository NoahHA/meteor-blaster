from setuptools import setup

setup(
    name='MeteorBlaster',
    version='1.0',
    description='2D Space-Based Shooting Game',
    author='Noah Hirst-Ashuach',
    packages=['meteor_blaster'],
    install_requires=['pygame'],
    license='MIT License',
    long_description=open('README.md').read(),
)
