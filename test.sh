# TIME=`date +%Y-%m-%d_%H-%M-%S`
files=`ls test/test*.jpg test/test*.png`
if [ -e test/tmp.txt ]; then
    rm test/tmp.txt
fi
touch test/tmp.txt

for f in $files
do
    ./src/extract_result.py $f >> test/tmp.txt
done
diff test/answer.txt test/tmp.txt
