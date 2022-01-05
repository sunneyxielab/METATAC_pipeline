#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 14:42:54 2020

@author: lixiang
Modified by Jian Fanchong on 2021/2/3
"""

import sys
import gzip

import networkx as nx


def META_seq(s):
    meta_seq = set()
    for l in s.split(','):
        meta_seq.update(l.split('-'))
    if '.' in meta_seq:
        meta_seq.remove('.')
    return(meta_seq)

def add_line(Cell_info, C1, C2):
    frag = Cell_info[C1]['frag'] == Cell_info[C2]['frag']
    #plate = (C1.split('_')[-3] == C2.split('_')[-3]) and (C1.split('_')[-2] == C2.split('_')[-2])
    plate = C1.split('_')[0].split('-')[-1] == C2.split('_')[0].split('-')[-1]
    row = C1.split('_')[-1].split('-')[0] == C2.split('_')[-1].split('-')[0]
    col = C1.split('_')[-1].split('-')[1] == C2.split('_')[-1].split('-')[1]
    meta = not Cell_info[C1]['META'].isdisjoint(Cell_info[C2]['META'])
    return(sum([frag,plate,row,col,meta]) >= 3)

def frag_dist(frag1,frag2):
    l1 = frag1.split('\t')
    l2 = frag2.split('\t')
    dist = abs(int(l1[1])-int(l2[1])) + abs(int(l1[2])-int(l2[2]))
    return(dist <= 5)

def merge_frag(frag1,frag2):
    l1 = frag1.split('\t')
    l2 = frag2.split('\t')
    s = min(int(l1[1]),int(l2[1]))
    e = max(int(l1[2]),int(l2[2]))
    return('\t'.join([l1[0],str(s),str(e)]))

def argmax_dict(D, keys = None):
    if not keys:
        keys = D.keys()
    m = 0
    arg_m = []
    for i in keys:
        if D[i]['freq'] > m:
            m = D[i]['freq']
            arg_m = [i]
        elif D[i]['freq'] == m:
            arg_m.append(i)
    return(arg_m)


f = gzip.open(sys.argv[1],'rt')
f2 = open(sys.argv[2],'w')
f3 = open(sys.argv[3],'w')

line = f.readline()
l = line.strip('\n').split('\t')
tmp_chr = l[0]
tmp_frag = '\t'.join(l[0:3])
cell_info = {l[3]:{'frag':tmp_frag, 'freq':int(l[4]), 'META':META_seq(l[5])}}

line = f.readline()
while(line):
    l = line.strip('\n').split('\t')
    frag = '\t'.join(l[0:3])
    if tmp_chr == l[0] and frag_dist(tmp_frag,frag):
        cell_info[l[3]] = {'frag':frag, 'freq':int(l[4]), 'META':META_seq(l[5])}
        tmp_frag = merge_frag(tmp_frag,frag)
    else:
        if len(cell_info) == 1:
            for c in cell_info:
                f2.write('\t'.join([cell_info[c]['frag'],c,str(cell_info[c]['freq'])])+'\n')
        else:
            cells = list(cell_info.keys())
            G = nx.Graph()
            G.add_nodes_from(cells)
            for i,c1 in enumerate(cells[:-1]):
                for c2 in cells[i+1:]:
                    if add_line(cell_info, c1, c2):
                        G.add_edge(c1,c2)
            
            for cc in nx.connected_components(G):
                if len(cc)==1:
                    for c in cc:
                        f2.write('\t'.join([cell_info[c]['frag'],c,str(cell_info[c]['freq'])])+'\n')
                else:
                    cs = argmax_dict(cell_info,keys = cc)
                    if len(cs)==1:
                        c = cs[0]
                        f2.write('\t'.join([cell_info[c]['frag'],c,str(cell_info[c]['freq'])])+'\n')
                    else:
                        for c in cs:
                            f3.write('\t'.join([cell_info[c]['frag'],c,str(cell_info[c]['freq'])])+'\n')
    
        tmp_chr = l[0]
        tmp_frag = frag
        cell_info = {l[3]:{'frag':frag, 'freq':int(l[4]), 'META':META_seq(l[5])}}
    
    line = f.readline()
    
    if not line:
        if len(cell_info) == 1:
            for c in cell_info:
                f2.write('\t'.join([cell_info[c]['frag'],c,str(cell_info[c]['freq'])])+'\n')
        else:
            cells = list(cell_info.keys())
            G = nx.Graph()
            G.add_nodes_from(cells)
            for i,c1 in enumerate(cells[:-1]):
                for c2 in cells[i+1:]:
                    if add_line(cell_info, c1, c2):
                        G.add_edge(c1,c2)
            
            for cc in nx.connected_components(G):
                if len(cc)==1:
                    for c in cc:
                        f2.write('\t'.join([cell_info[c]['frag'],c,str(cell_info[c]['freq'])])+'\n')
                else:
                    cs = argmax_dict(cell_info,keys = cc)
                    if len(cs)==1:
                        c = cs[0]
                        f2.write('\t'.join([cell_info[c]['frag'],c,str(cell_info[c]['freq'])])+'\n')
                    else:
                        for c in cs:
                            f3.write('\t'.join([cell_info[c]['frag'],c,str(cell_info[c]['freq'])])+'\n')

f.close()
f2.close()
f3.close()
