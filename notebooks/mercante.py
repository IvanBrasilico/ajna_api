"""Classes e funções para integrar XML do Mercante em tabelas."""
from xml.etree.ElementTree import Element

MERCANTE_DIR = 'mercante'

class ParseXML:

    def _campos(self):
        return [campo for campo in dir(self) if campo[0] != '_']

    def _parse_node(self, node):
        for campo in self._campos():
            # print(campo)
            alvo = node.find(campo) 
            if alvo is not None:
                # print(alvo.text, alvo.tag)
                destino = getattr(self, campo)
                if isinstance (destino, str):
                    setattr(self, campo, alvo.text)
                else:
                    setattr(self, campo, alvo)
            else:
                print('Não encontrou %s' % campo)

    def _to_dict(self):
        result = {}
        for campo in self._campos():
            valor = getattr(self, campo)
            if isinstance(valor, ParseXML):
                valor = str(valor)
            result[campo] = valor 
        return result
        

class Embarcador(ParseXML):
    cnpjShipper = ''
    idEmbarcador = ''

    def __repr__(self):
        return self.cnpjShipper
    
class Consignatario(ParseXML):
    tipoConsignatario = ''
    cnpjConsignatario = ''
    dadosComplementaresConsignatario = ''

    def __repr__(self):
        return self.cnpjConsignatario

class Conhecimento(ParseXML):
    def __init__(self):
        self.tipoMovimento:str = ''
        self.dataAtualizacao:str = ''
        self.horaAtualizacao:str = ''
        self.tipoTrafego:str = ''
        self.tipoBLConhecimento:str = ''
        self.numeroCEMaster:str = ''
        self.dataEmissao:str = ''
        self.cubagem:str = ''
        self.portoDestFinal:str = ''
        self.portoOrigemCarga:str = ''
        self.descricao:str = ''
        self.numeroCEmercante:str = ''
        self._embarcador:Element = None
        self._consignatario:Element = None

    
    @property
    def embarcador(self):
        return self._embarcador
        
    @embarcador.setter
    def embarcador(self, node: Element):
        self._embarcador = Embarcador()
        self._embarcador._parse_node(node)

    @property
    def consignatario(self):
        return self._consignatario
        
    @consignatario.setter
    def consignatario(self, node: Element):
        self._consignatario = Consignatario()
        self._consignatario._parse_node(node)
        
class Manifesto(ParseXML):
    def __init__(self):
        self.tipoMovimento:str = ''
        self.numero:str = ''
        self.codAgenciaInformante
<codigoEmpresaNavegacao
<numeroImoDPC
<dataEncerramento
<dataInicioOperacao>2019-09-27</dataInicioOperacao>
<portoCarregamento>BRSSA</portoCarregamento>
<portoDescarregamento>BRIBB</portoDescarregamento>
<tipoTrafego>3</tipoTrafego>
<numeroViagem>937S</numeroViagem>
<quantidadeConhecimento>7</quantidadeConhecimento>
<dataAtualizacao>2019-09-27</dataAtualizacao>
<horaAtualizacao>00:01:18</horaAtualizacao>
<codigoTerminalCarregamento>BRSSA002</codigoTerminalCarregamento>
<codigoTerminalDescarregamento>BRIBB002</codigoTerminalDescarregamento>


classes = {'conhecimentosEmbarque': Conhecimento,
          'manifestosCarga': Manifesto}
