import pandas as pd
import csv
import re

if __name__ == '__main__':
    df = pd.read_csv('../../python-psi-master/dataset/emerging-all.csv')
    df = df.dropna(axis=0, how='all')
    result = []
    for index, row in df.iterrows():
        temp = re.findall(r'\'(.*?)\'', row[1])
        temp_list = []
        for i in range(len(temp)):
            if temp[i][9:].find('"') != -1:
                temp_list.append(temp[i][9:-2])
            else:
                temp_list.append(temp[i][9:])
        temp_list = ','.join(temp_list)
        result.append(temp_list)
    result = pd.DataFrame(result, columns=['kwds'])
    result_list = list(set(list(result['kwds'].values)))
    newline = '\n'
    with open("../../python-psi-master/kwds.txt", 'w', encoding='utf-8', newline="") as csvfile:
        csvfile.write(newline.join(result_list))
