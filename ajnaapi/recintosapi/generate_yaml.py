from ajnaapi.recintosapi import models
from ajnaapi.utils import yaml_from_model

if __name__ == '__main__':  # pragma: no cover
    # print(yaml_from_model(models.AcessoVeiculo))
    # print(yaml_from_model(models.ConteinerUld))
    print(yaml_from_model(models.PesagemVeiculo))
    print(yaml_from_model(models.Semirreboque))
