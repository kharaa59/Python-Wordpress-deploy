import subprocess
import MySQLdb
import yaml

"""Définition des variables globales"""
CONFDATA = ""


def readYamlConfig():
    """Fonction de lecture du fichier YAML et vérification des erreurs"""
    with open('config.yaml','r') as configFile:
        try:
            yamlData = yaml.load(configFile)
            global CONFDATA = yamlData
        except yaml.YAMLError as exc:
            print(exc)
            sys.exit(1)
            

def updateApt():
    """Mise à jour de l'apt-get"""
    try:
        subprocess.call(['apt-get update'])
    except OSError:
        print ("Une erreur s'est produit lors de la mise à jour des paquets")


def apt_get_install(package_list):
    """Téléchargement et installation des paquets demandés"""

    for package in package_list:
        try:
            subprocess.call(['apt-get install -y '+package])
        except OSError:
            print ("Une erreur s'est produit lors de l'installation du paquet "+package)

def stateService(state, service_name):
    """Modification de l'état du service (start, restart, enable, stop...)"""
    try:
        subprocess.call(['systemctl '+state+' '+service_name])
    except OSError:
        print("Une erreur s'est produite lors de la modification d'état du service "+service_name)

class ApacheElem:
    def __init__(self, repository)
        self.repository = repository
    def installApache(self):
        """Installation du service via l'apt-get"""
        apt_get_install(['apache2'])
    
    def startApache(self):
        """Démarrage du service"""
        stateService('start','apache2.service')
        
    def configurationApache(self):
        """Modifier le fichier avec le fichier de conf avant de le copier"""
        apacheConfExample = open("configuration_files/apache.example.com.conf","r")
        apacheConfVariable = apacheConfExample.read()
        apacheConfVariableModify = apacheConfVariable.replace('_SERVERNAME_',CONFDATA['apache']['ServerName']).replace('_SERVERALIAS_',CONFDATA['apache']['ServerAlias']).replace('_SERVERADMIN_',CONFDATA['apache']['ServerAdmin']).replace('_DOCUMENTROOT_',CONFDATA['apache']['DocumentRoot'])
        apacheConf = open("/etc/apache2/sites-available/"+self.repository,"w")
        apacheConf.write(apacheConfVariableModify)
        apacheConfExample.close()
        apacheConf.close()
    
    def enableApacheConfiguration(self):
        try:
            subprocess.call(['a2ensite '+self.repository+'.conf'])
        except OSError:
            print ("Une erreur s'est produit lors de l'autorisation du fichier de configuration Apache")
    


class PhpElem:
    def installPhp(self):
        """Installation du service PHP 7.2"""
        apt_get_install(['php7.2', 'libapache2-mod-php7.2', 'php7.2-common', 'php7.2-mbstring', 'php7.2-xmlrpc', 'php7.2-soap', 'php7.2-gd', 'php7.2-xml', 'php7.2-intl', 'php7.2-mysql', 'php7.2-cli', 'php7.2-zip', 'php7.2-curl'])
        
    def configurationPhp(self):
        phpIniTemplate= open("configuration_files/php.ini","r")
        phpIni= open("/etc/php/7.2/apache2/php.ini","w")
        phpIni.write(phpIniTemplate.read())
        phpIni.close()
        phpIniTemplate.close()

class MariaDbElem:
    def __init__(self, password, wpdb, wpuser, wppassword):
        self.password = password
        self.wpdb = wpdb
        self.wpuser = wpuser
        self.wppassword = wppassword
    def installMariaDb(self):
        """Installation du service via l'apt-get"""
        apt_get_install(['mariadb-server', 'mariadb-client'])
    
    def secureDataBase(self):
        """Initial DataBase configuration"""
        paramMysql = {
            "host" = "localhost",
            "user" = "root",
            "passwd" = self.password,
            "db" = "myBase",
        }
        query = "ALTER USER CURRENT_USER() IDENTIFIED BY '"+paramMysql['passwd']+"'; \
        DELETE FROM mysql.user WHERE User=""; \
        DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1'); \
        DROP DATABASE IF EXISTS test; \
        FLUSH PRIVILEGES; \
        EXIT"

        try:
            conn = MySQLdb.connect(**paramMysql)
            cur = conn.cursor(MySQLdb.cursors.DictCursor)
            cur.execute(query)
        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0],e.args[1])
            sys.exit(1)
    
    def createWpDataBase(self):
        paramMysql = {
            "host" = "localhost",
            "user" = "root",
            "passwd" = self.password,
            "db" = "myBase",
        }
        query = "CREATE DATABASE "+self.wpdb+"; \
        CREATE USER '"+self.wpuser+"'@'localhost' IDENTIFIED BY "+self.wppassword+"; \
        GRANT ALL ON "+self.wpdb+".* TO '"+self.wpuser+"'@'localhost' IDENTIFIED BY '"+self.wppassword+"' WITH GRANT OPTION; \
        FLUSH PRIVILEGES; \
        EXIT"
        
        try:
            conn = MySQLdb.connect(**paramMysql)
            cur = conn.cursor(MySQLdb.cursors.DictCursor)
            cur.execute(query)
        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0],e.args[1])
            sys.exit(1)

class WordpressElem:
    def __init__(self):
        self.documentRoot = documentRoot
        self.urlDl = urlDl
        self.fileName = fileName
    """Installation de Wordpress dans le dossier défini dans le dossier de configuration"""
    def downloadWp(self):
        try:
            subprocess.call(['mkdir '+self.documentRoot])
        except OSError:
            print("Un erreur s'est produite lors de la création du dossier Wordpress")
        try:
            subprocess.call(['cd /tmp'])
        except OSError:
            print("Une erreur s'est produite lors de l'acces au dossier /tmp")
        try:
            subprocess.call(['wget '+self.urlDl])
        except OSError:
            print("Une erreur s'est produite lors du téléchargement de Wordpress")
        try:
            subprocess.call(['tar -xvzf '+self.fileName])
        except OSError:
            print("Une erreur s'est produite lors de l'extraction de Wordpress")
        try:
            subprocess.call(['mv wordpress '+self.documentRoot])
        except OSError:
            print("Une erreur s'est produite lors du déplacement du dossier Wordpress au répertoire défini")
        try:
            subprocess.call(['chown -R www-data:www-data '+self.documentRoot])
            subprocess.call(['chown -R 755 '+self.documentRoot])
        except OSError:
            print("Une erreur s'est produite lors de la modification des droits du dossier")

