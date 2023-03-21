import setuptools



setuptools.setup(
    name='pcs-lambda-framework',
    version='0.0.1',
    author='PCS',
    author_email='https://productivecloudsolutions.com',
    description='Installation of PCS Package',
    long_description_content_type="text/markdown",
    url='https://github.com/Productive-Cloud-Solutions/PCS-Lambda-Framework',
    project_urls = {
    },
    license="",
    packages=['pcs/util', 'pcs/controllers', 'pcs/frameworks', 'pcs/test', 'pcs/models'],
    install_requires=[],
)