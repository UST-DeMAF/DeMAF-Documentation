# Kubernetes Transformations

The Kubernetes transformation is implemented by two repositories:

- [**kubernetes-mps-plugin**](https://github.com/UST-DeMAF/kubernetes-mps-plugin): The DeMAF plugin service that parses the Kubernetes deployment model (*Step 1: Deployment Model Parser*), runs the MPS transformation, and requests the analysis of embedded deployment models.
- [**mps-transformation-kubernetes**](https://github.com/UST-DeMAF/mps-transformation-kubernetes): The JetBrains MPS project that defines the Kubernetes metamodel (language `Kubernetes`) and the generators that implement the *Main M2M Transformation* (Step 2), the *Model Merger* (Step 3), and the *Post M2M Transformation* (Step 4).

## Kubernetes Metamodel

The following diagram shows the Kubernetes metamodel as supported by the DeMAF:

```mermaid
classDiagram
    direction TB
    class KubernetesDeploymentModel

    class Deployment {
        +String name
        +int replicas
        +int minReadySeconds
        +int revisionHistoryLimit
        +int progressDeadlineSeconds
        +boolean paused
        +String deploymentStrategy
        +int rollingUpdateDeploymentMaxSurge
    }
    class StatefulSet {
        +String serviceName
    }
    class CronJob {
        +String name
        +String schedule
        +String timezone
        +String concurrentPolicy
        +int startingDeadlineSeconds
    }
    class Job {
        +String name
        +int parallelism
    }
    class PodSpec {
        +String hostname
        +String restartPolicy
    }
    class Container {
        +String name
        +String image
        +String imagePullPolicy
        +String workingDir
        +List~String~ command
        +List~String~ args
    }
    class ContainerPort {
        +String name
        +int port
        +String hostIP
        +int hostPort
        +String protocol
    }
    class EnvironmentVariable {
        +String key
        +String value
    }
    class VolumeMount {
        +String name
        +String mountPath
        +String mountPropagation
        +boolean readOnly
        +String subPath
        +String subPathExpr
    }
    class Volume {
        +String name
        +String persistentVolumeClaimName
        +boolean persistentVolumeClaimReadOnly
    }
    class PersistentVolumeClaim {
        +String name
        +String volumeName
        +String requests
        +String limit
    }
    class Service {
        +String name
        +String type
        +String clusterIP
        +String ipFamilyPolicy
        +String sessionAffinity
        +String loadBalancerIP
        +String externalName
        +String externalTrafficPolicy
        +String internalTrafficPolicy
        +int healthCheckNodePort
        +List~String~ ipFamilies
        +List~String~ clusterIPs
        +List~String~ externalIPs
        +List~String~ loadBalancerSourceRanges
    }
    class ServicePort {
        +String name
        +int port
        +String targetPort
        +String protocol
        +int nodePort
        +String appProtocol
    }
    class Selector {
        +String key
        +String value
    }
    class Ingress {
        +String ingressClassName
    }
    class IngressRule {
        +String host
    }
    class HTTPIngressRuleValue {
        +String path
        +String pathType
    }
    class IngressBackend {
        +String serviceName
        +String servicePortName
        +int servicePortPort
    }
    class ConfigMap {
        +String name
        +boolean immutable
    }
    class ObjectMeta {
        +String name
        +String generateName
        +String namespace
    }
    class Label {
        +String key
        +String value
    }

    KubernetesDeploymentModel "1" *-- "0..*" Deployment : deployments
    KubernetesDeploymentModel "1" *-- "0..*" PodSpec : pods
    KubernetesDeploymentModel "1" *-- "0..*" Service : services
    KubernetesDeploymentModel "1" *-- "0..*" PersistentVolumeClaim : persistentVolumeClaims
    KubernetesDeploymentModel "1" *-- "0..*" CronJob : cronJobs
    KubernetesDeploymentModel "1" *-- "0..*" Ingress : ingresses
    KubernetesDeploymentModel "1" *-- "0..*" ConfigMap : configMaps

    StatefulSet --|> Deployment
    Deployment "1" *-- "1..*" PodSpec : pods
    Deployment "1" *-- "1..*" Label : labels
    Deployment "1" *-- "0..*" Label : selectorMatchLabels
    CronJob "1" *-- "1" Job : job
    CronJob "1" *-- "0..*" Label : labels
    Job "1" *-- "1..*" PodSpec : pods

    PodSpec "1" *-- "1..*" Container : containers
    PodSpec "1" *-- "0..*" Container : initContainers
    PodSpec "1" *-- "0..*" Volume : volumes
    PodSpec "1" *-- "0..*" Label : labels
    Container "1" *-- "1..*" ContainerPort : containerPorts
    Container "1" *-- "0..*" EnvironmentVariable : environmentVariables
    Container "1" *-- "0..*" VolumeMount : volumeMounts

    Service "1" *-- "1..*" ServicePort : servicePorts
    Service "1" *-- "1..*" Selector : selectors

    Ingress "1" *-- "0..*" IngressRule : rules
    IngressRule "1" *-- "1..*" HTTPIngressRuleValue : httpPaths
    HTTPIngressRuleValue "1" *-- "1" IngressBackend : backend

    ConfigMap "1" *-- "0..1" ObjectMeta : metadata
    ConfigMap "1" *-- "0..*" Label : data
    ObjectMeta "1" *-- "0..*" Label : labels
    ObjectMeta "1" *-- "0..*" Label : annotations
```

The metamodel corresponds to the `Kubernetes` language of the MPS project (`Label` is named `StringStringMap` there).
The associations `ingresses` and `configMaps` exist only in the plugin's internal model, which stores parsed Ingress and ConfigMap objects.
The `KubernetesDeploymentModel` of the MPS language does not contain them, so these objects are not passed to the transformation.
The MPS language contains additional concepts that are not yet used by the transformation (e.g., `SecurityContext`, `EphemeralContainer`, and `ContainerRestartPolicy`) and are therefore omitted.

## Transformation Process

The transformation follows the four steps of the DeMAF transformation process: the deployment model parser, the main model-to-model (M2M) transformation, the model merger, and the post M2M transformation.

### Step 1: Deployment Model Parser

The parser reads the `.yaml` and `.yml` files at the given locations; for a directory, the files directly contained in it are read (subdirectories are not searched).
A file can contain several documents separated by `---`.
Each document is read from its top-level `kind` line up to the next `---`, so fields placed above `kind` (e.g., `metadata`) are ignored.
The document is parsed based on its Kubernetes `kind`:

| `kind` | Parsed into |
| --- | --- |
| `Deployment`, `StatefulSet`, `ReplicaSet` | `Deployment` with its `PodSpec`. The `volumeClaimTemplates` of a StatefulSet are parsed into `PersistentVolumeClaim`s and corresponding `Volume`s (see [Persistent Storage](#persistent-storage)). |
| `Service` | `Service` |
| `PersistentVolumeClaim` | `PersistentVolumeClaim` |
| `ConfigMap` | `ConfigMap` (not transformed) |
| `Ingress` | `Ingress` (not transformed) |
| any other kind | not parsed |

While parsing, references to other environment variables of the same container (`$(VAR_NAME)`) are replaced by the referenced value.
`CronJob`/`Job` and standalone `Pod` objects are part of the metamodel and have transformation rules (see below), but are currently not parsed.

### Step 2: Main M2M Transformation

The plugin serializes the parsed Kubernetes model to XML, which is imported and transformed into an EDMM model by the generator of the MPS project.

#### Overview of Mappings

| Kubernetes Object | EDMM Construct |
| --- | --- |
| Kubernetes Deployment Model | Base Component Types & Relation Types, `defaultKubernetesCluster` Component |
| Pod (in Deployment / Stateful Set) | Component & Component Type, hosted-on Relation |
| Container Port | Component Property |
| Environment Variable | Component Property & connects-to Relation |
| Container Image | Component Artifact & Component Type |
| Image Pull Policy | Component Property |
| Service Port | Component Property |
| PVC & Volume & Volume Mount | Component & attaches-to Relation, hosted-on Relation |
| Cron Job | Component & Component Type, hosted-on Relation |
| Pod (standalone) | Component & Component Type |
| Ingress | *not transformed* |
| Config Map | *not transformed* |

#### Details

##### Kubernetes Deployment Model

For each transformed Kubernetes deployment model, the following types are created:

- Relation types `DependsOn`, `ConnectsTo`, and `HostedOn`, where `ConnectsTo` and `HostedOn` are derived from `DependsOn`.
- Component types `BaseType`, `ContainerPlatform` (derived from `BaseType`), `KubernetesCluster` (derived from `ContainerPlatform`), and `DefaultKubernetesCluster` (derived from `KubernetesCluster`).
- If the model contains at least one PVC: The relation type `AttachesTo` (derived from `DependsOn`) with the required property `location`, and the component type `Storage` (derived from `BaseType`) with the required property `storage_size`.

In addition, a component `defaultKubernetesCluster` of type `DefaultKubernetesCluster` is created.
It represents the Kubernetes cluster that hosts all created components until the actual cluster is known (see [Step 4: Post M2M Transformation](#step-4-post-m2m-transformation)).

##### Pod (in Deployment / Stateful Set)

Deployment and stateful set objects specify the workload in the form of a pod running on the Kubernetes cluster.
Each `Deployment` (including stateful sets and replica sets) is mapped to:

- A **component** with the name of the deployment.
- A **component type** `<deployment name>-type` derived from `BaseType`.
  It contains the same property keys as the component.
  The type may be refined later based on the container image (see [Container Image](#container-image)).
- A **hosted-on relation** `<deployment name>_HostedOn_defaultKubernetesCluster` to the `defaultKubernetesCluster` component.

The properties and artifacts of the component are derived from the containers of the pod specification, as described below.
Other attributes of the deployment, such as `replicas` or `labels`, are not mapped.

If several containers result in properties with the same key, properties with identical values are merged into one property.
Properties with different values are kept, and their keys are suffixed with `_<value>` to make them unique.

##### Container Port

Each container port of a container becomes a component property of type `INTEGER`:

- Key: `containerPort`, followed by `_<port name>` if the port has a name.
- Value: the port number.

For example, `- containerPort: 5432` results in the property `containerPort: 5432`.

##### Environment Variable

Each environment variable of a container that has a literal `value` becomes a required component property with the variable name as key and the variable value as value.
Single quotes enclosing the value are replaced by double quotes.
Environment variables that obtain their value via `valueFrom` (e.g., from a config map or secret) are skipped by the parser.

Environment variables are also used to detect **connects-to relations**.
Kubernetes allows the implicit configuration of pod connections in environment variables that reference the name of a service object.
Since the software running in the container defines the naming scheme of the environment variables, this requires a semantic analysis:

1. Each `Service` is matched to the deployments it exposes: A service matches a deployment if each key-value pair of the service `selector` is contained in the deployment's `selector.matchLabels`.
2. An environment variable is considered a connection if its key contains one of the keywords `connect`, `host`, `server`, `url`, `uri`, `service`, `addr`, or `endpoint` (case-insensitive) and its value contains the name of a matched service.
   If several service names are contained, the longest one is chosen.
3. A connects-to relation `<source>_ConnectsTo_<target>` is created from the component of the deployment that defines the environment variable to the component of the deployment matched by the service.
   Relations from a deployment to itself are not created, and for each deployment only one relation to each target is created.

For example, the environment variable `SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/postgres` of the `backend` deployment contains the keyword `url` and the name of the `postgres` service.
Thus, the relation `backend_ConnectsTo_postgres` is created.

Connections are also detected across transformation processes, for example, if the Kubernetes manifests are spread across several embedded deployment models.
For this, the plugin passes the Kubernetes model of previous transformation processes of the same analysis to the MPS transformation.
Environment variables of newly transformed deployments that reference services of previously transformed deployments result in connects-to relations to the existing components, and vice versa.

##### Container Image

Each container of the pod specification is mapped to an **artifact** of the component:

- Type: `docker_image`
- Name: the container image, e.g., `postgres:12.16`
- File URI: `-`

The MPS transformation also maps init containers to artifacts, but `initContainers` are currently not parsed by the plugin.

For each newly created component with a `docker_image` artifact, the Kubernetes plugin requests an analysis by the Docker plugin.
The Docker plugin derives the component type from the image name without registry and tag, e.g., `postgres` for `postgres:12.16`.
It classifies the image as `DatabaseSystem` (e.g., PostgreSQL, MySQL, or MongoDB), `MessageBroker` (e.g., Kafka or RabbitMQ), or otherwise `SoftwareApplication`, and assigns the component type `<image name>-<classification>`, e.g., `postgres-DatabaseSystem`.
Thus, components using the same image share the same component type.
In addition, the Docker plugin replaces the file URI `-` with the URI of the image, e.g., on Docker Hub.
See the Docker transformation for details.

##### Image Pull Policy

The `imagePullPolicy` of each container becomes the component property `imagePullPolicy`.
If no image pull policy is specified, the parser uses the default `IfNotPresent`.

##### Service Port

Services are not mapped to components.
Instead, their ports are added to the components of the deployments they expose (see the service matching in [Environment Variable](#environment-variable)).
Each service port becomes a required component property:

- Key: `exposedPort`, followed by `_<port name>` if the service port has a name.
- Value: `<service port>:<container port>`, where the container port is the container port of the deployment that matches the `targetPort` of the service port by number or name. If no `targetPort` is specified, the service port is used.

Service ports are only mapped if the target port matches a container port of the deployment.
Headless services (`clusterIP: None`) are ignored.

For example, the `postgres` service with `port: 5432` and `targetPort: 5432` results in the property `exposedPort: 5432:5432` of the `postgres` component.

##### Persistent Storage

Kubernetes provides objects to deploy persistent storage for containers, namely the *Persistent Volume Claim (PVC)*, *Volume*, and *Volume Mount*.
A PVC matches a volume of a pod specification if the volume references the claim (`persistentVolumeClaim.claimName`) or if the claim references the volume (`volumeName`).
Each PVC is matched to the first matching volume only, so a PVC used by several workloads results in a single storage component attached to one of them.
For a `volumeClaimTemplate` of a stateful set, the parser creates a PVC named `<stateful set name>-<template name>` and a matching volume named `<template name>` in the pod specification.

Each matched pair of PVC and volume is mapped to:

- A **component** of type `Storage` with the property `storage_size`, which is set to the requested storage of the PVC (`resources.requests.storage`).
  It is named `<PVC name>-volume` if the PVC name ends with the volume name, otherwise `<PVC name>-<volume name>-volume`.
- An **attaches-to relation** from the storage component to the component of the workload whose pod specification contains the volume.
  The relation has the property `location`, which is set to the `mountPath` of the volume mount that references the volume.
  It is named `<PVC name>-mount` or `<PVC name>-<volume name>-mount`, analogous to the component.
- A **hosted-on relation** from the storage component to the `defaultKubernetesCluster` component.

##### Cron Job

A `CronJob` is mapped to a component `<name>-cronjob` and a component type `<name>-cronjob-type` derived from `ContainerPlatform`.
The component gets the properties `schedule`, `timezone`, `concurrentPolicy`, and `startingDeadlineSeconds` (if set) as well as the properties derived from the containers of the job's pod specification, analogous to deployments.
A hosted-on relation to the `defaultKubernetesCluster` component is created.

> [!NOTE]
> The transformation rules for cron jobs are implemented in the MPS project, but cron jobs are currently neither parsed by the plugin nor imported into the MPS transformation.

##### Pod (standalone)

A pod specification that is not part of a deployment is mapped to a component named after the pod's `hostname` and a component type `<hostname>type`.
Its properties and artifacts are derived from the containers as described above.
In contrast to deployments and cron jobs, no hosted-on relation to the `defaultKubernetesCluster` component is created.

> [!NOTE]
> Standalone `Pod` objects are currently not parsed by the plugin.
> Moreover, the plugin serializes standalone pods as `pods`, whereas the MPS transformation imports them from `podSpecs`.
> Thus, standalone pods would also not be passed to the transformation if they were parsed.

##### Ingress

An `Ingress` exposes HTTP routes from outside the cluster to services inside the cluster.
The metamodel covers the `ingressClassName` and, for each rule, the `host` and the HTTP `paths` with their `path`, `pathType`, and `backend`, which references a service by its `name` and a service port by its `name` or `number`.
However, the parser currently only reads the `ingressClassName` reliably:
If the list items of `rules` are indented at the same level as `rules` (`- host: ...` directly below `rules:`), no rules are parsed.
If they are indented further, the parser fails with an exception, which aborts the analysis.

The MPS project contains the template `reduce_Ingress_Properties`, which renders the rules of an ingress into a single property `ingress_rules` with the host, path, path type, and port of each rule.
However, no mapping rule applies this template.
Thus, no information about the external exposure of services is contained in the resulting EDMM model.

> [!NOTE]
> Ingress objects are parsed by the plugin, but not transformed.
> The `KubernetesDeploymentModel` of the MPS language does not contain ingresses, so they are not imported into the MPS transformation.

##### Config Map

A `ConfigMap` stores configuration data as key-value pairs, which pods consume as environment variables or as files in volumes.
The parser reads the `metadata.name`, the `immutable` flag, and the first key-value pair of `data`; further entries of `data` and the `binaryData` are not parsed.
However, if `data` directly follows the `metadata` block, as is common, the `data` entry is skipped, and the `immutable` flag is always parsed as `false`.
Environment variables that reference config map entries via `valueFrom.configMapKeyRef` are skipped (see [Environment Variable](#environment-variable)), and config maps mounted as volumes are not considered.

Config maps are not transformed into any EDMM constructs.
Thus, connections that are configured in config maps, e.g., in application-specific configuration files, are currently not detected.
For example, the Grafana component of the OpenTelemetry Demo is configured to connect to Jaeger, Prometheus, and OpenSearch in a config map, so these connects-to relations are missing in the reconstructed deployment architecture.

> [!NOTE]
> Config map objects are parsed by the plugin, but not transformed.
> The `KubernetesDeploymentModel` of the MPS language does not contain config maps, so they are not imported into the MPS transformation.

### Step 3: Model Merger

After the main M2M transformation, the result is merged into the EDMM model of the current transformation process:

- Components with the same name and component type name are merged into one component that contains the properties, operations, and artifacts of both. Relations of the merged components are redirected accordingly.
- Component types and relation types with the same name are merged.
- **Kubernetes objects**: If the existing EDMM model contains the component type `kubernetes_deployment`, a new component that is not merged as described above replaces the existing component whose component type starts with `kubernetes_` and whose property `metadata.name` equals the name of the new component.
  For example, the Terraform transformation creates such components for resources of the Terraform Kubernetes provider, e.g., a `kubernetes_deployment` resource.
- **Helm charts**: If the existing EDMM model contains the component type `helm_release`, a new component that is not merged as described above replaces an existing `helm_release` component whose property `name` is a prefix of the name of the new component, unless another new component has exactly that name.
  If several `helm_release` components match, only the one whose `name` property equals the name of the new component (if any) is replaced.
  For example, the Terraform transformation creates such components for `helm_release` resources of the Terraform Helm provider.

When a component is replaced, its relations are redirected to the new component and renamed to `<source>_<relation type>_<target>`.
The replaced component is removed, as is its component type if no other component uses it.

> [!NOTE]
> The replacement of Kubernetes objects is only triggered if a component type named exactly `kubernetes_deployment` exists, although components of any type starting with `kubernetes_` (e.g., `kubernetes_stateful_set`) can be replaced.

### Step 4: Post M2M Transformation

The post M2M transformation replaces the `defaultKubernetesCluster` component with the actual Kubernetes cluster if it is known.
A component is considered a Kubernetes cluster if its component type is `KubernetesCluster` or derived from it.
If the merged EDMM model contains another Kubernetes cluster besides `defaultKubernetesCluster`, for example, the `google_container_cluster` created by a Terraform deployment model:

- all hosted-on relations to `defaultKubernetesCluster` are redirected to that cluster component and renamed accordingly, and
- the `defaultKubernetesCluster` component and the `DefaultKubernetesCluster` component type are removed.

## Embedded Deployment Models

- **Docker** (reference embedding): Container images referenced by containers are analyzed by the Docker plugin (see [Container Image](#container-image)).
