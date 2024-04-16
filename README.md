# FAME 3

## Installation
* ```conda env create -f environment.yml```
* ```conda activate fame3```
* ```pip install -e .```

## About

This is the *fame3* program. It attempts to predict sites of metabolism (SOMs)
for the supplied chemical compounds. It is based on extra trees classifier trained 
for prediction of both phase I and phase II SOMs from the MetaQSAR database [1]. It contains 
a combined phase I and phase II (P1+P2) 
model and separate phase I (P1) and phase II (P2) models. For more details 
on the FAME 3 method, see the FAME 3 publication [2].

1. MetaQSAR: An Integrated Database Engine to Manage and Analyze Metabolic Data
   Alessandro Pedretti, Angelica Mazzolari, Giulio Vistoli, and Bernard Testa
   Journal of Medicinal Chemistry 2018 61 (3), 1019-1030
   DOI: 10.1021/acs.jmedchem.7b01473

2. TODO: add reference

## Contact Information

 - Martin Šícho - [martin.sicho@vscht.cz](mailto::martin.sicho@vscht.cz)
    - CZ-OPENSCREEN: National Infrastructure for Chemical Biology, Laboratory of Informatics and Chemistry, Faculty of Chemical Technology, University of Chemistry and Technology Prague, 166 28 Prague 6, Czech Republic
 - Johannes Kirchmair - [kirchmair@zbh.uni-hamburg.de](mailto::kirchmair@zbh.uni-hamburg.de)
    - Universität Hamburg, Faculty of Mathematics, Informatics and Natural Sciences, Department of Computer Science, Center for Bioinformatics, Hamburg, 20146, Germany
   
## Acknowledgement & Funding

We highly appreciate the help of Patrik
Rydberg and his collaborators who made their visualization code from the 
SMARTCyp program freely available as open source software.

This work was funded by the Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) - project number KI 2085/1-1 
and by the Ministry of Education of the Czech Republic - project numbers MSMT No 20-SVV/2017, NPU I - LO1220 and LM2015063.


## Contribute

```
conda env create -f environment.yml
conda activate fame
pip install -e .[dev,test]
ptw
```



