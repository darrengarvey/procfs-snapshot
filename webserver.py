#!/usr/bin/env python

import json
import os
import sqlite3
from twisted.web import server, resource, static
from twisted.web.template import Element, renderer, XMLFile, flattenString, tags
from twisted.web.error import Error
from twisted.python.filepath import FilePath
from twisted.internet import reactor
from db import Database
from util import LOGGER
from views import ProcessesView, ProcessView, SnapshotView, TimelineView


class RootView(resource.Resource):
    isLeaf = False
    numberRequests = 0

    def __init__(self, db, process_name_filter):
        resource.Resource.__init__(self)
        self.db = db
        self.process_name_filter = process_name_filter

    def getChild(self, name, request):
        print "Rendering child %s" % name
        if name == '' or name == "timeline":
            return TimelineView(self.db, self.process_name_filter)
        if name == "processes":
            return ProcessesView(self.db)
        elif name == "process":
            return ProcessView(self.db)
        elif name == "snapshot":
            return SnapshotView(self.db, self.process_name_filter)
        else:
            return resource.Resource.getChild(self, name, request)

def main(args):
    import logging
    if args.verbose:
        LOGGER.setLevel(logging.DEBUG)
    else:
        LOGGER.setLevel(logging.INFO)

    db = Database(args.db)
    root = RootView(db, args.filter)
    root.putChild('static', static.File("./static"))
    site = server.Site(root)
    LOGGER.info("Listening on http://localhost:%d" % args.port)
    reactor.listenTCP(args.port, site)
    reactor.run()

def parse_args():
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Snapshot statistics viewer')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='enable more verbose logging')
    parser.add_argument('-d', '--db', required=True,
                        help='path to store the data to (sqlite format)')
    parser.add_argument('-p', '--port', default=8080, type=int,
                        help='port to listen on (default: 8080')
    parser.add_argument('-f', '--filter', default='%',
                        help='filter for process names, % for wildcard (passed to SQL LIKE command)')
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    main(parse_args())
