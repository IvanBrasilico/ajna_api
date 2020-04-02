import io
import sys
import warnings
from base64 import b64decode

import matplotlib.pyplot as plt
import requests_pkcs12 as requests
from PIL import Image

warnings.simplefilter('ignore')
# BASE_URL = 'https://localhost/ajnaapi'
BASE_URL = 'https://ajna.labin.rf08.srf/ajnaapi'

if len(sys.argv) < 2:
    print('Informe CE-Mercante')
    sys.exit(0)

ce_mercante = sys.argv[1]

if len(sys.argv) > 2:
    usuario = sys.argv[2]
    senha = sys.argv[3]
    # Login por usuario e senha
    print('Fazendo login com usuário e senha')
    payload = {'username': usuario,
               'password': senha}
    print(payload)
    r = requests.post(BASE_URL + '/api/login',
                     json=payload,
                     verify=False)
else:
    # Login por Certificado
    print('Fazendo login com certificado')
    r = requests.get(BASE_URL + '/api/login_certificado',
                     pkcs12_filename='ivan.p12',
                     pkcs12_password='ivan',
                     verify=False)

print(r.status_code)
print(r.text)
jwt_token = r.json().get('access_token')
headers = {'Authorization': 'Bearer %s' % jwt_token}

# Pesquisar um conhecimento, retornar lista de contêineres e de imagens
payload = {'query': {'metadata.carga.conhecimento.conhecimento': ce_mercante},
           'projection': {'metadata.carga.container.container': 1, '_id': 1}
           }
r = requests.post(BASE_URL + '/api/grid_data',
                  json=payload,
                  headers=headers,
                  verify=False)
print(r.status_code)
print(r.text)

# Recuperar o conteúdo de uma imagem através do _id
for image_json in r.json():
    image_id = image_json['_id']
    r = requests.get(BASE_URL + '/api/image/%s' % image_id,
                     json=payload,
                     headers=headers,
                     verify=False)
    plt.imshow(Image.open(io.BytesIO(b64decode(r.json().get('content')))))
    plt.show()

# Retornar um JSON com um resumo das informações que o Banco do AJNA tem sobre o CE-Mercante
r = requests.get(BASE_URL + '/api/summary_aniita/%s' % ce_mercante,
                 json=payload,
                 headers=headers,
                 verify=False)
print(r.status_code)
print(r.text)

# Outras informações, como por exemplo recuperar pesagem em balança rodoviária
payload = {'query': {'metadata.carga.conhecimento.conhecimento': ce_mercante},
           'projection': {'metadata.carga.container': 1,
                          'metadata.pesagens': 1,
                          'metadata.carga.pesototal': 1,
                          }
           }
r = requests.post(BASE_URL + '/api/grid_data',
                  json=payload,
                  headers=headers,
                  verify=False)
print(r.status_code)
print(r.text)
