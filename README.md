# Principal Component Analysis as a Sanity Check for Bayesian Phylolinguistic Reconstruction

## About
Yugo Murawaki. 2024. Principal Component Analysis as a Sanity Check for Bayesian Phylolinguistic Reconstruction. In Proceedings of the 2024 Joint International Conference on Computational Linguistics, Language Resources and Evaluation (LREC-COLING 2024). (to appear).

## Requirements
- Python 3
- poetry
- [BEAST](https://www.beast2.org/)
  - BEAST Classic package
- [FigTree](http://tree.bio.ed.ac.uk/software/figtree/)

## Run the analysis

- Obtain a BEAST XML configuration file
  - Often published as part of supplementary materials of a paper
- Modify the XML file to sample ancestral node states
  
A line like
```xml
<log id="TreeWithMetaDataLogger.t:synthdata2" spec="beast.base.evolution.TreeWithMetaDataLogger" tree="@Tree.t:synthdata2"/>
```
should be rewritten as:
```xml
<log id="TreeWithTraitLogger.t:synthdata2" spec="beastclassic.evolution.likelihood.AncestralSequenceLogger" tree="@Tree.t:synthdata2" tag="ancestral-syndata2" data="@synthdata2" siteModel="@SiteModel.s:synthdata2"/
```
- Run BEAST and obtain a `trees` file (e.g., `synthdata-synthdata2.trees`)
- Run FigTree
  - Open the `trees` file
  - Click `Export Trees`
  - Check `Save all trees`
  - Check `Include Annotations (NEXUS & JSON only)`
  - Save as a NEX file (e.g., `synthdata-synthdata2.nex`)

- Convert the NEX file into a Python pickle
```sh
python scripts/parse_tree.py synthdata-synthdata2.nex synthdata-synthdata2.pkl
```

- Draw a PCA tree
```sh
python scripts/pca_tree.py synthdata-synthdata2.pkl 100 ancestral-syndata2 synthdata-synthdata2.100.png           
```
