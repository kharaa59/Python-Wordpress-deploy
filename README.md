# Python-Wordpress-deploy

Ce projet a pour but de déployer automatiquement un environnement Apache2 et PHP7.2 ainsi que l'installation d'un serveur Wordpress.
Ce script est prévu pour fonctionnement sous un environnement Debian 9.


## Pour commencer

* Télécharger le dossier via :  
`1. HTTP : [https://github.com/kharaa59/Python-Wordpress-deploy.git]`  
`2. Git : git clone https://github.com/kharaa59/Python-Wordpress-deploy.git` depuis votre dossier de travail 
* Completer le fichier config.yaml avec les différentes informations demandées :
`1. Les informations de configuration Apache` 
`2. Les informations de configuration de la base de données SQL` 
`3. Facultatif : Les informations de téléchargement Wordpress` 


### Pré-requis

* Python version 3 ou supérieur
`apt-get install python3` 
* Pip3 version 19.2.1 ou supérieur
`apt-get install python3-pip` 
`pip3 install --upgrade pip` 
* Modules Python Wget, Pyyaml, Pymysql
`pip3 install wget` 
`pip3 install pyyaml` 
`pip3 install pymysql` 
* Droit sudo


### Installation

Pour lancer le déploiement du script,


`sudo python3 test.py`


## Vérification de l'installation

Afin de vérifier le bon fonctionnement de l'installation :
* `Lancer un navigateur web` 
* `Se rendre sur IP_MACHINE/wordpress` , la page d'accueil Wordpress doit alors s'ouvrir


## Langages

* [Python3](https://www.python.org/)


## Break down

Afin de stopper le script en cas de rencontre d'erreurs, des breakdown ont été mis en place :

* 1 : Impossible de lire le fichier YAML
* 2 : Erreur lors de la mise à jour du gestion de paquets
* 3 : Erreur lors de l’installation des composants
* 4 : Erreur lors de la lecture du fichier template de configuration apache
* 5 : Erreur lors de l'ouverture du fichier apache du système
* 6 : Erreur lors de la modification de l’autorisation du fichier de configuration apache
* 7 : Erreur lors de l'ajout des paquets d’installation php
* 8 : Erreur lors de la sécurisation de la base de données
* 9 : Erreur lors de la connexion à la base de données
* 10 : Erreur lors de la création du dossier wordpress
* 11 : Erreur lors du téléchargement des fichies Wordpress
* 12 : Erreur lors de l’extraction du dossier Wordpress
* 13 : Erreur lors du déplacement du dossier Wordpress
* 14 : Erreur lors de la modification des droits sur le dossier Wordpress
* 15 : Erreur lors du changement de dossier système


## Versioning

Ce script est en version 1.0

## Auteurs

* **Anthony DOMMERY** - *Travail initial* - [kharaa59](https://github.com/kharaa59)


## Licence

Ce projet est sous licence Apache version 2.0 - voir le fichier [LICENCE](LICENCE) pour plus de détail