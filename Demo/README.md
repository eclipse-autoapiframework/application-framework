# Demo

Three examples are provided to illustrate the usage of the Vehicle Application Framework (VAF).
1. [HelloVaf](./HelloVaf/) is a simple one and the ideal starting point with the framework. It
   introduces to the three different project types and the Configuration as Code user front-end. 
   Two application modules exchange information internal to one executable.
2. [Vss](./Vss) extends the previous example and illustrates how imported datatype and interface
   information from the [COVESA Vehicle Signal Specification (VSS)](https://covesa.global/project/vehicle-signal-specification/) can be used.
3. [SilKit](./SilKit/) is an example project with two executables that communicate via the [Vector
   SIL Kit](https://github.com/vectorgrp/sil-kit). This illustrates the concept of middleware
   abstraction and how to do system-level tests with a distributed application and using VAF.
