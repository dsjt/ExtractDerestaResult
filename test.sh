# TIME=`date +%Y-%m-%d_%H-%M-%S`
files="dat/test0.jpg dat/test1.jpg dat/test2.jpg dat/test3.jpg"
for f in $files
do
    ./extract_result.py $f
done
open $files
