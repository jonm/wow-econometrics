from setuptools import setup, find_packages
setup(
    name="wowecon_make_training_dataset",
    version="0.1.4",
    namespace_packages=['wowecon'],
    packages=['wowecon','wowecon.training'],
    scripts=['make_training_dataset.py'],
    install_requires=['boto3==1.7.24',
                      'pytz==2018.4',
                      'humanfriendly==4.16.1'],
    package_data={
        '':['LICENSE']
        },
    author="Jon Moore",
    license="GPLv3",
    url="https://github.com/jonm/wow-econometrics"
)
