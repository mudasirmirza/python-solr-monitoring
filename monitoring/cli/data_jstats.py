__author__ = 'yury'

import sys
from subprocess import check_output


class DataJstats:

    # Stats coming from -gc
    metric_maps_gc = {
        "S0C": "current_survivor_space_0_capacity_KB",
        "S1C": "current_survivor_space_1_capacity_KB",
        "S0U": "survivor_space_0_utilization_KB",
        "S1U": "survivor_space_1_utilization_KB",
        "EC": "current_eden_space_capacity_KB",
        "EU": "eden_space_utilization_KB",
        "OC": "current_old_space_capacity_KB",
        "OU": "old_space_utilization_KB",
        "PC": "current_permanent_space_capacity_KB",
        "PU": "permanent_space_utilization_KB",
        "YGC": "number_of_young_generation_GC_events",
        "YGCT": "young_generation_garbage_collection_time",
        "FGC": "number_of_stop_the_world_events",
        "FGCT": "full_garbage_collection_time",
        "GCT": "total_garbage_collection_time"
    }

    # Stats coming from -gccapacity
    metric_maps_gccapacity = {
        "NGCMN": "minimum_size_of_new_area",
        "NGCMX": "maximum_size_of_new_area",
        "NGC": "current_size_of_new_area",
        "OGCMN": "minimum_size_of_old_area",
        "OGCMX": "maximum_size_of_old_area",
        "OGC": "current_size_of_old_area",
        "PGCMN": "minimum_size_of_permanent_area",
        "PGCMX": "maximum_size_of_permanent_area",
        "PGC": "current_size_of_permanent_area",
        "PC": "current_size_of_permanent_area"
    }

    # Stats coming from -gcnew
    metric_maps_gcnew = {
        "TT": "tenuring_threshold",
        "MTT": "maximum_tenuring_threshold",
        "DSS": "adequate_size_of_survivor"
    }

    def __init__(self, **kwargs):
        if kwargs.get("pid"):
            pid = kwargs.get("pid")
        else:
            pid = check_output(["pgrep", "java"]).split("\n")[0]
        self.pid = pid

    def get_metrics(self):
        metric_gs = self._get_metrics("-gc", self.metric_maps_gc)
        metric_gs_capacity = self._get_metrics("-gccapacity", self.metric_maps_gccapacity)
        metric_gs_new = self._get_metrics("-gcnew", self.metric_maps_gcnew)

        metric_gs.update(metric_gs_capacity)
        metric_gs.update(metric_gs_new)
        return metric_gs

    def _get_metrics(self, flag, metric_maps):
        '''Runs jstat with provided option on provided host, returns mapped stats'''

        # Get stats from jstat stdout
        # try :
        jstat_gc_out = check_output(["jstat", flag, self.pid])
        # except Exception as e:
        #    print e
        #    sys.exit(1)

        values_all = jstat_gc_out.split("\n")[1].split()
        # Remove non number strings
        values = [jstat_val for jstat_val in values_all if self.is_number(jstat_val)]
        # Transform float strings to float
        values = map(float, values)

        # Change stats titles to long names
        titles = jstat_gc_out.split("\n")[0].split()
        # Deal with -class special "double Bytes" output

        # {'NGC': {'value': 87040.0, 'desc': 'current_size_of_new_area'}, ...}
        return dict([(title, {"value": values[position], "desc": metric_maps[title]}) for position, title in enumerate(titles) if title in metric_maps])

    def is_number(self, s):
        '''returns true if string is a number'''
        try:
            float(s)
            return True
        except ValueError:
            pass
        try:
            import unicodedata
            unicodedata.numeric(s)
            return True
        except (TypeError, ValueError):
            pass
        return False
