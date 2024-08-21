# Principal Component Analysis as a Sanity Check for Bayesian Phylolinguistic Reconstruction

## About
Yugo Murawaki. 2024. [Principal Component Analysis as a Sanity Check for Bayesian Phylolinguistic Reconstruction](https://aclanthology.org/2024.lrec-main.1138/). In Proceedings of the 2024 Joint International Conference on Computational Linguistics, Language Resources and Evaluation (LREC-COLING 2024). ([arXiv](https://arxiv.org/abs/2402.18877)).

This is a refined version of old Python2 code available at https://github.com/murawaki/lexwave

## Requirements
- Python 3
- poetry
- [BEAST](https://www.beast2.org/)
  - BEAST Classic package
- [FigTree](http://tree.bio.ed.ac.uk/software/figtree/)

## Run basic analysis

- Obtain a BEAST XML configuration file
  - Often published as part of supplementary materials of a paper
- Edit the XML file to sample ancestral node states
  
A line like
  ```xml
  <log id="TreeWithMetaDataLogger.t:synthdata2" spec="beast.base.evolution.TreeWithMetaDataLogger" tree="@Tree.t:synthdata2"/>
  ```
should be rewritten as:
  ```xml
  <log id="TreeWithTraitLogger.t:synthdata2" spec="beastclassic.evolution.likelihood.AncestralSequenceLogger" tree="@Tree.t:synthdata2" tag="ancestral-syndata2" data="@synthdata2" siteModel="@SiteModel.s:synthdata2"/
  ```
- Run BEAST and obtain a `trees` file (e.g., `synthdata-synthdata2.trees`)
- Run FigTree to convert the `trees` file into a NEX file (we can skip this step, but we typically want to manually review the outcome before moving forward...)
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
  python scripts/pca_tree.py synthdata-synthdata2.pkl ancestral-syndata2 synthdata-synthdata2.last.png
  ```
  - The second argument specifies the tag given to `AncestralSequenceLogger`
  - The optional argument `--index=n` specifies the `n`-th tree in the pickle file
  - The optional argument `--dtype` must be specified if the substitution model is `BinaryCovarion` or `PDCovarion` because latent values must be mapped to binary values
  - You might want to edit the script as some plotting options are hard-coded

## Advanced techniques
`scripts/pca_kde.py` is similar to `scripts/pca_tree.py` but add kernel density estimation of a given clade
- The clade is specified by the leaf nodes sorted alphabetically and joined with colons (e.g., GaroGaro:JingphoJingpho:Rabha)

Several recent studies (e.g., linguistic analysis of Robbeets et al. (2021)) define multiple site models to account for varying rates associated with basic vocabulary items. In such instances, a straightforward solution is to define a logger for each site model. Consequently, multiple copies of the same tree are generated, each providing distinct information about the node states. A postprocessing step is necessary to merge them into a single tree with complete node states.
- `tea254pdcov-ucln-fbd-constrained.xml` of Robbeets et al. (2021), for example, defines a different distribution for each basic vocabulary item. Consequently, we need to define a logger to each vocabulary item (the file saved as `tea254pdcov-ucln-fbd-constrained-modified.xml`):
  ```xml
       <logger id="treelog.t:fire" spec="Logger" fileName="$(filebase).fire.trees" logEvery="50000" mode="tree">
           <log id="TreeWithMetaDataLogger.t:tree:fire" spec="beastclassic.evolution.likelihood.AncestralSequenceLogger" branchRateModel="@RelaxedClock.c:clock" tree="@Tree.t:tree" tag="ancestraldata" data="@orgdata.fire" siteModel="@SiteModel.s:fire" />
       </logger>
       <logger id="treelog.t:nose" spec="Logger" fileName="$(filebase).nose.trees" logEvery="50000" mode="tree">
           <log id="TreeWithMetaDataLogger.t:tree:nose" spec="beastclassic.evolution.likelihood.AncestralSequenceLogger" branchRateModel="@RelaxedClock.c:clock" tree="@Tree.t:tree" tag="ancestraldata" data="@orgdata.nose" siteModel="@SiteModel.s:nose" />
       </logger>
  ...
  ```
- Save the list to a file (e.g., `items`)
- Run BEST and obtain numerous `trees` files
- Combine these `tree` files into one pickle file
  ```sh
  python scripts/combine.py tea254pdcov-ucln-fbd-constrained-modified.{}.trees items ancestraldata tea254pdcov-ucln-fbd-constrained-modified.last.pkl
  ```
  - The first argument specifies the file path template instantiated by the second argument
