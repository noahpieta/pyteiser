import argparse
import numpy as np
import timeit
import numba
import bitarray
import random
import os
import sys

# to make sure relative import works
# for a detailed explanation, see test_matchmaker.py

current_script_path = sys.argv[0]
package_home_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
if package_home_path not in sys.path:
    sys.path.append(package_home_path)

import pyteiser.glob_var as glob_var
import pyteiser.structures as structures
import pyteiser.IO as IO
import pyteiser.matchmaker as matchmaker
import pyteiser.MI as MI
import pyteiser.wrappers.calculate_MI_profiles as calculate_MI_profiles



def handler():
    parser = argparse.ArgumentParser()

    parser.add_argument("--seedfile", type=str)
    parser.add_argument("--rna_fastafile", type=str)
    parser.add_argument("--outfile", type=str)


    parser.set_defaults(
        rna_fastafile = '/Users/student/Documents/hani/iTEISER/step_2_preprocessing/reference_files/reference_transcriptomes/narrow_down_transcripts_list/Gencode_v28_GTEx_expressed_transcripts_fasta/utr_3_fasta/Gencode_v28_GTEx_expressed_transcripts_from_coding_genes_3_utrs_fasta.txt',
        rna_bin_file='/Users/student/Documents/hani/iTEISER/step_2_preprocessing/reference_files/reference_transcriptomes/binarized/Gencode_v28_GTEx_expressed_transcripts_from_coding_genes_3_utrs_fasta.bin',
    )

    args = parser.parse_args()

    return args

# passing callables to timeit: use labmda
# read here: https://stackoverflow.com/questions/31550832/timeit-timeit-variable-importing-in-python



def time_reading_fasta(fasta_file):
    tr_dict_loc = {}
    seqs_order = []
    with open(fasta_file, 'r') as f:
        split_string = f.read().split('>')
        for entry in split_string:
            if entry == '':
                continue
            seq_start = entry.find('\n')
            annotation = entry[:seq_start]
            sequence_string = entry[seq_start + 1:].replace('\n', '')
            current_sequence = structures.w_sequence(len(sequence_string))
            current_sequence.from_sequence(sequence_string)

            time_create_object = timeit.timeit(lambda: structures.w_sequence(len(sequence_string)), number=100)
            time_fill_object = timeit.timeit(lambda: current_sequence.from_sequence(sequence_string), number=100)
            time_compress_object = timeit.timeit(lambda: current_sequence.compress(), number=100)
            time_compress_named_object = timeit.timeit(lambda: IO.compress_named_sequences({annotation: current_sequence}, [annotation]), number=100)

            print("Create object: %.5f" % time_create_object)
            print("Fill object: %.5f" % time_fill_object)
            print("Compress object: %.5f" % time_compress_object)
            print("Compress named object: %.5f" % time_compress_named_object)
            print()


            # curr_timing = timeit.timeit('current_sequence.from_sequence(sequence_string)',
            #                             'from __main__ import current_sequence, sequence_string')
            # print(curr_timing)

            #
            # tr_dict_loc[annotation] = current_sequence
            # seqs_order.append(annotation)

    return tr_dict_loc, seqs_order


def time_compressing_sequences(fasta_file):
    sequences_dict, seqs_order = IO.read_fasta(fasta_file)

    for i in range(len(seqs_order)):
        print(seqs_order[i])


@numba.jit(cache=True, nopython=True, nogil=True)
def do_iterate(x):
    a = 0
    for i in x:
        a = 1


def time_iterating():
    pr_list = [0] * 100000
    pr_numpy = np.array(pr_list)
    time_just_list = timeit.timeit(lambda: do_iterate(pr_list), number=10)
    time_numpy_list = timeit.timeit(lambda: do_iterate(pr_numpy), number=10)

    print("Iterating through 100k long list 10 times takes: ", time_just_list)
    print("Iterating through 100k numpy array 10 times takes: ", time_numpy_list)

    # iterating through numpy array takes 50 times faster than iterating through a list


def time_compressing_profile():
    TOY_ARRAY_LENGTH = 10000
    NUMBER_OF_ONES = 2000

    ones_indices_list = random.sample(range(TOY_ARRAY_LENGTH), NUMBER_OF_ONES)
    ones_indices_set = set(ones_indices_list)
    toy_array = [1 if x in ones_indices_set else 0 for x in range(TOY_ARRAY_LENGTH)]

    toy_bool_array = np.asarray(toy_array, dtype=bool)

    toy_bitarray = bitarray.bitarray(toy_array)
    toy_packbits_array = np.packbits(toy_bool_array)

    time_bitarray = timeit.timeit(lambda: bitarray.bitarray(toy_array), number=10000)
    time_packbits = timeit.timeit(lambda: np.packbits(toy_bool_array), number=10000)

    print("Bitarray conversion takes", time_bitarray)
    print("Numpy conversion takes", time_packbits)

    # Numpy packbits is ~13 times faster than bitarray
    # however, apparenlty, in the nu


def time_discretization():
    vect_to_discr_10k = np.random.normal(size=10000)
    time_discretization = timeit.timeit(lambda: MI.discret_eq_freq(vect_to_discr_10k, nbins=17), number=1000)
    print("Discretization takes: ", time_discretization)


def time_calculate_MI_profiles(calculate_with_numba):
    test_batch_folder = '/Users/student/Documents/hani/programs/pyteiser/data/test_1_batch_snrnpa1'
    seeds_filename = os.path.join(test_batch_folder, 'seeds_4-7_4-9_4-6_14-20_30k_1.bin')
    profiles_filename = os.path.join(test_batch_folder, 'snrnpa_profiles_4-7_4-9_4-6_14-20_30k_1.bin')
    exp_mask_filename = "/Users/student/Documents/hani/programs/pyteiser/data/mask_files/SNRNPA1_PSI_mask.bin"
    nbins = 15
    min_occurences = 5


    decompressed_profiles_array, index_array, values_array = IO.unpack_profiles_and_mask(profiles_filename,
                                                                                         exp_mask_filename, do_print=True)

    discr_exp_profile = MI.discretize_exp_profile(index_array, values_array, nbins)

    value, counts = np.unique(discr_exp_profile, return_counts=True, axis=0)
    print(counts)

    MI_values_array = calculate_MI_profiles.calculate_MI_for_seeds(decompressed_profiles_array, index_array, discr_exp_profile,
                                         min_occurences, calculate_with_numba, do_print = True)


def main():
    args = handler()

    # time_reading_fasta(args.rna_fastafile)
    # time_compressing_sequences(args.rna_fastafile)
    # time_iterating()
    # time_compressing_profile()
    # time_discretization()

    time_calculate_MI_profiles(calculate_with_numba = 'y')




if __name__ == "__main__":
    main()

