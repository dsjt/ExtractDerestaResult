# TIME=`date +%Y-%m-%d_%H-%M-%S`
files=`ls test/test*.jpg`
TEMP=test/test02.jpg
for f in $TEMP
do
    ./src/extract_result.py $f
done
eog $TEMP
