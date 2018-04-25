# LycheePy

Lychee is a distributed, easy to scale, processing server of geo-spatial information.

It allows you to: 
 * Publish pre-defined processing chains through a WPS interface. By doing so, users
 are abstracted about the chains complexity, because they do not have to build them 
 each time they want to chain processes. From the consumer users perspective, a 
 chain is just another process.
 * Automatize geo-spatial data publication through repositories, such as GeoServer, 
 FTP servers, or any other kind of repository.
 * Easily scale. LycheePy is a distributed system. Worker nodes are the ones which 
 provide the processing capabilities and execute processes, and you can add or remove 
 as many you require. Also, LycheePy will concurrently execute processes when it is 
 applicable to the chain's topology.


## Architecture

### Development View

The development architecture focuses on the software organization into modules.
The software is divided into little packages or subsystems which can be developed by 
small development teams, and they are organized on a layers hierarchy, where each one 
of them provide a well-defined interface.

Each component responsibilities need to be very well delimited, so there is only one reason
for it to change. This way, any change on the system will affect only component only.

Having their responsibilities and interfaces well defined, any component may be replaced 
with another implementation without affecting the others, and they may be reused for other
developments.

When exists a dependency between a component, and a interface of another component, then
the first should use a Gateway, which encapsulates the interaction with that interface. This
way, any change on that interface will only affect the Gateway and, ideally, not the 
component itself.

<development_view.png>
LycheePy components diagram.

On this view, we are able to distinguish 13 components, being 5 of them Gateways. The LycheePy development components are:

* **WPS**: An implementation of the OGC WPS standard, which exposes the _WPS I_ interface, 
    through which is able to able to retrieve discovery and execution requests of processes
    and chains. It depends on the _Configuration Gateway_ component in order to know the
    metadata of every available executables (processes and chains) available. 
    Also depends on the _Executor_ component in order to delegate executions.
* **Configuration Gateway**: A component which encapsulates the interaction with the
    _Configuration I_ interface, of the _Configuration_ component.
* **Configuration**: A component which exposes the Configuration I interface, trough which
    it is possible to add, modify, and delete processes and chains. It requires some kind 
    of persistence in order to store this configurations. Uses the Processes Gateway in
    order to store and delete processes.
* **Executor**: A component which encapsulates the execution of chains and processes. 
    Depends on the Broker Gateway in order to enqueue processes executions, and on the 
    Executions Gateway in order to inform the executions status.
* **Executions Gateway**: A component which encapsulates the interaction whit the Executions I interface, of the Executions component.
* **Executions**: A component which persists the status of all the chains executions. It exposes the Executions I interface, through which it is possible tu update or read those statuses.
* **Broker Gateway**: A component which encapsulates all the interaction whith the Messages Queue interface, of the Broker component. Trough this component, it is possible to enqueue tasks.
* **Broker**: A componen which is capable of receive tasks and store them on a queue. It ensures that those will be executed in the same order they where enqueued.
* **Worker**: A component which consumes tasks from the Mesages Queue interface, and executes them. It depends on the Processes Gateway in order to obtain the processes to execute them, and ond the Repository Gateway in order to perform geospatial data automatic publication.
* **Processes Gateway**: A component which encapsulates the interaction with the Processes I interface, of the Processes component.
* **Processes**: A component which stores the files of those processes available on the server.
* **Repository Gateway**: A component which encapsulates the interaction with the Repository I interface, of the Repository component.
* **Repository**:A component capable of storing geospatial data. It exposes a configuration interface, Repository I, and OWS interfaces.


### Physical View

The physical architecture is the mapping between the software and the hardware. It takes into account non-funcional requirements, such as availability, fault tolerance, performance, and scalability. The software its executed on a computers network (nodes).

The design of the development components have been carried out takign into account their capability to be distributed across different nodes on a network, searching for the maximum flexibility and taking full advantage of the distributed processing, making the system horizontally scalable.

The deployment of the software can be carried out taking into account acount a maximum disgregation, and a minimum disgregation. Between this two extremes, exist many intermediate combinations. 

The minimum disgregation, represented below, consists of deloying all the development components into the same node. This is a completely centralized schema, and it does not perform distributed processing, but there may be the possibiblity of perform paralell processing if the container's processor has multiple cores. It also carries with all the disvantages of a centralized system.

<physical_view_minimum.png>

On the maximum disgregation, represented below, all the development components, except gateways, are deployed on a dedicated node, plus a proxy and the necessary persistence components. This schema carries with all the advantages of a distributed system:
1. We can increase (or reduce) each nodes capabilities, according to our needs.
1. We can horizontally scale the processing capabilities, adding more Worker nodes.
1. As a consecuence of some nodes failure, it may not result on a complete unavailability. Of course, it depends on which component fails: For example, if we had multiple Worker nodes, and one of them fails, the processing capability decreases and the chains execution may be slower, but all the system's functionalities will still work; while if the Broker component fails, then we have lost the capability of execute processes and chains, but the system will still be able to attend discovery operations, the products will still be accessible by the users, and so on. Whatever is the case, the recovery to this any kind of failure should be faster, because the problem is isolated and it is easier tho identify and resolve, or to replace the node.

<physical_view_maximum.png>


## Implementation



## Deployment



## Static Configuration



## Publishing

### Publish a Process

### Publish a Chain

### Automatic Products Publication


## Discovering and Executing

### Discover

### Execute a Process

### Execute a Chain


## Requesting Chain Executions Status



## Discovering Automatically Published Products



## TODO List

 * TBD
 
