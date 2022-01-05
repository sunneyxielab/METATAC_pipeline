#!/bin/bash

IN=../00-rawdata
OUT=../01-cleandata
INDEX=.
scripts=./pyscripts
tmp=./tmp

mkdir -p $OUT
mkdir -p $tmp

cpu=1
mem=1G

act=do_cleanFq

function do_main {
id=$1

# read1=`ls $IN/$id/${id}*_R1*.fastq.gz`
# read2=`ls $IN/$id/${id}*_R2*.fastq.gz`
read1=`ls $IN/${id}/*_R1.f*q.gz`
read2=`ls $IN/${id}/*_R2.f*q.gz`

cat << EOF > $tmp/${act}_${id}.tmp.sh
#!/bin/bash
echo -ne ">:>\t"; date
echo $id

echo "\$read1 \$read2"

python $scripts/cleanFq.py $read1 $read2 $INDEX/indexToSample_v3.txt $INDEX/META16_Sequence.sh $OUT $id

echo -ne ">:>\t"; date
echo "Done..."
EOF
chmod 750 $tmp/${act}_${id}.tmp.sh

cat << EOF > $tmp/run_${act}_${id}.tmp.sh
#! /bin/bash

set -x
mkdir -p $OUT/$id
sbatch -J  ${act}_${id} \\
-D . \\
--export=ALL \\
-c $cpu \\
--partition=compute_new \\
--mem=$mem \\
-o $OUT/$id/${act}_${id}.o.txt \\
-e $OUT/$id/${act}_${id}.e.txt \\
$tmp/${act}_${id}.tmp.sh
set +x
EOF

# cat << EOF > run_${act}_${id}.tmp.sh
# #!/bin/bash
# #SBATCH -J ${act}_${id}
# #SBATCH -p cn_icg
# #SBATCH -N 1
# #SBATCH -o $OUT/$id/${act}_${id}.o.txt
# #SBATCH -e $OUT/$id/${act}_${id}.e.txt
# #SBATCH --no-requeue
# #SBATCH -A xie_g1
# #SBATCH --qos=xiecnicg
# #SBATCH -c $cpu
# pkurun  ${act}_${id}.tmp.sh
# EOF

chmod 750 $tmp/run_${act}_${id}.tmp.sh
bash $tmp/run_${act}_${id}.tmp.sh
}

ls $IN |while read Id
do
    if [[ ! -e $OUT/${Id}/${act}_${Id}.o.txt ]]
	then
		mkdir -p $OUT/$Id
		echo $Id
		do_main $Id
	else
	    echo "[skip] $Id"
	fi
done
