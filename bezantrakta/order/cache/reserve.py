from project.cache import ProjectCache


class OrderReserveCache(ProjectCache):
    entities = ('order_reserve', )

    def get_model_object(self, object_id, **kwargs):
        return kwargs['order_uuid']

    def cache_preprocessing(self, **kwargs):
        pass

    def cache_postprocessing(self, **kwargs):
        pass
