# How do I work this stuff?

Well, this is organised fairly poorly (as in, really poorly).

If you want to make a graph of an image, check the help for `scripts/testgraph.py`.

Compling and running the experiments (on the graphs I already made):

```sh
cd ciaran-mcs/
make

# ...

./tester.sh

# ...

./gbu-smr.sh
```

And then just kill the processees when you think you've done enough -- look at the files to figure out what ones were successful.
That's pretty much how I got the bounds data.

Other script `scripts/showmatch.py` is useful if you want to plot the MCS on the image to show component matching.