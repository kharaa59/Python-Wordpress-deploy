import subprocess
import pip
import shutil
import pwd
import grp
import os
import tarfile
try:
    import wget
except ImportError:
    subprocess.call(['pip', 'install', 'wget'])
    import wget
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
    def __init__(self, repository, paquets, documentConfName):
        self.repository = repository
        self.paquets = paquets
        self.documentConfName = documentConfName
    def installApache(self):
        """Installation du service via l'apt-get"""
        apt_get_install(self.paquets)
    
    def startApache(self):
        """Démarrage du service"""
        stateService('start','apache2.service')
        
    def configurationApache(self):
        global CONFDATA
        """Modifier le fichier avec le fichier de conf avant de le copier"""
        try:
            apacheConfExample = open(CONFDATA['apache']['configurationFile'],"r")
        except:
            print('Impossible d\'ouvrir le fichier template indiqué')
            sys.exit(1)
        apacheConfVariable = apacheConfExample.read()
        apacheConfVariableModify = apacheConfVariable.replace('_SERVERNAME_',CONFDATA['apache']['ServerName']).replace('_SERVERALIAS_',CONFDATA['apache']['ServerAlias']).replace('_SERVERADMIN_',CONFDATA['apache']['ServerAdmin']).replace('_DOCUMENTROOT_',CONFDATA['apache']['DocumentRoot'])
        try:
            apacheConf = open("/etc/apache2/sites-available/"+self.documentConfName,"w+")
        except:
            print('Impossible d\'ouvrir le fichier apache indiqué')
        apacheConf.write(apacheConfVariableModify)
        apacheConfExample.close()
        apacheConf.close()
    
    def enableApacheConfiguration(self):
        try:
            print('a2ensite '+self.documentConfName)
            subprocess.call(['a2ensite '+self.documentConfName], shell=True)
        except OSError:
            print ("Une erreur s'est produit lors de l'autorisation du fichier de configuration Apache")
    


class PhpElem:
    def __init__(self, paquets):
        self.paquets = paquets
    def installPhp(self):
        """Installation du service PHP 7.2"""
        apt_get_install(['ca-certificates', 'apt-transport-https', 'lsb-release'])
        try:
            subprocess.call(['wget -O /etc/apt/trusted.gpg.d/php.gpg https://packages.sury.org/php/apt.gpg'],shell=True)
            subprocess.call(['echo "deb https://packages.sury.org/php/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/php.list'],shell=True)
        except OSError:
            print("Une erreur s'est produite lors de l'ajout du paquet d'installation")
        updateApt()
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
    

    def secureDbInstallation(self):
        """Sécurisation de la BD"""
        print(self.password)
        test = 'mysql -e "UPDATE mysql.user SET Password = PASSWORD(\''+self.password+'\') WHERE User = \'root\'"'
        print(test)
        try:
            subprocess.call([test],shell=True)
        except OSError:
            print("Une erreur s'est produite lors de la modification du compte root")
        try:
            subprocess.call(['mysql -e "DELETE FROM mysql.user WHERE user=\'root\' AND host NOT IN (\'localhost\', \'127.0.0.1\', \'::1\')"'],shell=True)
        except OSError:
            print("Une erreur s'est produite lors de la suppression des comptes anonymes")
        try:
            subprocess.call(['mysql -e "UPDATE mysql.user SET plugin=\'\' WHERE user=\'root\'"'],shell=True)
        except OSError:
            print("Une erreur s'est produite lors de la suppression des comptes anonymes")
        try:
            subprocess.call(['mysql -e "DELETE FROM mysql.user WHERE user=\'\'"'],shell=True)
        except OSError:
            print("Une erreur s'est produite lors de la suppression des comptes anonymes")
        try:
            subprocess.call(['mysql -e "DROP DATABASE test"'],shell=True)
        except OSError:
            print("Une erreur s'est produite lors de la suppression de la BDD test")
        try:
            subprocess.call(['mysql -e "FLUSH PRIVILEGES"'],shell=True)
        except OSError:
            print("Une erreur s'est produite lors de l'attribution des privilèges")


    
    def createWpDataBase(self):
        paramMysql = {
            "host" : "localhost",
            "user" : "root",
            "passwd" : self.password,
            "db" : "mysql",
        }
        queries = [
            'CREATE DATABASE IF NOT EXISTS '+self.wpdb+';',
            "CREATE USER "+self.wpuser+" IDENTIFIED BY '"+self.wppassword+"';",
            'GRANT ALL ON '+self.wpdb+'.* TO '+self.wpuser+' IDENTIFIED BY \''+self.wppassword+'\' WITH GRANT OPTION;',
            'FLUSH PRIVILEGES;']
        print(queries)
        
        try:
            conn = MySQLdb.connect(**paramMysql)
            cur = conn.cursor(MySQLdb.cursors.DictCursor)
            for querie in queries:
                cur.execute(querie)           
        except (MySQLdb.Error) as e:
            print ("Error %d: %s" % (e.args[0],e.args[1]))
            sys.exit(1)

