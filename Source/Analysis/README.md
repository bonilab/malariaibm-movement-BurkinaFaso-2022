## Movement Analysis
The files contained within this directory were used for analyzing, calibrating, and verifying model movement. The subdirectory `Shared` contains data files and Matlab scripts that are used by the Matlab scripts that are present in this directory. Note that some data files from `../Common` are also referenced. 

`marshall_survey_condensed.csv` is the result of work to parse Marshall et al. (2016) EMS2 into a file that contains just the Burkina Faso survey results.

`model-rho-sweep.csv` is the summary of model runs that swept through the log(rho) values and tracked the total trips to the destination district from the source district.

The general workflow for this process is as follows:

1. `parse_marshall.py` was run to generate a mapping between the district ids assigned by the model to the districts used in Marshall et al. (2017)
2. `synthetic_study.m` was run to generate the data points for analysis.
3. `rho_comparison.m` was run to generate the IQR comparison plot.
4. `rho_distance.m` was run to generate synthetic vs. survey data distance plots.
