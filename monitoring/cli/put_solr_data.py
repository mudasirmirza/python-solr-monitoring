from monitoring.cli.data import DataCollector
from monitoring.cli.data_jstats import DataJstats
from monitoring.cli.data_solr_admin import DataSolrAdmin
from monitoring.cli.metrics import Metrics

from monitoring.cloudwatch_client import *
from monitoring.cli.args import config_parser
import random
import pprint
import boto
import boto.ec2.autoscale


CLIENT_NAME = 'CloudWatch-PutInstanceData'
FileCache.CLIENT_NAME = CLIENT_NAME

@FileCache
def get_autoscaling_group_name(region, instance_id, verbose):
    boto_debug = 2 if verbose else 0

    # TODO add timeout
    conn = boto.ec2.autoscale.connect_to_region(region, debug=boto_debug)

    if not conn:
        raise IOError('Could not establish connection to CloudWatch')

    autoscaling_instances = conn.get_all_autoscaling_instances([instance_id])

    if not autoscaling_instances:
        raise ValueError('Could not find auto-scaling information')

    return autoscaling_instances[0].group_name


def main():
    parser = config_parser()

    # exit with help, because no args specified
    if len(sys.argv) == 1:
        parser.print_help()
        return 1

    args = parser.parse_args()
    # print args

    if args.version:
        print CLIENT_NAME + ' version ' + VERSION
        return 0

    SLEEP = args.sleep

    try:
        # report_disk_data, report_mem_data, report_loadavg_data = validate_args(args)

        # avoid a storm of calls at the beginning of a minute
        if args.from_cron:
            time.sleep(random.randint(0, 19))

        if args.verbose:
            print 'Working in verbose mode'
            print 'Boto-Version: ' + boto.__version__

        data_start = DataCollector(DataJstats()).get_metrics()
        time.sleep( SLEEP )
        data_end = DataCollector(DataJstats(), DataSolrAdmin('http://localhost:8983/')).get_metrics()

        #metrics = Metrics(gct=(data_end["GCT"]["value"] - data_start["GCT"]["value"]))
        #print "GCT for minute: ", metrics.gct

        metadata = get_metadata()

        if args.verbose:
            print 'Instance metadata: ' + str(metadata)

        region = metadata['placement']['availability-zone'][:-1]
        instance_id = metadata['instance-id']
        autoscaling_group_name = get_autoscaling_group_name(region,
                instance_id,
                args.verbose)
        if args.verbose:
            print 'Autoscaling group: ' + autoscaling_group_name

        metrics = Metrics(region,
                          instance_id,
                          metadata['instance-type'],
                          metadata['ami-id'],
                          True,
                          autoscaling_group_name)

        if args.verbose:
            print '============'
            print 'Collected metrics:'
            for key, data in data_end.iteritems():
                print '    ' + key + '\t' + str(data['value'])
            print '============'

        metrics.add_metric('solr_GCT_perc', 'Percent', 100.0 * (data_end["GCT"]["value"] - data_start["GCT"]["value"]) / SLEEP)
        metrics.add_metric('solr_heap_used_perc', 'Percent', data_end["heap_used_perc"]["value"])

        if args.cache_hits:
            for key, data in [(key, data) for key, data in data_end.iteritems() if "_fc_hitratio" in key]:
                metrics.add_metric('solr_' + key, 'Percent', 100.0 * data_end[key]["value"])

        if args.cache_evictions:
            for key, data in [(key, data) for key, data in data_end.iteritems() if "_fc_evictions" in key]:
                metrics.add_metric('solr_' + key, 'Count', data_end[key]["value"])


        if args.verbose:
            print 'Metrics:'
            print metrics

        # if args.from_file:
        #     add_static_file_metrics(args, metrics)
        #
        # if report_mem_data:
        #     add_memory_metrics(args, metrics)
        #
        # if report_loadavg_data:
        #     add_loadavg_metrics(args, metrics)
        #
        # if report_disk_data:
        #     add_disk_metrics(args, metrics)

        # if args.verbose:
        #     print 'Request:\n' + str(metrics)

        if args.verify:
            if not args.from_cron:
                print 'Verification completed successfully. ' \
                      'No actual metrics sent to CloudWatch.'
        else:
            metrics.send(args.verbose)
            if not args.from_cron:
                print 'Successfully reported metrics to CloudWatch.'
    except Exception as e:
        log_error(str(e), args.from_cron)
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())
