from setuptools import setup, find_packages

version = '1.6'

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
      ],
      keywords='view rest docs',
      author='Stefan H. Holek',
      author_email='stefan@epy.co.at',
      url='http://pypi.python.org/pypi/jarn.viewdoc',
      license='BSD',
      packages=find_packages(),
      namespace_packages=['jarn'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'docutils',
      ],
      entry_points={
          'console_scripts': 'viewdoc=jarn.viewdoc.viewdoc:main',
      },
)
