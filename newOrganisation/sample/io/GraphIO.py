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

class GraphIO:
    def write(reaction_system:ReactionSystem, filename:str) -> None:
        pass
        
        
    def parse_to_graph(reaction_system:ReactionSystem)-> nx.MultiDiGraph:
        
        #ZU MACHEN, ordentliche keywords suchen
        graph = nx.MultiDiGraph(name=reaction_system.name)
        molecule_nodes = reaction_system.get_mentioned_molecules()
        molecule_nodes = [(node, 
                           {"graphics":{"type":"rectangle",
                                        "fill":"#000000"},
                            "att":{"Reaction":False}}) 
                          for node in molecule_nodes]
        graph.add_nodes_from(molecule_nodes)
        reaction_nodes = [(reaction.name, 
                           {"graphics":{"type":"triangle",
                                        "fill":"#FFFFFF"},
                            "att":{"Reaction":True}}) 
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
            for catalyst in reaction.get_catalyst_conjunctions():
                pass
def parse_edge(graph:nx.DiGraph, u:str, v:str, edge_type:edge_types, coefficient:str|None = None) -> None:
    if edge_type in [edge_types.INHIBITOR, edge_types.CATALYST]:
        color = "#D3D3D3"
    graph.add_edge(u, v, graphics={"fill":"#000000"},
                    att={"edge_type":edge_type})
    if coefficient:
        (graph[u, v].update({"weight",float(coefficient)}))