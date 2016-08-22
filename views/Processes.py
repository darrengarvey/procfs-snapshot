#
# Copyright 2013-2014 YouView TV Ltd and contributors.
# License: LGPL v2.1 or (at your option) any later version (see
# https://github.com/darrengarvey/memory-snapshot/blob/master/LICENSE
# for details).
#

import json
import os
import sqlite3
from twisted.web import resource
from twisted.web.template import Element, renderer, XMLFile, flattenString, tags
from twisted.web.error import Error
from twisted.python.filepath import FilePath

class ProcessesElement(Element):
    # These are the options used when showing the chart.
    chart_options = {
        "width": 700,
        "height": 400,
        "chartArea": { "width": "80%", "height": "80%" },
        "legend": {'position': 'right'},
        "pieSliceText": 'label',
        "is3D": True,
    }

    def __init__(self, template, data, labels, snapshot, processes, field):
        Element.__init__(self)
        self.loader = XMLFile(FilePath(template))
        self.chart_data = data
        self.labels = labels
        self.snapshot_id = snapshot
        self.process_ids = processes
        self.field = field

    @renderer
    def options(self, request, tag):
        return json.dumps(self.chart_options)

    @renderer
    def current_field(self, request, tag):
        return self.field

    @renderer
    def snapshot(self, request, tag):
        return self.snapshot_id

    @renderer
    def processes(self, request, tag):
        return json.dumps(self.process_ids)

    @renderer
    def data(self, request, tag):
        return str(self.chart_data)

    @renderer
    def field_title(self, request, tag):
        return tags.h1("Field")

    @renderer
    def fields(self, request, tag):
        return [tags.option(self.labels[link], value=link) for link in self.labels]
 
class ProcessesView(resource.Resource):
    isLeaf = False
    numberRequests = 0
    output = ""
    labels = {
        "HeapUSS": "USS heap size (Kb)",
        "CodeUSS": "USS code size (Kb)",
        "StackUSS": "USS stack size (Kb)",
        "OtherWritableUSS": "USS other writable size (Kb)",
        "OtherReadOnlyUSS": "USS other read only size (Kb)",
    }
    processes_table = "SummaryReport"

    def __init__(self, db_name):
        resource.Resource.__init__(self)
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)

    def renderOutput(self, output):
        self.output = output
 
    def getChild(self, name, request):
        print "Rendering child of ProcessesView: %s" % name
        if name == '':
            return self
        return resource.Resource.getChild(self, name, request)

    def render_GET(self, request):
        print "Rendering ProcessesView %s" % request.path

        c = self.conn.cursor()

        self.numberRequests += 1

        request.setHeader("content-type", "text/html")

        # TODO: Sanitise this input more. What about "/?field=", or
        #       "/?field='blah'" or even "/?field='stack, heap'"?
        field = request.args.get("field", ["HeapUSS"])[0]
        snapshot = request.args.get("snapshot", ["1"])[0]
        if not field in self.labels:
            raise Error("No such field '%s'" % field)
        label = self.labels[field]

        data = [['Process name', label]]
        processes = []
        stmt = "select pid, Process, %s from %s where snap_id = %s" % (field, self.processes_table, snapshot)
        #print stmt
        for row in c.execute(stmt):
            processes.append(int(row[0]))
            data.append([str(row[1]), int(row[2])])

        #import pprint
        #pprint.pprint(data)

        flattenString(
                None,
                ProcessesElement("static/memstats.html", data, self.labels, snapshot, processes, field)
            ).addCallback(self.renderOutput)
        request.write(self.output)
        return ""
