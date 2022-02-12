============
jarn.viewdoc
============
------------------------------------
Python documentation viewer
------------------------------------

**viewdoc** is a Python package documentation viewer. It converts
reST-formatted text to HTML and displays it in a browser window.
The viewer is typically used to check a package's long description before
uploading it to PyPI.

Contents
========

* Installation_
* Usage_
* Options_
* Arguments_
* Configuration_
* `Known Issues`_
* Related_
* Changelog_

Installation
============

viewdoc works with Python 2.7 - 3.10 and all released versions of setuptools
and distribute.

Use ``pip install jarn.viewdoc`` to install the ``viewdoc`` script.

Usage
=====

``viewdoc [options] [rst-file|egg-dir]``

Options
=======

``-s style, --style=style, or --style``
    Select the custom style added to the HTML output.

``-b browser, --browser=browser``
    Select the browser used for display. For a list of names see the
    `webbrowser`_ module.

``-c config-file, --config-file=config-file``
    Use config-file instead of the default ``~/.viewdoc``.

``-l, --list-styles``
    List available styles and exit.

``-h, --help``
    Print the help message and exit.

``-v, --version``
    Print the version string and exit.

Arguments
=========

``rst-file``
    The reST file to view.

``egg-dir``
    The Python package whose long description to view.
    Defaults to the current working directory.

.. _`webbrowser`: https://docs.python.org/3/library/webbrowser.html#webbrowser.register

Configuration
=============

viewdoc reads style information from its configuration file
``~/.viewdoc``. Edit this file to add your own styles.

Built-in Styles
---------------

``plain``
    Browser default with margins.

``pypi``
    New PyPI style with Google Fonts.

``sans``
    PyPI-like style without Google Fonts (the default).


Known Issues
============

If you are on macOS Sierra be aware of https://bugs.python.org/issue30392. As
a workaround specify the browser on the command line::

    $ viewdoc -b safari

or use the configuration file::

    [viewdoc]
    browser = safari

Related
=======

Also see our Python package releaser `jarn.mkrelease`_.

.. _`jarn.mkrelease`: https://github.com/Jarn/jarn.mkrelease

