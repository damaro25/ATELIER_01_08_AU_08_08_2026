/*==============================================================================
    RGPH4 GUINEE - QUESTIONNAIRE MENAGE ORDINAIRE
    SQUELETTE DE SYNTAXE STATA - RECODAGE DES VARIABLES
    Atelier : Recodage des variables et stabilisation des BDD (Groupe 1)
    Responsable atelier : Aly KOMAH

    RÈGLES DU GROUPE :
    - Ne jamais écraser une variable brute : toute variable recodée reçoit
      le suffixe _R (ex. P36 -> P36_R).
    - Chaque bloc de recodage est commenté (variable source, logique, auteur, date).
    - Vérifier systématiquement les effectifs avant/après (tab var, tab var_R)
      pour s'assurer qu'aucun cas n'est perdu ni mal classé.
    - Harmoniser le traitement des valeurs manquantes/NSP (souvent 8/9, 98/99,
      998/999 selon la longueur du champ dans le dictionnaire CSPro) -> .m ou .d
==============================================================================*/

capture log close
log using "recodage_RGPH4.log", replace text

use "ext_menage_ordinaire.dta", clear   // adapter le chemin/nom après export du CSPro

/*------------------------------------------------------------------------------
  1) NIVEAU D'INSTRUCTION (P36) -> NIVEAU D'INSTRUCTION AGREGE (P36_R)
     Modalités source (dictionnaire CSPro) :
     1 Préscolaire | 2 Primaire | 3 Collège | 4 Lycée
     5 Professionnel Technique A (sans BAC) | 6 Professionnel Technique B (avec BAC)
     7 Université
------------------------------------------------------------------------------*/
recode P36 (1 = 1 "Aucun/Préscolaire") (2 = 2 "Primaire") ///
           (3/4 = 3 "Secondaire (Collège/Lycée)") ///
           (5/6 = 4 "Technique/Professionnel") ///
           (7 = 5 "Supérieur") ///
           (else = .), gen(P36_R)
label variable P36_R "Niveau d'instruction (agrégé)"
tab P36 P36_R, missing

/*------------------------------------------------------------------------------
  2) AGE EN ANNEES REVOLUES (P05A) -> GRANDS GROUPES D'AGE (AGE5_R)
     P05A : numérique, 3 caractères, valeurs plausibles 0-134
------------------------------------------------------------------------------*/
gen AGE5_R = .
replace AGE5_R = 1 if inrange(P05A, 0, 4)
replace AGE5_R = 2 if inrange(P05A, 5, 14)
replace AGE5_R = 3 if inrange(P05A, 15, 24)
replace AGE5_R = 4 if inrange(P05A, 25, 34)
replace AGE5_R = 5 if inrange(P05A, 35, 44)
replace AGE5_R = 6 if inrange(P05A, 45, 54)
replace AGE5_R = 7 if inrange(P05A, 55, 64)
replace AGE5_R = 8 if P05A >= 65 & P05A < .
label define AGE5_R_L 1 "0-4 ans" 2 "5-14 ans" 3 "15-24 ans" 4 "25-34 ans" ///
                       5 "35-44 ans" 6 "45-54 ans" 7 "55-64 ans" 8 "65 ans et +"
label values AGE5_R AGE5_R_L
label variable AGE5_R "Grands groupes d'âge (5-14 puis 10 ans)"
tab AGE5_R, missing

/*------------------------------------------------------------------------------
  3) ETAT MATRIMONIAL (P60A) -> ETAT MATRIMONIAL AGREGE (P60A_R)
     1 Célibataire | 2 Marié(e) monogame | 3 Union libre monogame
     4 Marié(e) polygame | 5 Union libre polygame | 6 Veuf/veuve
     7 Séparé(e) | 8 Divorcé(e)
------------------------------------------------------------------------------*/
recode P60A (1 = 1 "Célibataire") ///
            (2/3 = 2 "Marié(e)/Union monogame") ///
            (4/5 = 3 "Marié(e)/Union polygame") ///
            (6 = 4 "Veuf/veuve") ///
            (7/8 = 5 "Séparé(e)/Divorcé(e)") ///
            (else = .), gen(P60A_R)
label variable P60A_R "État matrimonial (agrégé)"
tab P60A P60A_R, missing

/*------------------------------------------------------------------------------
  4) STATUT DANS LA PROFESSION (P57) -> STATUT AGREGE (P57_R)
     Regroupement indicatif salariat / indépendant / aide familial / autre
     -> À faire valider par le groupe avant application définitive
------------------------------------------------------------------------------*/
recode P57 (1/2 = 1 "Salarié (public/privé)") ///
           (3 = 2 "Employeur") ///
           (4/5 = 3 "Indépendant/à la tâche") ///
           (6/7 = 4 "Ouvrier qualifié/non qualifié") ///
           (8/10 = 5 "Coopérative/Apprenti/Stagiaire") ///
           (11 = 6 "Aide familial") ///
           (12 = 7 "Autre") ///
           (else = .), gen(P57_R)
label variable P57_R "Statut dans la profession (agrégé)"
tab P57 P57_R, missing

/*------------------------------------------------------------------------------
  5) VARIABLE "AUTRE, PRECISER" EN CLAIR (ex. H07_AUTRE, P13_AUTRE...)
     Ces variables alpha nécessitent un travail de RECLASSEMENT MANUEL :
     lister les modalités saisies en clair, les regrouper avec la nomenclature
     existante, puis recoder au cas par cas.
     Exemple générique (à adapter variable par variable) :
------------------------------------------------------------------------------*/
* contract H07_AUTRE, freq        // lister les réponses en clair les + fréquentes
* replace H07 = X if inlist(H07_AUTRE, "modalité déjà prévue mal saisie", ...)

/*------------------------------------------------------------------------------
  6) MODELE GENERIQUE A DUPLIQUER POUR CHAQUE NOUVELLE VARIABLE
------------------------------------------------------------------------------*/
* recode VARIABLE_SOURCE (ancien1/ancien2 = nouveau1 "Libellé 1") ///
*                        (ancien3       = nouveau2 "Libellé 2") ///
*                        (else = .), gen(VARIABLE_SOURCE_R)
* label variable VARIABLE_SOURCE_R "Description de la variable recodée"
* tab VARIABLE_SOURCE VARIABLE_SOURCE_R, missing

/*------------------------------------------------------------------------------
  CONTROLE QUALITE GLOBAL
------------------------------------------------------------------------------*/
foreach v of varlist P36_R AGE5_R P60A_R P57_R {
    di "=== `v' ==="
    tab `v', missing
}

save "ext_menage_ordinaire_recode.dta", replace
log close
