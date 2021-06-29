# GDC VEP Annotation Workflow
![Version badge](https://img.shields.io/badge/VEP-v84-<COLOR>.svg)
![Version badge](https://img.shields.io/badge/VEP-v102-<COLOR>.svg)

This workflow takes a VCF file and adds [Variant Effect Predictor](http://useast.ensembl.org/info/docs/tools/vep/index.html)
annotations using particular settings for the GDC harmonization process.

## Notes

* Tested on [cwltool](https://github.com/common-workflow-language/cwltool) version `1.0.20180306163216`
* See [GDC Reference Files](https://gdc.cancer.gov/about-data/data-harmonization-and-generation/gdc-reference-files)
* Plugins and Dockerfile available at https://github.com/NCI-GDC/vep-tool
* Currently, we are using VEP v84 with our customized cache file (see [VEP-SETUP.md](VEP-SETUP.md) for more information) or v102.
