# CatPyNet - A Python Package for analyzing autocatalytic networks

## Description
Autocatalytic networks are a part of all biological systems.
From the most basic cells to entire ecosystems they appear at every level.
Their analysis has recently shed new light on the beginnings of life and the functioning of the earliest organisms\cite{xavier2020autocatalytic, xavier2022small}, as well as niche emergence in ecosystems \cite{gatti2017biodiversity} and many other biology-unrelated fields. \cite{cultural_evolution}, \cite{therapy}
As such providing accessible tools for further studies and data evaluation is paramount to the expansion of this field of analysis.\\
This work introduces a python package, called CatPyNet, for autocatalytic reaction system evaluation and computations on those systems.
The package is heavily based on the java program CatReNet \cite{huson2024catrenet},\cite{steel2020structure} and provides much of the same functionality.
This includes calculation of different types of reflexively autocatalytic food-generated (RAFs) and constructively autocatalytic food-generated (CAFs) sets, polymer system generation for test data generation and basic visualization of the generated systems.
For this purpose the package includes a command line tool for algorithm application and a command line tool for polymer system generation, as well as a central module collecting most functions relevant to these purposes.
As such the package can be used from a command line or imported into other python scripts.
This package produces identical results to CatReNet with the same inputs, which, for most functions, allows the programs to be used in tandem or interchangeably.
The easy import and expandability, as well as the popularity of python as a programming language, are the main reasons for using this package.\\