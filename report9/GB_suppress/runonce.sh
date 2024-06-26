#!/bin/bash
# ../../build/src/CovidSim /c:8 /PP:preGB_R0=2.0.txt /P:p_NoInt.txt /CLP1:100000 /CLP2:0 /O:NoInt_R0=2.4 /D:../population/GB_pop2018_nhs.txt /M:../population/GB_pop2018.bin /S:../population/NetworkGB_8T.bin /R:1.2 98798150 729101 17389101 4797132

for R in 2.6
do
    rs=$(echo $R | awk '{print $1/2}')
    echo ../../build/src/CovidSim /c:120 /PP:preGB_R0=2.0.txt /P:p_NoInt.txt /CLP1:100000 /CLP2:0 /O:NoInt_R0=${R} /D:../population/GB_pop2018_nhs.txt /M:../population/GB_pop2018.bin /S:../population/NetworkGB_120T.bin /R:${rs} 98798150 729101 17389101 4797132
done
