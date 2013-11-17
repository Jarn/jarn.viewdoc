from setuptools import setup, find_packages

version = '2.0'

setup(name='jarn.viewdoc',
      version=version,
      description='Python documentation viewer',
      long_description=open('README.txt').read() + '\n' +
                       open('CHANGES.txt').read(),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
      ],
      keywords='view rest package docs',
      author='Stefan H. Holek',
      author_email='stefan@epy.co.at',
      url='http://pypi.python.org/pypi/jarn.viewdoc',
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
      use_2to3=True,
)
