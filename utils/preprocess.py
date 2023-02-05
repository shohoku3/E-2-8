import re
import csv
import pandas as pd


name = '../dataset/emerging-all'
textName= name+".txt"
csvName=name+".csv"

if __name__ == '__main__':
    file = open(textName,'rb')
    fw = open(csvName,'w')
    csvwrite = csv.writer(fw)
    for line in file.readlines():
        temp = []
        if len(line.decode().strip().split(";"))!=1:
            if re.search(r'^alert', line.decode().strip()):
                type = re.findall(r'^alert [A-Za-z]+', line.decode().strip())[0].split()[1]
                content = re.findall(r'content:\S*', line.decode().strip())
            else:
                type = re.findall(r'^#alert [A-Za-z]+', line.decode().strip())[0].split()[1]
                content = re.findall(r'content:\S*', line.decode().strip())
            if(len(content)!=0):
                temp.append(type)
                temp.append(content)
                csvwrite.writerow(temp)

