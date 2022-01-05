#!/bin/bash

act=do_mapping
sp=mouse
IN=../01-cleandata
OUT=../02-mapping
mkdir -p $OUT
cpu=2
mem=8g
ref=/share/home/lix/genomes/mouse/GRCm38/index
scripts=./pyscripts
tmp=./tmp


function do_main {
batch=$1
id=$2

read1=$IN/$batch/${id}/${id}_R1.fastq.gz
read2=$IN/$batch/${id}/${id}_R2.fastq.gz
cut1=$OUT/$batch/${id}/${id}_cut_R1.fastq.gz
cut2=$OUT/$batch/${id}/${id}_cut_R2.fastq.gz

aln=$OUT/$batch/${id}/${id}_${sp}_aln.bam
bedpe=$OUT/$batch/${id}/${id}_${sp}_bedpe.bed
frag=$OUT/$batch/${id}/${id}_${sp}_frag.bed

cat << EOF > $tmp/${act}_${id}_${sp}.tmp.sh
#!/bin/bash

# Adapter trimming
if [[ ! -e $cut1 ]]
then
    cutadapt --quiet -e 0.22 -j 10 -a CTGTCTCTTATACACATCT -o - $read1 |cutadapt --quiet -e 0.22 -j 10 -g AGATGTGTATAAGAGACAG -o $cut1 -
    cutadapt --quiet -e 0.22 -j 10 -a CTGTCTCTTATACACATCT -o - $read2 |cutadapt --quiet -e 0.22 -j 10 -g AGATGTGTATAAGAGACAG -o $cut2 -
fi

# Mapping

bowtie2 -p $cpu -X 2000 --local --mm --no-discordant --no-mixed -x $ref -1 $cut1 -2 $cut2 |samtools view -bS -F 12 |samtools sort -n - > $aln

# Generate fragments
bamToBed -i $aln -bedpe |grep chr |awk 'BEGIN{OFS="\\t"}(\$8>=30){print \$0}' |sort -k 1,1 -k 2g,2 -k 6g,6 |python $scripts/bedpe_process.py > $bedpe
cat $bedpe |grep chr[0-9XYM]* |awk 'BEGIN{OFS="\\t"}{print \$1,\$2+4,\$6-5,\$7,\$11}' > $frag
EOF

chmod 750 $tmp/${act}_${id}_${sp}.tmp.sh

cat << EOF > $tmp/run_${act}_${id}_${sp}.tmp.sh
#!/bin/bash

set -x

sbatch -J ${act}_${id}_${sp} --partition=compute_new --nodelist=node10 --export=ALL -c $cpu --mem=$mem -o $OUT/$batch/${id}/${act}2_${id}_${sp}.o.txt -e $OUT/$batch/${id}/${act}2_${id}_${sp}.e.txt $tmp/${act}_${id}_${sp}.tmp.sh

set +x
EOF

chmod 750 $tmp/run_${act}_${id}_${sp}.tmp.sh

echo $id
bash $tmp/run_${act}_${id}_${sp}.tmp.sh
}

function do_go {
ls $IN | while read Batch
do
    echo $Batch
	ls $IN/$Batch | grep -v clean | while read Id
	do
		 if [[ ! -e $OUT/$Batch/${Id}/${Id}_${sp}_frag.bed ]]
		 then
		    mkdir -p $OUT/$Batch/${Id}
			do_main $Batch $Id
		 else
            echo "[skip] $Id"
         fi
	done
done
}

do_go

