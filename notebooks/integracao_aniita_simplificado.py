import io
import sys
import warnings
from base64 import b64decode

import matplotlib.pyplot as plt
import requests_pkcs12 as requests
from PIL import Image

warnings.simplefilter('ignore')
BASE_URL = 'http://localhost:5004'
# BASE_URL = 'https://ajna.labin.rf08.srf/ajnaapi'
VIRASANA_URL = 'http://localhost:5001'
# VIRASANA_URL = 'https://ajna.labin.rf08.srf/virasana'

if len(sys.argv) < 4:
    print('Informe CE-Mercante, username e senha')
    sys.exit(0)

ce_mercante = sys.argv[1]
usuario = sys.argv[2]
senha = sys.argv[3]
# Login por usuario e senha
print('Fazendo login com usuário e senha')
payload = {'username': usuario, 'password': senha}
r = requests.post(BASE_URL + '/api/login',
                 json=payload,
                 verify=False)
jwt_token = r.json().get('access_token')
my_headers = {'Authorization': 'Bearer %s' % jwt_token}

# Pesquisar um conhecimento, retornar lista de contêineres e de imagens
payload = {'query': {'metadata.carga.conhecimento.conhecimento': ce_mercante},
           'projection': {'metadata.carga.container.container': 1, '_id': 1}
           }
r = requests.post(BASE_URL + '/api/grid_data', json=payload, headers=my_headers, verify=False)
print(r.status_code)
print(r.text)

# Pesquisar um conhecimento, retornar lista de contêineres e de imagens, url antigo
r = requests.post(VIRASANA_URL + '/grid_data', json=payload, headers=my_headers, verify=False)
print(r.status_code)
print(r.text)


