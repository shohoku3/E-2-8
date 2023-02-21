import binascii
import binascii
import pandas as pd
from sklearn.utils import shuffle
import os
import protocol
import math
import numpy as np
import helpers
import hashes as h
import bloom_filter as bf
import garbled_bloom_filter as gbf

def psi(PlayerInputSize,inputSet,keyWords):
    NumPlayers = 2
    PlayerInputSize = PlayerInputSize # 10
    SecParam = 40
    bitLength = 128
    # These parameters are meant for illustration and fast execution
    # they are not considered secure or optimal
    Nmaxones = 80 # 40
    p = 0.3 # 0.25 # Fraction of messages to use for Cut and Choose
    a = 0.27 # 0.25 # Probability a 1 is chosen by a player
    disableChecks = False
    # Initialize the protocol by calculating parameters,
    # creating the players, and generating random inputs
    # Note: at least 1 shared value is guaranteed
    Protocol = protocol.new(NumPlayers, Nmaxones, PlayerInputSize, SecParam, bitLength, p, a, disableChecks,inputSet,keyWords)
    # print("Starting protocol...")
    # print("k = {}".format(Protocol.params.k))
    # print("Not = {}".format(Protocol.params.Not))
    # print("gamma = {}".format(Protocol.params.gamma))
    # print("gammaStar = {} ".format(Protocol.params.gammaStar))
    # print("Simulating players joining protocol. Total: {}".format(Protocol.params.NumPlayers))
    # print("Step finished")

    # Perform the random oblivious transfer simulation for P0...Pt
    # print("Performing Random Oblivious Transfer simulation. {} transfers in total:".format(Protocol.params.Not))
    Protocol.perform_RandomOT()
    # print(Protocol.print_PlayerROTTable())
    Protocol.print_PlayerROTTable()
    # print("Counting each player's \"1s\":")
    # print(Protocol.print_PlayerMessageStats())
    Protocol.print_PlayerMessageStats()
    # print("Step finished\n")

    # Perform cut-and-choose simulation for P0...Pt
    # print("Performing Cut and Choose simulation. Size of c: {}. Size of j: {}".format(Protocol.params.C, Protocol.params.Not - Protocol.params.C))
    Protocol.perform_CutandChoose()
    # print("\nStep finished\n")

    # Create bloom filters for P1...Pt
    # print("Creating Bloom Filters. BF length: {}".format(Protocol.params.Nbf))
    Protocol.create_BloomFilters()
    # print("\nStep finished\n")

    # Create P1...Pt's injective functions
    # print("Creating injective functions for every Pi:")
    # print(Protocol.create_InjectiveFunctions())
    Protocol.create_InjectiveFunctions()
    # print("\nStep finished\n")

    # print("\nCreating randomized GBF for every Pi")
    # Instantiate P0's and P1's rGBF objects
    Protocol.create_RandomizedGBFs()
    # print("\nStep finished\n")

    # print("\nCalculating final output")
    # P0 performs XOR summation on its own j_messages[injective_func] where bit=1
    # P1 performs XOR summation on all P1...Pt's j_messages[injective_func] where bit = P1...Pt's choice
    Protocol.perform_XORsummation()

    # P0 calculates summary values for all elements of its input set
    # P1 calculates summary values for all elements of its input set (Every P1...Pt input values)
    Protocol.perform_SummaryValues()

    # P1 receives P0s summary values, compares them to its own
    # Intersections are recorded and output
    # print(Protocol.perform_Output())
    forPrint, intersections, output = Protocol.perform_Output()
    return output
    # print("\nStep finished\n")

def rhex(temp_list):
    result=[]
    for item in temp_list:
        byte_temp = item.encode('utf-8')
        rhex = binascii.hexlify(byte_temp)
        r_int=int(rhex, 16)
        r=r_int%100000000
        result.append(r)
    return result



if __name__ == '__main__':
    tn=0
    tp=0
    fn=0
    fp=0
    slide_size=20
    data = pd.read_csv('./dataset/traffic_result.csv')
    del data['Unnamed: 0']
    data = shuffle(data)
    init_benign = data.label.value_counts().benign
    init_malicious = data.label.value_counts().malicious
    print("Creating slide size: {}".format(slide_size))
    print("The num of benign traffic: {}".format(init_benign))
    print("The num of malicious traffic: {}".format(init_malicious))
    kwds_list=[]
    kwds_list = pd.read_csv('./dataset/kwds.csv')
    del kwds_list['Unnamed: 0']
    kwds_list=kwds_list.dropna()
    kwds_list=kwds_list['kwds'].tolist()
    kwds_list=rhex(kwds_list)
    for index, row in data.iterrows():
        try:
            temp_list = row['value'].split()
            result=rhex(temp_list)
            result_split=result[:10]
            PlayerInputSize=len(result_split)
            for i in range(int(math.floor(len(kwds_list)/slide_size))):
                output=psi(PlayerInputSize,result_split,kwds_list[i*slide_size:(i+1)*slide_size])
                if len(output)!=0 and row['label']=='benign':
                    tn+=1
                    continue
                if len(output)==0 and row['label']=='malicious':
                    fn+=1
                    continue
        except:
            print("error")
    print("The number of true positive: {} ".format(tn))
    print(tn/init_benign)
    # print(fp/init_malicious)
