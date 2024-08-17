# ghcr
The *GitHub Container Registry* (ghcr) is a service provided by GitHub that allows you to store and manage container images. Container images are self-contained packages that include all the necessary software and dependencies to run an application. The ghcr provides a centralized location for you to store and share your container images, making it easier to distribute and deploy your applications. With ghcr, you can leverage the power of GitHub's version control and collaboration features to manage your container images alongside your source code. This integration simplifies the development and deployment process, allowing you to seamlessly build, store, and distribute container images directly from your GitHub repositories. Whether you are building microservices, deploying applications in a cloud environment, or using containers for development and testing, the ghcr provides a reliable and efficient solution for managing your container images.

---
# Using the ghcr to push a docker container
First, we need to setup a GitHub Action (i.e. a workflow) in which our docker image will be build and finally pushed to the ghcr.
For this, we need to create a file in the `.github/workflows/` directory. In this example we'll call it `action.yml`.
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
# for the docker image tag we use an in-line evaluation the set the proper tag (i.e. latest for the stable, main branch and testing for the unstable, dev branch)
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

Lastly, we need a Dockerfile which is used to build the docker image.
An example can be seen here:
```Dockerfile
# the target docker image
# here we want to use Debian's Sid as latest (i.e. Bookworm) does not have OpenJDK 11 in it's repositories
FROM debian:sid

# update, upgrade and install required packages
# afterwards do not forget to clear the apt cache as otherwise the docker image will be larger than expected
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install --no-install-recommends -y openjdk-11-jdk maven curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# prepare the docker container and set it's working directory, i.e. the directory that the container's commands are executed in
RUN mkdir -p /app/target
WORKDIR /app

# copy over all required files for building
COPY pom.xml .
COPY src ./src

# do not forget the submodules and their required directories!
COPY mps-transformation-ansible ./mps-transformation-ansible
RUN mkdir -p /app/mps-transformation-ansible/transformationInput

# build the project
RUN mvn clean package -DskipTests

# specify the command which is executed upon start
CMD java -jar target/ansible-mps-plugin-0.0.1-SNAPSHOT.jar
```

With this we have a working pipeline to build and push a docker image. We can specify each aspect inside the Dockerfile or change and extend the GitHub action to feature more complex tasks.
In the future, we would like to extend this guide to use cache image as a means to speed up the building of the docker image.