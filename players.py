import message as ms
import bloom_filter
import garbled_bloom_filter as gbf
import randomized_gbf as rgbf
import helpers
import hashes as h
import binascii
import PySimpleGUI as sg

# Turn all debug prints to print in a window
print = sg.Print

# Base player class. Houses properties and methods common to both player types
class Player(object):
    def __init__(self, id, params, inputSet):
        self.id = id
        self.messages = []
        self.c_messages = []
        self.j_messages = []
        self.injective_function = []
        self.params = params
        self.inputSet = inputSet
        # self.create_RandomInputs()
        # print("Player {} created".format(self.id))

    def identify(self):
        return self.id

    def create_BloomFilter(self, hashes):
        self.bloom_filter = bloom_filter.new(self.params.Nbf, self.params.PlayerInputSize, hashes)
        for val in self.inputSet:
            self.bloom_filter.add(val)

    def create_InjectiveFunction(self):
        mIndex = 0
        zeroCache = []
        oneCache = []
        bitCaches = [zeroCache, oneCache]
        
        for bit in self.bloom_filter.indices:
            if len(bitCaches[bit]) != 0:
                self.injective_function.append(bitCaches[bit].pop())
            else:   
                while bit != self.j_messages[mIndex].bit:
                    bitCaches[1-bit].append(mIndex)
                    mIndex += 1
                self.injective_function.append(mIndex)
                mIndex += 1
        # self.test_InjectiveFunction()

    def test_InjectiveFunction(self):
        for index, val in enumerate(self.bloom_filter.indices):
            mi = self.injective_function[index]
            if val != self.j_messages[mi].bit:
                print("Player {} Injective function incorrect".format(self.id))
                return
        print("Player {} injective function valid".format(self.id))

    # Choose a bit 1, 0 weighted according to self.params.a as provided by protocol
    def pickBit(self):
        r = helpers.uRandomInt(16) % 100
        return 1 if (r / 100 < self.params.a) else 0

    def receiveOTMessage(self, message):
        self.messages.append(message)
    
    def getTotalOnes(self):
        total = 0
        for message in self.messages:
            if isinstance(message, list):
                for m in message:
                    total += 1 if m.bit == 1 else 0
            else:
                if message.bit == 1:
                    total += 1
        return total

    def create_RandomInputs(self):
        r_index = helpers.uRandomInt(16) % self.params.PlayerInputSize
        for i in range(0, self.params.PlayerInputSize):
            if i == r_index:
                r = self.params.shared_random
            else:
                r = helpers.uRandomInt(16) % 1000
            self.inputSet.append(r)

# Imagine a bicycle wheel. A "spoke" player is one on the outside
# All players P2+ will be spoke players
class PlayerSpoke(Player):
    def store_Message(self, message):
        self.messages.append(message)

# Imagine a bicycle wheel. A "hub" player is one in the middle
# p0 and p1 will both always be hub players
class PlayerHub(Player):
    def store_Transfer(self, transfer):
        self.messages.append(transfer)
    
    def create_GarbledBloomFilter(self, hashes):
        self.garbled_bloom_filter = gbf.new(self.params.Nbf, self.params.PlayerInputSize, self.params.bitLength, hashes)

    def create_RandomizedGBF(self, hashes):
       self.randomized_gbf = rgbf.new(self, hashes)
    
    def add_InputsToGBF(self):
        for elem in self.inputSet:
            self.garbled_bloom_filter.add(elem)

    def create_XOR_sums(self, players):
        self.randomized_gbf.create_XOR_sums(players)
    
    def create_SummaryValsToShare(self, hashes):
        self.sumValues = []
        sumValues = []
        for i in range(0, len(self.inputSet)):
            elem = self.inputSet[i]
            sumVal = self.randomized_gbf.get_GBF_XOR_sum(elem)
            sumVal = int.from_bytes(sumVal, 'big')
            sumVal = str(sumVal)
            sumVal = str(elem) + sumVal
            sumVal = hashes.randomOracle(sumVal)
            self.sumValues.append((elem, sumVal))
            sumValues.append(sumVal)
        return sumValues
    
    def find_Intersections(self, sumValues):
        output = []
        for (elem, P1sumVal) in self.sumValues:
            for P0sumVal in sumValues:
                if P0sumVal == P1sumVal:
                    output.append(elem)
        return output