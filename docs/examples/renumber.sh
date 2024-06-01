#!/bin/bash

for n in $(seq $1 89)
do
   m=$((n+1))
   f1=$(printf '%02d-' $n)
   f2=$(printf '%02d-' $m)
   p=$(ls $f1*.ipynb 2>/dev/null)
   if [[ -f $p ]]
   then
      q=$(echo $p | sed s/$f1/$f2/)
      echo $p $q
      git mv $p $q
   fi
done
