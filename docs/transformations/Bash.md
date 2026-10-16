# Bash Transformations

The Bash transformation is implemented by the [**bash-plugin**](https://github.com/UST-DeMAF/bash-plugin).
Bash scripts typically orchestrate the execution of deployment models of other deployment technologies, e.g., by calling `terraform apply` or `kubectl apply`.
Therefore, the plugin does not create EDMM constructs itself, but detects the embedded deployment models invoked by a script and requests their analysis by the corresponding plugins.
The analysis does not use a JetBrains MPS project.

## Transformation Process

A Bash script consists of commands, one per line.
A command invokes an embedded deployment model if it calls the CLI of a supported deployment technology.

The parser reads the files with the extension `.sh` at the given locations; for a directory, the files directly contained in it are read.

Each line is analyzed separately:

- Blank lines and lines starting with `#` are skipped and not annotated.
- The first word of the line is considered the called command.

The following commands are supported:

| Command | Technology of the embedded deployment model | Location of the embedded deployment model |
| --- | --- | --- |
| `terraform` | Terraform | For `init` and `apply`: the directory of the script joined with the directory given by `-chdir=<dir>`, otherwise the directory of the script |
| `kubectl` | Kubernetes | For `apply` and `create`: the directory of the script joined with the path given by `-f <path>`, otherwise the directory of the script |
| `helm` | Helm | The directory of the script; only `helm install` commands create an embedded deployment model |

If an embedded deployment model with the same location already exists, the command is added to its commands instead of creating a new one.
For Helm, all previous `helm repo ...` commands of the script are passed on together with the `helm install` command, so that the Helm plugin can add the required chart repositories.

## Embedded Deployment Models

The DeMAF currently supports the following embeddings of Bash deployment models, which are described in detail in the [overview of embedded deployment models](README.md#embedded-deployment-models):

- [Bash → Helm](README.md#bash--helm) (reference embedding)
- [Bash → Kubernetes](README.md#bash--kubernetes) (reference embedding)
- [Bash → Terraform](README.md#bash--terraform) (reference embedding)
