from envios.viewsets import EncomiendaViewSet
from envios.serializers import EncomiendaV2Serializer, EncomiendaDetailSerializer


class EncomiendaV2ViewSet(EncomiendaViewSet):
    """
    Versión 2 de la API de encomiendas.
    Usa un serializer distinto para demostrar versionado.
    """

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EncomiendaDetailSerializer

        return EncomiendaV2Serializer