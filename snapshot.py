from subprocess import Popen, PIPE
from parsers.tail import read_tailed_files

def parse_args():
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Snapshot statistics from a machine')
    parser.add_argument('--ip', default='',
                        help='connect to a remote host (recommended)')
    parser.add_argument('-u', '--user', default='root',
                        help='user to log into remote host with (default: root)')
    args = parser.parse_args()
    return args

def main(args):
    if args.ip == '':
        print ('Loading local procfs files')
        cmd = 'sudo bash -c "tail -n +1 /proc/*/{cmdline,smaps}"'
        stream = Popen(cmd, shell=True, bufsize=-1, stdout=PIPE).stdout
    elif args.ip != '':
        cmd = """ssh %s@%s 'bash -c "tail -n +1 /proc/*/{cmdline,smaps} 2>/dev/null"'""" % \
              (args.user, args.ip)
        #tail /proc/*/{cmdline,smaps}\'' % args.hostname
        stream = Popen(cmd, shell=True, bufsize=-1, stdout=PIPE).stdout

    print ('Reading stream now, cmd: %s' % cmd)
    processes = read_tailed_files(stream)

if __name__ == '__main__':
    main(parse_args())