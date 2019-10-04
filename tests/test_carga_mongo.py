# Tescases for integracao/carga_mongo.py
import json
import unittest

from ajnaapi.carga_mongo import CargaLoader, Manifesto

class CargaLoaderTestCase(unittest.TestCase):
    def setUp(self):
        self.loader = CargaLoader()
        self.exemplos = []
        with open('tests/exemplo_carga.json', 'r') as exemplo_in:
            self.exemplos.append(json.load(exemplo_in))


    def test_load_manifesto_from_gridfs(self):
        exemplo = self.exemplos[0]
        registrocarga = self.loader.load_from_gridfs(exemplo)
        rmanifesto = registrocarga.manifestos[0]
        print(registrocarga.manifestos)
        print(exemplo)
        metadata = exemplo.get('metadata')
        carga = metadata.get('carga')
        print(carga)
        manifesto = carga.get('manifesto')
        assert rmanifesto.manifesto == manifesto.get('manifesto')
        assert rmanifesto.tipomanifesto == manifesto.get('tipomanifesto')
