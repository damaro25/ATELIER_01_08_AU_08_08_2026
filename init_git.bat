@echo off
chcp 65001 > nul
echo --------------------------------------------------
echo Initialisation et synchronisation Git en cours...
echo --------------------------------------------------

:: 1. Initialise le dépôt Git local dans votre dossier courant
git init

:: 2. Renomme la branche par défaut en "main"
git branch -M main

:: 3. Indexe tous vos fichiers
git add .

:: 4. Enregistre le premier instantané (snapshot)
git commit -m "Initial commit - Documents de travail RGPH-4"

:: 5. Connecte votre dépôt local à votre dépôt GitHub distant via SSH
git remote add origin git@github.com:damaro25/ATELIER_01_08_AU_08_08_2026.git

:: 6. Envoie votre code sur GitHub et définit "main" comme branche par défaut
git push -u origin main

echo --------------------------------------------------
echo Opération terminée avec succès !
echo --------------------------------------------------
pause