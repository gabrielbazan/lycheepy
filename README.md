[![Build Status](https://travis-ci.com/gabrielbazan/lycheepy.svg?branch=master)](https://travis-ci.com/gabrielbazan/lycheepy)
[![GitHub license](https://img.shields.io/github/license/gabrielbazan/lycheepy.svg)]()


<img align="left" width="80" height="80" src="doc/architecture/lychee.png?raw=true">

# LycheePy

_LycheePy_ is a distributed processing server of geospatial data.

It allows you to: 
 * Publish pre-defined processing chains through a _WPS_ interface. By doing so, users are abstracted about the chains complexity, because they do not have to build them each time they want to chain processes. From the consumer users perspective, a chain is just another process.
 * Automatize geo-spatial data publication into repositories, such as _GeoServer_, _FTP_ servers, or any other kind of repository. You can easily add integrations to new kinds of repositories besides the currently supported.
 * Easily scale. LycheePy is a distributed system. _Worker_ nodes provide processing capabilities and execute processes, and you can add or remove as many you require. Also, LycheePy will concurrently execute processes when possible, according to the chains topology.


## Table of Contents

- [Architecture](#architecture)
  * [Development View](#development-view)
  * [Physical View](#physical-view)
- [Implementation](#implementation)
  * [Repository Structure](#repository-structure)
  * [Components](#components)
- [Deployment](#deployment)
- [Static Configuration](#static-configuration)
- [Publishing, Discovering, and Executing](#publishing-discovering-and-executing)
  * [An Example](#an-example)
  * [Publishing Processes](#publishing-processes)
  * [Publishing Chains](#publishing-chains)
  * [Discovering Executables](#discovering-executables)
  * [Executing](#executing)
  * [Registering Repositories](#registering-repositories)
  * [Discovering Automatically Published Products](#discovering-automatically-published-products)
- [Setting Up Your Development Environment](#setting-up-your-development-environment)
- [The Graphic User Interface](#the-graphic-user-interface)
- [Who Uses LycheePy?](#who-uses-lycheepy)
- [Ideas](#ideas)


## Architecture

### Development View

The development architecture focuses on the software organization into modules. The software is divided into little packages or subsystems which can be developed by small development teams, and they are organized on a layers hierarchy, where each one of them provide a well-defined interface.

Each component responsibilities need to be very well delimited, so there is only one reason for them to change. This way, any change on the system will affect one component only. Having their responsibilities and interfaces well defined, any component may be replaced with another with different implementation, without affecting the others, and they may be reused for other developments.

When there is a dependency between a component and interfaces of another component, then the first should use a _Gateway_, which encapsulates the interaction with those interfaces. This way, any change on those interfaces will only affect the Gateway and, ideally, not the components which use that gateway.

<p align="center">
  <img src="doc/architecture/development_view.png?raw=true" height="370px;">
</p>

On this view, we can distinguish 13 components, being 5 of them Gateways:

* **WPS**: An implementation of the _OGC WPS_ standard, which exposes the _WPS I_ interface, through which can retrieve discovery and execution requests of processes and chains. It depends on the _Configuration Gateway_ component, through which it can access to the metadata of every available executables (processes and chains). Also depends on the _Executor_ component, to which it delegates the execution requests it receives.
* **Configuration Gateway**: Encapsulates the interaction with the _Configuration I_ interface, of the _Configuration_ component.
* **Configuration**: Exposes the _Configuration I_ interface, trough which it is possible to add, modify, and delete processes and chains. It requires some kind of persistence in order to store these settings. Uses the _Processes Gateway_ to store and delete processes files.
* **Executor**: Encapsulates the execution of chains and processes. It can attend every execution request that may come from the WPS component, or some other component we may add in the future. Depends on the _Broker Gateway_ to enqueue processes executions, and on the _Executions Gateway_ in order to inform and update the executions statuses.
* **Executions Gateway**: Encapsulates the interaction with the _Executions I_ interface, of the _Executions_ component.
* **Executions**: Persists the status of all the chains executions that have finished (successfully or with errors) or are still running. It exposes the _Executions I_ interface, through which it is possible to update or read those statuses.
* **Broker Gateway**: Encapsulates every possible interaction with the _Messages Queue_ interface, of the _Broker_ component. Trough this component, it is possible to enqueue tasks.
* **Broker**: Capable of receive tasks and store them on a queue. It ensures that those will be executed in the same order they where enqueued. Publishers and consumers may be distributed across different hosts.
* **Worker**: Consumes tasks from the _Messages Queue_ interface and executes them. It depends on the _Processes Gateway_, to obtain the processes files, which will be later executed. Also depends on the _Repository Gateway_ to perform geospatial data automatic publication.
* **Processes Gateway**: Encapsulates the interaction with the _Processes I_ interface, of the _Processes_ component.
* **Processes**: Stores the files of those processes available on the server.
* **Repository Gateway**: Encapsulates the interaction with repositories for products publishing. This component implements an strategy for each supported repository type.


### Physical View

The physical architecture is the mapping between the software and the hardware. It considers non-functional requirements, such as availability, fault tolerance, performance, and scalability. The software its executed on a computers (_nodes_) network.

The design of the development components has been carried out considering their capability to be distributed across different nodes on a network, searching for the maximum flexibility, and taking full advantage of the distributed processing, making the system horizontally scalable.

The deployment of the software can be carried out considering a maximum _decomposition_, and a minimum decomposition. Between these two extremes, exist many intermediate combinations. 

The minimum decomposition, represented below, consists of deploying all the development components into the same node. This is a completely centralized schema, and it does not perform distributed processing, but there may be the possibility of performing parallel processing if the container's processor has multiple cores. It also carries with all the disadvantages of a centralized system.

<p align="center">
  <img src="doc/architecture/physical_view_minimum.png?raw=true" height="80px">
</p>

On the maximum decomposition, represented below, all the development components, except gateways, are deployed on a dedicated node, plus a proxy, and the necessary persistence components. This schema carries with all the advantages of a distributed system:
1. We can increase (or reduce) each nodes capabilities, according to our needs.
1. We can horizontally scale the processing capabilities, adding more Worker nodes.
1. Because of some nodes failure, it may not result on a complete system unavailability. Of course, it depends on which component fails: For example, if we had multiple Worker nodes, and one of them fails, the processing capability decreases and the chains execution may be slower, but all the system's functionalities will still work; while if the Broker component fails, then we have lost the capability of execute processes and chains, but the system will still be able to attend discovery operations, the products will still be accessible by the users, and so on. Whatever is the case, the recovery to any kind of failure should be faster, because the problem is isolated, and it is easier to identify and resolve, or to replace the node.

<p align="center">
  <img src="doc/architecture/physical_view_maximum.png?raw=true" height="370px">
</p>


## Implementation

This is the section we all might consider the most important, or at least the most attractive. Of course, it is important, but if you scrolled to here without reading about the [architecture](#architecture) then scroll up again :)

### Repository Structure

First, lets talk about the repository organization. At the root of it, we basically have three directories:
 * [lycheepy](/lycheepy), which contains the source code.
 * [doc](/doc), which contains the documentation.
 * [tests](/tests), which contains functional, and (in the future) unitary tests.

Inside the [lycheepy](/lycheepy) directory, we will find one folder per each development component, and everything we need to install and run the application. To ensure the proper distribution of these development components across different containers while we are developing, and even in production, we use [Docker Compose](https://docs.docker.com/compose/), so on this directory we'll find:
 * A [install_host_dependencies.sh](/lycheepy/install_host_dependencies.sh) executable file, which can be used in order to install the host dependencies, such as docker-compose.
 * The [docker-compose.yml](/lycheepy/docker-compose.yml) file. There are found all the containers definitions, their mutual dependencies, the ports they expose for mutual interaction, the ports they expose to the host, and so on.
 * A [start.sh](lycheepy/start.sh) executable file, which can be used to run all the containers for development purposes.

Inside each development component's directory, we will find a _Dockerfile_ file, and the source code of the component itself. Let's see with an example: The _Configuration_ development component is inside the [lycheepy/configuration](lycheepy/configuration) directory, and there we can see:
 * The _Dockerfile_.
 * A folder with the same name of the component, which contains the source code, in this case named [configuration](/lycheepy/configuration/configuration). Inside this folder you can organize your code just as you like.
 * A [requirements.txt](lycheepy/configuration/requirements.txt) file, because we are talking about a component which is implemented with Python, and on this level we should place all install-related files. We will only use this file while the component's installation.
 * A [wait-service.sh](/lycheepy/configuration/wait-service.sh) file, which is an utility to wait until a TCP port of another container starts listening. You can read more about this [here](https://docs.docker.com/compose/startup-order/).

If your component is implemented with Python and uses gateways, then they should be placed on a _gateways_ package, inside the component's sources folder. Inside this package, you can place one folder per each component dependency. This way, we can quickly know which components the component depends on. For example: The [WPS](/lycheepy/wps) component depends on the _Configuration_ component, so inside its [sources folder](/lycheepy/wps/wps) we place a [gateways](/lycheepy/wps/wps/gateways) package, and there we place a [configuration](/lycheepy/wps/wps/gateways/configuration) package, which contains the gateway.


### Components

Just as we said before, the development components are placed inside the [lycheepy](/lycheepy) directory.

#### WPS

Placed on the [wps](/lycheepy/wps) directory, it is an implementation of the OGC WPS standard. More precisely, it is a great Python implementation of that standard, named [PyWPS](http://pywps.org/). 

PyWPS uses a [configuration file](http://pywps.readthedocs.io/en/master/configuration.html), placed [here](/lycheepy/wps/wps/pywps.cfg), where you can:
 * Specify metadata about the server instance.
 * Configure the WPS server. For example, specifying how many processes can be running in parallel.
 * Configure logging policies, such as the logging level.

To make the processes and chains of the _Configuration_ component visible through the WPS interface, this component uses the [ConfigurationGateway](/lycheepy/wps/wps/gateways/configuration).

To delegate the execution requests to the _Executor_ component, we use an [adapter](/lycheepy/wps/wps/adapter). This translates the metadata coming from the _Configuration_ component, into special PyWPS _Process_ instances. When those instances are executed, they simply delegate it to the _Executor_ component.

The [ServiceBuilder](/lycheepy/wps/wps/service) is the one that takes the metadata from the _ConfigurationGateway_, calls the adapter, and appends those special processes to a PyWPS _Service_ instance.


#### Configuration

This is a very simple component, which exposes a ReST API, through which we can publish processes and chains. Right now, we are going to talk about its implementation, rather than [how to use its endpoints](#publishing).

The interface is implemented with the [Simply Restful](https://github.com/gabrielbazan/simply-restful/) framework, which uses _Flask_ and _SQLAlchemy_.

It uses a _PostgreSQL_ instance as persistence, but you could use another database supported by _SQLAlchemy_, such as _SQLite_.

It performs several validations over the chains topography, using [NetworkX](https://networkx.github.io/).

Finally, it publishes processes files on the _Processes_ component, so it uses a [gateway](/lycheepy/configuration/configuration/gateways). This gateway is shared by the _Configuration_ and _Worker_ components, so it is on a separated repository, and referenced as a git-submodule by both components.


#### Executor

It encapsulates the complexity that relies behind the distributed execution of processes and chains, while it provides a very clear interface.

It also keeps the executions statuses updated on the _Executions_ component, through the [ExecutionsGateway](/lycheepy/wps/wps/gateways/executions). Also depends on the [BrokerGateway](/lycheepy/wps/wps/gateways/broker) to enqueue processes executions.

It basically provides two public operations: _execute_process_ and _execute_chain_. When it comes to a process execution, it simply enqueues the process execution using the _BrokerGateway_. But the chains execution is a bit more complex.

On _LycheePy_, **a chain is a directed acyclic graph**, so they can be sliced into antichains by using the [AntiChains](https://networkx.github.io/documentation/networkx-1.10/reference/generated/networkx.algorithms.dag.antichains.html) algorithm. Let's see it with an example:

<p align="center">
  <img src="doc/architecture/antichains.png?raw=true" height="200px">
</p>

The algoritm produces a list of antichains, where an antichain is a list of processes. The particularity of each antichain is that there is no relationship between the processes it contains, so we could execute them in parallel (this means at the same time, using multiple processor cores, or in a distributed way).

We use _NetworkX_ to obtain the antichains, and encapsulate it on the [AntiChains](/lycheepy/wps/wps/executor/anti_chains.py) class. To execute a chain, a [Chain](/lycheepy/wps/wps/executor/chain.py) instance is built using the [ChainBuilder](/lycheepy/wps/wps/executor/chain_builder.py) class, starting from the metadata that comes from the _Configuration_ component. The _Chain_ class encapsulates all the execution logic, which basically consists of loop the antichains list, and send each antichain to the _Broker_, trough the _BrokerGateway_, to be concurrently executed.


#### Executions

This is a very simple component, which exposes a ReST API, through which we can read and update execution statuses. Right now, we are going to talk about its implementation, rather than [how to use its endpoints](#requesting-chain-executions-status).

The interface is implemented with the [Simply Restful](https://github.com/gabrielbazan/simply-restful/) framework, which uses _Flask_ and _SQLAlchemy_.

It uses a _PostgreSQL_ instance as persistence, but you could use another database supported by _SQLAlchemy_, such as _SQLite_.


#### Broker

In the architecture description, we said that this component receives tasks from the _Executor_ (the producer) trough the _BrokerGateway_. Then, these tasks are stored until the _Workers_ consume and execute them. The communication protocol between all these parts must consider that all of them may be located on different hosts, because our goal is to perform distributed processing.

So, to carry out all these functional and not functional requirements, we chose [Celery](http://www.celeryproject.org/): "An asynchronous task queue/job queue based on distributed message passing". It just fits perfectly: "The execution units, called tasks, are executed concurrently on a single or more worker servers".

So, in _Celery_, the workers define which tasks they can execute, and then begin to listen to a broker, which is usually a [RabbitMQ](https://www.rabbitmq.com/) instance, and the producers simply enqueue tasks into the broker. Yes, the _Broker_ component is a _RabbitMQ_ instance. 

The [BrokerGateway](/lycheepy/wps/wps/gateways/broker/gateway.py) uses a _Celery_ application to "talk" with the _Broker_. It enqueues tasks with the same name and parameters that the _Workers_ are expecting.


#### Worker

The [Worker](/lycheepy/worker/worker/distribution/worker.py) defines two tasks:
 * A _run_process_ task, which can execute a process, given its identifier and inputs values. Uses the [ProcessesGateway](https://github.com/gabrielbazan/lycheepy.processes) to obtain the process file.
 * A _run_chain_process_ task, which first executes the process, using the _run_process_, and then performs the automatic products publication, making use of the [RepositoryGateway](/lycheepy/worker/worker/gateways/repository), if any of the process outputs have been configured as automatically publishable.


#### Processes

This component responsibility is simple: It just stores the processes files. So, we have so many alternatives to implement it, some better than others: A FTP server, a database, a shared filesystem, and so on. We've chosen [vsftpd](https://security.appspot.com/vsftpd.html), an FTP server.

The thing here is the [gateway](https://github.com/gabrielbazan/lycheepy.processes/blob/master/gateway.py) to this component, which completely abstracts the gateway's clients about the "complexity" behind this. You can simply obtain a process instance by specifying its identifier.


#### Repository Gateway

The _Repository_ is an external System, capable to store geospatial data. Some repositories may make this data available to users, and they can do it trough different kinds of interfaces. Examples are [GeoServer](http://geoserver.org/), an _FTP_ repository, a _File System_, cloud services, and so on.

The [_Repository Gateway_](/lycheepy/worker/worker/gateways/repository) is the component which encapsulates the interaction with those external repositories, to perform products publication. The _Worker_ component makes use of this gateway, so LycheePy can publish products on multiple instances of different kinds of repositories, at the same time. You are not limited to a single repository, or to a single repository type.

You can easily add integrations with new kinds of repositories: 
There is a [Repository](/lycheepy/worker/worker/gateways/repository/repository.py) "interface" (in Python, the closest thing to an interface is an abstract class), which defines a single _publish_ method. So, all you got to do is create a class that implements that interface and its "_publish_" method, which is the one to be invoked to perform products publication. Yes, it is a _Strategy_ pattern.

<p align="center">
  <img src="doc/architecture/repositories_strategy.png?raw=true" height="120px">
</p>

LycheePy already provides integrations with _GeoServer_ and with _FTP_ servers. So yes, there are two strategies: 
 * The [GeoServerRepository](/lycheepy/worker/worker/gateways/repository/geo_server_repository.py) can publish rasters into a _GeoServer_ instance. It uses the [gsconfig](https://github.com/boundlessgeo/gsconfig) client to interact with a _GeoServer_ instance through its [ReST Configuration API](http://docs.geoserver.org/stable/en/user/rest/).
 * The [FtpRepository](/lycheepy/worker/worker/gateways/repository/ftp_repository.py) can publish any output file into any _FTP_ server.


## Deployment

For development purposes, all you need to run _LycheePy_ is clone the repository and execute the [start.sh](/lycheepy/start.sh) script. 

I still do not figure out the best way of deploying an application with docker-compose into production. I will require some more research.


## Static Configuration

You can configure the maximum amount of time that a process execution can take, on the _lycheepy/wps/wps/settings.py_ file:
```python
PROCESS_EXECUTION_TIMEOUT = 30
```


The PyWPS configuration file can be found in _lycheepy/wps/wps/pywps.cfg_.


The _Configuration_ component settings are placed on the _lycheepy/configuration/configuration/settings.py_ file. There, you can:

1. Configure its endpoints pagination. This takes effect on the chains list, the processes list, the supported formats list, and the supported data types list:
    * _DEFAULT_PAGE_SIZE_ specifies how many results will be returned when the user does not specify the _limit_ query parameter.
    * _MAX_PAGE_SIZE_ specifies the maximum amount of results can be returned, independently of the _limit_ query parameter.
2. Configure on which _form/data_ keys you expect the process metadata, and the process file, when a process is uploaded or updated:
    * _PROCESS_SPECIFICATION_FIELD_ specifies the key where you are expecting the process metadata.
    * _PROCESS_FILE_FIELD_ specifies the key where you are expecting the process file.
3. Configure the supported process file extensions, trough the _ALLOWED_PROCESSES_EXTENSIONS_ parameter. We are using PyWPS, though we only support _.py_ files.

```python
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

PROCESS_SPECIFICATION_FIELD = 'specification'
PROCESS_FILE_FIELD = 'file'

ALLOWED_PROCESSES_EXTENSIONS = ['py']
```

The _Executions_ component settings are placed on the _lycheepy/executions/executions/settings.py_ file. There, you can configure its endpoints pagination. This takes effect on the executions list:
   * _DEFAULT_PAGE_SIZE_ specifies how many results will be returned when the user does not specify the _limit_ query parameter.
   * _MAX_PAGE_SIZE_ specifies the maximum amount of results can be returned, independently of the _limit_ query parameter.
```python
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100
```


## Publishing, Discovering, and Executing

Here comes, I think, the best part. We will see how _LycheePy_ works with an example. 

### An Example

The _COSMO-Skymed_ mission, carried out by the _Italian Space Agency (ASI)_, consists of a constellation of four satellites equipped with _Synthetic Aperture Radar (SAR)_ operating at X-band. 

The COSMO-SkyMed products are divided in the following major classes:

<p align="center">
  <img src="doc/architecture/cosmo_products_classes.png?raw=true" height="110px">
  <br>
  Taken from the <a href="http://www.e-geos.it/products/pdf/csk-product%20handbook.pdf">COSMO-Skymed Products Handbook<a>
</p>

We will focus on the _SAR Standard_ products, which are the following:

<p align="center">
  <img src="doc/architecture/csk_products.png?raw=true" height="95px">
  <br>
  Taken from the <a href="http://www.e-geos.it/products/pdf/csk-product%20handbook.pdf">COSMO-Skymed Products Handbook<a>
</p>

And are generated by this chain:

<p align="center">
  <img src="doc/architecture/standard_processing_model.png?raw=true" height="110px">
  <br>
  Taken from the <a href="http://www.e-geos.it/products/pdf/csk-product%20handbook.pdf">COSMO-Skymed Products Handbook<a>
</p>

Of course, we do not have access to those processors, so we will use [dummy processes](/tests/cosmo/processes), which always return the same image.


### Publishing Processes

The processes administration is done trough the _Configuration_ component. Its configuration interface is available on the _{host}/configuration_ URI, trough the HTTP protocol.

#### Uploading a Process

You can publish processes using the _{host}/configuration/processes_ URI with the HTTP _POST_ method. You have to send two things to the server, using the _multipart/form-data_ HTTP header:
 * The process metadata, in a key named "specification".
 * The process file, in a key named "file".

Processes parameters (inputs and outputs) have _dataType_ OR _format_, they cannot have both or none.

Here you can see a metadata example for the [L0](/tests/processes/cosmo/L0.py) process:
```json
{
  "identifier": "L0",
  "title": "L0 Processor",
  "abstract": "The L0 processor generates the RAW product",
  "version": "0.1",
  "metadata": ["Level 0", "Processor"],
  "inputs": [
    {
      "identifier": "crude", 
      "title": "Crude data",
      "abstract": "Downloaded from the satellite to the ground station",
      "format": "GEOTIFF"
    }
  ],
  "outputs": [
    {
      "identifier": "RAW", 
      "title": "RAW product",
      "abstract": "The single output generated by this processor",
      "format": "GEOTIFF"
    }
  ]
}
```

That's it. Your process is now uploaded and published trough the _WPS_ interface. 


#### Listing Proceses

You can retrieve a list of the published processes, using the _{host}/configuration/processes_ URI with the HTTP _GET_ method.

```json
{
    "count": 1,
    "results": [
        {
            "id": 1,
            "identifier": "L0",
            "version": "0.1",
            "title": "L0 Processor",
            "abstract": "The L0 processor generates the RAW product",
            "metadata": ["Level 0", "Processor"],
            "inputs": [
                {
                    "format": "GEOTIFF",
                    "format": null,
                    "abstract": "Downloaded from the satellite to the ground station",
                    "identifier": "crude",
                    "title": "Crude data"
                }
            ],
            "outputs": [
                {
                    "dataType": null,
                    "format": "GEOTIFF",
                    "abstract": "The single output generated by this processor",
                    "identifier": "RAW",
                    "title": "RAW product"
                }
            ]
        }
    ]
}
```

#### Updating a Process

You can update a process using the _{host}/configuration/processes/{processId}_ URI, where _processId_ is the _id_ property of the process under edition, with the HTTP _PUT_ method.

It works equally than the process upload. With _multipart/form-data_ you'll send the process metadata in the same key, "specification", and optionally send the new process file in the same key, "file".


### Publishing Chains

#### Publishing a Chain

You can publish chains trough the _{host}/configuration/chains_ URI, using the HTTP _POST_ method, with "Content-type: application/json".

Remember that chains are also published trough the _WPS_ interface, so they need to have identical metadata than a process. 

You do not specify explicitly which are the inputs and outputs of a chain. Instead, you specify the "steps" of the chain, where a "step" is an edge of the directed acyclic graph. This edge goes from the "before" process to the "after" process. 

Given the chain steps, _LycheePy_ can build the graph and know which the inputs are, and which the outputs:
 * The chain inputs are the inputs of all the processes (nodes) with indegree 0.
 * The chain outputs are the outputs of all the processes (nodes) with outdegree 0.

_LycheePy_ will automatically try to map the outputs of the "before" process with the inputs of the "after" process, using their identifiers. It is case sensitive. If they do not match by identifier, you can specify an explicit mapping, like this:
```json
{
  "before": "ProcessA",
  "after": "ProcessB",
  "match": {
    "processAoutput": "processBinput"
  }
}
```
 
Here is an example of the SAR Standard Products chain:
```json
{
  "identifier": "Cosmo Skymed",
  "title": "CSK Standard Processing Model",
  "abstract": "An implementation of the SAR Standard Products chain",
  "version": "0.1",
  "metadata": ["Cosmo", "Skymed", "Mission", "Chain"],
  "steps": [
    {"before": "L0", "after": "L1A"},
    {"before": "L1A", "after": "L1B"},
    {"before": "L1B", "after": "L1C"},
    {"before": "L1B", "after": "L1D"}
  ],
  "publish": {
    "L0": ["RAW"],
    "L1A": ["SCS"],
    "L1B": ["MDG"],
    "L1C": ["GEC"],
    "L1D": ["GTC"]
  }
}
```

You can specify which outputs of which processes of the chain will be automatically published. And you simply need to use the "publish" property of the chain, as you can see on the example above. That property is an object, where its keys are the processes identifiers, and each one of them have a list of which outputs we wish to publish. Just as simple as that.

#### Listing Chains

You can retrieve a list of the published chains, using the _{host}/configuration/chains_ URI with the HTTP _GET_ method.

_LycheePy_ will calculate and show you which are inputs and the outputs of the chains. You can see it on the "inputs", and "outputs" properties:
```json
{
    "count": 1,
    "results": [
        {
            "id": 1,
            "identifier": "Cosmo Skymed",
            "version": "0.1",
            "title": "CSK Standard Processing Model",
            "abstract": "An implementation of the SAR Standard Products chain",
            "publish": {
                "L1D": ["GTC"],
                "L1B": ["MDG"],
                "L1A": ["SCS"],
                "L0": ["RAW"],
                "L1C": ["GEC"]
            },
            "steps": [
                {"after": "L1A", "match": {}, "before": "L0"},
                {"after": "L1B", "match": {}, "before": "L1A"},
                {"after": "L1C", "match": {}, "before": "L1B"},
                {"after": "L1D", "match": {}, "before": "L1B"}
            ],
            "metadata": ["Cosmo", "Skymed", "Mission", "Chain"],
            "inputs": [
                {
                    "format": "GEOTIFF",
                    "format": null,
                    "abstract": "Downloaded from the satellite to the ground station",
                    "identifier": "crude",
                    "title": "Crude data"
                }
            ],
            "outputs": [
                {
                    "dataType": null,
                    "format": "GEOTIFF",
                    "abstract": "GEC Product",
                    "identifier": "GEC",
                    "title": "GEC Product"
                },
                {
                    "dataType": null,
                    "format": "GEOTIFF",
                    "abstract": "GTC Product",
                    "identifier": "GTC",
                    "title": "GTC Product"
                }
            ]
        }
    ]
}
```

#### Updating a Chain

You can update a process using the _{host}/configuration/chains/{chainId}_ URI, where _chainId_ is the _id_ property of the chain under edition, with the HTTP _PUT_ method and "Content-type: application-json".

You simply need to send the chain metadata again. This will update the chain, and immediately be reflected on the _WPS_ interface.



### Discovering Executables

That was it, you published your processes and the chain. They now they are available trough the WPS interface. If you perform a _GetCapabilities_ operation, you'll see something like this:

_{host}/wps?service=WPS&request=getcapabilities_
```xml
<!-- PyWPS 4.0.0 -->
<wps:Capabilities xmlns:gml="http://www.opengis.net/gml" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" service="WPS" version="1.0.0" xml:lang="en-US" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsGetCapabilities_response.xsd" updateSequence="1">
    <ows:ServiceIdentification>
        <ows:Title>LycheePy Server</ows:Title>
        <ows:Abstract>LycheePy is a geospatial data processing server that allows you to expose predeterminated chains, and executes them in a distributed way. Also, it can be directly integrated with geospatial repositories, so you can configure these chains to automaticly publish outputs into them</ows:Abstract>
        <ows:Keywords>
            <ows:Keyword>LycheePy</ows:Keyword>
            <ows:Keyword>WPS</ows:Keyword>
            <ows:Keyword>PyWPS</ows:Keyword>
            <ows:Keyword>Processes</ows:Keyword>
            <ows:Keyword>Geospatial</ows:Keyword>
            <ows:Keyword>Distribution</ows:Keyword>
            <ows:Keyword>Automatic</ows:Keyword>
            <ows:Keyword>Products</ows:Keyword>
            <ows:Keyword>Publication</ows:Keyword>
            <ows:Keyword>Repositories</ows:Keyword>
            <ows:Type codeSpace="ISOTC211/19115">theme</ows:Type>
        </ows:Keywords>
        <ows:ServiceType>WPS</ows:ServiceType>
        <ows:ServiceTypeVersion>1.0.0</ows:ServiceTypeVersion>
        <ows:Fees>None</ows:Fees>
        <ows:AccessConstraints>None</ows:AccessConstraints>
    </ows:ServiceIdentification>
    <ows:ServiceProvider>
        <ows:ProviderName>LycheePy Development Team</ows:ProviderName>
        <ows:ProviderSite xlink:href="http://lycheepy.org/"/>
        <ows:ServiceContact>
            <ows:IndividualName>Gabriel Jose Bazan</ows:IndividualName>
            <ows:PositionName>Developer</ows:PositionName>
            <ows:ContactInfo>
                <ows:Phone>
                    <ows:Voice>+54</ows:Voice>
                </ows:Phone>
                <ows:Address>
                    <ows:AdministrativeArea>Argentina</ows:AdministrativeArea>
                    <ows:PostalCode>0</ows:PostalCode>
                    <ows:Country>World, Internet</ows:Country>
                    <ows:ElectronicMailAddress>gbazan@outlook.com</ows:ElectronicMailAddress>
                </ows:Address>
                <ows:OnlineResource xlink:href="http://lycheepy.org"/>
                <ows:HoursOfService>12:00-20:00UTC</ows:HoursOfService>
                <ows:ContactInstructions>Knock on the heavens door</ows:ContactInstructions>
            </ows:ContactInfo>
            <ows:Role>hallo</ows:Role>
        </ows:ServiceContact>
    </ows:ServiceProvider>
    <ows:OperationsMetadata>
        <ows:Operation name="GetCapabilities">
            <ows:DCP>
                <ows:HTTP>
                    <ows:Get xlink:href="http://wps/wps"/>
                    <ows:Post xlink:href="http://wps/wps"/>
                </ows:HTTP>
            </ows:DCP>
        </ows:Operation>
        <ows:Operation name="DescribeProcess">
            <ows:DCP>
                <ows:HTTP>
                    <ows:Get xlink:href="http://wps/wps"/>
                    <ows:Post xlink:href="http://wps/wps"/>
                </ows:HTTP>
            </ows:DCP>
        </ows:Operation>
        <ows:Operation name="Execute">
            <ows:DCP>
                <ows:HTTP>
                    <ows:Get xlink:href="http://wps/wps"/>
                    <ows:Post xlink:href="http://wps/wps"/>
                </ows:HTTP>
            </ows:DCP>
        </ows:Operation>
    </ows:OperationsMetadata>
    <wps:ProcessOfferings>
        <wps:Process wps:processVersion="0.1">
            <ows:Identifier>L0</ows:Identifier>
            <ows:Title>L0 Processor</ows:Title>
            <ows:Abstract>The L0 processor generates the RAW product</ows:Abstract>
        </wps:Process>
        <wps:Process wps:processVersion="0.1">
            <ows:Identifier>L1D</ows:Identifier>
            <ows:Title>L1D Processor</ows:Title>
            <ows:Abstract>Level 1D Processor, which generates the GTC product</ows:Abstract>
        </wps:Process>
        <wps:Process wps:processVersion="0.1">
            <ows:Identifier>Cosmo Skymed</ows:Identifier>
            <ows:Title>CSK Standard Processing Model</ows:Title>
            <ows:Abstract>An implementation of the SAR Standard Products chain</ows:Abstract>
        </wps:Process>
        <wps:Process wps:processVersion="0.1">
            <ows:Identifier>L1A</ows:Identifier>
            <ows:Title>Level 1A Process</ows:Title>
            <ows:Abstract>Level 1A Processor, which generates the SCS product</ows:Abstract>
        </wps:Process>
        <wps:Process wps:processVersion="1.0">
            <ows:Identifier>L1B</ows:Identifier>
            <ows:Title>L1B Processor</ows:Title>
            <ows:Abstract>Level 1B Processor, which generates the MDG product</ows:Abstract>
        </wps:Process>
        <wps:Process wps:processVersion="1.0">
            <ows:Identifier>L1C</ows:Identifier>
            <ows:Title>L1C Processor</ows:Title>
            <ows:Abstract>Level 1C Processor, which generates the GEC product</ows:Abstract>
        </wps:Process>
    </wps:ProcessOfferings>
    <wps:Languages>
        <wps:Default>
            <ows:Language>en-US</ows:Language>
        </wps:Default>
        <wps:Supported>
            <ows:Language>en-US</ows:Language>
        </wps:Supported>
    </wps:Languages>
</wps:Capabilities>
```

You can retrieve more specific details about a process with the _DescribeProcess_ operation:

_{host}/wps?service=WPS&request=describeprocess&version=1.0.0&identifier=**L0**_
```xml
<!-- PyWPS 4.0.0 -->
<wps:ProcessDescriptions xmlns:gml="http://www.opengis.net/gml" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsDescribeProcess_response.xsd" service="WPS" version="1.0.0" xml:lang="en-US">
    <ProcessDescription wps:processVersion="0.1" storeSupported="true" statusSupported="true">
        <ows:Identifier>L0</ows:Identifier>
        <ows:Title>L0 Processor</ows:Title>
        <ows:Abstract>The L0 processor generates the RAW product</ows:Abstract>
        <DataInputs>
            <Input minOccurs="1" maxOccurs="1">
                <ows:Identifier>crude</ows:Identifier>
                <ows:Title>Crude data</ows:Title>
                <ows:Abstract></ows:Abstract>
                <ComplexData maximumMegabytes="10">
                    <Default>
                        <Format>
                            <MimeType>image/tiff; subtype=geotiff</MimeType>
                        </Format>
                    </Default>
                    <Supported>
                        <Format>
                            <MimeType>image/tiff; subtype=geotiff</MimeType>
                        </Format>
                    </Supported>
                </ComplexData>
            </Input>
        </DataInputs>
        <ProcessOutputs>
            <Output>
                <ows:Identifier>RAW</ows:Identifier>
                <ows:Title>RAW product</ows:Title>
                <ComplexOutput>
                    <Default>
                        <Format>
                            <MimeType>image/tiff; subtype=geotiff</MimeType>
                        </Format>
                    </Default>
                    <Supported>
                        <Format>
                            <MimeType>image/tiff; subtype=geotiff</MimeType>
                        </Format>
                    </Supported>
                </ComplexOutput>
            </Output>
        </ProcessOutputs>
    </ProcessDescription>
</wps:ProcessDescriptions>
```

And about the chain, because it is just another process:

_{host}/wps?service=WPS&request=describeprocess&version=1.0.0&identifier=**Cosmo Skymed**_
```xml
<!-- PyWPS 4.0.0 -->
<wps:ProcessDescriptions xmlns:gml="http://www.opengis.net/gml" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsDescribeProcess_response.xsd" service="WPS" version="1.0.0" xml:lang="en-US">
    <ProcessDescription wps:processVersion="0.1" storeSupported="true" statusSupported="true">
        <ows:Identifier>Cosmo Skymed</ows:Identifier>
        <ows:Title>CSK Standard Processing Model</ows:Title>
        <ows:Abstract>An implementation of the SAR Standard Products chain</ows:Abstract>
        <DataInputs>
            <Input minOccurs="1" maxOccurs="1">
                <ows:Identifier>crude</ows:Identifier>
                <ows:Title>Crude data</ows:Title>
                <ows:Abstract></ows:Abstract>
                <ComplexData maximumMegabytes="10">
                    <Default>
                        <Format>
                            <MimeType>image/tiff; subtype=geotiff</MimeType>
                        </Format>
                    </Default>
                    <Supported>
                        <Format>
                            <MimeType>image/tiff; subtype=geotiff</MimeType>
                        </Format>
                    </Supported>
                </ComplexData>
            </Input>
        </DataInputs>
        <ProcessOutputs>
            <Output>
                <ows:Identifier>GEC</ows:Identifier>
                <ows:Title>GEC Product</ows:Title>
                <ComplexOutput>
                    <Default>
                        <Format>
                            <MimeType>image/tiff; subtype=geotiff</MimeType>
                        </Format>
                    </Default>
                    <Supported>
                        <Format>
                            <MimeType>image/tiff; subtype=geotiff</MimeType>
                        </Format>
                    </Supported>
                </ComplexOutput>
            </Output>
            <Output>
                <ows:Identifier>GTC</ows:Identifier>
                <ows:Title>GTC Product</ows:Title>
                <ComplexOutput>
                    <Default>
                        <Format>
                            <MimeType>image/tiff; subtype=geotiff</MimeType>
                        </Format>
                    </Default>
                    <Supported>
                        <Format>
                            <MimeType>image/tiff; subtype=geotiff</MimeType>
                        </Format>
                    </Supported>
                </ComplexOutput>
            </Output>
        </ProcessOutputs>
    </ProcessDescription>
</wps:ProcessDescriptions>
```

### Executing

So, you published and discovered your processes and the chain. Let's execute them trough _WPS_.

Processes can be executed with the _Execute_ operation, where you specify the identifier of the process you wish to execute, and a list of values for its inputs.

The examples below use the HTTP _POST_ method on the _{host}/wps/_ URI.

#### Executing a Process

The following example will execute the _L0_ processor:
```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<wps:Execute service="WPS" version="1.0.0" xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 ../wpsExecute_request.xsd">
  <ows:Identifier>L0</ows:Identifier>
  <wps:DataInputs>
        <wps:Input>
            <ows:Identifier>crude</ows:Identifier>
            <wps:Reference xlink:href="http://repository:8080/geoserver/ows?service=WCS&amp;version=2.0.0&amp;request=GetCoverage&amp;coverageId=nurc:Img_Sample&amp;format=image/tiff">
            </wps:Reference>
        </wps:Input>
    </wps:DataInputs>
</wps:Execute>
```

As a response, you will receive something like this:
```xml
<!-- PyWPS 4.0.0 -->
<wps:ExecuteResponse xmlns:gml="http://www.opengis.net/gml" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsExecute_response.xsd" service="WPS" version="1.0.0" xml:lang="en-US" serviceInstance="http://wps/wps?service=WPS&amp;request=GetCapabilities" statusLocation="http://wps/wps/outputs/f4a9ebf6-4d74-11e8-947e-0242ac12000a.xml">
    <wps:Process wps:processVersion="0.1">
        <ows:Identifier>L0</ows:Identifier>
        <ows:Title>L0 Processor</ows:Title>
        <ows:Abstract>The L0 processor generates the RAW product</ows:Abstract>
    </wps:Process>
    <wps:Status creationTime="2018-05-01T19:22:15Z">
        <wps:ProcessSucceeded>PyWPS Process L0 Processor finished</wps:ProcessSucceeded>
    </wps:Status>
    <wps:ProcessOutputs>
        <wps:Output>
            <ows:Identifier>RAW</ows:Identifier>
            <ows:Title>RAW product</ows:Title>
            <ows:Abstract></ows:Abstract>
            <wps:Reference href="http://{host_name_or_ip}/outputs/1f638322-9e9f-11e8-b5db-0242ac12000a/ows_yu78Ak" mimeType="image/tiff; subtype=geotiff" encoding="" schema=""/>
        </wps:Output>
    </wps:ProcessOutputs>
</wps:ExecuteResponse>
```


#### Executing a Chain

The _Cosmo Skymed_ process (our chain) takes only one input, the _crude_ data, and produces two outputs, the _GEC_ and _GTC_ products, just as we explained [before](#publishing-a-chain).

So, this request is identical to the [previous](#executing-a-process), since the _L0_ processor is the only with indegree 0, so it occupies the first place on the execution order:
```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<wps:Execute service="WPS" version="1.0.0" xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 ../wpsExecute_request.xsd">
  <ows:Identifier>Cosmo Skymed</ows:Identifier>
  <wps:DataInputs>
        <wps:Input>
            <ows:Identifier>crude</ows:Identifier>
            <wps:Reference xlink:href="http://repository:8080/geoserver/ows?service=WCS&amp;version=2.0.0&amp;request=GetCoverage&amp;coverageId=nurc:Img_Sample&amp;format=image/tiff">
            </wps:Reference>
        </wps:Input>
    </wps:DataInputs>
</wps:Execute>
```

As a response, you will receive something like this:
```xml
<!-- PyWPS 4.0.0 -->
<wps:ExecuteResponse xmlns:gml="http://www.opengis.net/gml" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsExecute_response.xsd" service="WPS" version="1.0.0" xml:lang="en-US" serviceInstance="http://wps/wps?service=WPS&amp;request=GetCapabilities" statusLocation="http://wps/wps/outputs/1fa4685e-4d75-11e8-947e-0242ac12000a.xml">
    <wps:Process wps:processVersion="0.1">
        <ows:Identifier>Cosmo Skymed</ows:Identifier>
        <ows:Title>CSK Standard Processing Model</ows:Title>
        <ows:Abstract>An implementation of the SAR Standard Products chain</ows:Abstract>
    </wps:Process>
    <wps:Status creationTime="2018-05-01T19:23:29Z">
        <wps:ProcessSucceeded>PyWPS Process CSK Standard Processing Model finished</wps:ProcessSucceeded>
    </wps:Status>
    <wps:ProcessOutputs>
        <wps:Output>
            <ows:Identifier>GEC</ows:Identifier>
            <ows:Title>GEC Product</ows:Title>
            <wps:Reference href="http://{host_name_or_ip}/outputs/1f638322-9e9f-11e8-b5db-0242ac12000a/ows_yu78Ak" mimeType="image/tiff; subtype=geotiff" encoding="" schema=""/>
        </wps:Output>
        <wps:Output>
            <ows:Identifier>GTC</ows:Identifier>
            <ows:Title>GTC Product</ows:Title>
            <wps:Reference href="http://{host_name_or_ip}/outputs/1f638322-9e9f-11e8-b5db-0242ac12000a/ows_yu78Ak" mimeType="image/tiff; subtype=geotiff" encoding="" schema=""/>
        </wps:Output>
    </wps:ProcessOutputs>
</wps:ExecuteResponse>
```

And all the processes outputs you made automatically publishable on the chain metadata, now are just published.


#### Requesting Chain Execution Statuses

The _WPS_ standard, on its 1.X and 2.X versions, implement a mechanism through which you can request execution statuses, which is specially useful when you are requesting asynchronous executions. This is done trough an identifier which the server will send you as a response for your execution request. But it is limited, because you can only request the status of a single execution ID.

With _LycheePy_ you can still use the _WPS_ mechanism, but it also gives you the possibility of requesting more sophisticated queries. 

Everything is done with the HTTP _GET_ method over the _{host}/executions/executions_ URI.

Let's see. For example, you could request the status of all the executions of the server. Those will include the ones which are still running, and those which already finished (successfully, or with errors):
```
{host}/executions/executions
```

Or you could need the same, but you want to see it chronologically ordered:
```
{host}/executions/executions?order_by=start__desc
```

Or you want to see all the executions of one specific chain:
```
{host}/executions/executions?chain_identifier=Cosmo Skymed&order_by=start__asc
```

Or you want to see all the failed executions of one specific chain:
```
{host}/executions/executions?chain_identifier=Cosmo Skymed&status__name__eq=FAILURE
```

Or to see the executions still running, together with the successful ones:
```
{host}/executions/executions?chain_identifier=Cosmo Skymed&status__name__in=SUCCESS;RUNNING
```

Or simply request the status of a very specific execution ID:
```
{host}/executions/executions?execution_id=41838c1c-4847-11e8-9afe-0242ac12000a
```

Or the last execution sent to the server:
```
{host}/executions/executions?order_by=start__desc&limit=1
```

And so on. Just combine filters as you like.

In all those cases, you'll retrieve a list like this:
```json
{
  "count": 1,
  "results": [
    {
      "status": {
        "id": 2,
        "name": "SUCCESS"
      },
      "end": "2018-04-25T05:13:05.713671Z",
      "start": "2018-04-25T05:13:04.354559Z",
      "reason": "",
      "chain_identifier": "Cosmo Skymed",
      "id": 1,
      "execution_id": "551352d0-4847-11e8-9afe-0242ac12000a"
    }
  ]
}
```


### Registering Repositories

You can dynamically configure the repositories where products will automatically published.

As we've seen, on a chain you can configure which processes outputs need to be published.
And when you do that, those outputs will be automatically published onto all the registered and enabled repositories.

#### Register a Repository

You can register a new repository using the _{host}/configuration/repositories_ URI with the HTTP _POST_ method. 

For now, you can register _Geo Server_ and _FTP_ repositories. 

For example, if you want to register a new _Geo Server_ repository:
```json
{
  "name": "My GeoServer Repository",
  "type": "GEO_SERVER",
  "configurations": {
    "host": "my_geoserver",
    "port": 80,
    "protocol": "http",
    
    "username": "me",
    "password": "123",
    "workspace": "lycheepy"
  }
}
```
Where _host_, _port_ and _protocol_ are mandatory settings.

Or, if you want to register a new _FTP_ repository:
```json
{
  "name": "My FTP Repository",
  "type": "FTP",
  "configurations": {
    "host": "my_ftp",
    "username": "me",
    "password": "123",
    "timeout": 60,
    
    "path": "lycheepy"
  }
}
```
Where _host_, _username_, _password_, and _timeout_ are mandatory settings.

When you register a new repository, by default it is enabled. This means that since it has been registered, publishable outputs will be automatically published onto it. If you want to register a new repository, but not enable it yet, then add the _"enabled"_ property with _false_ as value. Something like this:
```json
{
  "enabled": false,
  "name": "My Disabled FTP Repository",
  "type": "FTP",
  "configurations": {
    "host": "my_disabled_ftp",
    "username": "me",
    "password": "123",
    "timeout": 40
  }
}
```

#### List Repositories

Using the HTTP _GET_ method over the _{host}/configuration/repositories_ URI, you'll retrieve a list of all the registered repositories. Something like this:
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "name": "My GeoServer Repository",
      "type": "GEO_SERVER",
      "enabled": true,
      "configurations": {
        "host": "my_geoserver",
        "protocol": "http",
        "port": "8080"
      },
      "created": "2018-10-30T04:37:41.198935Z",
      "availableConfigurations": ["host", "username", "password", "protocol", "port", "path", "workspace"],
      "mandatoryConfigurations": ["host", "protocol", "port"]
    },
    {
      "id": 2,
      "name": "My FTP Repository",
      "type": "FTP",
      "enabled": true,
      "created": "2018-10-30T04:38:06.299574Z",
      "configurations": {
        "host": "my_ftp",
        "username": "me",
        "password": "",
        "timeout": "5",
        "path": "lycheepy"
      },
      "availableConfigurations": ["host", "username", "password", "timeout", "path"],
      "mandatoryConfigurations": ["host", "username", "password", "timeout"]
    }
  ]
}
```

#### Read a Repository

Using the HTTP _GET_ method over the _{host}/configuration/repositories/{id}_ URI, you can retrieve a specific repository by its identifier. Something like this:
```json
{
  "id": 1,
  "name": "My GeoServer Repository",
  "type": "GEO_SERVER",
  "enabled": true,
  "configurations": {
    "host": "my_geoserver",
    "protocol": "http",
    "port": "8080"
  },
  "created": "2018-10-30T04:37:41.198935Z",
  "availableConfigurations": ["host", "username", "password", "protocol", "port", "path", "workspace"],
  "mandatoryConfigurations": ["host", "protocol", "port"]
}
```

#### Update a Repository

Using the HTTP _PUT_ method over the _{host}/configuration/repositories/{id}_ URI, you can update a specific repository by its identifier. You can send one or more of the representation keys. For example, you could only update its _name_ by sending something like:
```json
{
  "name": "This is not my repository!"
}
```

Or update its configurations, and its name:
```json
{
  "name": "It was my repository",
  "configurations": {
    "host": "my_geoserver",
    "protocol": "http",
    "port": "8080"
  }
}
```

The repository type cannot be updated once it is created.

#### Enabling and Disabling a Repository

You can enable or disable a repository by simply using the HTTP _PUT_ method over the _{host}/configuration/repositories/{id}_ URI, and sending the "enabled" key. The _true_ value stands for enabled, and _false_ for deisabled.

Enabling example:
```json
{
  "enabled": true
}
```

Disabling example:
```json
{
  "enabled": false
}
```


#### Delete a Repository

And finally, using the HTTP _DELETE_ method over the _{host}/configuration/repositories/{id}_ URI, you can delete a specific repository by its identifier.


### Discovering Automatically Published Products

So, you (finally!) configured your repositories, your processes, some chains, and began executing some chains. Now, you want to access the automatically published products on the resistered repositories. 

Whatever is your repository, products are published using a naming convention, so you can quickly identify them:
```
{Chain Identifier}:{Execution ID}:{Process Identifier}:{Output Identifier}
```

#### The GeoServer Example

If you're using a _GeoServer_ instance, you could install the [CSW Plugin](http://docs.geoserver.org/latest/en/user/services/csw/index.html) to it. This exposes a new _OGC_ service: The _Catalog Service for the Web_ (_CSW_). This catalog is filled automatically as you publish data into the repository.

So, making use of the _CSW_ catalog, its _GetRecords_ operation, and the previously explained naming convention, we can request things like:
 * All the products, by simply not specifying any filter.
 * All the products of a chain, using only the chain identifier.
 * All the products of a chain execution, using only the Execution ID.
 * All the products of a process, using only the process identifier.
 * All the products of a process within a specific chain, using the chain identifier, and the process identifier.
 * All the products produced by a specific output of an specific process, using the process identifier, and the output identifier.
 * All the published outputs of a specific process within an execution, using the Execution ID, and the process identifier.
 * And so on.


For example, you could request all the products of an specific execution, using a filter like the following (replace your execution identifier):
```xml
<csw:GetRecords xmlns:csw="http://www.opengis.net/cat/csw/2.0.2" xmlns:ogc="http://www.opengis.net/ogc" service="CSW" version="2.0.2" resultType="results" startPosition="1" maxRecords="10" outputFormat="application/xml" outputSchema="http://www.opengis.net/cat/csw/2.0.2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/cat/csw/2.0.2 http://schemas.opengis.net/csw/2.0.2/CSW-discovery.xsd" xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:apiso="http://www.opengis.net/cat/csw/apiso/1.0">
  <csw:Query typeNames="csw:Record">
    <csw:ElementSetName>full</csw:ElementSetName>
    <csw:Constraint version="1.1.0">
      <ogc:Filter>
        <ogc:PropertyIsLike matchCase="false" wildCard="%" singleChar="_" escapeChar="\">
          <ogc:PropertyName>dc:title</ogc:PropertyName>
          <ogc:Literal>%2e389cae-2a2b-11e8-8048-0242ac12000a%</ogc:Literal>
        </ogc:PropertyIsLike>
      </ogc:Filter>
    </csw:Constraint>
  </csw:Query>
</csw:GetRecords>
```

And as a result, you'll get something like the following, which contains all the _RAW_, _SSC_, _DGM_, _GEC_, and _GTC_ products (in the case of our example):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<csw:GetRecordsResponse xmlns:csw="http://www.opengis.net/cat/csw/2.0.2" xmlns:rim="urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dct="http://purl.org/dc/terms/" xmlns:ows="http://www.opengis.net/ows" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.0.2" xsi:schemaLocation="http://www.opengis.net/cat/csw/2.0.2 http://repository:8080/geoserver/schemas/csw/2.0.2/record.xsd">
    <csw:SearchStatus timestamp="2018-04-25T05:22:58.854Z"/>
    <csw:SearchResults numberOfRecordsMatched="5" numberOfRecordsReturned="5" nextRecord="0" recordSchema="http://www.opengis.net/cat/csw/2.0.2" elementSet="full">
        <csw:Record>
            <dc:identifier>lycheepy:Cosmo Skymed:41838c1c-4847-11e8-9afe-0242ac12000a:L0:RAW</dc:identifier>
            <dc:creator>GeoServer Catalog</dc:creator>
            <dct:references scheme="OGC:WMS">http://repository:8080/geoserver/wms?service=WMS&amp;request=GetMap&amp;layers=lycheepy:Cosmo Skymed:41838c1c-4847-11e8-9afe-0242ac12000a:L0:RAW</dct:references>
            <dc:subject>Cosmo Skymed:41838c1c-4847-11e8-9afe-0242ac12000a:L0:RAW</dc:subject>
            <dc:subject>WCS</dc:subject>
            <dc:subject>GeoTIFF</dc:subject>
            <dc:description>Generated from GeoTIFF</dc:description>
            <dc:title>Cosmo Skymed:41838c1c-4847-11e8-9afe-0242ac12000a:L0:RAW</dc:title>
            <dc:type>http://purl.org/dc/dcmitype/Dataset</dc:type>
            <ows:BoundingBox crs="urn:x-ogc:def:crs:EPSG:6.11:4326">
                <ows:LowerCorner>40.61211948610636 14.007123867581605</ows:LowerCorner>
                <ows:UpperCorner>41.06318200414095 14.555170176382685</ows:UpperCorner>
            </ows:BoundingBox>
        </csw:Record>
        <csw:Record>
            <dc:identifier>lycheepy:Cosmo Skymed:41838c1c-4847-11e8-9afe-0242ac12000a:L1A:SCS</dc:identifier>
            <dc:creator>GeoServer Catalog</dc:creator>
            <dct:references scheme="OGC:WMS">http://repository:8080/geoserver/wms?service=WMS&amp;request=GetMap&amp;layers=lycheepy:Cosmo Skymed:41838c1c-4847-11e8-9afe-0242ac12000a:L1A:SCS</dct:references>
            <dc:subject>Cosmo Skymed:41838c1c-4847-11e8-9afe-0242ac12000a:L1A:SCS</dc:subject>
            <dc:subject>WCS</dc:subject>
            <dc:subject>GeoTIFF</dc:subject>
            <dc:description>Generated from GeoTIFF</dc:description>
            <dc:title>Cosmo Skymed:41838c1c-4847-11e8-9afe-0242ac12000a:L1A:SCS</dc:title>
            <dc:type>http://purl.org/dc/dcmitype/Dataset</dc:type>
            <ows:BoundingBox crs="urn:x-ogc:def:crs:EPSG:6.11:4326">
                <ows:LowerCorner>40.61211948610636 14.007123867581605</ows:LowerCorner>
                <ows:UpperCorner>41.06318200414095 14.555170176382685</ows:UpperCorner>
            </ows:BoundingBox>
        </csw:Record>
        <csw:Record>
            <dc:identifier>lycheepy:Cosmo Skymed:41838c1c-4847-11e8-9afe-0242ac12000a:L1B:MDG</dc:identifier>
            <dc:creator>GeoServer Catalog</dc:creator>
            <dct:references scheme="OGC:WMS">http://repository:8080/geoserver/wms?service=WMS&amp;request=GetMap&amp;layers=lycheepy:Cosmo Skymed:41838c1c-4847-11e8-9afe-0242ac12000a:L1B:MDG</dct:references>
            <dc:subject>Cosmo Skymed:41838c1c-4847-11e8-9afe-0242ac12000a:L1B:MDG</dc:subject>
            <dc:subject>WCS</dc:subject>
            <dc:subject>GeoTIFF</dc:subject>
            <dc:description>Generated from GeoTIFF</dc:description>
            <dc:title>Cosmo Skymed:41838c1c-4847-11e8-9afe-0242ac12000a:L1B:MDG</dc:title>
            <dc:type>http://purl.org/dc/dcmitype/Dataset</dc:type>
            <ows:BoundingBox crs="urn:x-ogc:def:crs:EPSG:6.11:4326">
                <ows:LowerCorner>40.61211948610636 14.007123867581605</ows:LowerCorner>
                <ows:UpperCorner>41.06318200414095 14.555170176382685</ows:UpperCorner>
            </ows:BoundingBox>
        </csw:Record>
        <csw:Record>
            <dc:identifier>lycheepy:Cosmo Skymed:41838c1c-4847-11e8-9afe-0242ac12000a:L1C:GEC</dc:identifier>
            <dc:creator>GeoServer Catalog</dc:creator>
            <dct:references scheme="OGC:WMS">http://repository:8080/geoserver/wms?service=WMS&amp;request=GetMap&amp;layers=lycheepy:Cosmo Skymed:41838c1c-4847-11e8-9afe-0242ac12000a:L1C:GEC</dct:references>
            <dc:subject>Cosmo Skymed:41838c1c-4847-11e8-9afe-0242ac12000a:L1C:GEC</dc:subject>
            <dc:subject>WCS</dc:subject>
            <dc:subject>GeoTIFF</dc:subject>
            <dc:description>Generated from GeoTIFF</dc:description>
            <dc:title>Cosmo Skymed:41838c1c-4847-11e8-9afe-0242ac12000a:L1C:GEC</dc:title>
            <dc:type>http://purl.org/dc/dcmitype/Dataset</dc:type>
            <ows:BoundingBox crs="urn:x-ogc:def:crs:EPSG:6.11:4326">
                <ows:LowerCorner>40.61211948610636 14.007123867581605</ows:LowerCorner>
                <ows:UpperCorner>41.06318200414095 14.555170176382685</ows:UpperCorner>
            </ows:BoundingBox>
        </csw:Record>
        <csw:Record>
            <dc:identifier>lycheepy:Cosmo Skymed:41838c1c-4847-11e8-9afe-0242ac12000a:L1D:GTC</dc:identifier>
            <dc:creator>GeoServer Catalog</dc:creator>
            <dct:references scheme="OGC:WMS">http://repository:8080/geoserver/wms?service=WMS&amp;request=GetMap&amp;layers=lycheepy:Cosmo Skymed:41838c1c-4847-11e8-9afe-0242ac12000a:L1D:GTC</dct:references>
            <dc:subject>Cosmo Skymed:41838c1c-4847-11e8-9afe-0242ac12000a:L1D:GTC</dc:subject>
            <dc:subject>WCS</dc:subject>
            <dc:subject>GeoTIFF</dc:subject>
            <dc:description>Generated from GeoTIFF</dc:description>
            <dc:title>Cosmo Skymed:41838c1c-4847-11e8-9afe-0242ac12000a:L1D:GTC</dc:title>
            <dc:type>http://purl.org/dc/dcmitype/Dataset</dc:type>
            <ows:BoundingBox crs="urn:x-ogc:def:crs:EPSG:6.11:4326">
                <ows:LowerCorner>40.61211948610636 14.007123867581605</ows:LowerCorner>
                <ows:UpperCorner>41.06318200414095 14.555170176382685</ows:UpperCorner>
            </ows:BoundingBox>
        </csw:Record>
    </csw:SearchResults>
</csw:GetRecordsResponse>
```


## Setting Up Your Development Environment

First of all, clone the repository. LycheePy uses git-submodules, so you should clone recursively:
```
git clone https://github.com/gabrielbazan/lycheepy.git --recursive
```

Then, install _docker-ce_, and _docker-compose_, by running:
```
cd lycheepy/lycheepy/
sudo ./install_host_dependencies.sh
```

Now everything we need is installed. To build an run, do the following:
```
sudo ./start.sh
```

And now you're able to use your LycheePy instance.


## The Graphic User Interface

LycheePy also has a web client! You you can find [here](https://github.com/gabrielbazan/lycheepy.cli).


## Who Uses LycheePy?

<a href="https://www.spacesur.com/">
    <img src="https://media.licdn.com/dms/image/C4E0BAQEQOjb-MHjTDQ/company-logo_200_200/0?e=2159024400&v=beta&t=YiOE6cXePgO8_jLtLiAIdZUdZ7wHCIf3Dsp98R8TL28" height="100px" width="100px">
</a>



Do you use it? Add yourself! :)


## Ideas

Feel free to contribute, or come up with some ideas!
