@echo off
chcp 65001 > nul

:: 3. Indexe tous vos fichiers
git add .

:: 4. Enregistre le premier instantané (snapshot)
git commit -m "Agenda 2063 Union africaine"


:: 6. Envoie votre code sur GitHub et définit "main" comme branche par défaut
git push -u origin main

echo --------------------------------------------------
echo Opération terminée avec succès !
echo --------------------------------------------------
pause