# -*- coding: utf-8 -*-
# from six.moves.configparser import ConfigParser
from ConfigParser import ConfigParser

import codecs
import logging
import os


DIST_CONFIG_FILE = '.pypirc'
SETUP_CONFIG_FILE = 'setup.cfg'
SECTION_NAME = 'dependencychecker_provides'

logger = logging.getLogger(__name__)


class Config(object):
    """Wrapper around the .pypirc and setup.cfg files."""

    def __init__(self, config_filename=DIST_CONFIG_FILE):
        """Grab the package configuration.

        This is a combination of .pypirc in the home directory and
        setup.cfg in the package.
        """
        self.config_filename = config_filename
        self._read_configfile()

    def _read_configfile(self):
        """Read the PyPI config and setup.cf and store it.
        """
        rc = self.config_filename
        if not os.path.isabs(rc):
            rc = os.path.join(os.path.expanduser('~'), self.config_filename)
        filenames = [rc, SETUP_CONFIG_FILE]
        files = [f for f in filenames if os.path.exists(f)]
        if not files:
            self.config = None
            return
        self.config = ConfigParser()
        for filename in files:
            with codecs.open(filename, 'r', 'utf8') as fp:
                self.config.readfp(fp)

    def provides(self):
        """Return information on packages that provide other packages.

        See https://github.com/reinout/z3c.dependencychecker/issues/41

        Sample config to say the the Zope2 package provides packages
        Products.Five and Testing::

            [dependencychecker_provides]
            # Packages that provide (contain) other packages:
            Zope2 =
                Products.Five
                Testing

        Alternatively::

            [dependencychecker]
            provides =
                # Packages that provide (contain) other packages:
                Zope2 = Products.Five Testing

        Bad: this seems uglier.
        Good: here Zope2 is not turned into zope2 lowercase.
        We might need this.

        Return empty dict when nothing has been configured.

        """
        default = {}
        if self.config is None:
            return default
        if not self.config.has_section(SECTION_NAME):
            return default
        providers = self.config.options(SECTION_NAME)
        if not providers:
            return default
        result = {}
        for provider in providers:
            value = self.config.get(SECTION_NAME, provider)
            value = value.strip().splitlines()
            provided = []
            for name in value:
                if u'#' in name:
                    name = name[:name.find(u'#')]
                name = name.strip()
                if not name:
                    continue
                # We split on spaces, so you can add multiple packages on one
                # line.
                provided.extend(name.split())
            result[provider] = provided
        return result
