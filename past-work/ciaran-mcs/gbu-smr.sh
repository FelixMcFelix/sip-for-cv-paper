mkdir -p results-gbu-smr

NODES=260

for i in `seq 0 $NODES`;
do
	./solve_subgraph_isomorphism --format=lad_pos --except=$i sequential test/gbu3smr.txt test/gbu2smr.txt > results-gbu-smr/$i &
done

