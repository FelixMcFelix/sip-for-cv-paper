load '../resources/gnuplot-palettes/magma.pal'

set xlabel xl
set ylabel yl

set terminal pngcairo size 700,600 enhanced font 'Verdana,10'
set output outpng

set datafile separator comma
plot filename using (column(xc)):(column(yc)) title "" with points pointtype 20

set terminal tikz color standalone size 6in,6in
set output outtikz

plot filename using (column(xc)):(column(yc)) title "" with points pointtype 20

set out