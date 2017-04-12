load '../resources/gnuplot-palettes/magma.pal'

set xlabel "Curve Threshold"
set ylabel "Accuracy"

set terminal pngcairo size 700,600 enhanced font 'Verdana,10'
set output outpng

set datafile separator comma
plot filename title "" with linespoints pointtype 20

set terminal tikz color standalone size 2in,2in
set output outtikz

plot filename title "" with linespoints pointtype 20

set out