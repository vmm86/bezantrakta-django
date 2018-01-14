from django.db.models import F

from project.cache import ProjectCache

from ..models import TicketServiceSchemeVenueBinder, TicketServiceSchemeSector


class TicketServiceSchemeSectorCache(ProjectCache):
    entities = ('ticket_service_scheme', 'ticket_service_sectors', )

    def get_model_object(self, object_id, **kwargs):
        # Схема зала
        return TicketServiceSchemeVenueBinder.objects.annotate(
            scheme_id=F('ticket_service_scheme_id'),
            sector_title=F('ticket_service_scheme_title'),
        ).values(
            'scheme_id',
            'sector_title',
            'scheme'
        ).get(
            ticket_service_id=kwargs['ticket_service_id'],
            scheme_id=object_id,
        )

    def set_cache_key(self, entity, object_id, **kwargs):
        self.key = '{entity}.{ticket_service_id}.{object_id}'.format(
            entity=entity,
            ticket_service_id=kwargs['ticket_service_id'],
            object_id=object_id
            )

    def cache_preprocessing(self, **kwargs):
        # Секторы, привязанные к схеме зала (если они были созданы)
        sectors = TicketServiceSchemeSector.objects.annotate(
            sector_id=F('ticket_service_sector_id'),
            sector_title=F('ticket_service_sector_title'),
            sector_scheme=F('sector'),
        ).values(
            'sector_id',
            'sector_title',
            'sector',
        ).filter(
            scheme__ticket_service_id=kwargs['ticket_service_id'],
            scheme__ticket_service_scheme_id=self.value['scheme_id'],
        )
        self.value['sectors'] = list(sectors) if sectors is not None else None

    def cache_postprocessing(self, **kwargs):
        pass
