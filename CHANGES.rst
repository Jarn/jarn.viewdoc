Changelog
=========

2.5 - Unreleased
----------------

- Support Python 2.7 - 3.11.
  [stefan]

- Do not require setup.py or setup.cfg if pyproject.toml exists.
  [stefan]

- Filter some deprecation warnings.
  [stefan]

- Warn if long_description metadata is missing.
  [stefan]

2.4 - 2022-02-26
----------------

- Support Python 2.7 - 3.10.
  [stefan]

- Fix code block background color in ``pypi`` style.
  [stefan]

- Keep links underlined in ``pypi`` style.
  [stefan]

- Add output colors.
  [stefan]

- Do not require setup.py if setup.cfg exists.
  [stefan]

- Move metadata to setup.cfg.
  [stefan]

- Move tests out of ``jarn.viewdoc`` namespace.
  [stefan]

- Include tests in sdist but not in wheel.
  [stefan]

2.3 - 2019-01-28
----------------

- Support ``python -m jarn.viewdoc``.
  [stefan]

2.2 - 2019-01-25
----------------

- Drop Python 2.6 support, add Python 3.7.
  [stefan]

- Update styles in light of new PyPI (warehouse).
  [stefan]

- Default to ``sans`` style because new PyPI uses Google Fonts.
  [stefan]

- Convert dashes to underscores in config parser optionxform.
  [stefan]

2.1 - 2017-10-06
----------------

- Add MANIFEST.in.
  [stefan]

2.0 - 2017-07-20
----------------

- Update ``pypi`` stylesheet (grey code blocks).
  [stefan]

- Automatically upgrade stylesheet information.
  [stefan]

- Add -b option to specify the browser to use.
  [stefan]

- Protect against bad or incomplete locale settings.
  [stefan]

1.8 - 2017-01-30
----------------

- Support Python 2.6 - 3.6 without 2to3.
  [stefan]

1.7 - 2014-03-22
----------------

- Update PyPI stylesheet links in the face of new python.org.
  [stefan]

- Add new ``pypi`` style and rename previous one to ``classic``.
  [stefan]

1.6 - 2013-11-21
----------------

- Support Python 3.x.
  [stefan]

1.5 - 2012-07-11
----------------

- Restore Python 2.5 compatibility.
  [stefan]

1.4 - 2011-11-25
----------------

- Warn if ``~/.viewdoc`` has errors instead of raising an exception.
  [stefan]

1.3 - 2011-10-31
----------------

- Be more careful with what we put on the PYTHONPATH.
  [stefan]

- Add ``small`` style to the default config.
  [stefan]

1.2 - 2011-07-19
----------------

- Pass the PYTHONPATH to subprocesses.
  [stefan]

- Avoid temp file when extracting the long description.
  [stefan]

- Add -l option to list available styles.
  [stefan]

- Add --*style* shortcut for -s *style*.
  [stefan]

1.1 - 2011-02-08
----------------

- Add -s option to select styles on the command line.
  [stefan]

- In ``pypi`` style, only underline reference links.
  [stefan]

1.0 - 2010-12-30
----------------

- Initial release
  [stefan]

