# Helm Transformations

The Helm transformation is implemented by the [**helm-plugin**](https://github.com/UST-DeMAF/helm-plugin).
Helm provides reusable and templated Kubernetes deployment models called Helm charts.
Every Helm chart contains an embedded Kubernetes deployment model.
Therefore, the plugin does not create EDMM constructs itself, but renders the Kubernetes deployment model of a Helm chart and requests its analysis by the Kubernetes plugin.
The analysis does not use a JetBrains MPS project.

## Transformation Process

A Helm deployment model is given by Helm CLI commands, which are passed on by the plugin of the embedding deployment technology (see [Embedded Deployment Models](#embedded-deployment-models)).
The plugin processes the commands of the Helm deployment model in their order:

| Command | Processing |
| --- | --- |
| `helm repo add <name> <url>` | The command is executed, so that the chart repository is available for rendering. |
| `helm install <release> <chart> [options]` | The command is rewritten to `helm template <release> <chart> [options]` and executed. The rendered Kubernetes manifests are saved as `<release>.yaml` in the output directory of the plugin (`kube.output.directory`). |
| any other command | ignored |

All options of the `helm install` command, such as `--set`, `-f`, or `--version`, are passed on to `helm template`, so that the templated values are resolved from the given configuration.

> [!NOTE]
> The commands are executed in the working directory of the plugin, not in the directory of the embedding deployment model.
> Thus, local charts and value files referenced by relative paths are not found.
> The release name is read from the third word of the command, so options placed before the release name are not supported.

## Embedded Deployment Models

The DeMAF currently supports the following embeddings of Helm deployment models, which are described in detail in the [overview of embedded deployment models](../README.md#embedded-deployment-models):

- [Bash → Helm](../README.md#bash--helm) (reference embedding)
- [Helm → Kubernetes](../README.md#helm--kubernetes) (containment embedding)
- [Terraform → Helm](../README.md#terraform--helm) (reference embedding)
