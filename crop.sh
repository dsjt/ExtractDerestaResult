# デレステの結果のスクショから数字部分を切り出すプログラム

usage_exit() {
        echo "Usage: $0 [-d dir] img ..." 1>&2
        exit 1
}

while getopts d: OPT
do
    case $OPT in
        d) directory=$OPTARG
           ;;
        \?) usage_exit
    esac
done
shift $((OPTIND - 1))

tune=$1

if [ -z $directory ]; then
    directory=`date +%Y-%m-%d_%H-%M-%S`
fi

if [ ! -e $directory ]; then
    mkdir $directory
fi

# 曲名
convert -crop 102x21+215+141 -type GrayScale $tune $directory/title.jpg
# 難易度
convert -crop 96x20+173+100 $tune $directory/difficulty.jpg

# 楽曲Lv
convert -crop 11x15+419+103 -resize 18x26 -type GrayScale $tune $directory/lv01.jpg
convert -crop 11x15+431+103 -resize 18x26 -type GrayScale $tune $directory/lv02.jpg

# perfect
convert -crop 16x23+371+206 -resize 18x26 -type GrayScale $tune $directory/PERFECT01.jpg
convert -crop 16x23+390+206 -resize 18x26 -type GrayScale $tune $directory/PERFECT02.jpg
convert -crop 16x23+409+206 -resize 18x26 -type GrayScale $tune $directory/PERFECT03.jpg
convert -crop 16x23+428+206 -resize 18x26 -type GrayScale $tune $directory/PERFECT04.jpg
# great
convert -crop 16x23+371+241 -resize 18x26 -type GrayScale $tune $directory/GREAT01.jpg
convert -crop 16x23+390+241 -resize 18x26 -type GrayScale $tune $directory/GREAT02.jpg
convert -crop 16x23+409+241 -resize 18x26 -type GrayScale $tune $directory/GREAT03.jpg
convert -crop 16x23+428+241 -resize 18x26 -type GrayScale $tune $directory/GREAT04.jpg
# nice
convert -crop 16x23+371+276 -resize 18x26 -type GrayScale $tune $directory/NICE01.jpg
convert -crop 16x23+390+276 -resize 18x26 -type GrayScale $tune $directory/NICE02.jpg
convert -crop 16x23+409+276 -resize 18x26 -type GrayScale $tune $directory/NICE03.jpg
convert -crop 16x23+428+276 -resize 18x26 -type GrayScale $tune $directory/NICE04.jpg
# bad
convert -crop 16x23+371+311 -resize 18x26 -type GrayScale $tune $directory/BAD01.jpg
convert -crop 16x23+390+311 -resize 18x26 -type GrayScale $tune $directory/BAD02.jpg
convert -crop 16x23+409+311 -resize 18x26 -type GrayScale $tune $directory/BAD03.jpg
convert -crop 16x23+428+311 -resize 18x26 -type GrayScale $tune $directory/BAD04.jpg
# miss
convert -crop 16x23+371+346 -resize 18x26 -type GrayScale $tune $directory/MISS01.jpg
convert -crop 16x23+390+346 -resize 18x26 -type GrayScale $tune $directory/MISS02.jpg
convert -crop 16x23+409+346 -resize 18x26 -type GrayScale $tune $directory/MISS03.jpg
convert -crop 16x23+428+346 -resize 18x26 -type GrayScale $tune $directory/MISS04.jpg

# combo
convert -crop 17x24+365+400 -resize 18x26 -type GrayScale $tune $directory/COMBO01.jpg
convert -crop 17x24+386+400 -resize 18x26 -type GrayScale $tune $directory/COMBO02.jpg
convert -crop 17x24+407+400 -resize 18x26 -type GrayScale $tune $directory/COMBO03.jpg
convert -crop 17x24+428+400 -resize 18x26 -type GrayScale $tune $directory/COMBO04.jpg

# full combo
convert -crop 105x28+372+368 $tune $directory/full_combo.jpg

# new record
convert -crop 105x29+372+450 $tune $directory/new_record.jpg

# score
convert -crop 18x26+301+480 -resize 18x26 -type GrayScale $tune $directory/score01.jpg
convert -crop 18x26+322+480 -resize 18x26 -type GrayScale $tune $directory/score02.jpg
convert -crop 18x26+343+480 -resize 18x26 -type GrayScale $tune $directory/score03.jpg
convert -crop 18x26+364+480 -resize 18x26 -type GrayScale $tune $directory/score04.jpg
convert -crop 18x26+385+480 -resize 18x26 -type GrayScale $tune $directory/score05.jpg
convert -crop 18x26+406+480 -resize 18x26 -type GrayScale $tune $directory/score06.jpg
convert -crop 18x26+427+480 -resize 18x26 -type GrayScale $tune $directory/score07.jpg

# high score
convert -crop 16x21+321+521 -resize 18x26 -type GrayScale $tune $directory/high_score01.jpg
convert -crop 16x21+339+521 -resize 18x26 -type GrayScale $tune $directory/high_score02.jpg
convert -crop 16x21+357+521 -resize 18x26 -type GrayScale $tune $directory/high_score03.jpg
convert -crop 16x21+375+521 -resize 18x26 -type GrayScale $tune $directory/high_score04.jpg
convert -crop 16x21+393+521 -resize 18x26 -type GrayScale $tune $directory/high_score05.jpg
convert -crop 16x21+411+521 -resize 18x26 -type GrayScale $tune $directory/high_score06.jpg
convert -crop 16x21+429+521 -resize 18x26 -type GrayScale $tune $directory/high_score07.jpg

# PRP
convert -crop 15x19+332+573 -resize 18x26 -type GrayScale $tune $directory/PRP01.jpg
convert -crop 15x19+348+573 -resize 18x26 -type GrayScale $tune $directory/PRP02.jpg
convert -crop 15x19+364+573 -resize 18x26 -type GrayScale $tune $directory/PRP03.jpg
convert -crop 15x19+380+573 -resize 18x26 -type GrayScale $tune $directory/PRP04.jpg
