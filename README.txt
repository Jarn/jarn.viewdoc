============
jarn.viewdoc
============
---------------------------------
View Python package documentation
---------------------------------

**viewdoc** is a Python package documentation viewer. It converts
reST-formatted files to HTML and displays them in a browser window.

Installation
============

viewdoc requires Python 2.6. Use ``easy_install jarn.viewdoc`` to install
the ``viewdoc`` script. Then put it on your system PATH by e.g. symlinking
it to ``/usr/local/bin``.

Usage
=====

``viewdoc [options] [rst-file|egg-dir]``

Options
=======

``-h, --help``
    Print the help message and exit.

``-v, --version``
    Print the version string and exit.

``rst-file``
    The reST file to view.

``egg-dir``
    The Python package whose reST-formatted long description to view.
    Defaults to the current working directory.

