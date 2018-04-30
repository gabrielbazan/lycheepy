<img align="left" width="80" height="80" src="doc/architecture/lychee.png?raw=true">

# LycheePy

_LycheePy_ is a distributed, easy to scale, processing server of geo-spatial data.

It allows you to: 
 * Publish pre-defined processing chains through a _WPS_ interface. By doing so, users are abstracted about the chains complexity, because they do not have to build them each time they want to chain processes. From the consumer users perspective, a chain is just another process.
 * Automatize geo-spatial data publication through repositories, such as _GeoServer_, _FTP_ servers, or any other kind of repository.
 * Easily scale. LycheePy is a distributed system. _Worker_ nodes are the ones which provide the processing capabilities and execute processes, and you can add or remove as many you require. Also, LycheePy will concurrently execute processes when it is applicable to the chain's topology.


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
* **Configuration**: Exposes the _Configuration I_ interface, trough which it is possible to add, modify, and delete processes and chains. It requires some kind of persistence in order to store this settings. Uses the _Processes Gateway_ in order to store and delete processes files.
* **Executor**: Encapsulates the execution of chains and processes. It can attend every execution request that may come from the WPS component, or some other component we may add in the future. Depends on the _Broker Gateway_ to enqueue processes executions, and on the _Executions Gateway_ in order to inform and update the executions statuses.
* **Executions Gateway**: Encapsulates the interaction with the _Executions I_ interface, of the _Executions_ component.
* **Executions**: Persists the status of all the chains executions that have finished (successfully or with errors) or are still running. It exposes the _Executions I_ interface, through which it is possible to update or read those statuses.
* **Broker Gateway**: Encapsulates every possible interaction with the _Messages Queue_ interface, of the _Broker_ component. Trough this component, it is possible to enqueue tasks.
* **Broker**: Capable of receive tasks and store them on a queue. It ensures that those will be executed in the same order they where enqueued. Publishers and consumers may be distributed across different hosts.
* **Worker**: Consumes tasks from the _Messages Queue_ interface and executes them. It depends on the _Processes Gateway_, to obtain the processes files, which will be later executed. Also depends on the _Repository Gateway_ to perform geospatial data automatic publication.
* **Processes Gateway**: Encapsulates the interaction with the _Processes I_ interface, of the _Processes_ component.
* **Processes**: Stores the files of those processes available on the server.
* **Repository Gateway**: Encapsulates the interaction with the _Repository I_ interface, of the _Repository_ component.
* **Repository**: Capable of storing geospatial data. 


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

First of all, lets talk about the repository organization. At the root of it, we basically have three directories:
 * [lycheepy](/lycheepy), which contains the source code.
 * [doc](/doc), which contains the documentation.
 * [tests](/tests), which contains functional, and (in the future) unitary tests.

