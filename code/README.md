# Instructions for Running!

All scripts run on python 2.7.

If you want to fully regenerate the datasets, you will need ImageMagick installed. You will also need to download a copy of the HWRT dataset -- link and instructions are located in resources/hwrt.
This WILL take a sizeable amount of time! Only do this if you're absurdly paranoid.

```sh
./prep_data.sh
```

To then generate all graphs (again, lengthy amount of time):

```sh
python batchgraph.py
```

If you wish to run the experiments, you'll first need to change ```num_cores = 8``` in config.py as appropriate for your system. After this, build the job lists and compile the similarity tools and classifier:

```sh
./make_jobs.sh
cd sip-mcs
make
```

To run the experiments after this, from this folder run each of these, wait patiently until all the `search_subgraph_isomorphism` or `solve_subgraph_isomorphism` processes quit and stop spamming your terminal:

```sh
cd jobs/mcs
./run_tests.sh
```
and

```sh
cd jobs/search
./run_tests.sh
```

To generate plots from the results:

```sh
./process_results.sh
```