class WordpressElem:
    def __init__(self, documentRoot, urlDl, fileName):
        self.documentRoot = documentRoot
        self.urlDl = urlDl
        self.fileName = fileName
    """Installation de Wordpress dans le dossier défini dans le dossier de configuration"""
    def downloadWp(self):
        tempDir = CONFDATA['wordpress']['tempDir']
        currentDir = os.getcwd()
        try:
            if not os.path.exists(self.documentRoot):
                os.mkdir(self.documentRoot)
        except OSError:
            print ("Creation of the directory %s failed" % path)
        try:
            os.chdir(tempDir)
        except OSError:
            print("Une erreur s'est produite lors de l'acces au dossier "+tempDir)
        try:
            wget.download(self.urlDl, tempDir+'/'+self.fileName)
        except :
            print("Une erreur s'est produite lors du téléchargement de Wordpress")
        try:
            tar = tarfile.open(tempDir+'/'+self.fileName, "r:gz")
            tar.extractall()
            tar.close()
        except :
            print("Une erreur s'est produite lors de l'extraction de Wordpress")
        try:
            files = os.listdir(tempDir+'/wordpress')
            for f in files:
                shutil.move(tempDir+'/wordpress/'+f, self.documentRoot)
        except OSError:
            print("Une erreur s'est produite lors du déplacement du dossier Wordpress au répertoire défini")
        try:
            os.chown(self.documentRoot,pwd.getpwnam("www-data").pw_uid,grp.getgrnam("www-data").gr_gid)
            os.chmod(self.documentRoot, 0o755)
            for root, dirs, files in os.walk(self.documentRoot):
                for d in dirs:
                    os.chmod(os.path.join(root, d), 0o755)
                    os.chown(os.path.join(root, d), pwd.getpwnam("www-data").pw_uid,grp.getgrnam("www-data").gr_gid)
                for f in files:
                    os.chown(os.path.join(root, f), pwd.getpwnam("www-data").pw_uid,grp.getgrnam("www-data").gr_gid)
                    os.chmod(os.path.join(root, f), 0o755)
        except OSError:
            print("Une erreur s'est produite lors de la modification des droits du dossier")
        try:
            os.chdir(currentDir)
        except OSError:
            print("Une erreur s'est produite lors de l'acces au dossier "+currentDir)



def main():
    readYamlConfig()
    print (CONFDATA)
    updateApt()
    apache = ApacheElem(CONFDATA['apache']['DocumentRoot'], CONFDATA['apache']['paquets'],CONFDATA['apache']['DocumentConfName'])
    apache.installApache()
    apache.startApache()
    mariaDb = MariaDbElem(CONFDATA['sql']['rootPassword'], CONFDATA['sql']['wordpressDbName'], CONFDATA['sql']['wordpressUser'], CONFDATA['sql']['wordpressUserPassword'], CONFDATA['sql']['paquets'])
    mariaDb.installMariaDb()
    mariaDb.secureDbInstallation()
    php = PhpElem(CONFDATA['php']['paquets'])
    php.installPhp()
    mariaDb.createWpDataBase()
    wordpress = WordpressElem(CONFDATA['apache']['DocumentRoot'], CONFDATA['wordpress']['url'], CONFDATA['wordpress']['fileName'])
    wordpress.downloadWp()
    apache.configurationApache()
    apache.enableApacheConfiguration()
    stateService('reload','apache2')
    
main()