from subprocess import Popen, PIPE
from parsers.tail import read_tailed_files
from db import Database
from util import LOGGER

def parse_args():
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Snapshot statistics from a machine')
    parser.add_argument('--ip', default='',
                        help='connect to a remote host (recommended)')
    # Multiple pids could be set using bash expansion: {1234,2345}
    parser.add_argument('-p', '--pid', default='*',
                        help='the pid(s) to look up (default: *)')
    parser.add_argument('-u', '--user', default='root',
                        help='user to log into remote host with (default: root)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='enable more verbose logging')
    parser.add_argument('--overwrite', action='store_true',
                        help='always overwrite the db, even if it exists')
    parser.add_argument('--db', required=True,
                        help='path to store the data to (sqlite format)')
    args = parser.parse_args()
    return args


def read_smaps(args):
    # This is the command to grap all of the necessary info.
    # Note that -v is passed to tail - this is so we always the filename
    # given to us, which is needed for parsing.
    cmd = """bash -c "tail -v -n +1 /proc/%s/{cmdline,smaps} 2>/dev/null;
tail -v -n +1 /proc/meminfo" """
    if args.ip == '':
        print ('Loading local procfs files')
        cmd = "sudo %s" % (cmd % args.pid)
        stream = Popen(cmd, shell=True, bufsize=-1, stdout=PIPE).stdout
    elif args.ip != '':
        cmd = """ssh %s@%s '%s'""" % (args.user, args.ip, cmd % args.pid)
        #tail /proc/*/{cmdline,smaps}\'' % args.hostname
        stream = Popen(cmd, shell=True, bufsize=-1, stdout=PIPE).stdout

    LOGGER.info('Reading procfs with cmd: %s' % cmd)
    return read_tailed_files(stream)


def main(args):
    import logging
    if args.verbose:
        LOGGER.setLevel(logging.DEBUG)
    else:
        LOGGER.setLevel(logging.INFO)

    # Get the database handle
    conn = Database(args.db, args.overwrite)
    # Read all the data we need
    processes, memory_regions = read_smaps(args)

    LOGGER.info('Found {} process(es) and {} used memory fragments'.format(
                len(processes), len(memory_regions)))
    LOGGER.info('Regions: %s' % memory_regions)



if __name__ == '__main__':
    main(parse_args())