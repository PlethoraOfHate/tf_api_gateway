from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='tf_api_gateway',
      version='0.2',
      description='Wrapper for the Terraform Enterprise API',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
      ],
      url='http://github.com/PlethoraOfHate/tf_api_gateway',
      download_url='https://github.com/PlethoraOfHate/tf_api_gateway/archive/0.1.tar.gz',
      author='Stephen Mercier',
      author_email='stephen.mercier@gmail.com',
      license='Apache License 2.0',
      keywords=['terraform', 'atlas'],
      packages=['tf_api_gateway'],
      include_package_data=True,
      zip_safe=False)