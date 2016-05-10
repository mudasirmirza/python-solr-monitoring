import argparse


def to_lower(s):
    return s.lower()


def config_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''
  Collects memory, swap, and disk space utilization on an Amazon EC2 instance
  and sends this data as custom metrics to Amazon CloudWatch.''', epilog='''
Supported UNITS are bytes, kilobytes, megabytes, and gigabytes.
Examples (Taken from https://github.com/osiegmar/cloudwatch-mon-scripts-python)
 To perform a simple test run without posting data to Amazon CloudWatch
  ./put_instance_stats.py --mem-util --verify --verbose
  or
  # If installed via pip install cloudwatchmon
  mon-put-instance-stats.py --mem-util --verify --verbose
 To set a five-minute cron schedule to report memory and disk space utilization
 to CloudWatch
  */5 * * * * ~/cloudwatchmon/put_instance_stats.py --mem-util --disk-space-util --disk-path=/ --from-cron
  or
  # If installed via pip install cloudwatchmon
  * /5 * * * * /usr/local/bin/mon-put-instance-stats.py --mem-util --disk-space-util --disk-path=/ --from-cron
  To report metrics from file
  mon-put-instance-stats.py --from-file filename.csv
    ''')

    cache_group = parser.add_argument_group('cache metrics')
    cache_group.add_argument('--cache-hits',
                              action='store_true',
                              help='Reports cache hits.')
    cache_group.add_argument('--cache-evictions',
                              action='store_true',
                              help='Reports cache evictions.')

    exclusive_group = parser.add_mutually_exclusive_group()
    exclusive_group.add_argument('--from-cron',
                                 action='store_true',
                                 help='Specifies that this script is running from cron.')
    exclusive_group.add_argument('--verbose',
                                 action='store_true',
                                 help='Displays details of what the script is doing.')

    parser.add_argument('--verify',
                        action='store_true',
                        help='Checks configuration and prepares a remote call.')
    parser.add_argument('--version',
                        action='store_true',
                        help='Displays the version number and exits.')
    parser.add_argument('--sleep',
                        nargs='?',
                        type=int,
                        const=60,
                        default=60,
                        help='How much time to sleep between metric collections in seconds. By default 60')

    return parser
