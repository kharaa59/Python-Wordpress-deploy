"""
Le projet consiste à déployer automatiquement un serveur web sur lequel sera installé Wordpress
Pour cela, nous installerons :
- Apache2
    *Installation Apache
    *Stop, start et enable service
    *Test Apache2 est bien installé
- MariaDB
    *Installation mariadb-server & mariadb-client
    *Stop, start et enable service
    *Installation mysql_secure_installation
        *Enter current password for root (enter for none): Just press the Enter
        *Set root password? [Y/n]: Y
        *New password: Enter password
        *Re-enter new password: Repeat password
        *Remove anonymous users? [Y/n]: Y
        *Disallow root login remotely? [Y/n]: Y
        *Remove test database and access to it? [Y/n]:  Y
        *Reload privilege tables now? [Y/n]:  Y
    *Restart mariadb
- PHP7
    *Sur Ubuntu :
        *sudo apt-get install software-properties-common
        *sudo add-apt-repository ppa:ondrej/php
    *Installation php7.2 libapache2-mod-php7.2 php7.2-common php7.2-mbstring php7.2-xmlrpc php7.2-soap php7.2-gd php7.2-xml php7.2-intl php7.2-mysql php7.2-cli php7.2-zip php7.2-curl
    *Modifier php.ini :
        *file_uploads = On
        *allow_url_fopen = On
        *memory_limit = 256M
        *upload_max_filesize = 100M
        *max_execution_time = 360
        *date.timezone = America/Chicago
-Restart Apache2.service
- Wordpress
    *Création BD Wordpress
    *Download lastest WP version et installation
    *Ajouter les autorisations WP
- Configuration Apache2
- Autoriser WP et rewrite module sur Apache2
- Configuration WP

"""

import os


def updateApt():
    """Mise à jour de l'apt-get"""
    os.system('apt-get update')


def apt_get_install(package_list):
    """Téléchargement et installation des paquets demandés"""

    for package in package_list:
        os.system('apt-get install -y '+package)

def stateService(state, service_name):
    """Modification de l'état du service (start, restart, enable, stop...)"""
    os.system('systemctl '+state+' '+service_name)

class ApacheElem:
    def installApache(self):
        """Installation du service via l'apt-get"""
        apt_get_install(['apache2'])
    
    def startApache(self):
        """Démarrage du service"""
        stateService('start','apache2.service')
    


class PhpElem:
    def installPhp(self):
        """Installation du service PHP 7.2"""
        apt_get_install(['php7.2', 'libapache2-mod-php7.2', 'php7.2-common', 'php7.2-mbstring', 'php7.2-xmlrpc', 'php7.2-soap', 'php7.2-gd', 'php7.2-xml', 'php7.2-intl', 'php7.2-mysql', 'php7.2-cli', 'php7.2-zip', 'php7.2-curl'])

class MariaDbElem:
    def __init__(self, password):
        self.password = password
    def installMariaDb(self):
        """Installation du service via l'apt-get"""
        apt_get_install(['mariadb-server', 'mariadb-client'])
    
    def secureDataBase(self):
        """Initial DataBase configuration"""
        os.system('mysql --user=root <<_EOF_ \
        UPDATE mysql.user SET Password=PASSWORD("'+self.password+'") >HERE User="root"; \
        DELETE FROM mysql.user WHERE ser=""; \
        DELETE FROM mysql.user WHERE User="root" AND Host NOT IN ("localhost", "127.0.0.1", "::1"); \
        DROP DATABASE IF EXISTS test; \
        FLUSH PRIVILEGES; \
        _EOF_')

class WordpressElem:
    pass

