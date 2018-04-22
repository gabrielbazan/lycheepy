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
* **Broker**: 
* **Worker**: 
* **Processes Gateway**: 
* **Processes**: 
* **Repository Gateway**: 
* **Repository**:


 Broker Gateway: Componente que encapsula la interacci
´on con la interfaz Messages Queue, del componente
Broker, permitiendo la publicaci´on de tareas en esta
interfaz.
 Broker: Componente capaz de recibir tareas y de almacenarlas
en una cola. Asegura que las tareas sean ejecutadas
en el mismo orden con el que se encolaron.
 Worker: Componente que consume las tareas de la
interfaz Messages Queue, y las ejecuta. Depende de
Processes Gateway para obtener los procesos a ejecutar,
y de Repository Gateway para realizar la publicaci´on
autom´atica de productos geoespaciales.
 Processes Gateway: Componente que encapsula la interacci
´on con la interfaz Processes I, del componente
Processes.
 Processes: Componente que almacena los archivos de los
procesos disponibles en el servidor.
 Repository Gateway: Componente que encapsula la
interacci´on con la interfaz Repository I, del componente
Repository.
 Repository: Componente capaz de almacenar datos
geoespaciales. Expone una interfaz de configuraci´on,
Repository I, y una interfaz para la consulta de datos
geoespaciales, OWS.



### Physical View

<physical_view_maximum.png>

<physical_view_minimum.png>


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
 
