from subprocess import Popen, PIPE
from parsers.tail import read_tailed_files
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
    parser.add_argument('--db', help='path to store the data to (sqlite format)')
    args = parser.parse_args()
    return args


def read_smaps(args):
    # This is the command to grap all of the necessary info.
    if args.ip == '':
        print ('Loading local procfs files')
        cmd = 'sudo bash -c "tail -n +1 /proc/%s/{cmdline,smaps}"' % args.pid
        stream = Popen(cmd, shell=True, bufsize=-1, stdout=PIPE).stdout
    elif args.ip != '':
        cmd = """ssh %s@%s 'bash -c "tail -n +1 /proc/{}/{cmdline,smaps} 2>/dev/null"'""".format(
              (args.user, args.ip, args.pid))
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

    # Read all the data we need
    processes, memory_regions = read_smaps(args)

    LOGGER.info('Found {} process(es) and {} used memory fragments'.format(
                len(processes), len(memory_regions)))
    LOGGER.info('Regions: %s' % memory_regions)

if __name__ == '__main__':
    main(parse_args())