![Alt text](/images_github/pyteiser_logo_v2_hossein.png?raw=true)
# Pyteiser
A framework for identifying the structural motifs that are informative of whole-genome measurements across all the transcripts

### Table of contents

### Introduction
pyteiser identifies structural motifs that could explain genome-wide changes in gene expression, stability or other quantitative transcriptomic measures.
pyteiser encodes structural motifs as context-free grammars (CFG) that represents short stem-loop structures along with a known primary sequence. <br>
First, pyteiser generates a comprehensive set of short seeds (of length 8-16) with a given information content: the seeds are generated in the way that they are not too specific but also not too general. An example seed would have a secondary structure of `<<<<......>>>>` and a sequence of `AAUNNGNGNUNAUU`. <br>
Then, the given RNA sequences (for example, 3'UTRs) are scanned for the occurrence of all the seeds. At that stage, each seed is assigned a binary representation vector, showing which transcripts contain matches for this seed and which ones do not. For example, if a user provided expression values for N sequences, the representation vector will be of length N and each element will be set to "1" if the corresponding fragment has a match to the given seed or "0" if it doesn't.  <br>
Then, each seed's binary vector is tested to assess whether it is informative of the input whole-genome measurements. For example, if the expression change values for transcripts [A, B, C and D] are [High, High, Low, Low] and the binary representation vector for seed X is [1, 1, 0, 0] we make a conclusion that the seed X might be informative of the expression changes. To capture such dependency we use Mutual Information (MI) (see Cover and Thomas, 2006). <br>
Then, pyteiser runs several non-parametric statistical tests to determine which seeds are significantly informative of expression changes and which ones are not. The seeds that did not pass the statistical tests get filtered out. <br>
Then, the seeds that passed the tests are classified by "families" - groups of seeds with very similar representation vectors. The initial set of seeds pyteiser works with is redundant, so several seeds can be very similar to each other and match the same sequences. Such redundant groups of seeds get collapsed into groups or "families". <br>
Then, a single representative seed is chosen for family. The representative seeds is then optimized by a greedy algorithm. The algorithm applies small consecutive changes to sequence and structure of the motif up until the changes don't make the seed more informative of genome-wide measurements anymore. For example, if changing the 1st nucleotide of the seed `AAUNNGNGNUNAUU` to 'G' makes the seed's representation vector more informative of the observed expression values, the algorithm keeps such change. The final oprimized seed is being tested for robustness: the statistical tests for seed significance are being repeated with down-sampled expression data. If the seed is not robust to down-sampling of expression data, it gets filtered out. <br>
Finally, the seeds that have passed all the tests are ranked by how informative are they in regard to the transcriptomic measures provided. Text and graphic reports are being printed, showing motif logos, patterns of their representation, their statistical significance etc. <br>

pyteiser is a successor of TEISER (see [link](https://tavazoielab.c2b2.columbia.edu/TEISER/)). pyteiser is built around the same concept. The overall pipeline is similar, however, several changes and improvements were made. pyteiser performs additional testing of seed matches using *in silico* RNA secondary structure prediction. The statistical tests and optimization algorithms were improved. pyteiser is also capable of handling SHAPE RNA secondary structure probing data; such data provide additional information about RNA secondary structures that do or do not exist in the cell *in vivo*.

pyteiser is written in Python 3.7. The computationally heavy funcions are implemented efficiently through extensive usage on [numpy](https://numpy.org/) arrays and [numba](http://numba.pydata.org/) Python compiler.

## Getting started
### Requirements
pyteiser requires the following dependencies to be installed:
- Python modules:
	- numpy
	- numba
	- pandas
- Other tools:
	- ViennaRNA
It is highly recommended to install the dependencies through conda.
install miniconda


### Installation
Currently, pyteiser is distributed as a set of scripts rather than a pip-installable package. Release of pip-installable version is scheduled for February 2020. <br>
You can either run a command `git clone https://github.com/goodarzilab/pyteiser.git` in your terminal or click "Clone or download" in the top right corner of this page.

## Usage
The package consists of:
- set of modules where the core functions are implemented (`pyteiser/pyteiser`)
- set of wrapper scripts that implement individual steps of the pipeline (`pyteiser/pyteiser/wrappers`)

Several steps of the pipeline are computationally demanding and therefore are recommended to be run on a High Performance Computing machine. Depending on the institution / company you are at the HPC you are using might have different job submission requirements. In particular, the keywords for memory or time requests might differ among individual HPC systems. We recommend running each step of the pipeline individually since it might be hard to reserve cores on HPC for long enough to be able to run the whole pipeline in a single run. <br>
We provide frameworks for either running the scripts on your own machine or submitting it to SGE-based HPCs through `qsub` command. <br>
For each computationally heavy step of the pipeline, we provide a script that runs on its own and also a script that is adjusted for submission through qsub.  <br>
We also provide a universal script for qsub submission (named `qsub_universal_submission.py`) that lets you (i) specify the keywords the HPC machine you're using requires, (ii) request how much time, memory and cores do you want to use and (iii) submit any of the computationally heavy scripts from the pipeline. <br>
For any script, you can list the required arguments with the command
```
python <script_name> --help
```
You will have to specify the input and output folders you want to use. All the numeric parameters have preset default values; changing them is not recommended unless you have a very specific reason to do so. <br>
Below, the steps of the pipeline are listed along with the name of the corresponding script.

### Steps of the pipeline:
#### 1. Generate seeds
	Use pyteiser/seeds_generator.py
#### 2. Convert sequences from fasta to binary format
	Use pyteiser/wrappers/binarize_sequences.py
#### 3. Precalculate seed occurence profiles
	Use pyteiser/wrappers/calculate_seed_profiles.py - run on HPC!
#### 4. Preprocess the expression file of interest
	Use either pyteiser/wrappers/preprocess_expression_profile_ensembl.py or pyteiser/wrappers/preprocess_custom_expression_profile.py
#### 5. Calculate MI values for all the seeds
	Use pyteiser/wrappers/calculate_MI_profiles.py - run on HPC!
#### 6. Choose significance thresholds
	Use pyteiser/wrappers/choose_significant_seeds_v3.py - run on HPC!
#### 7. Combine seeds that passed
	Use pyteiser/wrappers/combine_passed_seeds.py
#### 8. Classify seeds by families
	Use pyteiser/wrappers/filter_passed_seeds_with_CMI.py
#### 9. Optimize seeds
	Use pyteiser/wrappers/optimize_seeds_single_chunk.py - run on HPC! You can submit it with pyteiser/wrappers/qsub_optimize_seeds.py
#### 10. Combine optimized seeds
	Use pyteiser/wrappers/combine_optimized_seeds.py

### Input files formats
The user is expected to provide 2 input files: a table with the genome-wide measurements of interest and a fasta file with sequences of reference transcriptome.


### Preprocessing of input files


### License
MIT license

### Citing
See the preprint

### About pyteiser
pyteiser has been developed in Goodarzi lab at UCSF by Matvei Khoroshkin and Hani Goodarzi

