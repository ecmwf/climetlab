:
# See https://github.com/vscode-restructuredtext/vscode-restructuredtext/issues/280
for n in $(find . -name '*.rst')
do
   m=$(echo $n | sed 's/\.rst//' | sed 's,^\./,,')
   egrep ":doc:.$m" index.rst > /dev/null || echo $m
done
