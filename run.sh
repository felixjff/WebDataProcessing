#!/bin/bash

echo "----- SETUP:\n"
echo "----- SETUP: load gcc/6.4.0\n"
module load gcc/6.4.0
echo "----- SETUP: load python"
module load python/3.5.2

echo "----- SETUP: load prun"
module load prun

prun -o testrun -v -np 1 runner.sh $1