
pydeps
======

.. image:: https://readthedocs.org/projects/pydeps/badge/?version=latest
   :target: https://readthedocs.org/projects/pydeps/?badge=latest
   :alt: Documentation Status

.. image:: https://travis-ci.org/thebjorn/pydeps.svg
   :target: https://travis-ci.org/thebjorn/pydeps


.. image:: https://coveralls.io/repos/github/thebjorn/pydeps/badge.svg?branch=master
   :target: https://coveralls.io/github/thebjorn/pydeps?branch=master

.. image:: https://pepy.tech/badge/pydeps
   :target: https://pepy.tech/project/pydeps
   :alt: Downloads

Python module dependency visualization. This package installs the ``pydeps``
command, and normal usage will be to use it from the command line.

Version 1.7.2 includes a new flag, ``--no-output``, which prevents creation of the .svg/.png file.

Version 1.7.1 fixes excludes in .pydeps files (thanks to @eqvis for the bugreport).

New in version 1.7.0: The new ``--reverse`` flag reverses the direction of the arrows in the dependency graph, so they point _to_ the imported module instead of _from_ the imported module (thanks to @goetzk for the bugreport and @tobiasmaier for the PR!).

New in version 1.5.0: Python 3 support (thanks to @eight04 for the PR)

New in version 1.3.4: ``--externals`` will now include modules that haven't been installed (what ``modulefinder`` calls ``badmodules``).

New in version 1.2.8: A shortcut for finding the direct external dependencies of
a package was added::

    pydeps --externals mypackage

which will print a json formatted list of module names to the screen, e.g.::

    (dev) go|c:\srv\lib\dk-tasklib> pydeps --externals dktasklib
    [
        "dkfileutils"
    ]

which meaans that the ``dktasklib`` package only depends on the ``dkfileutils``
package.

This functionality is also available programatically::

    import os
    from pydeps.pydeps import externals
    # the directory that contains setup.py (one level up from actual package):
    os.chdir('package-directory')  
    print externals('mypackage')

New in version 1.2.5: The defaults are now sensible, such that::

    pydeps mypackage

will likely do what you want. It is the same as
``pydeps --show --max-bacon=2 mypackage`` which means display the
dependency graph in your browser, but limit it to two hops (which
includes only the modules that your module imports -- not continuing
down the import chain).  The old default behavior is available with
``pydeps --noshow --max-bacon=0 mypackage``.

To install::

    pip install pydeps

To create graphs you need to install Graphviz_ (make sure the ``dot``
command is on your path).

.. Note:: to display the resulting `.svg` files, ``pydeps`` by default
          calls ``firefox foo.svg``.  This is can be overridden with
          the ``--display PROGRAM`` option, where ``PROGRAM`` is an
          executable that can display the image file of the graph.

.. Note:: Please report bugs and feature requests on GitHub at
          https://github.com/thebjorn/pydeps/issues

This is the result of running ``pydeps`` on itself (``pydeps pydeps``):

.. image:: https://raw.githubusercontent.com/thebjorn/pydeps/master/docs/_static/pydeps.svg?sanitize=true


