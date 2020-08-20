# Kiuwan and Bitbucket pipelines

As a powerful CI/CD tool, bitbucket offers the possibility to define pipelines with all the steps that your source code needs to be compiled/tested/analyzed/promoted and so on.

I will define here the steps we need to invoke Kiuwan analysis:

1)	Create bitbucket-pipelines.yml
In the root folder of the project we need to create the file bitbucket-pipelines.yml.
This file will define the steps that will be executed in the pipeline. The execution of the pipeline runs on a private host machine from bitbucket. 

2)	Choose a docker base image
We can specify a docker base image with our software requirements. If we don’t specify a docker base image, bitbucket is offering two:
atlassian/default-image:1
atlassian/default-image:2
You can check what they exactly offer here:
https://support.atlassian.com/bitbucket-cloud/docs/use-docker-images-as-build-environments/
In Kiuwan case we need a docker base image with Java8 and Python3. So we can use this image:
```sh
image: openkbs/jdk-mvn-py3
```

3)	Define the step: Kiuwan analysis
Then we want to indicate that we would like to run a Kiuwan analysis. The steps to run a Kiuwan analysis are: 
##### download Kiuwan Local Analyzer
##### run the analysis itself
These entire steps can be implemented in a script. I chose Python but you can use java, php, javascript and many other languages. 
All the logic to analyze is in the python script that you can download from here:
https://github.com/sebastianrevuelta/KiuwanBitbucketPipeline

The way to invoke the analysis from the file bitbucket-pipelines.yml is:
```sh
image: openkbs/jdk-mvn-py3

pipelines:
  default:
    - step:
        script:
          - python3 kla.py $KIUWAN_URL baseline
 ```

This script uses some variables from Bitbucket:
* BITBUCKET_PROJECT_KEY (it will be use as Kiuwan app name)
* BITBUCKET_CLONE_DIR (it is the path with the source code)
* BITBUCKET_BUILD_NUMBER (to tag the analysis)

And some user variables:
- KIUWAN_URL (workspace scope, it should be: https://www.kiuwan.com at least you have a Kiuwan On Premise installation)
- KIUWAN_USER (workspace scope)
- KIUWAN_PASS (workspace scope)
- KIUWAN_SQL_TYPE (project scope, to indicate the sql “flavour” of the project, it can be: plsql | Informix | transactsql). Check Kiuwan documentation to know more 
- KIUWAN_ADVANCED_PARAMS (project scope, to indicate some additional parameters, as ignore=insights or domain-id if you are using SSO authentication). 

To define workspace variables, you need to go to:
##### Workspace -> Settings -> Pipelines – Workspace variables
 
To define project variables, you need to go to:
##### Project  -> Project Settings -> Repository variables.
 
You can check all the default bitbucket variables here:
https://support.atlassian.com/bitbucket-cloud/docs/variables-in-pipelines/

4)	Define the scope of the analysis
Finally, indicate that you can define the scope of the analysis in the bitbucket-pipelines.yml file:
```sh
python3 kla.py $KIUWAN_URL baseline 
```
The value can be baseline or completeDelivery or partialDelivery according to your needs. Please check Kiuwan documentation to know more about Kiuwan scope analysis.


