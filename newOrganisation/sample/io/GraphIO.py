from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import networkx as nx
from tqdm import tqdm
from enum import StrEnum

from sample.model.MoleculeType import MoleculeType
from sample.model.Reaction import Reaction
from sample.model.ReactionSystem import ReactionSystem

class edge_types(StrEnum):
    
    REACTANT = "reactant"
    PRODUCT  = "product"
    INHIBITOR = "inhibitor"
    CATALYST = "catalyst"
    CATALYST_CONJUNCTION = "catalyst_conjuntion"
    
class node_types(StrEnum):
    
    REACTION = "reaction"
    MOLECULE = "molecule"
    CATALYST_CONJUNCTION = "catalyst_conjunction"


SUPPORTED_GRAPH_FILE_FORMATS = [".gml"]

def write(reaction_system:ReactionSystem|list, filename:str) -> None:
    
    if isinstance(reaction_system, list):
        if len(reaction_system) > 1:
            output = os.path.split(os.path.abspath(filename))
            output_directory = os.path.join(output[0],output[1].split(".")[0])
            output_file = output[1]
            os.path.join(output_directory, output_file)
            os.makedirs(os.path.dirname(output_directory), exist_ok=True)
    
    for i, rs in enumerate(reaction_system):        
        graph = parse_to_graph(rs)
        if len(reaction_system) > 1:
            output_file = ".".join([output_file.split(".")[0] + str(i), output_file.split(".")[1]])
            filename = os.path.join(output_directory, output_file)
        if ".gml" in filename:
            nx.write_gml(graph, filename)
        #elif ".graphml" in filename:
        #    nx.write_graphml_xml(graph, filename)
        else:
            tqdm.write("File format not recognized." +
                    " Assumed .gml.")
            nx.write_gml(graph, filename)
            
        
def parse_to_graph(reaction_system:ReactionSystem)-> nx.DiGraph:
    
    graph = nx.DiGraph(name=reaction_system.name)
    molecule_nodes = reaction_system.get_mentioned_molecules()
    molecule_nodes = [(node.name, 
                        {"graphics":{"NodeShape":"ELLIPSE",
                                    "fill":"#000000"},
                        "att":{"node_type":node_types.MOLECULE,
                                "Food":False}}) 
                        for node in molecule_nodes]
    graph.add_nodes_from(molecule_nodes)
    for food in reaction_system.foods:
        graph.nodes[food.name]["att"]["Food"] = True
    reaction_nodes = [(reaction.name, 
                        {"graphics":{"NodeShape":"TRIANGLE",
                                    "fill":"#FFFFFF"},
                        "att":{"node_type":node_types.REACTION}}) 
                        for reaction in reaction_system.reactions]
    graph.add_nodes_from(reaction_nodes)
    
    for reaction in reaction_system.reactions:
        for i,reactant in enumerate(reaction.reactants):
            if reaction.reactant_coefficients:
                coefficient = reaction.reactant_coefficients[i]
            else:
                coefficient = None
            match reaction.direction:
                case "forward":
                    parse_edge(graph,reactant.name, reaction.name,
                                edge_types.REACTANT, coefficient)
                case "reverse":
                    parse_edge(graph, reaction.name, reactant.name,
                                edge_types.PRODUCT, coefficient)
                case "both":
                    parse_edge(graph,reactant.name, reaction.name,
                                edge_types.REACTANT, coefficient)
                    parse_edge(graph, reaction.name, reactant.name,
                                edge_types.PRODUCT, coefficient)
        for i,product in enumerate(reaction.products):
            if reaction.product_coefficients:
                coefficient = reaction.product_coefficients[i]
            else:
                coefficient = None
            match reaction.direction:
                case "reverse":
                    parse_edge(graph,product.name, reaction.name,
                                edge_types.REACTANT, coefficient)
                case "forward":
                    parse_edge(graph, reaction.name, product.name,
                                edge_types.PRODUCT, coefficient)
                case "both":
                    parse_edge(graph,product.name, reaction.name,
                                edge_types.REACTANT, coefficient)
                    parse_edge(graph, reaction.name, product.name,
                                edge_types.PRODUCT, coefficient)
        for inhibitor in reaction.inhibitions:
            parse_edge(graph, inhibitor.name, reaction.name,
                        edge_types.INHIBITOR)
        for catalyst in [cata.name for cata in reaction.get_catalyst_conjunctions()]:
            if "&" in catalyst:
                catalyst_node = [(catalyst,{"graphics":{"NodeShape":"OCTAGON",
                                                      "fill":"#000000"},
                                          "att":{"node_type":
                                              node_types.CATALYST_CONJUNCTION}})]
                graph.add_nodes_from(catalyst_node)
                parse_edge(graph, catalyst, reaction.name, edge_types.CATALYST)
                catalyst_elements = catalyst.split("&")
                for catalyst_element in catalyst_elements:
                    parse_edge(graph, catalyst_element, catalyst, edge_types.CATALYST_CONJUNCTION)
            else:
                parse_edge(graph, catalyst, reaction.name, edge_types.CATALYST)
    
    return graph    

def parse_edge(graph:nx.DiGraph, u:str, v:str, edge_type:edge_types, coefficient:str|None = None) -> None:
    if edge_type == edge_types.INHIBITOR:
        color = "#FF0000"
        arrow = "T"
    elif edge_type in [edge_types.CATALYST, edge_types.CATALYST_CONJUNCTION]:
        color = "#00FF00"
        arrow = "Arrow"
    elif edge_type in [edge_types.REACTANT, edge_types.PRODUCT]:
        color = "#000000"
        arrow = "Arrow"
    else:
        tqdm.write("Edge type: " + edge_type + " isn't recognized." +
                   "REACTANT properties are used.")
        color = "#000000"
        arrow = "Arrow"
        
    graph.add_edge(u, v, graphics={"fill":color,
                                   "ArrowShape":arrow},
                    att={"edge_type":edge_type})
    if coefficient:
        try:
            graph[u][v]["weight"]=float(coefficient)
        except ValueError:
            graph[u][v]["weight"]=coefficient