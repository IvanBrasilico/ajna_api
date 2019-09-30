Teste de separação da API do virasana

```
$git clone https://github.com/IvanBrasilico/ajna_api
$cd ajna_api
$python3 -m virtualenv api-venv
$. api-venv/bin/activate
$pip install -e .[dev]
$python wsgi.py (debug)
$gunicorn wsgi:app (production)

```