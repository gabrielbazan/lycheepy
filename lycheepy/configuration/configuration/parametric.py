from simplyrestful.settings import configure_from_module
configure_from_module('settings')
from simplyrestful.database import session
from models import DataType, Format


objects = [
    DataType(name='float'),
    DataType(name='boolean'),
    DataType(name='integer'),
    DataType(name='string'),
    DataType(name='positiveInteger'),
    DataType(name='anyURI'),
    DataType(name='date'),
    DataType(name='dateTime'),
    DataType(name='scale'),
    DataType(name='angle'),
    DataType(name='nonNegativeInteger'),
    Format(name='GEOJSON', mime_type='application/vnd.geo+json', extension='.geojson'),
    Format(name='JSON', mime_type='application/json', extension='.json'),
    Format(name='SHP', mime_type='application/x-zipped-shp', extension='.zip'),
    Format(name='GML', mime_type='application/gml+xml', extension='.gml'),
    Format(name='GEOTIFF', mime_type='image/tiff; subtype=geotiff', extension='.tiff'),
    Format(name='WCS', mime_type='application/xogc-wcs', extension='.xml'),
    Format(name='WCS100', mime_type='application/x-ogc-wcs; version=1.0.0', extension='.xml'),
    Format(name='WCS110', mime_type='application/x-ogc-wcs; version=1.1.0', extension='.xml'),
    Format(name='WCS20', mime_type='application/x-ogc-wcs; version=2.0', extension='.xml'),
    Format(name='WFS', mime_type='application/x-ogc-wfs', extension='.xml'),
    Format(name='WFS100', mime_type='application/x-ogc-wfs; version=1.0.0', extension='.xml'),
    Format(name='WFS110', mime_type='application/x-ogc-wfs; version=1.1.0', extension='.xml'),
    Format(name='WFS20', mime_type='application/x-ogc-wfs; version=2.0', extension='.xml'),
    Format(name='WMS', mime_type='application/x-ogc-wms', extension='.xml'),
    Format(name='WMS130', mime_type='application/x-ogc-wms; version=1.3.0', extension='.xml'),
    Format(name='WMS110', mime_type='application/x-ogc-wms; version=1.1.0', extension='.xml'),
    Format(name='WMS100', mime_type='application/x-ogc-wms; version=1.0.0', extension='.xml'),
    Format(name='TEXT', mime_type='text/plain', extension='.txt'),
    Format(name='NETCDF', mime_type='application/x-netcdf', extension='.nc'),
]


if __name__ == '__main__':
    try:
        session.add_all(objects)
        session.commit()
    except:
        session.rollback()
