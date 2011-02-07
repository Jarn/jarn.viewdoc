============
jarn.viewdoc
============
---------------------------------
View Python package documentation
---------------------------------

**viewdoc** is a Python package documentation viewer. It converts
reST-formatted files to HTML and displays them in a browser window.
It is typically used to check a package's long description before
uploading it to PyPI.

Installation
============

viewdoc requires Python 2.4 or higher. Use ``easy_install jarn.viewdoc`` to
install the ``viewdoc`` script. Then put it on your system PATH by e.g.
symlinking it to ``/usr/local/bin``.

**Upgrade Note:** If you have viewdoc 1.0 on your system, you must delete
your existing ``~/.viewdoc`` file in order to get the updated styles.

Usage
=====

``viewdoc [options] [rst-file|egg-dir]``

Options
=======

``-s style, --style=style``
    Select the custom styles added to the HTML output. Used to override the
    configuration file setting of the same name.

``-h, --help``
    Print the help message and exit.

``-v, --version``
    Print the version string and exit.

``rst-file``
    The reST file to view.

``egg-dir``
    The Python package whose long description to view.
    Defaults to the current working directory.

Configuration
=============

The program reads style information from its configuration file
``~/.viewdoc``. Edit this file to change the defaults and to add your own
styles.
