# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fileIO.IOManager import OUTPUT_FILE_FORMATS, INPUT_FILE_FORMATS
from settings.ReactionNotation import ReactionNotation, ArrowNotation
import tools.CommandLineTool as clt
import main.CatPyNet as cpn
import fileIO.GraphIO as gio
from algorithm.AlgorithmBase import AlgorithmBase
from algorithm.MaxRAFAlgorithm import MaxRAFAlgorithm
from algorithm.MaxCAFAlgorithm import MaxCAFAlgorithm
from algorithm.MinIRAFHeuristic import MinIRAFHeuristic
from algorithm.CoreRAFAlgorithm import CoreRAFAlgorithm
from algorithm.MaxPseudoRAFAlgorithm import MaxPseudoRAFAlgorithm
from os import listdir
from os.path import isfile, join
from tqdm import tqdm

algos = AlgorithmBase.list_all_algorithms()
mypath = "G:\\Github\\BA-Jan\\test_files"
respath = "D:\\Users\\jrls2_000\\Documents\\UNI\\_BA\\test_data_results"
test_files = [f for f in listdir(mypath) if isfile(join(mypath, f)) 
              and os.path.splitext(f)[1] in INPUT_FILE_FORMATS]

real_res = {"Max RAF":{"example-0.crs":{"food":3,
                                        "reactions":["r1", "r2", "r3"]},
                       "example-1.crs":{"food":12,
                                        "reactions":["r1", "r2", "r3", "r'1", "r'2", "r'3"]},
                       "example-10.crs":{"food":2,
                                        "reactions":["r1", "r2", "r3"]},
                       "example-2.crs":{"food":5,
                                        "reactions":["r1", "r2", "r3", "r4", "r5"]},
                       "example-3.crs":{"food":1,
                                        "reactions":["r1", "r2", "r3","r'1", "r'2", "r'3",
                                                     "r#1", "r#2", "r#3", "r#'1", "r#'2", "r#'3",
                                                     "r_theta", "r_x"]},
                       "example-4.crs":{"food":1,
                                        "reactions":["r1", "r2", "r3", "r4", "r5", "r6",
                                                     "r7", "r8", "r9"]},
                       "example-5.crs":{"food":2,
                                        "reactions":["r11", "r12", "r13", "r14",
                                                     "r21", "r22", "r23", "r24",
                                                     "r31", "r32", "r33", "r34",
                                                     "r41", "r42", "r43", "r44"]},
                       "example-6.crs":{"food":1,
                                        "reactions":["r1", "r2", "r3", "r4", "r5", "r6","r7"]},
                       "example-7.crs":{"food":4,
                                        "reactions":["r1", "r2", "r3"]},
                       "example-8.crs":{"food":4,
                                        "reactions":["r01", "r02", "r03", "r04", "r05", "r06",
                                                     "r07", "r08", "r09", "r10",
                                                     "r11", "r12", "r13", "r14", "r15", "r16",
                                                     "r17"]},
                       "example-9.crs":{"food":5,
                                        "reactions":["r1", "r2", "r3", "r4"]},
                       "inhibitions-1.crs":{"food":3,
                                        "reactions":["r1"]}},
            "Max CAF":{"example-0.crs":{"food":0,
                                        "reactions":[]},
                       "example-1.crs":{"food":0,
                                        "reactions":[]},
                       "example-10.crs":{"food":2,
                                        "reactions":["r1", "r2", "r3"]},
                       "example-2.crs":{"food":4,
                                        "reactions":["r3", "r4", "r5"]},
                       "example-3.crs":{"food":0,
                                        "reactions":[]},
                       "example-4.crs":{"food":0,
                                        "reactions":[]},
                       "example-5.crs":{"food":0,
                                        "reactions":[]},
                       "example-6.crs":{"food":0,
                                        "reactions":[]},
                       "example-7.crs":{"food":4,
                                        "reactions":["r1", "r2", "r3"]},
                       "example-8.crs":{"food":4,
                                        "reactions":["r01", "r02", "r03", "r04", "r05", "r06",
                                                     "r07", "r08", "r09", "r10",
                                                     "r11", "r12", "r13", "r14", "r15", "r16",
                                                     "r17"]},
                       "example-9.crs":{"food":0,
                                        "reactions":[]},
                       "inhibitions-1.crs":{"food":3,
                                        "reactions":["r1"]}},
            "Max Pseudo RAF":{"example-0.crs":{"food":3,
                                        "reactions":["r1", "r2", "r3", "r4", "r5", "r6"]},
                       "example-1.crs":{"food":12,
                                        "reactions":["r1", "r2", "r3", "r'1", "r'2", "r'3"]},
                       "example-10.crs":{"food":2,
                                        "reactions":["r1", "r2", "r3"]},
                       "example-2.crs":{"food":5,
                                        "reactions":["r1", "r2", "r3", "r4", "r5"]},
                       "example-3.crs":{"food":1,
                                        "reactions":["r1", "r2", "r3","r'1", "r'2", "r'3",
                                                     "r#1", "r#2", "r#3", "r#'1", "r#'2", "r#'3",
                                                     "r_theta", "r_x"]},
                       "example-4.crs":{"food":1,
                                        "reactions":["r1", "r2", "r3", "r4", "r5", "r6",
                                                     "r7", "r8", "r9"]},
                       "example-5.crs":{"food":2,
                                        "reactions":["r11", "r12", "r13", "r14",
                                                     "r21", "r22", "r23", "r24",
                                                     "r31", "r32", "r33", "r34",
                                                     "r41", "r42", "r43", "r44"]},
                       "example-6.crs":{"food":1,
                                        "reactions":["r1", "r2", "r3", "r4", "r5", "r6","r7"]},
                       "example-7.crs":{"food":4,
                                        "reactions":["r1", "r2", "r3"]},
                       "example-8.crs":{"food":4,
                                        "reactions":["r01", "r02", "r03", "r04", "r05", "r06",
                                                     "r07", "r08", "r09", "r10",
                                                     "r11", "r12", "r13", "r14", "r15", "r16",
                                                     "r17"]},
                       "example-9.crs":{"food":6,
                                        "reactions":["r1", "r2", "r3", "r4", "r5", "r6",
                                                     "r7"]},
                       "inhibitions-1.crs":{"food":3,
                                        "reactions":["r1"]}},
            "iRAF":{"example-0.crs":{"food":3,
                                        "reactions":3},
                       "example-1.crs":{"food":12,
                                        "reactions":3},
                       "example-10.crs":{"food":2,
                                        "reactions":1},
                       "example-2.crs":{"food":5,
                                        "reactions":1},
                       "example-3.crs":{"food":1,
                                        "reactions":8},
                       "example-4.crs":{"food":1,
                                        "reactions":1},
                       "example-5.crs":{"food":2,
                                        "reactions":1},
                       "example-6.crs":{"food":1,
                                        "reactions":1},
                       "example-7.crs":{"food":4,
                                        "reactions":1},
                       "example-8.crs":{"food":4,
                                        "reactions":1},
                       "example-9.crs":{"food":6,
                                        "reactions":4},
                       "inhibitions-1.crs":{"food":3,
                                        "reactions":1},
                       "prokaryotic-network.crs":{"food":3,
                                        "reactions":1}}}

