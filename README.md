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

The software components of the development view have been delimitaded taking into account the posibility of

La delimitacion de los componentes del software ´
en la vista de desarrollo se llevo a cabo teniendo en mente la ´
posibilidad de brindar la maxima flexibilidad posible para la ´
distribucion de cada uno de ellos a trav ´ es de varios nodos ´
interconectados en una red, sacando el maximo provecho ´
posible del procesamiento distribuido, y desarrollando a su
vez un sistema horizontalmente escalable.

El despliegue del software puede llevarse a cabo teniendo en
cuenta una disgregacion m ´ ´ınima y una disgregacion m ´ axima ´
posibles, existiendo puntos intermedios entre estos dos extremos.
La disgregacion m ´ ´ınima, representada en la Fig. 22, consiste
en desplegar todos los componentes en un mismo nodo.
Este esquema es completamente centralizado, y no realiza
procesamiento distribuido, aunque puede existir la posibilidad
de realizar proceso en paralelo, si es que el procesador de este
nodo dispone de mas de un n ´ ucleo. A su vez, tiene todas las ´
desventajas mencionadas en la seccion VI. 

<physical_view_minimum.png>

La disgregacion m ´ axima, representada en la Fig. 23, con- ´
siste en desplegar cada uno de los componentes de desarrollo
que exponen interfaces en un nodo dedicado. Ademas, despl- ´
iega un proxy y aquellos componentes de persistencia necesarios.
Este esquema trae consigo todas las ventajas descritas
en la seccion VI, ya que permite: ´
1) Aumentar (o reducir) las capacidades de cada uno de los
nodos segun su necesidad. ´
2) Podemos escalar horizontalmente la capacidad de procesamiento
del servidor, agregando mas instancias del ´
nodo Worker.
3) La falla de uno de los nodos podr´ıa no resultar en una
falla total en el sistema. Esto, por supuesto, dependera´
del componente: Por ejemplo, si existiesen varios nodos
Worker y perdieramos uno, la ´ unica consecuencia es ´
que la capacidad de procesamiento disminuye, pero el
sistema sigue funcionando a la perfeccion; mientras ´
que si el componente Broker ha cesado de funcionar,
entonces hemos perdido la capacidad de procesar pedidos
de ejecucion, pero a ´ un podr ´ ´ıamos responder a
operaciones de descubrimiento, porque Configuration
sigue funcionando. Cual sea el caso, la recuperacion ante ´
un error en uno de los nodos tiene que ser mas r ´ apida ´
que en un esquema centralizado, porque el problema esta´
aislado y es facil de identificar y resolver, o de generar ´
un nodo identico.

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
 
