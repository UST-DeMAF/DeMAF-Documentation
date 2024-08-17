# EnPro-Documentation
Documentations and artifacts of the EnPro University Stuttgart summer semester 2024.  
Within this document you can find a general instruction on how the project is build and used.  
For a guide to MPS testing see [this file](mps-testing/README.md).  

---
# DeMAF Documentation

DeMAF is organized in one big GITHUB Project (https://github.com/UST-DeMAF) with several (Sub-) Repositories. 
Most of the repositories are *“Plugin”* repositories which represent functions of the tool for a specific deployment technology.

![DeMAF_Overview](resources/images/DeMAF_Overview_2.png)

DeMAF is organized in a microservice architecture. To run the tool you need to run every microservice as well as the databases. For easy use, we recommend deployment on your local machine with `docker-compose`. 

---
# Getting Started:
1. To deploy the DeMAF Tool with `docker-compose`, it is required to install Docker and Docker Compose (https://docs.docker.com/compose/install/). Install depending on your OS Docker Desktop, as describe on the website.

2. Clone the Deployment Config Tool (https://github.com/UST-DeMAF/deployment-config.git) 
    -	`git clone https://github.com/UST-DeMAF/deployment-config.git`

3. Start the Docker Desktop Application

4. Go to the `volume` folder of the `deployment-config` repository on your system and run `docker-compose pull && docker-compose up -d` on your system.
    - The console output looks like this:
      ![Command_Line_Docker_command](resources/images/docker_compose_pull_docker_compose_compose.jpg)

    - Inside the docker-application you also see, that the containers are running:
      ![Docker](resources/images/docker_container.jpg)

5.	Clone the DeMAF-Shell to your system:
    - `git clone https://github.com/UST-DeMAF/demaf-shell.git`

6.	Open the `demaf-shell` folder and run the command: 
    - `mvnw spring-boot:run`

    - The DeMAF-shell boots up:
      ![DeMAF_Shell](resources/images/DeMAF_Shell.jpg)
 
7.	Inside the DeMAF-shell you can run the following commands:
    - `transform`: transforms a deployment model into a EDMM Model
      - **args**: 
        - `location` (short: `l`): location of the deployment model
          - `technology` (short: `t`): deployment technology used (depends on available plugins `[bash, terraform, ...]`)
          - `commands` (short: `c`): specify how the deployment model is executed (e.g., for Terraform, you can pass parameters for the execution plan)
      - **Example**:
        -  Clone the Example Deployment Model:  
          `git clone https://github.com/Well5a/kube`
        -  Run `transform --location file:/usr/share/kube/azure-start.sh --technology bash --commands ./azure-start.sh` inside the DeMAF-shell

    - `plugins`: List all (available) registered plugins

---
## Help Section
If you encounter problems during installation and initial use, the following points may help you:

1. If you try to run `docker pull && docker-compose up -d` command and you receive the following error:
  ```log
  C:\Users\USER\deployment-config>docker-compose pull && docker-compose up -d time="2024-05-24T12:12:57+02:00" level=warning msg="C:\\Users\\USER\\deployment-config\\docker-compose.yml: `version` is obsolete" unable to get image 'well5a/kubernetes-mps-plugin:latest': error during connect: this error may indicate that the docker daemon is not running: Get "http://%2F%2F.%2Fpipe%2Fdocker_engine/v1.45/images/well5a/kubernetes-mps-plugin:latest/json": open //./pipe/docker_engine: The system cannot find the specified file
  ```
  - **Make sure the Docker-Application is running**


