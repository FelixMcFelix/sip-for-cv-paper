set terminal pngcairo size 700,600 enhanced font 'Verdana,10'
set output outpng

set datafile separator comma
plot filename matrix rowheaders columnheaders using 1:2:3 with image pixels

set terminal tikz color standalone size 6in,6in
set output outtikz

plot filename matrix rowheaders columnheaders using 1:2:3 with image pixels

set out