#!/usr/bin/env python

from subprocess import Popen, PIPE
from sh import whoami
import sys
import time
from parsers.tail import read_tailed_files
from db import Database
from util import LOGGER


def parse_args():
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Snapshot statistics from a machine')
    parser.add_argument('--host', default='',
                        help='connect to a remote host (recommended)')
    parser.add_argument('--password',
                        help='the password for the remote user given with --user')
    # Multiple pids could be set using bash expansion: {1234,2345}
    parser.add_argument('-p', '--pid', default='*',
                        help='the pid(s) to look up (default: *)')
    parser.add_argument('-u', '--user', default='root',
                        help='user to log into remote host with (default: root)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='enable more verbose logging')
    parser.add_argument('--overwrite', action='store_true',
                        help='always overwrite the db, even if it exists')
    parser.add_argument('-d', '--db', required=True,
                        help='path to store the data to (sqlite format)')
    parser.add_argument('-c', '--count', default=1, type=int,
                        help='the number of snapshots to collect')
    parser.add_argument('--period', type=int, default=0,
                        help='number of seconds between subsequent snapshots')
    args = parser.parse_args()

    if args.count > 1 and 0 == args.period:
        print ('Error: You must set the period if count > 1\n')
        parser.print_help()
        sys.exit(1)

    return args


def read_stats(args):
    # This is the command to grab all of the necessary info.
    # Note that -v is passed to tail - this is so we always the filename
    # given to us, which is needed for parsing.
    # As processes can be transient, we can get errors here about
    # non-existent files, so ignore them, this is expected.
    cmd = 'nice tail -v -n +1 '\
              '/proc/%s/{cmdline,smaps} '\
              '/proc/meminfo '\
              '/proc/loadavg '\
              '/proc/uptime '\
              '/proc/vmstat '\
          '2>/dev/null; ' \
          'nice find /proc/%s -type f -name stat '\
            '-exec tail -v -n +1 {} \; 2>/dev/null | '\
            'awk \''\
              '/==>/ {print} '\
              '/^[0-9]/ {print \$2, \$10, \$12, \$14, \$15, \$22}\';'


    # Accept a space-separated list of pids as that is what pidof(8) returns and
    # it's quite likely you'll want to invoke this script with something like:
    #
    #     --pid "`pidof foobar`"
    #
    # at some point.
    if args.pid.isdigit() or args.pid == '*':
        pids = args.pid
    else:
        pids = '{%s}' % args.pid.replace(' ', ',')

    # root can see all of /proc, another user is likely not going to be able
    # to read all of it. This isn't a hard error, but won't give a full view
    # of the system.
    if (args.host == '' and whoami().strip() != "root") or\
       (args.host != '' and args.user != 'root'):
        LOGGER.warning("If not running as root you may not see all info.")

    if args.host == '':
        LOGGER.info('Loading local procfs files')
        cmd = "bash -c \"%s\"" % (cmd % (pids, pids))
    elif args.host != '':
        ssh = (
            "ssh %s@%s"
            " -o UserKnownHostsFile=/dev/null"
            " -o StrictHostKeyChecking=no"
            " -o LogLevel=error"
            % (args.user, args.host)
        )
        if args.password:
            ssh = "sshpass -p %s %s" % (args.password, ssh)
        else:
            ssh = "%s -o PasswordAuthentication=no" % ssh

        cmd = """%s "%s" """ % (ssh, cmd % (pids, pids))

    LOGGER.info('Reading procfs with cmd: %s' % cmd)
    p = Popen(cmd, shell=True, bufsize=-1, stdout=PIPE, stderr=PIPE)
    stats = read_tailed_files(p.stdout)
    if p.poll() != 0:
        LOGGER.error("Command failed with: %r" % p.stderr.read().strip())
        sys.exit(1)

    return stats


def main(args):
    import logging
    if args.verbose:
        LOGGER.setLevel(logging.DEBUG)
    else:
        LOGGER.setLevel(logging.INFO)

    # Get the database handle
    db = Database(args.db, args.overwrite)

    for i in range(args.count):
        if i > 0:
            time.sleep(args.period)
        # Read all the data we need
        system_stats, processes, memory_stats = read_stats(args)

        LOGGER.info('Found {} process(es) and {} used memory fragments'.format(
                    len(processes), len(memory_stats)))
        LOGGER.info('Regions: %s' % memory_stats)

        db.add(args.host if len(args.host) else '[local]', system_stats, memory_stats, processes)

if __name__ == '__main__':
    main(parse_args())
