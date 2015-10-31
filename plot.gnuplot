set terminal png nocrop enhanced size 1000,200 font "arial,8" 
set output targetfn
#set key bmargin left horizontal Right noreverse enhanced autotitle box lt black linewidth 1.000 dashtype solid
#set samples 800, 800

# add bg grid
set style line 102 lc rgb '#767779' lt 0 lw 1
set xtics 1
set ytics 5
set grid xtics ytics back ls 102
set xrange [1:39]
set title sourcefn
plot sourcefn with lines title "Total", avgfn with lines title "Average", primfn with lines title "Primary'

