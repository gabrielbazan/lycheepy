# PyGPC Installation

## Dependencies Installation

### Operative System
    install ubuntu server 16.04 x64
        host: gpc
        user: gpc
        pass: gpc
    sudo apt-get update
    sudo apt-get install openssh-server
    sudo apt-get install vim

### Samba
    sudo apt-get install samba
    sudo smbpasswd -a gpc
        gpc
    mkdir /home/gpc/src
    sudo vim /etc/samba/smb.conf
    Add the following:
        [src]
        path = /home/gpc/src
        valid users = gpc
        read only = no
    sudo service smbd restart

### Git
    sudo apt-get install git

### Geoserver
    Install Java
        To uninstall first, follow: http://askubuntu.com/questions/84483/how-to-completely-uninstall-java
        sudo apt-get install software-properties-common
        sudo add-apt-repository ppa:webupd8team/java
        sudo apt-get update
        sudo apt-get install oracle-java8-installer
    Follow: http://docs.geoserver.org/latest/en/user/installation/linux.html
    
    INSTALL ALSO THE CSW EXTENSION:
        http://docs.geoserver.org/stable/en/user/services/csw/installing.html#csw-installing
        http://docs.geoserver.org/stable/en/user/services/csw/tutorial.html

    ENABLE CORS
        Edit the /usr/share/geoserver/webapps/geoserver/WEB-INF/web.xml file and uncomment where indicated. Search for :/CORS.
        Put the install\jetty-servlets-9.2.13.v20150730.jar file in the /usr/share/geoserver/webapps/geoserver/WEB-INF/lib folder.
## Supervisor
    sudo apt-get install supervisor
    cd /etc/supervisor/conf.d/
    sudo ln -s /home/gpc/src/pygpc/install/supervisord.conf .
    sudo mkdir /var/log/pygpc/
    sudo mkdir /var/log/pygpc/geoserver
    sudo supervisorctl reread > update > status

### PyWPS

#### Virtualenv
    sudo apt-get install python-pip python-dev build-essential
    sudo pip install virtualenv
    sudo pip install --upgrade pip

    sudo apt-get install python-gdal

    sudo apt-get install libxml2-dev libxslt1-dev

    cd
    virtualenv pywps-venv --system-site-packages
    cd pywps-venv
    source bin/activate
    pip install lxml
    git clone https://github.com/gabrielbazan/pywps.git
    cd pywps
    python setup.py install


## PyGPC Installation
  
### Install PostgreSQL and PostGIS
    sudo apt-get install -y postgresql postgresql-contrib
    sudo -u postgres psql postgres
    \password postgres
    Follow http://askubuntu.com/questions/423165/remotely-access-postgresql-database
    host    all        all         all                   md5

    sudo apt-get install -y postgis postgresql-9.5-postgis-2.2
    sudo -u postgres psql -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;" gpc


### REST API Installation
    
    sudo apt-get install binutils libproj-dev gdal-bin
    
    cd
    cd pywps-venv
    source bin/activate

    pip install -r ../src/PyGPC/requirements.txt

    cd
    cd src/PyGPC

    python manage.py makemigrations
    python manage.py migrate
    python manage.py createsuperuser

    python manage.py loaddata api/fixtures/fixtures.json
    