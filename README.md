# Projet 7 - Implémentez un modèle de scoring
***

Projet 7 de la formation Data Scientist dispensée par OpenClassRooms.


## But du projet : 
***

Le but du projet est de développer un dashboard interactif fournissant un score d'accord de prêt pour les clients

Le projet est décomposé en deux parties :
1) Construire un modèle de scoring qui donnera une prédiction sur la probabilité de faillite d'un client de façon automatique.
   - nettoyage des données issues de kaggle
   - resampling sur jeu de données déséquilibré
   - création d'un modèle de machine learning prédisant le score d'un client (accordé ou refusé)

2) Construire un dashboard interactif à destination des gestionnaires de la relation client permettant d'interpréter les prédictions faites par le modèle, et d’améliorer la connaissance client des chargés de relation client.
   - mise en place d'une API Flask retournant le score du client
   - création d'un dashboard avec Flask
   - déploiement de l'API et du dashboard sur Heroku, via git
   

## Compétences évaluées :
***

- Présenter son travail de modélisation à l'oral
- Réaliser un dashboard pour présenter son travail de modélisation
- Rédiger une note méthodologique afin de communiquer sa démarche de modélisation
- Utiliser un logiciel de version de code pour assurer l’intégration du modèle
- Déployer un modèle via une API dans le Web


## Données :
***

Les données proviennent du site de kaggle : https://www.kaggle.com/c/home-credit-default-risk/data

La partie feature engineering est issue de : https://www.kaggle.com/jsaguiar/lightgbm-with-simple-features


