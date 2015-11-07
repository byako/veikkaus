Set of scripts to fetch, and animate results of lotto

./fetch-results.py - gets result of veikkaus lotto for single week
 - saves JSON into ./results/*
 - takes parameters : year (2009-$YEAR), week (0-52)

./gen_plot_source.py - convert JSONs into gnuplot source
 - creates input files for gnuplot out of results/* into plot/*
 - takes no parameters, processes all files in results/*

./anim.sh: creates anim.gif
 - creates with gnuplot 1000x200 px png/* images out of plot/*
 - combines with convert png/* into anime.gif