Inside the [lycheepy](/lycheepy) directory, we will find one folder per each development component, and everything we need to install and run the application. To ensure the proper distribution of these development components across different containers while we are developing, and even in production, we use [Docker Compose](https://docs.docker.com/compose/), so on this directory we'll find:
 * A [host_dependencies.sh](/lycheepy/host_dependencies.sh) executable file, which can be used in order to install the host dependencies, such as docker-compose.
 * The [docker-compose.yml](/lycheepy/docker-compose.yml) file. There are found all the containers definitions, their mutual dependencies, the ports they expose for mutual interaction, the ports they expose to the host, and so on.
 * A [start.sh](lycheepy/start.sh) executable file, which can be used to run all the containers for development purposes.

Inside each development component's directory, we will find a _Dockerfile_ file, and the source code of the component itself. Lets see with an example: The _Configuration_ development component is inside the [lycheepy/configuration](lycheepy/configuration) directory, and there we can see:
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

It uses a _PostgreSQL_ instance as persistence, but you could use other database supported by _SQLAlchemy_, such as _SQLite_.

It performs several validations over the chains topography, using [NetworkX](https://networkx.github.io/).

Finally, it publishes processes files on the _Processes_ component, so it uses a [gateway](/lycheepy/configuration/configuration/gateways). This gateway is shared by the _Configuration_ and _Worker_ components, so it is on a separated repository, and referenced as a git-submodule by both components.


#### Executer

It encapsulates the compexity that relies behind the distributed execution of processes and chains, while it provides a very clear interface.

It also keeps the executions statuses updated on the _Executions_ component, through the [ExecutionsGateway](/lycheepy/wps/wps/gateways/executions). Also depends on the [BrokerGateway](/lycheepy/wps/wps/gateways/broker) to enqueue processes executions.

It basically provides two public operations: _execute_process_, and _execute_chain_. When it comes to a process execution, it simply enqueues the process execution using the _BrokerGateway_. But the chains execution is a bit more complex.

Chains are sliced into antichains by using the [AntiChains](https://networkx.github.io/documentation/networkx-1.10/reference/generated/networkx.algorithms.dag.antichains.html) algorithm. Lets see it with an example:

<p align="center">
  <img src="doc/architecture/antichains.png?raw=true" height="200px">
</p>

The algoritm produces a list of antichains, where an antichain is a list of processes. The particularity of each antichain is that there is no relationship between the processes it contains, so we could execute them in parallel (this means at the same time, using multiple processor cores, or in a distributed way).

We use _NetworkX_ to obtain the antichains, and encapsulate it on the [AntiChains](/lycheepy/wps/wps/executor/anti_chains.py) class. To execute a chain, a [Chain](/lycheepy/wps/wps/executor/chain.py) instance is built using the [ChainBuilder](/lycheepy/wps/wps/executor/chain_builder.py) class, starting from the metadata that comes from the _Configuration_ component. The _Chain_ class encapsulates all the execution logic, which basically consists of loop the antichains list, and send each antichain to the _Broker_, trough the _BrokerGateway_, to be concurrently executed.


#### Executions

This is a very simple component, which exposes a ReST API, through which we can read and update execution statuses. Right now, we are going to talk about its implementation, rather than [how to use its endpoints](#requesting-chain-executions-status).

The interface is implemented with the [Simply Restful](https://github.com/gabrielbazan/simply-restful/) framework, which uses _Flask_ and _SQLAlchemy_.

It uses a _PostgreSQL_ instance as persistence, but you could use other database supported by _SQLAlchemy_, such as _SQLite_.


#### Broker

In the architecture description, we said that this component receives tasks from the _Executor_ (the producer) trough the _BrokerGateway_. Then, these tasks are stored until the _Workers_ consume and execute them. The communication protocol between all these parts must consider that all of them may be located on different hosts, because our goal is to perform distributed processing.

So, to carry out all these functional and not functional requirements, we chose [Celery](http://www.celeryproject.org/): "An asynchronous task queue/job queue based on distributed message passing". It just fits perfectly: "The execution units, called tasks, are executed concurrently on a single or more worker servers".

So, in _Celery_, the workers define which tasks they can execute, and then begin to listen to a broker, which is usually a [RabbitMQ](https://www.rabbitmq.com/) instance, and the producers simply enqueue tasks into the broker. Yes, the _Broker_ component is a _RabbitMQ_ instance. 

The [BrokerGateway](/lycheepy/wps/wps/gateways/broker/gateway.py) uses a _Celery_ application to "talk" with the _Broker_. It enqueues tasks with the same name and parameters that the _Workers_ are expecting.


#### Worker

The [Worker](/lycheepy/worker/worker/distribution/worker.py) defines two tasks:
 * A _run_process_ task, which can execute a process, given its identifier and inputs values. Uses the [ProcessesGateway](https://github.com/gabrielbazan/lycheepy.processes) to obtain the process file.
 * A _run_chain_process_ task, which first executes the process, using the _run_process_, and then performs the automatic products publication, making use of the [RepositoryGateway](/lycheepy/worker/worker/gateways/repository), if any of the process outputs have been configured as automaticly publishable.


#### Processes

This component responsibility is simple: It just stores the processes files. So we have so many alternatives to implement it, some better than others: A FTP server, a database, a shared filesystem, and so on. We've chosen [vsftpd](https://security.appspot.com/vsftpd.html), an FTP server.

The thing here is the [gateway](https://github.com/gabrielbazan/lycheepy.processes/blob/master/gateway.py) to this component, which completely abstracts the gateway's clients about the "complexity" behind this. You can simply obtain a process instance by specifying its identifier.


#### Repository

Description here.



## Deployment



## Static Configuration

You can configure on which repositories the geospatial data will be automaticly published on the _worker/worker/settings.py_ file. It is a dictionary where each key determines a supported repository kind, and for each one of them we specify a list of repositories of that kind. So we could, for example, publish on multiple geoserver instances and multiple FTP servers at the same time.
```python
REPOSITORIES = {
    Repositories.GEO_SERVER: [
        {
            'protocol': 'http',
            'host': 'repository',
            'port': 8080
        }
    ],
    Repositories.FTP: [
        {
            'ip': 'ftp_repository',
            'username': 'lycheepy',
            'password': 'lycheepy',
            'timeout': 120
        }
    ]
}
```

You can also configure the maximum amount of time that a process execution can take, on the _lycheepy/wps/wps/settings.py_ file:
```python
PROCESS_EXECUTION_TIMEOUT = 30
```

The PyWPS configuration file can be found in _lycheepy/wps/wps/pywps.cfg_.


The _Configuration_ component settings are placed on the _lycheepy/configuration/configuration/settings.py_ file. There, you can:
 1. Configure its endpoints pagination. This takes effect on the chains list, the processes list, the supported formats list, and the supported data types list:
  * _DEFAULT_PAGE_SIZE_ specifies how many results will be returned when the user does not specify the _limit_ query parameter.
  * _MAX_PAGE_SIZE_ specifies the maximum amount of results can be returned, independently of the _limit_ query parameter.
 1. Configure on which _form/data_ keys you expect the process metadata, and the process file, when a process is uploaded or updated.
  * _PROCESS_SPECIFICATION_FIELD_ specifies the key where you are expecting the process metadata.
  * _PROCESS_FILE_FIELD_ specifies the key where you are expecting the process file.
 1. Configure the supported process file extensions, trough the _ALLOWED_PROCESSES_EXTENSIONS_ parameter. We are using PyWPS, though we only support _.py_ files.
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


## Publishing

### Publish a Process

```json
{
  "identifier": "L0",
  "title": "L0 Processor",
  "abstract": "L0 Processor, which generates the RAW product",
  "version": "0.1",
  "metadata": ["Level 0", "Processor"],
  "inputs": [
    {
      "identifier": "crude", 
      "title": "crude",
      "abstract": "Crude data",
      "dataType": "string"
    }
  ],
  "outputs": [
    {
      "identifier": "RAW", 
      "title": "RAW output",
      "abstract": "RAW data",
      "format": "GEOTIFF"
    }
  ]
}
```

### Publish a Chain

```json
{
  "identifier": "Cosmo Skymed",
  "title": "CSK Standard Processing Model",
  "abstract": "This chain is a demostration example",
  "version": "0.1",
  "metadata": ["CSK", "Mission", "Chain"],
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


### Automatic Products Publication


## Discovering and Executing

### Discover

{{wps}}?service=WPS&request=getcapabilities
{{wps}}?service=WPS&request=describeprocess&version=1.0.0&identifier=L0

### Execute a Process

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<wps:Execute service="WPS" version="1.0.0" xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 ../wpsExecute_request.xsd">
  <ows:Identifier>L0</ows:Identifier>
  <wps:DataInputs>
    <wps:Input>
      <ows:Identifier>crude</ows:Identifier>
      <wps:Data>
        <wps:LiteralData>/mission/crude/crude1.sar</wps:LiteralData>
      </wps:Data>
    </wps:Input>
  </wps:DataInputs>
</wps:Execute>
```

### Execute a Chain

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<wps:Execute service="WPS" version="1.0.0" xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 ../wpsExecute_request.xsd">
  <ows:Identifier>Cosmo Skymed</ows:Identifier>
  <wps:DataInputs>
    <wps:Input>
      <ows:Identifier>crude</ows:Identifier>
      <wps:Data>
        <wps:LiteralData>/sar/data/acquisition.sar</wps:LiteralData>
      </wps:Data>
    </wps:Input>
  </wps:DataInputs>
</wps:Execute>
```

## Requesting Chain Executions Status

{{executions}}/executions
{{executions}}/executions?chain_identifier=Cosmo Skymed&order_by=start__desc
{{executions}}/executions?execution_id=41838c1c-4847-11e8-9afe-0242ac12000a

```json
{
  "count": 6,
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
      "id": 6,
      "execution_id": "551352d0-4847-11e8-9afe-0242ac12000a"
    }
  ]
}
```

## Discovering Automatically Published Products

{{repository}}/geoserver/csw

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


## TODO List

 * TBD
 
