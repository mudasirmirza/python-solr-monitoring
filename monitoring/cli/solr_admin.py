import urlparse
import urllib2
import json

class DataSolrAdmin:
    SYSTEM_INFO_URL = '/solr/admin/info/system?wt=json'
    CORES_INFO_URL = '/solr/admin/cores?wt=json&indexInfo=false'
    CACHE_INFO_URL_FORMAT = '/solr/%s/admin/mbeans?stats=true&wt=json&cat=CACHE&key=filterCache'

    '''
    each tuple contains (key, description, jpath)
    '''
    system_info_map = [
            ('heap_free', 'free_heap_memory_in_bytes', 'jvm.memory.raw.free'),
            ('heap_total', 'total_heap_memory_in_bytes', 'jvm.memory.raw.total'),
            ('heap_max', 'max_heap_memory_in_bytes', 'jvm.memory.raw.max'),
            ('heap_used', 'used_heap_memory_in_bytes', 'jvm.memory.raw.used'),
            ('heap_used_perc', 'used_perc_heap_memory_in_bytes', 'jvm.memory.raw.used%'),

            ('memory_total', 'total_memory_in_bytes', 'system.totalPhysicalMemorySize'),
            ('memory_free', 'free_memory_in_bytes', 'system.freePhysicalMemorySize'),
            ]

    cache_info_map = [
            ('fc_hitratio', 'filter_cache_hitratio', 'filterCache.stats.hitratio'),
            ('fc_evictions', 'filter_cache_evictions', 'filterCache.stats.evictions'),
            ]

    def __init__(self, solr_host):
        self.solr_host = solr_host

    def get_metrics(self):
        collected = self._collect(
                self._read_solr_response(self.SYSTEM_INFO_URL),
                self.system_info_map)

        for core in self._get_cores():
            url = self.CACHE_INFO_URL_FORMAT % (core,)
            json_response = self._read_solr_response(url)

            collected.update(self._collect(
                json_response['solr-mbeans'][1],
                self.cache_info_map,
                core + '_'))

        return collected

    def _collect(self, json_dict, entry_map, prefix=''):
        return dict((prefix + key, {'value': self._jpath(json_dict, path), 'desc': prefix + desc})
                for (key, desc, path) in entry_map)

    def _get_cores(self):
        cores_info = self._read_solr_response(self.CORES_INFO_URL)
        return cores_info['status'].keys()

    def _read_solr_response(self, rel_path):
        url = urlparse.urljoin(self.solr_host, rel_path)
        json_response = urllib2.urlopen(url).read()
        return json.loads(json_response)

    def _jpath(self, json_dict, path):
        elem = json_dict
        try:
            for x in path.split("."):
                elem = elem.get(x)
        except:
            pass

        return elem
