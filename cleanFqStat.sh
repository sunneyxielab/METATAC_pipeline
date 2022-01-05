#!/bin/bash

IN=../01-cleandata
OUT=../merge
date=0607
mkdir -p $OUT

function do_go2 {
output_file=${OUT}/cleanFqStat.txt
echo "Batch	Total	Cell_id	Barcode	META" > $output_file
ls $IN | grep -v txt | while read Batch
do
	Total=`grep '^Total' $IN/$Batch/${date}_do_cleanFq_${Batch}.o.txt |cut -d ' ' -f 2`
	grep ^${Batch}_ $IN/$Batch/${date}_do_cleanFq_${Batch}.o.txt |awk 'BEGIN{OFS="\t"}{print "'$Batch'\t'$Total'",$0}' >> $output_file
done
}
do_go2; exit

