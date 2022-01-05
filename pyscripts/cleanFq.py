# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 20:20:00 2019

@author: moximonx
"""

import os
import sys
import gzip

R1_index = set()
R2_index = set()
indexToSample = dict()
f = open(sys.argv[3],'r')
line = f.readline()
while(line):
    i1,i2,i = line.strip('\n').split('\t')
    R1_index.add(i1)
    R2_index.add(i2)
    indexToSample[i1+' '+i2] = i
    line = f.readline()
R1_index = list(R1_index)
R2_index = list(R2_index)
f.close()

META_sequence = dict()
f = open(sys.argv[4],'r')
line = f.readline()
line = f.readline()
k = 1
while(line):
    META_sequence[line.strip('\n')] = k
    k += 1
    line = f.readline()
    line = f.readline()
f.close()

R1_longest_len = max([len(i) for i in R1_index])
R2_longest_len = max([len(i) for i in R2_index])

base = 'ACGTN'

def index_extend(index_list,extend_list,l):
    index_dict = dict()
    blacklist = set()
    for i in index_list:
        if len(i) < l:
            m = l - len(i)
            for j in extend_list:
                index = i + j[0:m]
                for k in range(l):
                    for b in base:
                        tolerant_index = index[0:k]+b+index[(k+1):]
                        if tolerant_index not in index_dict:
                            index_dict[tolerant_index] = i
                        elif index_dict[tolerant_index] != i:
                            blacklist.add(tolerant_index)
        else:
            index = i
            for k in range(len(i)):
                for b in base:
                    tolerant_index = index[0:k]+b+index[(k+1):]
                    if tolerant_index not in index_dict:
                        index_dict[tolerant_index] = i
                    elif index_dict[tolerant_index] != i:
                        blacklist.add(tolerant_index)
    for index in blacklist:
        del(index_dict[index])
    return(index_dict)

R1_index_dict = index_extend(R1_index,META_sequence,R1_longest_len)
R2_index_dict = index_extend(R2_index,META_sequence,R2_longest_len)

adaptor = 'AGATGTGTATAAGAGACAG'
META_longest_len = max([len(i) for i in META_sequence])
META_index_dict = dict()
blacklist = set()
for i in META_sequence:
    if len(i) < META_longest_len:
        m = META_longest_len - len(i)
        index = i + adaptor[0:m]
    else:
        index = i
    for k in range(META_longest_len-1):
        for l in range(k+1,META_longest_len):
            for b1 in base:
                for b2 in base:
                    tolerant_index = index[0:k]+b1+index[(k+1):l]+b2+index[l+1:]
                    if tolerant_index not in META_index_dict:
                        META_index_dict[tolerant_index] = META_sequence[i]
                    elif META_index_dict[tolerant_index] != META_sequence[i]:
                        blacklist.add(tolerant_index)
for index in blacklist:
    del(META_index_dict[index])

output_dir = sys.argv[5]
ID = sys.argv[6]

output_R1 = dict()
output_R2 = dict()
for index in indexToSample:
    i = indexToSample[index]
    if not os.path.exists('/'.join([output_dir,ID,ID+'_'+i])):
        os.makedirs('/'.join([output_dir,ID,ID+'_'+i]))
    output_R1[i] = gzip.open('/'.join([output_dir,ID,ID+'_'+i,ID+'_'+i+'_R1.fastq.gz']),'wt')
    output_R2[i] = gzip.open('/'.join([output_dir,ID,ID+'_'+i,ID+'_'+i+'_R2.fastq.gz']),'wt')

total_number = 0
pass_number = 0
read_number = dict()
META_number = dict()
for index in indexToSample:
    read_number[indexToSample[index]] = 0
    META_number[indexToSample[index]] = 0

f1 = gzip.open(sys.argv[1],'rt')
f2 = gzip.open(sys.argv[2],'rt')

read1 = dict()
read2 = dict()
while(1):
    for i in range(1,5):
        read1[i] = f1.readline()
        read2[i] = f2.readline()
    
    if not read1[1]:
        break
    total_number += 1
    
    if read1[2][0:R1_longest_len] in R1_index_dict and read2[2][0:R2_longest_len] in R2_index_dict:
        i1 = R1_index_dict[read1[2][0:R1_longest_len]]
        i2 = R2_index_dict[read2[2][0:R2_longest_len]]
        
        l1 = len(i1)
        l2 = len(i2)
        if read1[2][l1:l1+META_longest_len] in META_index_dict:
            M1 = META_index_dict[read1[2][l1:l1+META_longest_len]]
        else:
            M1 = '.'
        if read2[2][l2:l2+META_longest_len] in META_index_dict:
            M2 = META_index_dict[read2[2][l2:l2+META_longest_len]]
        else:
            M2 = '.'
        
        if M1 != '.' and M2 != '.':
            META_number[indexToSample[i1+' '+i2]] +=1
        
        read1[1] = '@'+str(M1)+'-'+str(M2)+'_'+read1[1][1:]
        read2[1] = '@'+str(M1)+'-'+str(M2)+'_'+read2[1][1:]
        
        for i in range(1,5):
            output_R1[indexToSample[i1+' '+i2]].write(read1[i])
            output_R2[indexToSample[i1+' '+i2]].write(read2[i])
        read_number[indexToSample[i1+' '+i2]] +=1
        pass_number += 1
f1.close()
f2.close()

for i in output_R1:
    output_R1[i].close()
    output_R2[i].close()

print('Total: %d' %total_number)
print('Pass: %d' %pass_number)
print('Pass ratio: %f' %(pass_number/total_number))
for i in read_number:
    print('\t'.join([ID+'_'+i,str(read_number[i]),str(META_number[i])]))
