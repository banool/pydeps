# -*- coding: utf-8 -*-
"""cli entrypoints.
"""
from __future__ import print_function
import json
import os
import pprint
import sys
from . import py2depgraph, cli, dot, target
from .depgraph2dot import dep2dot, cycles2dot
import logging
log = logging.getLogger(__name__)


def _pydeps(trgt, **kw):
    # Pass args as a **kw dict since we need to pass it down to functions
    # called, but extract locally relevant parameters first to make the
    # code prettier (and more fault tolerant).
    show_cycles = kw.get('show_cycles')
    nodot = kw.get('nodot')
    no_output = kw.get('no_output')
    output = kw.get('output')
    fmt = kw['format']
    show_svg = kw.get('show')
    reverse = kw.get('reverse')
    if os.getcwd() != trgt.workdir:
        # the tests are calling _pydeps directoy
        os.chdir(trgt.workdir)

    dep_graph = py2depgraph.py2dep(trgt, **kw)

    if kw.get('show_deps'):
        cli.verbose("DEPS:")
        pprint.pprint(dep_graph)

    import_times_file = kw.get('import_times_file')
    if import_times_file:
        add_import_times(dep_graph, import_times_file)

    print(dep_graph)

    dotsrc = depgraph_to_dotsrc(dep_graph, show_cycles, nodot, reverse)

    if not nodot:
        if kw.get('show_dot'):
            cli.verbose("DOTSRC:")
            print(dotsrc)

        if not no_output:
            svg = dot.call_graphviz_dot(dotsrc, fmt)

            with open(output, 'wb') as fp:
                cli.verbose("Writing output to:", output)
                fp.write(svg)

            if show_svg:
                dot.display_svg(kw, output)


def add_import_times(dep_graph, import_times_file):
    IGNORED = ["main", "__main__"]
    import_times = {}
    with open(import_times_file, "r") as f:
        content = f.read().splitlines()
        for l in content:
            if l.startswith("import time: "):
                s = l.split()
                import_times[s[6]] = s[2]
    for imp, v in dep_graph.sources.items():
        if imp in IGNORED:
            import_time = 0
        elif imp in import_times:
            import_time = int(import_times[imp])
        else:
            raise RuntimeError("Import times file incomplete, missing {}".format(imp))
        v.import_time = import_time

def depgraph_to_dotsrc(dep_graph, show_cycles, nodot, reverse):
    """Convert the dependency graph (DepGraph class) to dot source code.
    """
    if show_cycles:
        dotsrc = cycles2dot(dep_graph, reverse=reverse)
    elif not nodot:
        dotsrc = dep2dot(dep_graph, reverse=reverse)
    else:
        dotsrc = None
    return dotsrc


def externals(trgt, **kwargs):
    """Return a list of direct external dependencies of ``pkgname``.
       Called for the ``pydeps --externals`` command.
    """
    kw = dict(
        T='svg', config=None, debug=False, display=None, exclude=[], externals=True,
        format='svg', max_bacon=2**65, no_config=True, nodot=False,
        noise_level=2**65, noshow=True, output=None, pylib=True, pylib_all=True,
        show=False, show_cycles=False, show_deps=False, show_dot=False,
        show_raw_deps=False, verbose=0, include_missing=True,
    )
    kw.update(kwargs)
    depgraph = py2depgraph.py2dep(trgt, **kw)
    pkgname = trgt.fname
    log.info("DEPGRAPH: %s", depgraph)
    pkgname = os.path.splitext(pkgname)[0]

    res = {}
    ext = set()

    for k, src in list(depgraph.sources.items()):
        if k.startswith('_'):
            continue
        if not k.startswith(pkgname):
            continue
        if src.imports:
            imps = [imp for imp in src.imports if not imp.startswith(pkgname)]
            if imps:
                for imp in imps:
                    ext.add(imp.split('.')[0])
                res[k] = imps
    # return res  # debug
    return list(sorted(ext))


def pydeps(**args):
    """Entry point for the ``pydeps`` command.

       This function should do all the initial parameter and environment
       munging before calling ``_pydeps`` (so that function has a clean
       execution path).
    """
    _args = args if args else cli.parse_args(sys.argv[1:])
    inp = target.Target(_args['fname'])
    log.debug("Target: %r", inp)

    if _args.get('output'):
        _args['output'] = os.path.abspath(_args['output'])
    else:
        _args['output'] = os.path.join(
            inp.calling_dir,
            inp.modpath.replace('.', '_') + '.' + _args.get('format', 'svg')
        )

    with inp.chdir_work():
        _args['fname'] = inp.fname
        _args['isdir'] = inp.is_dir

        if _args.get('externals'):
            del _args['fname']
            exts = externals(inp, **_args)
            print(json.dumps(exts, indent=4))
            return exts  # so the tests can assert
        else:
            # this is the call you're looking for :-)
            return _pydeps(inp, **_args)


if __name__ == '__main__':  # pragma: nocover
    pydeps()
