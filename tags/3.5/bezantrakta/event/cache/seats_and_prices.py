from dateutil.parser import parse

from project.cache import ProjectCache
from project.shortcuts import timezone_now


class EventSeatsPricesCache(ProjectCache):
    entities = ('seats_and_prices', )
    database_first = False

    def get_object(self, object_id, **kwargs):
        pass

    def cache_preprocessing(self, **kwargs):
        pass

    def cache_postprocessing(self, **kwargs):
        self.value['updated'] = parse(self.value['updated']) if 'updated' in self.value else timezone_now()
        self.value['seats'] = self.value['seats'] if 'seats' in self.value else {}
        self.value['prices'] = sorted(self.value['prices']) if 'prices' in self.value else []
