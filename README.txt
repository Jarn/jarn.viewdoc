============
jarn.viewdoc
============
------------------------------------
Python documentation viewer
------------------------------------

**viewdoc** is a Python package documentation viewer. It converts
reST-formatted text to HTML and displays it in a browser window.
It is typically used to check a package's long description before
uploading it to PyPI.

Also see `jarn.mkrelease`_.

.. _`jarn.mkrelease`: http://pypi.python.org/pypi/jarn.mkrelease

Installation
============

viewdoc requires Python 2.5 or higher. Use ``easy_install jarn.viewdoc`` to
install the ``viewdoc`` script. Then put it on your system PATH by e.g.
symlinking it to ``/usr/local/bin``.

**Upgrade Note:** If you have jarn.viewdoc < 1.3 installed, move away
your existing ``~/.viewdoc`` file to get the updated styles.

Usage
=====

``viewdoc [options] [rst-file|egg-dir]``

Options
=======

``-s style, --style=style, or --style``
    Select the custom style added to the HTML output. Used to override the
    configuration file setting of the same name.

``-l, --list-styles``
    List available styles and exit.

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

viewdoc reads style information from its configuration file
``~/.viewdoc``. Edit this file to add your own styles.

