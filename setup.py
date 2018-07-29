from setuptools import setup, find_packages

version = '2.2'

setup(name='jarn.viewdoc',
      version=version,
      description='Python documentation viewer',
      long_description=open('README.rst').read() + '\n' +
                       open('CHANGES.rst').read(),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
      ],
      keywords='view rest rst package docs rst2html long-description',
      author='Stefan H. Holek',
      author_email='stefan@epy.co.at',
      url='https://github.com/Jarn/jarn.viewdoc',
      license='BSD-2-Clause',
      packages=find_packages(),
      namespace_packages=['jarn'],
      include_package_data=True,
      zip_safe=False,
      test_suite='jarn.viewdoc.tests',
      install_requires=[
          'setuptools',
          'docutils >= 0.14',
          'pygments >= 2.2.0',
      ],
      entry_points={
          'console_scripts': 'viewdoc=jarn.viewdoc.viewdoc:main',
      },
)
