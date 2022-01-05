#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 22:15:13 2019

@author: lixiang
"""

import sys

line = sys.stdin.readline()
tmp = line.strip('\n').split('\t')
tmp_ps = min(int(tmp[1]),int(tmp[4]))
tmp_me = max(int(tmp[2]),int(tmp[5]))
tmp_pe = min(int(tmp[2]),int(tmp[5]),tmp_me)
tmp_ms = max(int(tmp[1]),int(tmp[4]),tmp_ps)
tmp_q = int(tmp[7])
tmp_META = {'-'.join(sorted(tmp[6].split('_')[0].split('-')))}
line = sys.stdin.readline()
c = 1
while(line):
    l = line.strip('\n').split('\t')
    ps = min(int(l[1]),int(l[4]))
    me = max(int(l[2]),int(l[5]))
    pe = min(int(l[2]),int(l[5]),me)
    ms = max(int(l[1]),int(l[4]),ps)
    if tmp[0]==l[0] and abs(tmp_ps-ps)+abs(tmp_me-me)<=5:
        tmp_ps = min(tmp_ps,ps)
        tmp_me = max(tmp_me,me)
        tmp_pe = max(tmp_pe,pe)
        tmp_ms = min(tmp_ms,ms)
        tmp_q = max(tmp_q,int(l[7]))
        tmp_META.add('-'.join(sorted(l[6].split('_')[0].split('-'))))
        c += 1
        line = sys.stdin.readline()
    else:
        tmp[6] = ','.join(sorted(list(tmp_META)))
        tmp[7] = str(tmp_q)
        sys.stdout.write('\t'.join([tmp[0],str(tmp_ps),str(tmp_pe),tmp[0],
            str(tmp_ms),str(tmp_me),tmp[6],tmp[7],'+','-',str(c)])+'\n')
        tmp = l.copy()
        tmp_ps = min(int(tmp[1]),int(tmp[4]))
        tmp_me = max(int(tmp[2]),int(tmp[5]))
        tmp_pe = min(int(tmp[2]),int(tmp[5]),tmp_me)
        tmp_ms = max(int(tmp[1]),int(tmp[4]),tmp_ps)
        tmp_q = int(tmp[7])
        tmp_META = {'-'.join(sorted(tmp[6].split('_')[0].split('-')))}
        c = 1
        line = sys.stdin.readline()
    if not line:
        tmp[6] = ','.join(sorted(list(tmp_META)))
        tmp[7] = str(tmp_q)
        sys.stdout.write('\t'.join([tmp[0],str(tmp_ps),str(tmp_pe),tmp[0],
            str(tmp_ms),str(tmp_me),tmp[6],tmp[7],'+','-',str(c)])+'\n')