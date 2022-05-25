import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By


class AutomacaoProjetoVer:
    def __init__(self, palavra_chave: str, ano=None, texto_procurado: str = None):
        self.webdriver = None
        self.actions = None
        self.palavra_chave = palavra_chave
        self.ano = str(ano)
        self.texto_procurado = texto_procurado

    def filtrar_documentos(self):
        self.webdriver = webdriver.Chrome()
        self.actions = ActionChains(self.webdriver)

        self.webdriver.get('https://acordaos.economia.gov.br/solr/acordaos2/browse/')

        campo_busca = self.webdriver.find_element(by=By.XPATH, value='//*[@id="q"]')
        campo_busca.send_keys(self.palavra_chave)

        botao_buscar = self.webdriver.find_element(by=By.XPATH, value='//*[@id="querySubmit"]')
        botao_buscar.click()

        paginas = int(self.webdriver.find_element(by=By.XPATH, value='//*[@id="content"]/div[6]/span[3]').text)
        documentos = []

        for pagina in range(paginas):
            botao_visualizacao_json = self.webdriver.find_element(by=By.XPATH, value='//*[@id="footer"]/div[1]/a[4]')
            self.actions.move_to_element(botao_visualizacao_json).perform()
            botao_visualizacao_json.click()

            retorno_json = self.webdriver.find_element(by=By.XPATH, value='/html/body/pre').text
            json_dados = json.loads(retorno_json)

            for documento in json_dados['response']['docs']:
                if 'id' in documento and 'ano_sessao_s' in documento and 'conteudo_txt' in documento:
                    doc_id = documento['id']
                    ano_sessao_s = documento['ano_sessao_s']
                    conteudo_txt = documento['conteudo_txt']

                    documentos.append({"id": doc_id,
                                       "ano_sessao_s": ano_sessao_s,
                                       "conteudo_txt": conteudo_txt})

            self.webdriver.back()

            if pagina+1 != paginas:
                botao_proxima_pagina = self.webdriver.find_element(by=By.CLASS_NAME, value='next-page')
                botao_proxima_pagina.click()

        df_documentos = pd.DataFrame(documentos, dtype=str)

        if self.ano:
            df_documentos = df_documentos[df_documentos['ano_sessao_s'] == self.ano]

        if self.texto_procurado:
            df_documentos = df_documentos[df_documentos['conteudo_txt'].str.contains(self.texto_procurado)]

        self.webdriver.close()

        return df_documentos


if __name__ == '__main__':
    automacao = AutomacaoProjetoVer(palavra_chave='covid',
                                    ano=2021,
                                    texto_procurado='coronavírus')
    documentos_filtrados = automacao.filtrar_documentos()
    print(documentos_filtrados)
