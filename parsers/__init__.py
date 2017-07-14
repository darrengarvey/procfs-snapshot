
import parser
import loadavg
import meminfo
import stat
import uptime
import vmstat

import util

all_parsers = util.find_all_subclasses(parser.Parser)


def get_parser(section_name, *args, **kwargs):
    try:
        return all_parsers['Parser_{}'.format(section_name)](*args, **kwargs)
    except KeyError:
        raise TypeError('Could not find parser for "{0}"'.format(section_name))
