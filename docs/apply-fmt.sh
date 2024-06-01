:
for n in $(find . -name '*.rst')
do
   rstfmt  $n
done
