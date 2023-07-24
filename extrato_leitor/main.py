#!/usr/bin/env python

import os
import re
from pandas import DataFrame, concat
from PyPDF2 import PdfReader
from typing import Union

START_PAGE = 3
VERSION = 0.2


def _token_replace(list_tokens):
    return [re.sub("( \n)+", "\t", row) for row in list_tokens]


def nu_credit_page_process(
    pdf_reader: PdfReader, page_number: int
) -> Union[list, None]:
    """Retorna uma lista contendo dados existentes em uma determinada página
    de um extrato de cartão em PDF.

    Args:
        pdf_reader (_type_): Objeto do pacote PyPDF2 que controla a leitura
        do PDF.
        page_numer (int): número da página no arquivo.

    Raises:
        ValueError:

    Returns:
        list: contendo dados de uma página
    """

    if page_number < len(pdf_reader.pages):
        page_text = pdf_reader.pages[page_number].extract_text()
        expr2 = "[0-3][0-9] [A-Z]{3} \n \n[\w*/ \-.]+ \n(?:\.*[0-9]{1,3})+\,[0-9]{2} \n"
        matches = re.findall(expr2, page_text)
        return _token_replace(matches)
    else:
        print("Invalid page number")
        raise ValueError


def parse_table(pdf_reader: PdfReader) -> DataFrame:
    """Esse método monta uma tabela com dados de extrado através de um
    DataFrame do Pandas, a partir de um layout em pdf pré-definido, aqui
    processado pelo método `page_process`.

    Args:
        pdf_reader (PdfReader): Objeto do pacote PyPDF2 que controla a leitura
        do PDF.

    Returns:
        DataFrame: Tabela para ser exportada.
    """

    new_doc = []
    for i in range(START_PAGE, len(pdf_reader.pages)):
        print(f"Lendo página: {i}")
        new_doc += nu_credit_page_process(pdf_reader, page_number=i)

    extrato_df = (
        DataFrame(
            [row.split("\t") for row in new_doc],
            columns=["Date", "Shop Name", "Value (R$)", "to_be_dropped"],
        )
        .drop(["to_be_dropped"], axis=1)
        .dropna(axis=0, how="all")
    )

    return extrato_df


def _single_():
    FILEPATH = "faturas/fatura.pdf"

    print(f"Leitor de Extratos - {VERSION}")

    new_file_path = input(f"Escreva o nome do arquivo (Padrão={FILEPATH}): ")
    print(new_file_path)

    if new_file_path:
        new_name = new_file_path
    else:
        new_name = FILEPATH

    pdf_reader = PdfReader(new_name)
    extrato_df = parse_table(pdf_reader)

    print(f"Tabela gerada: {extrato_df.shape[0]} linhas obtidas")

    extrato_df.to_csv(
        f'{new_file_path.replace(".pdf","")}_extracted.csv', sep=";", index=False
    )


def batch_process():
    """Método para executar e consolidar extratos em lote."""

    VERSION = 0.2
    DEFAULT_DIR = "./faturas/nubank/"
    NOME_SAIDA = "faturas_nubank.csv"

    print(f"Leitor de Extratos - {VERSION}")

    files_list = sorted(
        list(map(lambda x: re.findall("(\w+\.pdf)", x)[0], os.listdir(DEFAULT_DIR)))
    )

    registry = dict()
    lines = 0
    for name in files_list:
        pdf_reader = PdfReader(os.path.join(DEFAULT_DIR, name))
        extrato_df = parse_table(pdf_reader)
        lines += extrato_df.shape[0]
        registry[name.strip(".pdf")] = extrato_df
        print(f"Arquivo {name} processado com sucesso!")

    print(f"Consolidando arquivos: {files_list} -  Totalizando {lines} linhas")

    df_consolidado = concat([v for _, v in registry.items()])

    print(f"Tabela gerada: {df_consolidado.shape[0]} linhas obtidas")

    df_consolidado.to_csv(f"{NOME_SAIDA}", sep=";", index=False)


if __name__ == "__main__":
    escolha = input(
        """ Escolha uma opção:
          1. Processar um arquivo.
          2. Processar arquivos em um diretório (batch).
          """
    )

    print(f"Opcao {escolha}!")

    if escolha == "1":
        _single_()
    elif escolha == "2":
        batch_process()
    else:
        print("Opção inválida!")
