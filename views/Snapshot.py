import json
import os
import sqlite3
from twisted.web import resource
from twisted.web.template import Element, renderer, XMLFile, flattenString, tags
from twisted.web.error import Error
from twisted.python.filepath import FilePath
from util import LOGGER

class SnapshotElement(Element):
    # These are the options used when showing the chart.
    chart_options = {
        'width': 1600,
        'height': 600,
        'chartArea': { 'width': '80%', 'height': '90%' },
        'maxDepth': 2,
        'useWeightedAverageForAggregation': True,
    }
    def __init__(self, template, data, snapshot, maxDepth = 0):
        Element.__init__(self)
        self.loader = XMLFile(FilePath(template))
        self.chart_data = data
        self.snapshot_id = snapshot
        if maxDepth > 0:
            self.chart_options['maxDepth'] = maxDepth

    @renderer
    def options(self, request, tag):
        return json.dumps(self.chart_options)

    @renderer
    def snapshot(self, request, tag):
        return str(self.snapshot_id)

    @renderer
    def next_link(self, request, tag):
        return tags.a('Next', href='/snapshot/?snapshot=%s' % (self.snapshot_id + 1))

    @renderer
    def prev_link(self, request, tag):
        return tags.a('Prev', href='/snapshot/?snapshot=%s' % max(0, self.snapshot_id - 1))

    @renderer
    def data(self, request, tag):
        return json.dumps(self.chart_data)

 
class SnapshotView(resource.Resource):
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

    def __init__(self, db, process_name_filter):
        resource.Resource.__init__(self)
        self.db = db
        self.process_name_filter = process_name_filter

    def renderOutput(self, output):
        self.output = output
 
    def getChild(self, name, request):
        print "Rendering child of SnapshotView: %s" % name
        if name == '':
            return self
        return resource.Resource.getChild(self, name, request)

    def render_GET(self, request):
        LOGGER.info('Rendering SnapshotView %s' % request.path)

        self.numberRequests += 1

        request.setHeader('content-type', 'text/html')

        if 'snapshot' in request.args:
            snapshot = int(request.args.get('snapshot', ['1'])[0])
        elif 'snapshot_date' in request.args:
            snapshot = self.db.get_snapshot_id(request.args['snapshot_date'][0])

        data = [
            ['Process', 'Parent', 'Size (Kb)'],
            ['machine', None, 0],
        ]
        processes = []
        fields = [
            "heap",
            "stack",
            "ro_shared",
            "ro_private",
            "rw_shared",
            "rw_private",
            "rx_shared",
            "rx_private",
            "rwx_shared",
            "rwx_private",
        ]

        extra_data = []
        units = 1024 * 1024 # Units in MB
        for row in self.db.get_process_info(snapshot_id=snapshot,
                                            name=self.process_name_filter):
            # Unfortunately we need to make every entry unique, so add
            # the pid into the description of the entries.
            pid = int(row[0])
            process = '%s (%0.2fMb, frags:%d, pid:%d)' % \
                      (row[1].split('/')[-1], # process name
                       float(row[2]) / units, # pss in MB
                       int(row[3]),           # number of memory fragments
                       pid)
            data.append([str(process), 'machine', 0])
            for i, field in enumerate(row[4:]):
                extra_data.append(['%s (%0.2fMb, pid:%d)' % \
                                   (fields[i], float(field) / units, pid),
                                   process,
                                   int(field)])

        data += extra_data

        flattenString(
                None,
                SnapshotElement('static/snapshot-tree.html', data, snapshot)
            ).addCallback(self.renderOutput)
        request.write(self.output)
        return ""
