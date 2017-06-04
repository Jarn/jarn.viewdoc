============
jarn.viewdoc
============
------------------------------------
Python documentation viewer
------------------------------------

**viewdoc** is a Python package documentation viewer. It converts
reST-formatted text to HTML and displays it in a browser window.

viewdoc is typically used to check a package's long description before
uploading it to PyPI.

Installation
============

viewdoc works with Python 2.6 - 3.6 and all released versions of setuptools
and distribute.

Use ``pip install jarn.viewdoc`` to install the ``viewdoc`` script.

**Upgrade Note:** If you have jarn.viewdoc < 1.9 installed,
run ``viewdoc --upgrade`` to get the updated styles.

Usage
=====

``viewdoc [options] [rst-file | egg-dir]``

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

``--upgrade``
    Upgrade the configuration file.

``rst-file``
    The reST file to view.

``egg-dir``
    The Python package whose long description to view.
    Defaults to the current working directory.

Configuration
=============

viewdoc reads style information from its configuration file
``~/.viewdoc``. Edit this file to add your own styles.

