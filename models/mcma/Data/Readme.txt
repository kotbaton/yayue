This dir (./Data/) provides space for analyses of diverse model instances
by diverse users. Some analyses might require substantial space (especially,
if many iterations are made). Therefore, the analyses should be done locally
(and also locally backup'ed, if desired), i.e., the analyses' results should not
be committed to the common repo.
In order to facilitate this, each user should create a sub-dir of ./Data/
named after his/her name. Then add the dir name to the ./Data/.gitignore file.
Also your version of the ana_dir.yml should not be committed. Therefore, the
content of the .gitignore file should include:
ana_dir*
marek/
(where marek should be replaced by your name).
One can create diverse versions of the ana_dir.yml files and move them around
as desired to switch between diverse analyses.
Finally, note that the above preparations needs to be done only once on each
computer running the MCMA app.

Each analysis is done in a dedicated directory on a local computer.
During the analysis diverse files are created/updated in the corresponding
analysis dir and its sub-dirs. The dirs/sub-dirs (except of the analysis dir
that must be created for each analysis), as well as the needed files are created
by the mcma-app (according to the content of ./Data/usr_name/ana_dir/cfg_usr.yml
file). Information that enables continuation of analysis from the last
analysis stage is stored there. This includes the requested results of also the
core model values for each iteration of the analysis; the latter can be used for
model-instance analysis in the core-model outcome space.

The MCMA app has been modified to enable specification of each analysis (and
the corresponding options for each analysis run of the selected model instance)
without (the originally required) modification of the code. To achieve this,
the specification of each analysis is now done through the two YAML files:
- ./Data/ana_dir.yml defining the location of the dir dedicated to the analysis, and
- ./Data/your_name/yyy/cfg_usr.yml defining options for the current analysis run.

Here is the summary of the step-by-step preparation of the MCMA analysis:
1. Prepare the core model in the dill format and store it in the ./Models dir.
   This dir contains several already prepared models; therefore you can also
   explore analysis of the provided models. New models should have names
   composed of unique (within the ./Models dir) root-name and dll extension,
   e.g., jg2.dll. Models committed in the ./Models/ dir are assumed to be ready
   for the MCMA analysis. Therefore, please test each model before committing
   it to the ./Models dir.
2. For each MCMA analysis create a subdirectory of the ./Data/usr_name/ dir.
   This sub-dir is referred to as the ana_dir (from: analysis directory).
3. In order to use this dir for the current analysis prepare the ./Data/ana_dir.yml
   file by copying the ./Data/dirTempl.yml template file to ./Data/ana_dir.yml file
   and modify the latter files following the info included in the template file.
   You can make further modifications to switch between diverse analyses.
4. The second needed yaml file is dedicated to each analysis.
   The easiest way to create this file is to copy the config template file
   ./Data/cfgTempl.yml to ./Data/usr_name/ana_dir/cfg_usr.yml, and modify it
   following the info included in the template file.
   For initializing the analysis one needs to define only two options, namely:
   - model_id: replace the jg1 by the root name of the core model you want to
     analyse, e.g., jg2
   - crit_def: define the criteria (see below).
   Modifications of other options in ana_dir/cfg_usr.yml is optional; it is
   typically done for subsequent analysis runs.

The criteria are now defined by the value of the crit_def key (instead of the
previously required dedicated text-file). The value of this key is
composed of the list of lists (see the example in ana_dir/cfg_usr.yml copied
from the template).  Each sub-list is composed of three items.
Each name of these items should be max. 8 characters long without spaces; only
the following characters are allowed: letters, _, numbers.
The meaning of the three items:
- name of the criterion,
- criterion type: one of the following predefined ids: min, max,
- name of the core model outcome variable defining the corresponding criterion.

