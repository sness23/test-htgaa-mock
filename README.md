# test-htgaa-mock
HTGAA23

To generate the image:

convert marilyn-monroe-6.jpg -negate -resize 40x40 -threshold 50% marilyn.txt
tail -n +2 marilyn.txt | grep -v "(0," | cut -f 1 -d ":" > marilyn.csv
