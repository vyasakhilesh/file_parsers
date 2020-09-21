
#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import json
import os
import multiprocessing as mp
import time
import argparse
from collections import OrderedDict
import re
import string

pattern_list = ["\s\s\sConcept Id:\s", "\sMap Score:\s", "\s\s\sScore:\s", "\s\s\sSemantic Types:\s"]

# pattern_list = ["Concept Id: ", "Map Score: ", "Score: ", "Semantic Types: "]


def parse(filename):
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    return lines[2:] # First two lines can be neglected 

def extract_filename(filename):
    b = os.path.basename(filename)
    return os.path.splitext(b)[0]


def check_alphanum_type(l):
    for i in l:
        if(i.isalnum()):
            pass
        else:
            return False
    return True

# def check_digit_type(l):
#     for i in l:
#         if(i.isdigit()):
#             pass
#         else:
#             return False
#     return True


def parse_obj(lines, filename):
    tmp_dict = OrderedDict()
    filename = extract_filename(filename)
    #print (lines)
    tmp_dict['pmid'] = []
    # print (lines)
    # print ([line for line in lines if re.search(pattern_list[0],line)])
    # print ([line for line in lines if re.search(pattern_list[0],line)])
    tmp_dict['Concept Id'] = [re.sub(pattern_list[0], '', line.rstrip()) for line in lines if re.search(pattern_list[0],line)]
    tmp_dict['Map Score'] =  [int(re.sub(pattern_list[1], '', line.rstrip()))*-.001 for line in lines if re.search(pattern_list[1],line)]
    tmp_dict['Score'] = [int(re.sub(pattern_list[2], '', line.rstrip()))*-.001 for line in lines if re.search(pattern_list[2],line)]
    tmp_dict['Semantic Types'] = [re.sub(pattern_list[3], '', line).rstrip() for line in lines if re.search(pattern_list[3],line)]
    tmp_dict['pmid']= [filename for i in range(len(tmp_dict['Concept Id']))]
    print (tmp_dict)
    length_flag = len(tmp_dict['Concept Id']) == len(tmp_dict['Map Score']) == len(tmp_dict['Score']) == len(tmp_dict['Semantic Types'])
    type_flag = check_alphanum_type(tmp_dict['Concept Id']) # & check_digit_type(tmp_dict['Map Score']) & check_digit_type(tmp_dict['Score'])
    if length_flag & type_flag:
        return tmp_dict
    else:
        return {}
  


def paserFile(filename):
    l = parse_obj(parse(filename), filename) #start extracting from line number 2
    df = pd.DataFrame(l, columns=l.keys()).dropna(how='all')
    return df
    

def run_parser(files_list_all, start_id, end_id, output_path):
    print ("Processing files_{}_from_[start:_{}_end:_{})".format(len(files_list_all), start_id+1, end_id+1))
    df_file = pd.DataFrame()
    pool = mp.Pool(mp.cpu_count())
    print ('No of pools', pool)
    startTime = time.time()

    files = files_list_all[start_id:end_id]
    for result in pool.map(paserFile, files):
        startTime = time.time()
        df_file = df_file.append(result, ignore_index=True)
        del result
        elapsedTime = time.time() - startTime
        print ("Time_by_Pool: ", elapsedTime)

    
    pool.close()
    pool.join()
    
    elapsedTime = time.time() - startTime
    print ("\t\t Time_Taken_by_File_Parsing_Each_Loop: ", elapsedTime)
    
    df_file.to_csv(os.path.join(output_path,'parsed_file_{}_{}.tsv'.format(start_id+1, end_id+1)), sep='\t', index=False, encoding='utf-8')
    del df_file
    
    return None

def add_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input_path', dest='input_path', help='txt_file path', required=True)
    parser.add_argument('-o','--output_path', dest='output_path', help='tsv_file path', required=True)
    parser.add_argument('-n','--n_files_per_loop', dest='n_files_per_loop', type=int, help='number of files per loop', required=True)
    return parser

    
def write_output(df_file, start_id, end_id, output_path):
    df_file.to_csv(os.path.join(output_path,'parsed_file_{}_{}.tsv'.format(start_id+1, end_id+1)), sep='\t', index=False, encoding='utf-8')
    del df_file
    return None


def main():
    
    parser = add_arguments()
    args = parser.parse_args()
    input_path = args.input_path
    output_path = args.output_path
    n_files_per_loop = args.n_files_per_loop
    print ("input_path: {}, output_path: {}, n_files_per_loop: {}".format(input_path, output_path, n_files_per_loop))

    files_list_all = [os.path.join(input_path, file) for file in sorted(os.listdir(input_path))]
    print ('Sample_file: {}, number_of_files: {}'.format(files_list_all[0], len(files_list_all)))
    

    # File parser
    n_files = len(files_list_all)

    start_end_id_l = [(i*n_files_per_loop, i*n_files_per_loop + n_files_per_loop) \
                    for i in range(0, n_files//n_files_per_loop)] +\
                    [((n_files//n_files_per_loop)*n_files_per_loop, n_files)]
    

    out = [run_parser(files_list_all, s_i, e_i, output_path) for s_i, e_i in start_end_id_l]

if __name__ == "__main__":
    print("Start: JSONParser")
    startTime = time.time()
    main()
    elapsedTime = time.time() - startTime
    print ("\t\t Total_Time", elapsedTime)
    print('End: JSONParser')

