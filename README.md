# malariaibm-movement-BurkinaFaso-2022

[Penn State](https://www.psu.edu/) - [Center for Infectious Disease Dynamics (CIDD)](https://www.huck.psu.edu/institutes-and-centers/center-for-infectious-disease-dynamics) - [Boni Lab](http://mol.ax/)

---

# Overview

This repository contains a frozen snapshot of the code and intermediate data used to prepare the manuscript by Zupko et al. (2023) which appeared in *Scientific Reports*. Due to the size of the intermediate data (27.5 MB) this repository uses [Git Large File Storage](https://git-lfs.github.com/) and may be limited in terms of bandwidth as a result.  All studies run by the simulation use YAML files (in `Studies`) to provide the configuration and ASC files (in `Data/GIS`) for spatial data. 

Due to the complex nature of the simulation, [primary living documentation](https://github.com/rjzupkoii/PSU-CIDD-Malaria-Simulation) to build and run the simulation is hosted with the repository that contains active development. The version 4.1.1.1 code base was used to run the replicates used for the analysis described in the manuscript. 

---

Please cite the manuscript as follows:

Zupko, R. J., Nguyen, T. D., Wesolowski, A., Gerardin, J., & Boni, M. F. (2023). National-scale simulation of human movement in a spatially coupled individual-based model of malaria in Burkina Faso. *Scientific Reports*, 13(1), 321. doi: https://doi.org/10.1038/s41598-022-26878-5

## Binary Files

The compiled version of the simulation used for the studies is provided in the `Binaries` directory, which was  compiled and ran on in the following environment:

```
LSB Version:    :core-4.1-amd64:core-4.1-noarch:cxx-4.1-amd64:cxx-4.1-noarch:desktop-4.1-amd64:desktop-4.1-noarch:languages-4.1-amd64:languages-4.1-noarch:printing-4.1-amd64:printing-4.1-noarch
Distributor ID: RedHatEnterpriseServer
Description:    Red Hat Enterprise Linux Server release 7.9 (Maipo)
Release:        7.9
Codename:       Maipo
```

---

### Original Repositories
- Malaria Simulation, version 4.1.1.1: https://github.com/rjzupkoii/PSU-CIDD-Malaria-Simulation
- Burkina Faso analysis and plots: https://github.com/rjzupkoii/PSU-CIDD-Burkina-Faso
- Support scripts and infrastructure: https://github.com/bonilab/PSU-CIDD-MaSim-Support
