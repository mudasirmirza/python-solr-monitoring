__author__ = 'yury'


class DataCollector:

    def __init__(self, *kargs):
        self.data_sources = kargs

    def get_metrics(self):
        data = {}
        for source in self.data_sources:
            data.update(source.get_metrics())
        return data
