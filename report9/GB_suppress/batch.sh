#!/bin/bash

allR="2.0 2.2 2.4 2.6"
R="2.0"
allx="60 100 200 300 400"
x="60"
allz="0.75 0.5 0.25"
z="0.75"
alli="CI_HQ_SD PC_CI_SD PC_CI_HQ_SD"
i="PC_CI_HQ_SD"

for R in $allR
do
    rs=$(echo $R | awk '{print $1/2}')
    echo ../../build/src/CovidSim /NR:10 /c:70 /PP:preGB_R0=2.0.txt /P:p_NoInt.txt /CLP1:100000 /CLP2:0 /O:meanT8_NR10/NoInt_R0=${R} /D:../population/GB_pop2018.bin /L:../population/NetworkGB_8T.bin /R:${rs} 98798150 729101 17389101 4797132
    for x in $allx
    do
	for z in $allz
	do
	    q=1000
	    y=$(echo $x  $z | awk '{print $1 * $2}')
	    #echo $y
	    for i in $alli
	    do
		echo ../../build/src/CovidSim /NR:10 /c:70 /PP:preGB_R0=2.0.txt /P:p_${i}.txt /CLP1:${x} /CLP2:${q} /CLP3:${q} /CLP4:${q} /CLP5:${y} /O:meanT8_NR10/${i}_${x}_${y}_R0=${R} /D:../population/GB_pop2018.bin /L:../population/NetworkGB_8T.bin /R:${rs} 98798150 729101 17389101 4797132
	    done
	done
    done
done


# rs=$(echo $R | awk '{print $1/2}')
# ../../build/src/CovidSim /NR:10 /c:70 /PP:preGB_R0=2.0.txt /P:p_NoInt.txt /CLP1:100000 /CLP2:0 /O:meanT8_NR10/NoInt_R0=${R} /D:../population/GB_pop2018.bin /L:../population/NetworkGB_8T.bin /R:${rs} 98798150 729101 17389101 4797132

# q=1000
# y=$(echo $x  $z | awk '{print $1 * $2}')
# ../../build/src/CovidSim /NR:10 /c:70 /PP:preGB_R0=2.0.txt /P:p_${i}.txt /CLP1:${x} /CLP2:${q} /CLP3:${q} /CLP4:${q} /CLP5:${y} /O:meanT8_NR10/${i}_${x}_${y}_R0=${R} /D:../population/GB_pop2018.bin /L:../population/NetworkGB_8T.bin /R:${rs} 98798150 729101 17389101 4797132