``pydeps`` also contains an Erdős-like scoring function (a.k.a. Bacon
number, from Six degrees of Kevin Bacon
(http://en.wikipedia.org/wiki/Six_Degrees_of_Kevin_Bacon) that lets
you filter out modules that are more than a given number of 'hops'
away from the module you're interested in.  This is useful for finding
the interface a module has to the rest of the world.


To find pydeps' interface to the Python stdlib (less some very common
modules).

::

    pydeps pydeps --show --max-bacon 2 --pylib -x os re types _* enum

.. image:: https://raw.githubusercontent.com/thebjorn/pydeps/master/docs/_static/pydeps-pylib.svg?sanitize=true

``--max-bacon 2`` (the default) gives the modules that are at most 2
hops away, and modules that belong together have similar colors.
Compare that to the output with the ``--max-bacon=0`` (infinite)
filter:

.. image:: https://raw.githubusercontent.com/thebjorn/pydeps/master/docs/_static/pydeps-pylib-all.svg?sanitize=true
   :width: 40%

All options can also be set in a ``.pydeps`` file using ``.ini`` file
syntax (parsable by ``ConfigParser``). Command line options override
options in the ``.pydeps`` file in the current directory, which again
overrides options in the user's home directory
(``%USERPROFILE%\.pydeps`` on Windows and ``${HOME}/.pydeps``
otherwise).

``pydeps`` can detect and display cycles with the ``--show-cycles``
parameter.  This will _only_ display the cycles, and for big libraries
it is not a particularly fast operation.  Given a folder with the
following contents (this uses yaml to define a directory structure,
like in the tests)::

        relimp:
            - __init__.py
            - a.py: |
                from . import b
            - b.py: |
                from . import a

``pydeps relimp --show-cycles`` displays:

.. image:: https://raw.githubusercontent.com/thebjorn/pydeps/master/docs/_static/pydeps-cycle.svg?sanitize=true

An attempt has been made to keep the intermediate formats readable,
eg. the output from ``pydeps --show-deps ..`` looks like this::

    ...
    "pydeps.mf27": {
        "imported_by": [
            "__main__",
            "pydeps.py2depgraph"
        ],
        "kind": "imp.PY_SOURCE",
        "name": "pydeps.mf27",
        "path": "pydeps\\mf27.py"
    },
    "pydeps.py2depgraph": {
        "imported_by": [
            "__main__",
            "pydeps.pydeps"
        ],
        "imports": [
            "pydeps.depgraph",
            "pydeps.mf27"
        ],
        "kind": "imp.PY_SOURCE",
        "name": "pydeps.py2depgraph",
        "path": "pydeps\\py2depgraph.py"
    }, ...

Usage::

    usage: pydeps [-h] [--config FILE] [--no-config] [--version] [-L LOG] [-v]
                  [-o file] [-T FORMAT] [--display PROGRAM] [--noshow]
                  [--show-deps] [--show-raw-deps] [--show-dot] [--nodot]
                  [--show-cycles] [--debug] [--noise-level INT] [--max-bacon INT]
                  [--pylib] [--pylib-all] [--include-missing]
                  [-x FNAME [FNAME ...]] [--externals] [--reverse]
                  fname

positional arguments:
  fname                 filename

optional arguments:
  -h, --help                             show this help message and exit
  --config FILE                          specify config file
  --no-config                            disable processing of config files
  --version                              print pydeps version
  -L LOG, --log LOG                      set log-level to one of CRITICAL, ERROR, WARNING,
                                         INFO, DEBUG, NOTSET.
  -v, --verbose                          be more verbose (-vv, -vvv for more verbosity)
  -o file                                write output to 'file'
  -T FORMAT                              output format (svg|png)
  --display PROGRAM                      program to use to display the graph (png or svg file
                                         depending on the T parameter)
  --noshow                               don't call external program to display graph
  --show-deps                            show output of dependency analysis
  --show-raw-deps                        show output of dependency analysis before removing
                                         skips
  --show-dot                             show output of dot conversion
  --nodot                                skip dot conversion
  --no-output                            don't create .svg/.png file, implies --no-show (-t/-o
  --sigmajs                              print sigma.js compatible json to stdout
                                         will be ignored)  
  --show-cycles                          show only import cycles
  --debug                                turn on all the show and verbose options
  --noise-level INT                      exclude sources or sinks with degree greater than
                                         noise-level
  --max-bacon INT                        exclude nodes that are more than n hops away
                                         (default=2, 0 -> infinite)
  --pylib                                include python std lib modules
  --pylib-all                            include python all std lib modules (incl. C modules)
  --x FNAME, --exclude FNAME             input files to skip (multiple file names can be provided)
  --externals                            create list of direct external dependencies
  --reverse                              draw arrows to (instead of from) imported modules



     
You can of course import ``pydeps`` from Python (look in the
``tests/test_relative_imports.py`` file for examples.

Contributing
------------
#. Fork it
#. Create your feature branch (git checkout -b my-new-feature)
#. Commit your changes (git commit -am 'Add some feature')
#. Push to the branch (git push origin my-new-feature)
#. Create new Pull Request


.. _Graphviz: http://www.graphviz.org/Download.php


