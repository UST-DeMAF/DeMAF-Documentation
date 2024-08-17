# Feature Branching Model:

1. There are **two** permanent branches per repository *`main`* and *`dev`*.

2. The default working branch is *`dev`*.

3. A new feature branch **must** be forked from the current *`dev`* branch for the development of a new feature.

4. The name of the feature branch **must** be based on the respective ticket name (i.e. ES-XX).

5. Once work on a feature branch has been completed, a pull request **must** be placed onto the *`dev`* branch.

6. Pull requests **must** be checked by at least one developer and pass the pipeline.

7. Occasionally, if a small hotfix is required, one may also push directly to the *`dev`* branch.

