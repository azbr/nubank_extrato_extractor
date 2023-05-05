#!/usr/bin/env python

import os
import re
import pandas as pd
from PyPDF2 import PdfReader

def _token_replace(list_tokens):
    return [ re.sub('( \n)+','\t', row) for row in list_tokens ]

def page_process(page_number):
    
    if page_number < len(pdf_reader.pages):
        page_text = pdf_reader.pages[page_number].extract_text()
        expr2 = "[0-3][0-9] [A-Z]{3} \n \n[\w*/ \-.]+ \n(?:\.*[0-9]{1,3})+\,[0-9]{2} \n"
        matches = re.findall(expr2, page_text)
        return _token_replace(matches)
    else:
        print('Invalid page number')
        raise ValueError


if __name__ == "__main__":

    VERSION=0.1
    FILEPATH='fatura.pdf'
    START_PAGE=3
    
    print(f"Leitor de Extratos - {VERSION}")

    new_file_path = input(f'Escreva o nome do arquivo (Padrão={FILEPATH}): ')
    print(new_file_path)

    if new_file_path:
        new_name= new_file_path
    else:
        new_name=FILEPATH

    pdf_reader = PdfReader(new_name)
    
    new_doc = []
    for i in range(START_PAGE, len(pdf_reader.pages)):
        print(f'Lendo página: {i}')
        new_doc += page_process(page_number=i)
    
    extrato_df = pd.DataFrame(
    [row.split('\t') for row in new_doc], 
    columns=['Date','Shop Name', 'Value (R$)', 'to_be_dropped'])\
        .drop(['to_be_dropped'], axis=1)\
        .dropna(axis=0, how='all')
    
    extrato_df.to_csv(f'{new_file_path.replace(".pdf","")}_extracted.csv', sep=';', index=False)
