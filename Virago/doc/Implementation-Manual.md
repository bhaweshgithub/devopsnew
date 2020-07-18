# Implementation Manual

Author: Stephan Lo
Version: Oct 17 2018

## General Guidelines
* Folder structure: `assembly/*`
* Each directory has a README.md, which explians the content and sense of the structure
* Chart ...
* Folder Naming Conventions
** `src`: code in the sense of production software
** `test`: test code
** `build`: temporary stuff to support a deployment (thus listed in .gitignore)

* Screen Shots ...

## Setup

This setup-guide describes how to get a Virago pipeline in an AWS account running.
It is assumed that you have acces
* to the gitlab-git repository
* and to the account you want the pipeline to deploy to.

### Pipeline
1. Deploy the pipeline itself, see `assembly/pipeline` in the order of the folder numbers