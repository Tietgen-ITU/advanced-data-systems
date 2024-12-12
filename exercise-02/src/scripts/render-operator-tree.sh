#!/bin/bash

path=$1

files=$(ls $path)

for file in $files
do
    dname=$(dirname $file)
    fname=$(basename $file)
    python render-operator-tree.py $file > "${dname}/operator-trees/${fname}.dot"
done