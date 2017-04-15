mkdir -p results

NODES=245

for i in `seq 0 $NODES`;
do
	./solve_subgraph_isomorphism --format=lad_pos --except=$i sequential test/norm.txt test/180.txt > results/$i &
done

