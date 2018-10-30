from simplyrestful.settings import configure_from_module
configure_from_module('settings')
from simplyrestful.database import session
from models import (
    DataType, Format, RepositoryType, RepositorySetting, RepositoryTypeSetting, Repository, RepositoryConfiguration
)


# Repository types
geo_server = RepositoryType(name=RepositoryType.GEO_SERVER)
ftp = RepositoryType(name=RepositoryType.FTP)

# Repository settings
host = RepositorySetting(name=RepositorySetting.HOST)
username = RepositorySetting(name=RepositorySetting.USERNAME)
password = RepositorySetting(name=RepositorySetting.PASSWORD)
timeout = RepositorySetting(name=RepositorySetting.TIMEOUT)
protocol = RepositorySetting(name=RepositorySetting.PROTOCOL)
port = RepositorySetting(name=RepositorySetting.PORT)
path = RepositorySetting(name=RepositorySetting.PATH)
workspace = RepositorySetting(name=RepositorySetting.WORKSPACE)

# Repository type settings
geo_server_host = RepositoryTypeSetting(type=geo_server, setting=host, mandatory=True)
geo_server_username = RepositoryTypeSetting(type=geo_server, setting=username)
geo_server_password = RepositoryTypeSetting(type=geo_server, setting=password)
geo_server_protocol = RepositoryTypeSetting(type=geo_server, setting=protocol, mandatory=True)
geo_server_port = RepositoryTypeSetting(type=geo_server, setting=port, mandatory=True)
geo_server_path = RepositoryTypeSetting(type=geo_server, setting=path)
geo_server_workspace = RepositoryTypeSetting(type=geo_server, setting=workspace)
ftp_host = RepositoryTypeSetting(type=ftp, setting=host, mandatory=True)
ftp_username = RepositoryTypeSetting(type=ftp, setting=username, mandatory=True)
ftp_password = RepositoryTypeSetting(type=ftp, setting=password, mandatory=True)
ftp_timeout = RepositoryTypeSetting(type=ftp, setting=timeout, mandatory=True)
ftp_path = RepositoryTypeSetting(type=ftp, setting=path)

# Default repository
# TODO: The default repository will be removed someday
default_repository = Repository(
    type=geo_server,
    name='Default repository',
    configurations=[
        RepositoryConfiguration(type_setting=geo_server_host, value='repository'),
        RepositoryConfiguration(type_setting=geo_server_port, value='8080'),
        RepositoryConfiguration(type_setting=geo_server_protocol, value='http')
    ]
)


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

    geo_server,
    ftp,

    host,
    username,
    password,
    timeout,
    protocol,
    port,
    path,
    workspace,

    geo_server_host,
    geo_server_username,
    geo_server_password,
    geo_server_protocol,
    geo_server_port,
    geo_server_path,
    geo_server_workspace,
    ftp_host,
    ftp_username,
    ftp_password,
    ftp_timeout,
    ftp_path,

    default_repository
]


if __name__ == '__main__':
    try:
        session.add_all(objects)
        session.commit()
    except:
        session.rollback()
