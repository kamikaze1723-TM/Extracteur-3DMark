# Extracteur 3DMark

Extracteur 3DMark est une application open-source permettant de lire et d'extraire rapidement les données des fichiers de résultats 3DMark (`.3dmark-result`). L'application génère un résumé propre des performances (CPU, GPU, Températures, Fréquences, Scores) et permet de l'exporter en PDF, avec des graphiques détaillés de vos sessions de benchmark.

## Fonctionnalités

- **Extraction Intelligente** : Importation et analyse de fichiers `.3dmark-result` et `.zip`.
- **Drag & Drop** : Glissez-déposez simplement votre fichier directement dans la fenêtre de l'application.
- **Analyse Matérielle** : Détection complète du matériel (CPU, GPU, RAM, Carte Mère, BIOS, OS, API, etc.).
- **Graphiques Intégrés** : Visualisez l'évolution de vos FPS, charge GPU, températures et fréquences directement dans l'interface, avec un rendu fluide et lisible.
- **Historique Local** : L'application sauvegarde vos résultats localement, vous permettant de suivre l'évolution de vos performances dans le temps via la fenêtre d'Historique.
- **Export PDF Avancé** : Générez en un clic un rapport PDF complet incluant vos informations matérielles, vos scores, ainsi que vos graphiques de performance.
- **Bilingue** : Interface disponible en Français et en Anglais.
- **Interface Moderne et Personnalisable** : 
  - Thèmes Clair et Sombre (Dark Mode).
  - Barre de titre sur mesure sans bordure (Frameless) avec gestion native du glissement et du "magnétisme" Windows (Aero Snap).
  - Support de l'Immersive Dark Mode natif de Windows 11.

## Captures d'écran
<p align="center">
  <img src="assets/app_empty.png" alt="Interface vide">
  <br>
  <i>L'application prête à analyser vos fichiers.</i>
</p>

<p align="center">
  <img src="assets/app_data.png" alt="Interface chargée">
  <br>
  <i>L'interface principale affichant les données extraites d'un benchmark.</i>
</p>

<p align="center">
  <img src="assets/pdf_export.png" alt="Export PDF">
  <br>
  <i>Exemple du rapport PDF généré automatiquement.</i>
</p>

## Installation et Utilisation
Vous pouvez installer l'application complète via l'exécutable d'installation disponible dans le dossier des releases de ce projet.

1. Téléchargez `Install_Extracteur_3DMark.exe`.
2. Lancez l'installateur et suivez les instructions.
3. Lancez "Extracteur 3DMark" depuis votre bureau ou menu démarrer.

## Compilation depuis le code source
Si vous souhaitez compiler l'application vous-même :
1. Assurez-vous d'avoir Python 3.x installé (ainsi que `pip`).
2. Installez les dépendances :
   ```cmd
   pip install -r requirements.txt
   ```
3. (Optionnel) Pour créer l'installateur complet, installez Inno Setup et exécutez :
   ```cmd
   python build.py
   ```

## Licence
Ce projet est distribué sous la licence **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**.
Vous êtes libre d'utiliser, de modifier et de distribuer ce logiciel pour des projets personnels ou open-source, **à condition de respecter ces deux règles absolues :**
1. **Pas d'utilisation commerciale** : Interdiction absolue de vendre ou monétiser ce logiciel ou son code.
2. **Mention obligatoire de l'auteur** : Vous devez explicitement créditer l'auteur originel (`Kamikaze_TM`) en cas de réutilisation ou de modification.
