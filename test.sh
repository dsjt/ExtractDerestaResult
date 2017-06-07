# TIME=`date +%Y-%m-%d_%H-%M-%S`
files=`ls dat/test*.jpg`
for f in $files
do
    ./extract_result.py $f
done
open $files
