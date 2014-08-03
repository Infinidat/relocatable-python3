##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Bootstrap a buildout-based project

Simply run this script in a directory containing a buildout.cfg.
The script accepts buildout command-line options, so you can
use the -c option to specify an alternate configuration file.
"""

import os
import shutil
import sys
import tempfile
import glob
import re

from optparse import OptionParser

tmpeggs = tempfile.mkdtemp()

usage = '''\
[DESIRED PYTHON FOR BUILDOUT] bootstrap.py [options]

Bootstraps a buildout-based project.

Simply run this script in a directory containing a buildout.cfg, using the
Python that you want bin/buildout to use.

Note that by using --find-links to point to local resources, you can keep
this script from going over the network.
'''

def normalize_to_url(option, opt_str, value, parser):
    # copied from zc.buildout-1.x bootstrap.py
    from urllib import pathname2url
    if value:
        if '://' not in value:  # It doesn't smell like a URL.
            value = 'file://%s' % (
                pathname2url(
                os.path.abspath(os.path.expanduser(value))),)
        if opt_str == '--download-base' and not value.endswith('/'):
            # Download base needs a trailing slash to make the world happy.
            value += '/'
    else:
        value = None
    name = opt_str[2:].replace('-', '_')
    setattr(parser.values, name, value)

ezsetup_source = 'https://bitbucket.org/pypa/setuptools/raw/0.8/ez_setup.py'
setuptools_source = "https://pypi.python.org/packages/source/s/setuptools/"
pypi_index = "https://pypi.python.org/simple/"

parser = OptionParser(usage=usage)
parser.add_option("-v", "--version", help="use a specific zc.buildout version")

parser.add_option("-t", "--accept-buildout-test-releases",
                  dest='accept_buildout_test_releases',
                  action="store_true", default=False,
                  help=("Normally, if you do not specify a --version, the "
                        "bootstrap script and buildout gets the newest "
                        "*final* versions of zc.buildout and its recipes and "
                        "extensions for you.  If you use this flag, "
                        "bootstrap and buildout will get the newest releases "
                        "even if they are alphas or betas."))
parser.add_option("-c", "--config-file",
                  help=("Specify the path to the buildout configuration "
                        "file to be used."))
parser.add_option("-f", "--find-links",
                  help=("Specify a URL to search for buildout releases"))
# in closed networks, one needs to provide the location of ez_setup.py
parser.add_option("--setup-source", action="callback", dest="setup_source",
                  callback=normalize_to_url, nargs=1, type="string",
                  help=("Specify a URL or file location for the setuptool's ez_setup.py"),
                  default=ezsetup_source)
# in closed networks, one needs to provide the location of the setuptools and buildout archives
parser.add_option("--download-base", action="callback", dest="download_base",
                  callback=normalize_to_url, nargs=1, type="string",
                  help=("Specify a URL or directory for downloading setuptools and buildout"),
                  default=setuptools_source)
# in closed networks, one needs to provide an index server to find buildout on
parser.add_option("--index-url", action="callback", dest="index_url",
                  callback=normalize_to_url, nargs=1, type="string",
                  help=("Specify an alternative for PyPI simple index url"),
                  default=pypi_index)
# explicit setuptools version
parser.add_option("--setuptools-version", action="store", dest="setuptools_version", type="string",
                  help=("Specifiy a specific version of setuptools to use"),
                  )
options, args = parser.parse_args()

######################################################################
# load/install setuptools

def _cleanup_old_zc_buildout_modules():
    # installing setuptools imported the site module, which added all the stuff in site-packages to sys.path,
    # even though in the case Python was executed -S.
    # we want to remove all traces for this
    for item in sys.path:
        if 'zc' in item:
            sys.path.remove(item)
    for module in sys.modules.keys():
        if 'zc' in module:
            del sys.modules[module]

def _cleanup_setuptools_and_distribute_modules():
    # installing setuptools imported the site module, which added all the stuff in site-packages to sys.path,
    # even though in the case Python was executed -S.
    # we want to remove all traces for this
    paths_to_remove = [item for item in sys.path if 'setuptools-' in item or 'distribute-' in item]
    # the python-setuptools installs setuptools in a different way
    paths_to_remove.extend(item for item in sys.path if glob.glob(os.path.join(item, 'setuptools-*'))
                           and 'dist-packages' in item)
    paths_to_remove.extend(item for item in sys.path if glob.glob(os.path.join(item, 'distribute-*'))
                           and 'dist-packages' in item)
    # virtualenv creates under site-packages a directory named setuptools/ with an __init__.py inside in
    # this causes makes setuptools importable if that site-packages is in sys.path
    # in this case, pkg_resources is directly under site-packages/
    # so it must go
    paths_to_remove.extend(item for item in sys.path if
                           os.path.exists(os.path.join(item, "setuptools")) and
                           os.path.exists(os.path.join(item, "pkg_resources.py")) and
                           'site-packages' in item)
    sys.path = list(set(sys.path) - set(paths_to_remove))


to_reload = False
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

_cleanup_setuptools_and_distribute_modules()
_cleanup_setuptools_and_distribute_modules()  # wtf need to run twice

try:
    import pkg_resources
    import setuptools
except ImportError:
    ez = {}

    # XXX use a more permanent ez_setup.py URL when available.
    exec(urlopen(options.setup_source).read(), ez)
    setup_args = dict(to_dir=tmpeggs, download_delay=0)
    if options.download_base:
        setup_args['download_base'] = options.download_base
        if options.download_base.startswith("file://"):
            download_base = urlparse(options.download_base).path
            if os.path.exists(download_base):
                files = glob.glob(os.path.join(download_base, "setuptools-*.tar.gz"))
                if len(files) == 1:
                    setuptools_version = re.match("setuptools-(?P<version>.*).tar.gz",
                                                  os.path.basename(files[0])).groupdict()['version']
                    setup_args['version'] = setuptools_version
    if options.setuptools_version:
        setup_args['version'] = options.setuptools_version
    ez['use_setuptools'](**setup_args)

    if to_reload:
        reload(pkg_resources)
    import pkg_resources
    # This does not (always?) update the default working set.  We will
    # do it.
    for path in sys.path:
        if path not in pkg_resources.working_set.entries:
            pkg_resources.working_set.add_entry(path)

######################################################################
# Install buildout

ws = pkg_resources.working_set

cmd = [sys.executable, '-c',
       'from setuptools.command.easy_install import main; main()',
       '-mZqNxd', tmpeggs]

find_links = os.environ.get(
    'bootstrap-testing-find-links',
    options.find_links or
    ('http://downloads.buildout.org/'
     if options.accept_buildout_test_releases else None)
    )
if find_links:
    cmd.extend(['-f', find_links])
if options.download_base:
    cmd.extend(["-f", options.download_base])
if options.index_url:
    cmd.extend(["-i", options.index_url])
setuptools_path = ws.find(
    pkg_resources.Requirement.parse('setuptools')).location

requirement = 'zc.buildout'
version = options.version
if version is None and not options.accept_buildout_test_releases:
    # Figure out the most recent final version of zc.buildout.
    import setuptools.package_index
    _final_parts = '*final-', '*final'

    def _final_version(parsed_version):
        for part in parsed_version:
            if (part[:1] == '*') and (part not in _final_parts):
                return False
        return True
    kwargs = dict(search_path=[setuptools_path])
    if options.index_url:
        kwargs['index_url'] = options.index_url
    index = setuptools.package_index.PackageIndex(**kwargs)
    if find_links:
        index.add_find_links((find_links,))
    if options.download_base:
        index.add_find_links((options.download_base,))
    req = pkg_resources.Requirement.parse(requirement)
    if index.obtain(req) is not None:
        best = []
        bestv = None
        for dist in index[req.project_name]:
            distv = dist.parsed_version
            if _final_version(distv):
                if bestv is None or distv > bestv:
                    best = [dist]
                    bestv = distv
                elif distv == bestv:
                    best.append(dist)
        if best:
            best.sort()
            version = best[-1].version
if version:
    requirement = '=='.join((requirement, version))
cmd.append(requirement)

import subprocess
if subprocess.call(cmd, env=dict(os.environ, PYTHONPATH=setuptools_path)) != 0:
    raise Exception(
        "Failed to execute command:\n%s",
        repr(cmd)[1:-1])

######################################################################
# Import and run buildout
# installing setuptools imported site.py, which added zc.buildout to the WorkingSet if it was previously installed
# this may raise a VerionConflict here; we just need to resolve the location of the buildout we just installed
# so we clear the WorkingSet
_cleanup_old_zc_buildout_modules()
ws.by_key = {}
ws.add_entry(tmpeggs)
ws.require(requirement)
import zc.buildout.buildout

if not [a for a in args if '=' not in a]:
    args.append('bootstrap')

# if -c was provided, we push it back into args for buildout' main function
if options.config_file is not None:
    args[0:0] = ['-c', options.config_file]

zc.buildout.buildout.main(args)
shutil.rmtree(tmpeggs)
