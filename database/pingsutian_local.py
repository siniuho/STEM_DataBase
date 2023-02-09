#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  9 08:08:56 2023

@author: siniuho
"""
import pandas as pd
import numpy as np
import os
import random as rd
import re
import textwrap as twr

pd.set_option('display.unicode.east_asian_width', True)

path = os.getcwd()
dict_names = [
    'Embree台英詞典.csv', 
    'iTaigi華台對照.csv', 
    'Maryknoll台英詞典.csv', 
    '台日大詞典.csv', 
    '台灣植物名類.csv', 
    '台灣白話基礎例句.csv', 
    '台華線上對照.csv',
    '教育部台語辭典.csv',
    '甘字典.csv'
    ]
glos_names = [
    '高中以下化學名詞.csv',
    '高中以下地球科學名詞.csv',
    '高中以下數學名詞.csv',
    '高中以下物理學名詞.csv',
    '高中以下生命科學名詞.csv',
    '高中以下資訊名詞.csv'
    ]

replace_set = {'；': ';'} # add the replacement sets here {<to_replace> : <value>, ...}

glos_lang = ['en', 'zh'] # selected languages in specifice glossaries

# dictionary columns to be input and output
in_HanLoTaibunPoj = [3, 4, 8]
out_HanLoTaibunPoj = [1, 3, 4, 6, 8]
out_HanLoTaibunKip = [7]
out_EngBun = [0, 2, 5]

str1 = '望遠鏡'
str2 = '代數; 幾何'
test1 = [str1]
test2 = [str2]
test3 = [str1, str2]
test_set = [test1, test2, test3]

##############################################################################

def import_df(get_all_info):            # import Dictionaries and Glossaries
    global dict_set, glos_set
    dict_set = []                       # Dictionary set
    for n in range(len(dict_names)):
        fullpath = path + '/dictionaries/' + dict_names[n]
        df = pd.read_csv(fullpath)
        df.name = dict_names[n][:-4]    # truncate filename extension
        dict_set.append(df)
        #print('{:20s}   ===>   dict_set[{:d}]'.format(dict_names[n][:-4], n))
    #print('')
    glos_set = []                       # glossary set
    for m in range(len(glos_names)):
        fullpath = path + '/glossaries/' + glos_names[m]
        df = pd.read_csv(fullpath)
        df.rename({'中文名稱': 'zh', '英文名稱': 'en'}, axis = 1, inplace = True)
        df.name = glos_names[m][:-4]    # truncate filename extension
        glos_set.append(df)
        #print('{:20s}   ===>   glos_set[{:d}]'.format(glos_names[m][:-4], m))
    print(f'\n已經匯入 {n} 本詞典佮 {m} 本詞彙集！ \n')
    if get_all_info == True:
        get_info(dict_set + glos_set)
        
def get_info(df_set):           # get the info of the dict_setataFrame set (dict or glos)
    for df in df_set:
        print('.' * 12 + '[' + df.name + ']' + '.' * 12)
        print(df.info())
        print(-' * 54')

# ============================================================================

def count_NaN(df_set):          # counts NaN in the dict_setataFrame set
    for df in df_set:
        NaN_count = df.isna().sum().sum()
        print(f'NaN in {df.name} = {NaN_count}')
        
def kill_NaN(df_set):           # replace all NaN by '~~~'
    for df in df_set:
        df.replace(np.nan, '~~~', inplace = True)

# ============================================================================

def count_semicolon(df_set, columns):   # counts both types of semicolons in the dict_setataFrame set
    for semicolon in ['；', ';']:
        half_or_full = 'full' if (semicolon == '；') else 'half'
        for column in columns:
            x = 0
            for df in df_set:
                for item in df[column]:
                    if semicolon in item:
                        x += 1
            print(f'{half_or_full} in {column} = {x}')

def replace_char(df_set, columns):      # replace each <to_replace> by <value> according to replace_set
    for df in df_set:
        for column in columns:
            for string in replace_set:
                df[column] = df[column].str.replace(string, replace_set[string])
                
# ============================================================================

def col_in(number):
    dict_selected_header = 0
    if number in in_HanLoTaibunPoj:
        dict_selected_header = 'HanLoTaibunPoj'
    else:
        dict_selected_header = 'HoaBun'
    return dict_selected_header 

def col_out(number):
    dict_selected_header = [col_in(number), 'KipUnicode']
    if number in out_HanLoTaibunPoj:
        dict_selected_header.append('HanLoTaibunPoj')
    if number in out_HanLoTaibunKip:
        dict_selected_header.append('HanLoTaibunKip') 
    if number in out_EngBun:
        dict_selected_header.append('EngBun') 
    return dict_selected_header

# ============================================================================
def expand(term_list):   # expand the entries that are sepetated by semicolons
    expanded_list = []
    for term in term_list:
        expanded_list = expanded_list + term.split(';')
    return expanded_list

prefix = '...... ['
preferredWidth = 70
wrapper = twr.TextWrapper(initial_indent = prefix, width = preferredWidth,
                               subsequent_indent=' ' * len(prefix))

def lookup(term, return_count):       # look up a term
    count = 0
    details = ''
    pat = re.compile(r'\s+')
    for n in range(len(dict_set)): # look up in each dictiornary
        result = dict_set[n][dict_set[n][col_in(n)].str.contains(term)][col_out(n)]
        if result.empty == False: # if anything was found
            #print(result)
            count += 1
            # print(f'* [{term}] is found in [{dict_set[n].name}].')
            # print(result.to_string(header = False, index = False)) # print the result every time
            result1 = result.to_string(header = False, index = False) + '\n'
            result1 = pat.sub(' ', result1).strip()
            result1 = wrapper.fill(result1)
            details += f'{result1}] 佇 [{dict_set[n].name}] \n'
             
    '''
    if count == 1:
        print(f'{term:^24s}: {count:2d} entry was found.')
    elif count == 0:
        print(f'{term:^24s}: {count:2d} entry was found.')
    else:
        print(f'{term:^24s}: {count:2d} entries were found.')
    '''
    if return_count == True:
        return count, details
    else:
        return None

def lookup_series(term_list): # look up a list of terms
    term_list = expand(term_list)       
    for term in term_list:
        print('-' * 54)
        print(term)
        lookup(term, return_count = False)

def lookup_glossary(glossary): # look up every terms in any glossary.
    df = glossary[glos_lang]
    for i in range(len(df.index)):
        print('-' * 54)
        entry = ''
        for lang in glos_lang:
            result = df[lang].iloc[[i]]
            term_list = expand(result)
            for term in term_list:
                count, details = lookup(term, return_count = True)
                result1 = result.to_string(header = False, index = False)
                details1 = (' ' + details + '\n') if count != 0 else ''
                result2 = f'* [{lang}] {result1:15s} 佇 {count:2d} 本詞典內有收 \n{details1.lstrip()}'
            entry += result2 
        entry = entry[:-2]
        print(f'{entry}')
            
def lookup_randomly(integer):
    glos_num = rd.randrange(len(glos_set))
    print('=' * 54)
    print('詞彙集名稱 = '+ glos_set[glos_num].name)
    lookup_glossary(glos_set[glos_num].sample(integer))
    
def lookup_test(glos_num, start, end):
    print('=' * 54)
    print('詞彙集名稱 = '+ glos_set[glos_num].name)
    lookup_glossary(glos_set[glos_num][start:end])
        
# ============================================================================

def count_kill_NaN(df_set, count):
    if count == True:
        print('Before killing NaN ...')
        count_NaN(df_set)
        print()
    kill_NaN(df_set)
    if count == True:
        print('After killing NaN ...')
        count_NaN(df_set)
        print()

def count_replace(df_set, columns, count):
    if count == True:
        print('Before replacement ...')
        count_semicolon(df_set, columns)
        print()
    replace_char(df_set, columns)
    if count == True:
        print('After replacement ...')
        count_semicolon(df_set, columns)
        print()

##############################################################################

# main

#print('Current directory =', os.getcwd())
import_df(get_all_info = False)
count_kill_NaN(dict_set, count = False)
count_replace(glos_set, glos_lang, count = False)
#lookup_randomly(5)

        

