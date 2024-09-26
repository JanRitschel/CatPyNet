if __name__ == "__main__":
    """ import catPyNet.main.CatPyNet as cpn

    cpn.apply_algorithm_to_file(algorithm="max raf", 
                                input_file="drive:\\absolute\\path\\to\\input.crs",
                                output_path="drive:\\absolute\\path\\to\\output.crs")

    import catPyNet.main.CatPyNet as cpn
    import catPyNet.Utilities as ut
    from catPyNet.model.ReactionSystem import ReactionSystem

    input_rs = cpn.parse_input_file_to_rs(file_name="drive:\\absolute\\path\\to\\input.crs")
    closure_molecules = ut.compute_closure(input_rs.foods, input_rs.reactions)
    closure_reactions = ut.filter_reactions(closure_molecules, input_rs.reactions)
    output_rs = ReactionSystem("output_rs",
                            foods=closure_molecules,
                            reactions=closure_reactions)
    cpn.export_rs_to_output_file(output_systems=[output_rs],
                                output_path="drive:\\absolute\\path\\to\\output.crs")
    """
    import catPyNet.main.CatPyNet as cpn
    import catPyNet.Utilities as ut
    from catPyNet.algorithm.MaxRAFAlgorithm import MaxRAFAlgorithm
    from catPyNet.algorithm.MaxPseudoRAFAlgorithm import MaxPseudoRAFAlgorithm
    from catPyNet.algorithm.AlgorithmBase import AlgorithmBase
    from tqdm import tqdm
    import sys
    import os
    sys.path.insert(0, os.path.abspath(
        os.path.join(os.path.dirname(__file__), '.')))
    
    algorithms = AlgorithmBase.list_all_algorithms()
    tqdm.write(str(algorithms))
    input_rs = cpn.parse_input_file_to_rs(file_name="G:\\Github\\BA-Jan\\test_results\\test_reactions.crs")
    for algorithm in algorithms:
        tqdm.write(algorithm)
        algo = AlgorithmBase.get_algorithm_by_name(algorithm)()    
        max_raf = cpn.apply_algorithm_to_rs(input_rs, algo)
        products = ut.add_all_mentioned_products(max_raf.foods, max_raf.reactions)
        products.difference_update(max_raf.foods)
        #for product in products:
        tqdm.write(algorithm + str((len(products))))
        tqdm.write(algorithm + str((len(max_raf.reactions))))