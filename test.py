import subprocess
import pip
import shutil
import pwd
import grp
try:
    import yaml
except ImportError:
    subprocess.call(['pip', 'install', 'pyyaml'])
    import yaml
try:
    import pymysql
except ImportError:
    subprocess.call(['pip', 'install', 'pymysql'])
    import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb

"""Définition des variables globales"""
CONFDATA = ""
 
        
def readYamlConfig():
    """Fonction de lecture du fichier YAML et vérification des erreurs"""
    with open('config.yaml','r') as configFile:
        try:
            global CONFDATA
            yamlData = yaml.load(configFile)
            CONFDATA = yamlData
        except yaml.YAMLError as exc:
            print(exc)
            sys.exit(1)
            

def updateApt():
    """Mise à jour de l'apt-get"""
    try:
        subprocess.call(['apt-get', 'update'], shell=True)
    except OSError:
        print ("Une erreur s'est produit lors de la mise à jour des paquets")


def apt_get_install(package_list):
    """Téléchargement et installation des paquets demandés"""

    for package in package_list:
        try:
            subprocess.call(['apt-get install -y '+package], shell=True)
        except (OSError) as e:
            print ("Une erreur s'est produit lors de l'installation du paquet "+package)
            print (e)

def stateService(state, service_name):
    """Modification de l'état du service (start, restart, enable, stop...)"""
    try:
        subprocess.call(['systemctl '+state+' '+service_name], shell=True)
    except (OSError) as e:
        print("Une erreur s'est produite lors de la modification d'état du service "+service_name)
        print (e)

class ApacheElem:
    def __init__(self, repository, paquets):
        self.repository = repository
        self.paquets = paquets
    def installApache(self):
        """Installation du service via l'apt-get"""
        apt_get_install(self.paquets)
    
    def startApache(self):
        """Démarrage du service"""
        stateService('start','apache2.service')
        
    def configurationApache(self):
        global CONFDATA
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
    def __init__(self, paquets):
        self.paquets = paquets
    def installPhp(self):
        """Installation du service PHP 7.2"""
        apt_get_install(self.paquets)
        
    def configurationPhp(self):
        phpIniTemplate= open("configuration_files/php.ini","r")
        phpIni= open("/etc/php/7.2/apache2/php.ini","w")
        phpIni.write(phpIniTemplate.read())
        phpIni.close()
        phpIniTemplate.close()

class MariaDbElem:
    def __init__(self, password, wpdb, wpuser, wppassword, paquets):
        self.password = password
        self.wpdb = wpdb
        self.wpuser = wpuser
        self.wppassword = wppassword
        self.paquets = paquets
                    
    def installMariaDb(self):
        """Installation du service via l'apt-get"""
        apt_get_install(self.paquets)
    
    def secureDataBase(self):
        """Initial DataBase configuration"""
        paramMysql = {
            "host" : "localhost",
            "user" : "root",
            "passwd" : self.password,
            "db" : "myBase",
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
        except (MySQLdb.Error) as e:
            print ("Error %d: %s" % (e.args[0],e.args[1]))
            sys.exit(1)
    
    def createWpDataBase(self):
        paramMysql = {
            "host" : "localhost",
            "user" : "root",
            "passwd" : self.password,
            "db" : "myBase",
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
        except (MySQLdb.Error) as e:
            print ("Error %d: %s" % (e.args[0],e.args[1]))
            sys.exit(1)

class WordpressElem:
    def __init__(self):
        self.documentRoot = documentRoot
        self.urlDl = urlDl
        self.fileName = fileName
    """Installation de Wordpress dans le dossier défini dans le dossier de configuration"""
    def downloadWp(self):
        try:
            os.mkdir(self.documentRoot)
        except OSError:
            print ("Creation of the directory %s failed" % path)
        try:
            os.chdir('/tmp')
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
            shutil.move('/tmp/wordpress', self.documentRoot+'/wordpress')
        except OSError:
            print("Une erreur s'est produite lors du déplacement du dossier Wordpress au répertoire défini")
        try:
            os.chown(self.documentRoot,pwd.getpwnam("www-data").pw_uid,grp.getgrnam("www-data:www-data").gr_gid)
            for root, dirs, files in os.walk(self.documentRoot):
                for d in dirs:
                    os.chmod(os.path.join(root, d), 755)
                for f in files:
                    os.chmod(os.path.join(root, f), 755)
        except OSError:
            print("Une erreur s'est produite lors de la modification des droits du dossier")



def main():
    readYamlConfig()
    print (CONFDATA)
    updateApt()
    apache = ApacheElem(CONFDATA['apache']['DocumentRoot'], CONFDATA['apache']['paquets'])
    apache.installApache()
    apache.startApache()
    mariaDb = MariaDbElem(CONFDATA['sql']['rootPassword'], CONFDATA['sql']['wordpressDbName'], CONFDATA['sql']['wordpressUser'], CONFDATA['sql']['wordpressUserPassword'], CONFDATA['sql']['paquets'])
    mariaDb.installMariaDb()
    
main()