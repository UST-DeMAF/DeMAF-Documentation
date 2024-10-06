# The GitHub Container registry (ghcr)
The following is an excerpt from [Working with the Container registry]https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry).

## [About the Container registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#about-the-container-registry)

> The Container registry stores container images within your organization or personal account, and allows you to associate an image with a repository. You can choose whether to inherit permissions from a repository, or set granular permissions independently of a repository. You can also access public container images anonymously.

## [Labelling container images](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#labelling-container-images)

The container images may be labelled using the following:

> | Key | Description |
> | --- | --- |
> | `org.opencontainers.image.source` | The URL of the repository associated with the package. For more information, see "[Connecting a repository to a package](https://docs.github.com/en/packages/learn-github-packages/connecting-a-repository-to-a-package#connecting-a-repository-to-a-container-image-using-the-command-line)." |
> | `org.opencontainers.image.description` | A text-only description limited to 512 characters. This description will appear on the package page, below the name of the package. |
> | `org.opencontainers.image.licenses` | An SPDX license identifier such as "MIT," limited to 256 characters. The license will appear on the package page, in the "Details" sidebar. For more information, see [SPDX License List](https://spdx.org/licenses/). |

## [Troubleshooting](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#troubleshooting)

> - The Container registry has a 10 GB size limit for each layer.
> - The Container registry has a 10 minute timeout limit for uploads.

---
# Using the ghcr to push a docker container
## The CI workflow

First, we need to setup a GitHub Action (i.e. a *workflow*) in which our docker image will be build and finally pushed to the ghcr. For this, we need to create a file in the `.github/workflows/` directory.
A basic GitHub actions file might look something like this:

```yaml
# the name of our action
name: buildAndPushImage

# conditions when the action should be run automatically
# in this case whenever something gets pushed to the branches main and dev
# or when a PR is created that is targeting the dev branch
on:
  push:
    branches:
      - 'main'
      - 'dev'
  pull_request:
    branches:
      - 'dev'

# environmental variables (i.e. global variables)
# for the docker image tag we use an in-line evaluation the set the proper tag 
# (i.e. latest for the stable, main branch and testing for the unstable, dev branch)
env:
  # our target URL, this can either be a user or organization like here
  IMAGE_URL: ghcr.io/ust-demaf
  # the name of the docker image
  IMAGE_NAME: ansible-mps-plugin
  # the tag of the docker image
  IMAGE_TAG: ${{ github.ref == 'refs/heads/main' && 'latest' || 'testing' }}

# these are the jobs that will be run one after the other
jobs:
  # the name of the job
  build-using-dockerfile-push-2-ghcr:
    # on which docker container the job should be run on
    runs-on: ubuntu-latest

    # which steps should be taken
    steps:
      # using GitHub's checkout action to get the latest commit
      - uses: actions/checkout@v4
        # wether or not submodules should be included as well
        # IMPORTANT: the submodules MUST be pushed to the repository beforehand!!!
        with:
          submodules: 'true'

      # login to the ghcr using the GITHUB_TOKEN and a user
      - name: Login to GitHub Container Registry
        run: echo ${{ secrets.GITHUB_TOKEN }} | docker login ghcr.io -u well5a --password-stdin

      # build the docker container using a Dockerfile and tagging it accordingly
      - name: Build the Docker image
        run: docker build . --file Dockerfile --tag $IMAGE_URL/$IMAGE_NAME:$IMAGE_TAG

      # push the final docker image to the ghcr
      - name: Push the Docker image
        run: docker push $IMAGE_URL/$IMAGE_NAME:$IMAGE_TAG
```

For our purposes we only have to change the `IMAGE_NAME` varibale to the corresponding plugin name. The tag *latest* will be used for any commits on the *main* branch while *testing* will be used for the *dev* branch.

---
## The Dockerfile 

Lastly, we need a *Dockerfile* which is used to build the docker image. For this we use two build steps for the plugins as the *build* step uses a larger image than the *runtime* image.
An example can be seen here:

```Dockerfile
# First, we need to set the docker image we want to use for building the final application. 
# In this case it is the maven docker image using Eclipse Temurin JDK 11:

# Stage 1: Build the application using Maven with Eclipse Temurin JDK 11
FROM maven:3.8.6-eclipse-temurin-11 AS build

# Set the working directory for the build stage
WORKDIR /app

# Copy the Maven project file and source code into the container
COPY pom.xml .
COPY src ./src
COPY mps-transformation-ansible ./mps-transformation-ansible

# Create the necessary directory for transformation input
RUN mkdir -p /app/mps-transformation-ansible/transformationInput

# We want to have *two* images - *-slim* and the regular one. 
# For this we use the environmental variable `SLIM` to distinguish. 
# The -slim tagged image will *not* have MPS pre-installed.

# Conditionally comment out the line 'executor.execute(prepareMps)' if SLIM=1
ARG SLIM
RUN if [ "$SLIM" != "1" ]; then \
    sed -i 's/executor\.execute(prepareMps)/\/\/ executor.execute(prepareMps)/' /app/src/main/java/ust/tad/ansiblempsplugin/analysis/TransformationService.java; \
    fi

# Build the project, using multiple threads and skipping tests
RUN mvn -T 2C -q clean package -DskipTests

# Download MPS iff SLIM!=1
RUN if [ "$SLIM" != "1" ]; then \
    cd mps-transformation-ansible && \
    ./gradlew prepareMps; \
    fi

# Remove JBR tarball and MPS/Plugin zips
RUN rm -rf /app/mps-transformation-ansible/build/download

# Finally, we choose a runtime docker image which used when we run the application
# In this case we chose the openJDK 11 JRE slim edition.

# Stage 2: Create a minimal runtime image using OpenJDK 11 JRE
FROM openjdk:11-jre-slim

# Set the working directory for the runtime stage
WORKDIR /app

# Copy all built files from the build stage to the runtime stage
COPY --from=build /app /app

# Set the command to run the application
CMD ["java", "-jar", "/app/target/ansible-mps-plugin-0.0.1-SNAPSHOT.jar"]
```

With this we have a working pipeline to build and push a docker image. We can specify each aspect inside the Dockerfile or change and extend the GitHub action to feature more complex tasks.
In the future, we would like to extend this guide to use cache image as a means to speed up the building of the docker image.

An example can be seen with the visualization service's [workflow](https://github.com/UST-DeMAF/visualization-service/blob/main/.github/workflows/buildAndPushImage.yml) and [Dockerfile](https://github.com/UST-DeMAF/visualization-service/blob/main/Dockerfile) (which uses an Alpine Linux based docker image). Another example can be seen with the Ansible plugin's [workflow](https://github.com/UST-DeMAF/ansible-mps-plugin/blob/main/.github/workflows/buildAndPushImage.yml) and [Dockerfile](https://github.com/UST-DeMAF/ansible-mps-plugin/blob/main/Dockerfile) (this uses the example code from above).

---
## Using the ghcr
To then use the built docker images from the ghcr we can simply use the following command:

```bash
docker pull ghcr.io/ust-demaf/[image name]:[tag]
```

So, for example, if we want to pull the Ansible plugin using the latest tag we can run:

```bash
docker pull ghcr.io/ust-demaf/ansible-mps-plugin:latest
```

This pulls the latest version (i.e. the version from the *main* branch) of the Ansible plugin with MPS pre-installed.

To see a list of all available docker images from the UST-DeMAF organization visit the *[Packages](https://github.com/orgs/UST-DeMAF/packages)* tab from the organization's main page.