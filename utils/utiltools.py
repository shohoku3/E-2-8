import math
from faker import Faker
import pandas as pd
import random
import re
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

fake = Faker()

def read_kwdlist():
    kwds_list = pd.read_csv('../dataset/kwds.csv')
    del kwds_list['Unnamed: 0']
    return kwds_list

def genTraffics(kwds_list,traffic_nums,percentage):
    malicious_traffic=[]
    malicious_nums=math.floor(traffic_nums * percentage)
    benign_nums=traffic_nums-malicious_nums
    kwds_list_sample=kwds_list.sample(n=malicious_nums)
    total_byte = 512
    kwds_list_sample = kwds_list_sample.fillna(fake.md5())
    for index, row in kwds_list_sample.iterrows():
        padding_len = total_byte - len(row['kwds'])
        if row['kwds'].isdigit():
            temp_len = 0
            result = row['kwds']
            while temp_len<=padding_len:
                temp_len += len(row['kwds'])
                result = result+' ' + str(fake.random_number(digits=len(row['kwds'])))
            malicious_traffic.append(result)
            # print(result)
        elif row['kwds'].isalpha() and row['kwds'].isupper():
            fake.words(nb=padding_len).insert(random.randint(0,int(padding_len/2)),row['kwds'])
            result = row['kwds']+' '+' '.join(fake.words(nb=padding_len)).upper()
            malicious_traffic.append(result)
            # print(result)
        elif row['kwds'].isalpha() and row['kwds'].islower():
            fake.words(nb=padding_len).insert(random.randint(0,int(padding_len/2)),row['kwds'])
            result = row['kwds']+' '+' '.join(fake.words(nb=padding_len)).lower()
            malicious_traffic.append(result)
            # print(result)
        elif re.search(r'=',row['kwds']):
            result = row['kwds'] +' '+ ' '.join(fake.words(nb=padding_len))
            malicious_traffic.append(result[:total_byte])
            # print(result)
        elif re.search(r'-', row['kwds']):
            uuid4_padding_list= [fake.uuid4() for _ in range(int(padding_len/len(fake.uuid4())))]
            result = row['kwds']+' '+ ' '.join(uuid4_padding_list)
            if len(result)>total_byte:
                result = result[:total_byte]
            malicious_traffic.append(result)
        elif re.search(r'/',row['kwds']):
            uri_padding_list= [fake.uri() for _ in range(padding_len)]
            result = row['kwds'] +' '+ ' '.join(uri_padding_list)
            malicious_traffic.append(result[:total_byte])
        elif re.search(r'[|](.*?)',row['kwds']):
            shlex_padding_list=[]
            for i in range(int(padding_len/3)):
                shlex_padding_list.append('|'+fake.uuid4()[:2])
            result = row['kwds'] + ' '.join(shlex_padding_list)
            malicious_traffic.append(result[:total_byte])
        else:
            if re.search(r'[,]',row['kwds']):
                result = row['kwds']+ ' ' +' '.join(fake.words(nb=padding_len))
                malicious_traffic.append(result[:total_byte])
            else:
                result = row['kwds'] + ' ' +' '.join(fake.words(nb=padding_len))
                malicious_traffic.append(result[:total_byte])
    benign_traffic = [' '.join(fake.words(nb=padding_len))[:total_byte] for _ in range(benign_nums)]
    # benign_traffic = [fake.pystr(min_chars=total_byte,max_chars=total_byte+2)[:total_byte] for _ in range(benign_nums)]
    malicious_label= ['malicious' for _ in range(malicious_nums)]
    benign_label= ['benign' for _ in range(benign_nums)]
    malicious_result = pd.DataFrame({'label':malicious_label,'value':malicious_traffic})
    benign_result = pd.DataFrame({'label':benign_label,'value':benign_traffic})
    traffic_result = malicious_result.append(benign_result)
    traffic_result.to_csv('../dataset/traffic_result.csv')
    return traffic_result

if __name__ == '__main__':
    kwds_list = read_kwdlist()
    traffic_result = genTraffics(kwds_list,traffic_nums=5000,percentage=0.4)



