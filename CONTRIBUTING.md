# Contributing guidelines

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

## Types of Contributions

You can contribute in many ways:

### Report Bugs

Report bugs at https://github.com/IFCA/deepaas/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* If you can, provide detailed steps to reproduce the bug.
* If you don't have steps to reproduce the bug, just note your observations in
  as much detail as you can. Questions to start a discussion about the issue
  are welcome.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug"
is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "please-help" is open to whoever wants to implement it.

Please do not combine multiple feature enhancements into a single pull request.

Note: this project is very conservative, so new features that aren't tagged
with "please-help" might not get into core. We're trying to keep the code base
small, extensible, and streamlined. Whenever possible, it's best to try and
implement feature ideas as separate projects outside of the core codebase.

### Write Documentation

cASO could always use more documentation, whether as part of the official cASO
docs, in docstrings, or even on the web in blog posts, articles, and such.

If you want to review your changes on the documentation locally, you can do::

    pip install -r docs/requirements.txt
    make servedocs

This will compile the documentation, open it in your browser and start
watching the files for changes, recompiling as you save.

### Submit Feedback

The best way to send feedback is to file an issue at the follwing URL:

    https://github.com/IFCA/deepaas/issues

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

## Setting Up the Code for Local Development

Here's how to set up `deepaas` for local development.

1. Fork the `deepaas` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/deepaas.git

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up your fork for local development::

    $ mkvirtualenv deepaas
    $ cd deepaas/
    $ python setup.py develop

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

Now you can make your changes locally.

5. When you're done making changes, check that your changes pass the tests and
   the style checks (pep8, flake8 and
   https://docs.openstack.org/hacking/latest/):

    $ pip install tox
    $ tox

Please note that tox runs the style tests automatically, since we have a test
environment for it (named pep8).

If you feel like running only the pep8 environment, please use the following
command::

    $ tox -e pep8

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Check that the test coverage hasn't dropped::

    $ tox -e cover

8. Submit a pull request through the GitHub website.


## Contributor Guidelines

### Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 2.7, 3.4, 3.6 on Travis CI.
4. Check https://travis-ci.org/IFCA/deepaas/pull_requests to ensure the tests pass
   for all supported Python versions and platforms.

### Coding Standards

* PEP8
* We follow the OpenStack Style Guidelines: https://docs.openstack.org/hacking/latest/user/hacking.html#styleguide
* Write new code in Python 3.

## Testing with tox

Tox uses `py.test` under the hood, hence it supports the same syntax for selecting tests.

For further information please consult the `pytest usage docs`_.

To run a particular test class with tox::

    $ tox -e py '-k TestCasoManager'

To run some tests with names matching a string expression::

    $ tox -e py '-k generate'

Will run all tests matching "generate", test_generate_files for example.

To run just one method::

    $ tox -e py '-k "TestCasoManager and test_required_fields"'

To run all tests using various versions of python in virtualenvs defined in tox.ini, just run tox.::

    $ tox

This configuration file setup the pytest-cov plugin and it is an additional
dependency. It generate a coverage report after the tests.

It is possible to tests with some versions of python, to do this the command
is:

    $ tox -e py27,py34

Will run py.test with the python2.7, python3.4 and pypy interpreters, for
example.
