from setuptools import setup, find_packages

version = '1.0a1'

setup(name='jarn.viewdoc',
      version=version,
      description='View Python package documentation',
      long_description=open('README.txt').read() + '\n' +
                       open('CHANGES.txt').read(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 2',
      ],
      keywords='view rest docs',
      author='Jarn AS',
      author_email='info@jarn.com',
      url='http://www.jarn.com/',
      license='BSD',
      packages=find_packages(),
      namespace_packages=['jarn'],
      include_package_data=True,
      zip_safe=False,
      test_suite='jarn.viewdoc.tests',
      install_requires=[
          'setuptools',
          'docutils',
      ],
      entry_points={
          'console_scripts': 'viewdoc=jarn.viewdoc.viewdoc:main',
      },
)
