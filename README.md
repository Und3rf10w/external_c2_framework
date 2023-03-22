# external_c2 framework
Golang framework for building and utilizing interfaces to transfer data between frameworks, with a specific focus on serving as an extension to Command and Control frameworks.

Currently, this is only intended as an implementation of Cobalt Strike's External C2 specification as described in [this spec document](https://www.cobaltstrike.com/downloads/externalc2spec.pdf), but is subject to change as the project matures.

It provides a basic implant to faciliate the external c2 process, and a server to shuttle the c2. It provides flexible transport mechanisms.


# Architecture
This project consists of the following main parts:
- Transports
- Encoders

# Building
This project makes extensive use of go build tags and [VSCode](https://vscodium.com/). If you import the root of this project into VSCode or VSCodium, you will have an identical development environment.

Tasks have been provided that change your [.vscode/settings.json](/.vscode/settings.json) to enable you to quickly switch VSCode's context between the component you are developing for.

## Client 
First, run the task `Set VSCode to Client Environment (overwrites settings.json)`

> **Warning**
> Running this task will wipe your [.vscode/settings.json](/.vscode/settings.json) file

Finally, run the `Build Client` Task

## Server
First, run the task `Set VSCode to Server Environment (overwrites settings.json)`

> **Warning**
> Running this task will wipe your [.vscode/settings.json](/.vscode/settings.json) file

Finally, run the `Build Server` Task