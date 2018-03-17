FROM ubuntu:16.04

# Add Geoserver configuration file
ADD web.xml /root/

# Upgrade
RUN apt-get update && apt-get upgrade -y

# Install Java
RUN apt-get install -y software-properties-common debconf-utils
RUN add-apt-repository ppa:webupd8team/java
RUN apt-get update
RUN echo "oracle-java8-installer shared/accepted-oracle-license-v1-1 select true" | debconf-set-selections
RUN apt-get install -y oracle-java8-installer

# Install Geoserver
RUN apt-get install -y wget unzip
RUN wget https://razaoinfo.dl.sourceforge.net/project/geoserver/GeoServer/2.12.2/geoserver-2.12.2-bin.zip -O geoserver.zip
RUN mkdir -p /usr/share/geoserver
RUN unzip geoserver.zip -d /usr/share/geoserver
RUN echo "export GEOSERVER_HOME=/usr/share/geoserver" >> ~/.profile
RUN . ~/.profile
RUN chown -R root /usr/share/geoserver/

# Install CSW extension
RUN wget https://ufpr.dl.sourceforge.net/project/geoserver/GeoServer/2.12.2/extensions/geoserver-2.12.2-csw-plugin.zip -O csw.zip
RUN unzip -o csw.zip -d /usr/share/geoserver/geoserver-2.12.2/webapps/geoserver/WEB-INF/lib

# Enable CORS
RUN rm /usr/share/geoserver/geoserver-2.12.2/webapps/geoserver/WEB-INF/web.xml
RUN mv /root/web.xml /usr/share/geoserver/geoserver-2.12.2/webapps/geoserver/WEB-INF/

# Start Geoserver
CMD cd /usr/share/geoserver/geoserver-2.12.2/bin/ && sh startup.sh
