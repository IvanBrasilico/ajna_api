"""
Classes para lidar com a tradução de entidades do CARGA de e para o MongoDB.

Pode lidar com as tabelas importadas, JSON e com o GridFS (fs.files)
"""


# @dataclass  - only in Python3.7
class Manifesto:
    """Estrutura Manifestos."""

    def __init__(self):
        self.manifesto = ''
        self.tipomanifesto = ''


class RegistroCarga:
    """Estrutura de um documento do CARGA."""

    def __init__(self):
        self.manifestos: list[Manifesto] = []


class CargaLoader:
    """Alimenta as classes de dados."""

    def load_from_gridfs(self, grid_data: dict) -> list:
        lista_manifestos = []
        metadata = grid_data.get('metadata')
        carga = metadata.get('carga')
        manifestos = carga.get('manifesto')
        print(manifestos)
        if isinstance(manifestos, dict):
            manifestos = [manifestos]
        print(manifestos)
        if isinstance(manifestos, list):
            for manifesto in manifestos:
                lista_manifestos.append(self.load_manifesto_from_dict(manifesto))
        result = RegistroCarga()
        result.manifestos = lista_manifestos
        return result

    def load_manifesto_from_dict(self, manifesto: dict):
        result = Manifesto()
        result.manifesto = manifesto.get('manifesto')
        result.tipomanifesto = manifesto.get('tipomanifesto')
        return result
