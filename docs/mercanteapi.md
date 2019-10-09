## Exemplos de utilização da API

#### Consulta por ID
$ curl 127.0.0.1:5004/api/conhecimentosEmbarque/151905216696400
```json
[
  {
    "codigoEmpresaNavegacao": "999999999996", 
    "codigoTerminalCarregamento": "", 
    "consignatario": "111111111111111", 
    "create_date": "Tue, 08 Oct 2019 14:37:06 GMT", 
    "cubagem": "0000000011.501", 
    "dataAtualizacao": "2019-09-27", 
    "dataEmissao": "2019-09-18", 
    "descricao": "8 PALLET(S) CONTAINING 28 DRUMS + 160 JERRYCANS WITH: WOODEN PACKAGE TREATED AND CERTIFIED FUMIGATE PALLETS STC: LEATHER FINISHING PRODUCTS CLASS 9 UN 3082", 
    "embarcador": "ACME INC", 
    "horaAtualizacao": "15:50:25", 
    "index": 5, 
    "indicadorShipsConvenience": "false", 
    "manifestoCE": "1519501923835", 
    "numeroCEMaster": "151905216415591", 
    "numeroCEmercante": "151905216696400", 
    "paisDestinoFinalMercante": "", 
    "portoDestFinal": "BRSSZ", 
    "portoOrigemCarga": "ESBCN", 
    "tipoBLConhecimento": "12", 
    "tipoMovimento": "I", 
    "tipoTrafego": "5"
  }
]
```
#### Consulta data de atualização maior ou igual que data consultada
$ curl 127.0.0.1:5004/api/conhecimentosEmbarque/new/2019-10-08t14:37:46
```json
  { ... 
    "horaAtualizacao": "13:17:38", 
    "index": 47, 
    "indicadorShipsConvenience": "false", 
    "manifestoCE": "1519501913910", 
    "numeroCEMaster": "", 
    "numeroCEmercante": "151905213465903", 
    "paisDestinoFinalMercante": "", 
    "portoDestFinal": "BRSSZ", 
    "portoOrigemCarga": "INHZR", 
    "tipoBLConhecimento": "10", 
    "tipoMovimento": "A", 
    "tipoTrafego": "5"
  },
   ...
   ,
  {...
    "portoDestFinal": "BRSSZ", 
    "portoOrigemCarga": "CNNGB", 
    "tipoBLConhecimento": "12", 
    "tipoMovimento": "I", 
    "tipoTrafego": "5"
  }, 
  { ...
    "horaAtualizacao": "13:18:54", 
    "index": 50, 
    "indicadorShipsConvenience": "", 
    "manifestoCE": "1319501869234", 
    "numeroCEMaster": "", 
    "numeroCEmercante": "131905208149255", 
    "paisDestinoFinalMercante": "", 
    "portoDestFinal": "BRIGI", 
    "portoOrigemCarga": "INMUN", 
    "tipoBLConhecimento": "11", 
    "tipoMovimento": "A", 
    "tipoTrafego": "5"
  }
]
```


#### Consulta por qualquer campo texto
$ curl 127.0.0.1:5004/api/conhecimentosEmbarque?consignatario=111111111111111
```json

[
  {
    "codigoEmpresaNavegacao": "999999999996", 
    "codigoTerminalCarregamento": "", 
    "consignatario": "111111111111111", 
    "create_date": "Tue, 08 Oct 2019 14:37:06 GMT", 
    "cubagem": "0000000011.501", 
    "dataAtualizacao": "2019-09-27", 
    "dataEmissao": "2019-09-18", 
    "descricao": "8 PALLET(S) CONTAINING 28 DRUMS + 160 JERRYCANS WITH: WOODEN PACKAGE TREATED AND CERTIFIED FUMIGATE PALLETS STC: LEATHER FINISHING PRODUCTS CLASS 9 UN 3082", 
    "embarcador": "ACME INC", 
    "horaAtualizacao": "15:50:25", 
    "index": 5, 
    "indicadorShipsConvenience": "false", 
    "manifestoCE": "1519501923835", 
    "numeroCEMaster": "151905216415591", 
    "numeroCEmercante": "151905216696400", 
    "paisDestinoFinalMercante": "", 
    "portoDestFinal": "BRSSZ", 
    "portoOrigemCarga": "ESBCN", 
    "tipoBLConhecimento": "12", 
    "tipoMovimento": "I", 
    "tipoTrafego": "5"
  }
]
```
