import boto
import boto.ec2.cloudwatch
import datetime

AWS_LIMIT_METRICS_SIZE = 20

class Metrics:
    def __init__(self, region, instance_id, instance_type, image_id,
                 aggregated, autoscaling_group_name):
        self.names = []
        self.units = []
        self.values = []
        self.dimensions = []
        self.region = region
        self.instance_id = instance_id
        self.instance_type = instance_type
        self.image_id = image_id
        self.aggregated = aggregated
        self.autoscaling_group_name = autoscaling_group_name

    def add_metric(self, name, unit, value, mount=None, file_system=None):
        common_dims = {}
        if mount:
            common_dims['MountPath'] = mount
        if file_system:
            common_dims['Filesystem'] = file_system

        dims = []

        if self.aggregated != 'only':
            dims.append({'InstanceId': self.instance_id})

        if self.autoscaling_group_name:
            dims.append({'AutoScalingGroupName': self.autoscaling_group_name})

        if self.aggregated:
            dims.append({'InstanceType': self.instance_type})
            dims.append({'ImageId': self.image_id})
            dims.append({})

        self.__add_metric_dimensions(name, unit, value, common_dims, dims)

    def __add_metric_dimensions(self, name, unit, value, common_dims, dims):
        for dim in dims:
            self.names.append(name)
            self.units.append(unit)
            self.values.append(value)
            self.dimensions.append(dict(common_dims.items() + dim.items()))

    def send(self, verbose):
        boto_debug = 2 if verbose else 0

        # TODO add timeout
        conn = boto.ec2.cloudwatch.connect_to_region(self.region,
                                                     debug=boto_debug)

        if not conn:
            raise IOError('Could not establish connection to CloudWatch')

        size = len(self.names)

        for idx_start in xrange(0, size, AWS_LIMIT_METRICS_SIZE):
            idx_end = idx_start + AWS_LIMIT_METRICS_SIZE
            response = conn.put_metric_data('System/Linux',
                                            self.names[idx_start:idx_end],
                                            self.values[idx_start:idx_end],
                                            datetime.datetime.utcnow(),
                                            self.units[idx_start:idx_end],
                                            self.dimensions[idx_start:idx_end])

            if not response:
                raise ValueError('Could not send data to CloudWatch - '
                                 'use --verbose for more information')

    def __str__(self):
        ret = ''
        for i in range(0, len(self.names)):
            ret += '{0}: {1} {2} ({3})\n'.format(self.names[i],
                                                 self.values[i],
                                                 self.units[i],
                                                 self.dimensions[i])
        return ret
