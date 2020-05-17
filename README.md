# CM-graph
[![Documentation Status](https://readthedocs.org/projects/cm-graph/badge/?version=latest)](https://cm-graph.readthedocs.io/en/latest/?badge=latest)

The Python Toolbox for multichannel EEG-EMG connectivity analysis. This package is an extention of mne-tool with the focus on the application of the newest graph and network theory.  It is first developped to investigate stroke and autism spectral disorder(ASD) via EEG-EMG coherence marker 

# Workflow:
The current contribution workflow is being developped. A detailed tutorial will be released in [readthedocs](https://cm-graph.readthedocs.io/en/latest/) in a few days.

## Contribution:
You are welcomed to use modules of CM-graph and make your own contribution. There are few steps to begin with:
- fork the project at your own (remote) repository
- clone your (remote) repository at your computer (local repository).
- create a branch named 'dev_feature' and start to playing with the codes
- commit and push your changes to your own (remote) repository:
- to show your contribution, please create a pull request from your dev branch to CM-graph\master
- you can always syncronize your forked repository and cm-graph:
```git
git add upstream https://github.com/CM-connectivity/CM-graph.git
fetch upstream
git checkout master (or your dev branch)
git merge upstream\master
```