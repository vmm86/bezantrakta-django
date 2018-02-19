from dateutil.parser import parse
# from operator import itemgetter

from project.cache import ProjectCache


class EventSeatsPricesCache(ProjectCache):
    entities = ('seats_and_prices', )
    database_first = False

    def get_object(self, object_id, **kwargs):
        pass

    def cache_preprocessing(self, **kwargs):
        pass

    def cache_postprocessing(self, **kwargs):
        self.value['updated'] = parse(self.value['updated'])
        # self.value['seats'] = sorted(self.value['seats'], key=itemgetter('ticket_id'))
        self.value['prices'] = sorted(self.value['prices'])
