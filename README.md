# external_c2 framework
Golang framework for building and utilizing interfaces to transfer data between frameworks, with a specific focus on serving as an extension to Command and Control frameworks.

Currently, this is only intended as an implementation of Cobalt Strike's External C2 specification as described in [this spec document](https://www.cobaltstrike.com/downloads/externalc2spec.pdf), but is subject to change as the project matures.

It provides a basic implant to faciliate the external c2 process, and a server to shuttle the c2. It provides flexible transport mechanisms.


# Architecture
This project consists of the following main parts:
- Transports
- Encoders
