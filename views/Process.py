import json
import os
import sqlite3
from twisted.web import resource
from twisted.web.template import Element, renderer, XMLFile, flattenString, tags
from twisted.web.error import Error
from twisted.python.filepath import FilePath

class ProcessElement(Element):
    # These are the options used when showing the chart.
    chart_options = {
        "width": 700,
        "height": 400,
        "chartArea": { "width": "80%", "height": "80%" },
        "legend": {'position': 'right'},
        "pieSliceText": 'label',
        "is3D": True,
    }

    def __init__(self, template, data, labels):
        Element.__init__(self)
        self.loader = XMLFile(FilePath(template))
        self.chart_data = data
        self.labels = labels

    @renderer
    def options(self, request, tag):
        return json.dumps(self.chart_options)

    @renderer
    def data(self, request, tag):
        return str(self.chart_data)

    @renderer
    def field_title(self, request, tag):
        return tags.h1("Field")

    @renderer
    def fields(self, request, tag):
        return [tags.option(self.labels[link], value=link) for link in self.labels]
 
class ProcessView(resource.Resource):
    isLeaf = True
    output = ""
    conn = sqlite3.connect("mem.db")
    labels = {
        "HeapUSS": "USS heap size (Kb)",
        "CodeUSS": "USS code size (Kb)",
        "StackUSS": "USS stack size (Kb)",
        "OtherWritableUSS": "USS other writable size (Kb)",
        "OtherReadOnlyUSS": "USS other read only size (Kb)",
    }
    fields = ", ".join(label for label in labels)
    process_detail_table = "SummaryReport"

    def __init__(self, db_name):
        resource.Resource.__init__(self)
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)

    def renderOutput(self, output):
        self.output = output
 
    def render_GET(self, request):
        print "Rendering ProcessView"
        if not "snapshot" in request.args:
            raise Error("No snapshot id specified")
        if not "pid" in request.args:
            raise Error("No process id specified")

        c = self.conn.cursor()

        request.setHeader("content-type", "text/html")
        process_id = request.args["pid"][0]
        snapshot_id = request.args["snapshot"][0]
        data = [['Memory type', "Value (Kb)"]]
        stmt = "select Process, %s from %s where pid = '%s' and snap_id = '%s'" % (self.fields, self.process_detail_table, process_id, snapshot_id)
        print "stmt = %s" % stmt
        for row in c.execute(stmt):
            for (i, field) in enumerate(self.labels):
                data.append([self.labels[field], int(row[i+1])])

        flattenString(
                None,
                ProcessElement("static/process-stats.html", data, self.labels)
            ).addCallback(self.renderOutput)

        request.write(self.output)
        return ""
 
