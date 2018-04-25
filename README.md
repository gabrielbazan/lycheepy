# LycheePy

Lychee is a distributed, easy to scale, processing server of geo-spatial data.

It allows you to: 
 * Publish pre-defined processing chains through a WPS interface. By doing so, users are abstracted about the chains complexity, because they do not have to build them each time they want to chain processes. From the consumer users perspective, a chain is just another process.
 * Automatize geo-spatial data publication through repositories, such as GeoServer, FTP servers, or any other kind of repository.
 * Easily scale. LycheePy is a distributed system. Worker nodes are the ones which provide the processing capabilities and execute processes, and you can add or remove as many you require. Also, LycheePy will concurrently execute processes when it is applicable to the chain's topology.


## Architecture

### Development View

The development architecture focuses on the software organization into modules. The software is divided into little packages or subsystems which can be developed by small development teams, and they are organized on a layers hierarchy, where each one of them provide a well-defined interface.

Each component responsibilities need to be very well delimited, so there is only one reason for it to change. This way, any change on the system will affect only component only.

Having their responsibilities and interfaces well defined, any component may be replaced with another implementation without affecting the others, and they may be reused for other developments.

When exists a dependency between a component, and interfaces of another component, then the first should use a Gateway, which encapsulates the interaction with those interfaces. This way, any change on those interfaces will only affect the Gateway and, ideally, not the component which uses the gateway.

![Alt text](doc/architecture/development_view.png?raw=true "LycheePy components diagram.")

On this view, we are able to distinguish 13 components, being 5 of them Gateways. The LycheePy development components are:

* **WPS**: An implementation of the OGC WPS standard, which exposes the _WPS I_ interface, through which is able to able to retrieve discovery and execution requests of processes and chains. It depends on the _Configuration Gateway_ component in order to know the metadata of every available executables (processes and chains) available. Also depends on the _Executor_ component in order to delegate executions.
* **Configuration Gateway**: A component which encapsulates the interaction with the _Configuration I_ interface, of the _Configuration_ component.
* **Configuration**: A component which exposes the _Configuration I_ interface, trough which it is possible to add, modify, and delete processes and chains. It requires some kind of persistence in order to store this configurations. Uses the _Processes Gateway_ in order to store and delete processes.
* **Executor**: A component which encapsulates the execution of chains and processes. Depends on the _Broker Gateway_ in order to enqueue processes executions, and on the _Executions Gateway_ in order to inform the executions status.
* **Executions Gateway**: A component which encapsulates the interaction whit the _Executions I_ interface, of the _Executions_ component.
* **Executions**: A component which persists the status of all the chains executions. It exposes the _Executions I_ interface, through which it is possible tu update or read those statuses.
* **Broker Gateway**: A component which encapsulates all the interaction whith the _Messages Queue_ interface, of the _Broker_ component. Trough this component, it is possible to enqueue tasks.
* **Broker**: A component which is capable of receive tasks and store them on a queue. It ensures that those will be executed in the same order they where enqueued.
* **Worker**: A component which consumes tasks from the _Mesages Queue_ interface, and executes them. It depends on the _Processes Gateway_ in order to obtain the processes to execute them, and ond the _Repository Gateway_ in order to perform geospatial data automatic publication.
* **Processes Gateway**: A component which encapsulates the interaction with the _Processes I_ interface, of the _Processes_ component.
* **Processes**: A component which stores the files of those processes available on the server.
* **Repository Gateway**: A component which encapsulates the interaction with the _Repository I_ interface, of the _Repository_ component.
* **Repository**: A component capable of storing geospatial data. It exposes a configuration interface, _Repository I_, and _OWS_ interfaces.


### Physical View

The physical architecture is the mapping between the software and the hardware. It takes into account non-funcional requirements, such as availability, fault tolerance, performance, and scalability. The software its executed on a computers network (nodes).

The design of the development components have been carried out takign into account their capability to be distributed across different nodes on a network, searching for the maximum flexibility and taking full advantage of the distributed processing, making the system horizontally scalable.

The deployment of the software can be carried out taking into account acount a maximum disgregation, and a minimum disgregation. Between this two extremes, exist many intermediate combinations. 

The minimum disgregation, represented below, consists of deloying all the development components into the same node. This is a completely centralized schema, and it does not perform distributed processing, but there may be the possibiblity of perform paralell processing if the container's processor has multiple cores. It also carries with all the disvantages of a centralized system.

![Alt text](doc/architecture/physical_view_minimum.png?raw=true "LycheePy minimum disgregation.")

On the maximum disgregation, represented below, all the development components, except gateways, are deployed on a dedicated node, plus a proxy and the necessary persistence components. This schema carries with all the advantages of a distributed system:
1. We can increase (or reduce) each nodes capabilities, according to our needs.
1. We can horizontally scale the processing capabilities, adding more Worker nodes.
1. As a consecuence of some nodes failure, it may not result on a complete unavailability. Of course, it depends on which component fails: For example, if we had multiple Worker nodes, and one of them fails, the processing capability decreases and the chains execution may be slower, but all the system's functionalities will still work; while if the Broker component fails, then we have lost the capability of execute processes and chains, but the system will still be able to attend discovery operations, the products will still be accessible by the users, and so on. Whatever is the case, the recovery to this any kind of failure should be faster, because the problem is isolated and it is easier tho identify and resolve, or to replace the node.

![Alt text](doc/architecture/physical_view_maximum.png?raw=true "LycheePy maximum disgregation.")


## Implementation



## Deployment



## Static Configuration



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
 