def run_everything():
    #algos.remove("iRAF")
    #algos = ["iRAF"]
    total_test_files = (len(algos) * 2 * (len(OUTPUT_FILE_FORMATS) - 1) * len(ReactionNotation) 
                        * len(ArrowNotation) * len(test_files))
    with tqdm(desc="Total Test Files:", total=total_test_files) as tot_f:
        for algo in algos:
            for zipped in [True, False]:
                for output_format in OUTPUT_FILE_FORMATS:
                    for reaction_notation in ReactionNotation:
                        for arrow_notation in ArrowNotation:
                            if not output_format: continue
                            output_addition = os.path.join(algo, 
                                                        str(zipped), 
                                                        output_format.removeprefix("."), 
                                                        reaction_notation.value,
                                                        arrow_notation.value)
                            
                            output_path = os.path.join(respath, output_addition)
                            
                            cpn.apply_to_directory(algo,
                                                mypath,
                                                output_path,
                                                zipped,
                                                output_format,
                                                reaction_notation,
                                                arrow_notation,
                                                100,
                                                True)
                            
                            tot_f.update(len(test_files))
                            
def test_one_algo(algo:AlgorithmBase):
    total_test_files = (len(ReactionNotation) * len(ArrowNotation) * len(test_files))
    output_format = ".crs"
    time_dict = {}
    with tqdm(desc=algo.NAME + " Test Files:", total=total_test_files) as tot_f:
        for reaction_notation in ReactionNotation:
            for arrow_notation in ArrowNotation:
                if not output_format: continue
                output_addition = os.path.join(algo.NAME,
                                            output_format.removeprefix("."), 
                                            reaction_notation.value,
                                            arrow_notation.value)
                
                output_path = os.path.join(respath, output_addition)
                
                output_systems = cpn.apply_to_directory(algo,
                                    mypath,
                                    output_path,
                                    output_format=output_format,
                                    zipped=False,
                                    reaction_notation=reaction_notation,
                                    arrow_notation=arrow_notation,
                                    overwrite_ok=True,
                                    heuristic_runs=100,
                                    time_dict=time_dict)
                
                tot_f.update(len(test_files))
    output_foods = {}
    output_reactions = {}
    food_truth = {}
    reaction_truth = {}
    filenames = [os.path.split(file)[1] for file in test_files]
    for i, rs in enumerate(output_systems):
        filename = filenames[i]
        output_foods.update({filename:rs.food_size})
        output_reactions.update({filename:[r.name for r in rs.reactions]})
    if algo.NAME in ["Max RAF", "Max CAF", "Max Pseudo RAF"]:
        for file in filenames:
            file_dict = real_res[algo.NAME][file]
            food_truth.update({file:file_dict["food"] == output_foods[file]})
            tqdm.write(file)
            tqdm.write("Food: " + str(file_dict["food"] == output_foods[file]))
            file_dict_reactions = file_dict["reactions"]
            file_dict_reactions.sort()
            output_reactions[file].sort()
            reaction_truth.update({file:file_dict_reactions == output_reactions[file]})
            tqdm.write("Reactions: " + str(file_dict_reactions == output_reactions[file]))
    if algo.NAME in ["iRAF"]:
        for file in filenames:
            file_dict = real_res[algo.NAME][file]
            food_truth.update({file:file_dict["food"] == output_foods[file]})
            tqdm.write(file)
            tqdm.write("Food: " + str(file_dict["food"] == output_foods[file]))
            file_dict_reactions = file_dict["reactions"]
            reaction_truth.update({file:file_dict_reactions == len(output_reactions[file])})
            tqdm.write("Reactions: " + str(file_dict_reactions == len(output_reactions[file])))
    
        tqdm.write("Food: ")
        for key, value in zip(food_truth.keys(), food_truth.values()):
            if not value: tqdm.write(key)
        
        tqdm.write("Reactions: ")
        for key, value in zip(reaction_truth.keys(), reaction_truth.values()):
            if not value: tqdm.write(key)
        
    
    tqdm.write(str(float(sum(time_dict.values())) / float(len(time_dict.values()))))
    return all(food_truth.values()) and all(reaction_truth.values())
    
    
        

if __name__ == "__main__":
    
    reaction_system = cpn.parse_input_file(os.path.join(mypath, "inhibitions-1.crs"))
    gio.print_rs_as_graph(reaction_system)
    #tqdm.write(str(test_one_algo(MinIRAFHeuristic)))
    #run_everything()           
    
    
    
    """ for algo in algos:
        if algo=="iRAF":continue
        algo_respath = respath + "\\" + algo
        for j, file in enumerate(test_files):
            if j == 14: continue
            sys.argv.append("-c")
            sys.argv.append(algo)
            sys.argv.append("-z")
            sys.argv.append("False")
            sys.argv.append("-of")
            sys.argv.append(".crs")
            sys.argv.append("-i")
            sys.argv.append(mypath + "\\"+ file)
            sys.argv.append("-o")
            full_file = algo_respath + "\\" + "result-" + file
            os.makedirs(os.path.dirname(full_file), exist_ok=True)
            sys.argv.append(full_file)
            clt.main()
            for i in range(1, len(sys.argv)):
                del sys.argv[1]
            gc.collect() """
    
    print([[chr(v) for v in range(ord("a"), ord("a") + 26)]])
