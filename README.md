# GAMA web: Galician Metrical Analyzer

This Django app is the web version of GAMA, the Galician Metrical Analyzer. It provides a metrical analysis of poetry in Galician.

The scansion algorithm is [Jumper](https://github.com/grmarco/jumper/blob/master/jumper.py) ([Marco Remón & Gonzalo, 2021](http://journal.sepln.org/sepln/ojs/ojs/index.php/pln/article/view/6324)). This is included in module `gumper/gumper.py` (Gumper = Galician Jumper). Jumper was created for Spanish, but we adapted its data to work with Galician.

We also added a preprocessing to handle non-normative orthography in Galician. Most processing time is due to this preprocessing; scansion with Jumper is very fast.

More details in the app's *About* page: in [English](https://prf2.org/en/gama/about/), [Galician](https://prf2.org/en/gama/about/) and [French](https://prf2.org/fr/gama/about/) so far.

## Citation

Moreau, Pauline & Ruiz Fabo, Pablo. (2025). GAMA web: Interface for the metrical analysis of Galician poetry. CiTIUS - Universidade de Santiago de Compostela.