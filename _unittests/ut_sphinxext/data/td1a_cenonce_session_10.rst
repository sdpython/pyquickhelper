
.. _td1acenoncesession10rst:

TD 10 : DataFrame et Matrice
============================

**Links:**

    * :download:`notebook <td1a_cenonce_session_10.ipynb>`
    * :download:`html <td1a_cenonce_session_10.html>`
    * :download:`PDF <td1a_cenonce_session_10.pdf>`
    * :download:`python <td1a_cenonce_session_10.py>`

**Notebook:**

Les `DataFrame <http://en.wikipedia.org/wiki/Data_frame>`__ se sont
imposés pour manipuler les données. Avec cette façon de représenter les
données, associée à des un ensemble de méthodes couramment utilisées, ce
qu'on faisait en une ou deux boucles se fait maintenant en une seule
fonction. Cette séance contient beaucoup d'exemples et peu d'exercices.
Il est conseillé de supprimer toutes les sorties et de les exécuter une
à une.
**Plan**

-  `Trouver chaussure à ses stats <#intro>`__
-  `DataFrame (pandas) <#df>`__

   -  `création / lecture / écriture <#io>`__
   -  `index <#index>`__
   -  `Notation avec le symbole : <#ix>`__
   -  `Exercice 1 : créer un fichier Excel <#exo1>`__

-  `Manipuler un DataFrame <#df2>`__

   -  `6 opérations : filtrer, union, sort, group by, join,
      pivot <#op>`__

   -  `Exercice 2 <#exo2>`__

-  `Dates <#date>`__
-  `Matrix, Array (numpy) <#mat>`__

   -  `création / lecture / écriture <#mat>`__
   -  `DataFrame/Matrix/Array <#diff>`__

-  `Calcul matriciel <#mat2>`__

   -  `Exercice 3 <#exo3>`__

-  `Annexes <#annex>`__

   -  `Créer un fichier Excel avec plusieurs feuilles <#excel>`__

L'introduction ne contient pas d'éléments nécessaires à la réalisation
du TD.

.. raw:: html

   <h2 id="intro">

Trouver chaussure à ses stats

.. raw:: html

   </h2>

La programmation est omni-présente lorsqu'on manipule des données. On
leur applique des traitements parfois standards, souvent adaptés pour la
circonstance. On souhaite toujours programmer le moins possible mais
aussi ne pas avoir à réapprendre un langage à chaque fois qu'on doit
manipuler les données.
Le logiciel `MATLAB <http://www.mathworks.fr/products/matlab/>`__ a
proposé voici 30 ans un premier environnement de travail facilitant le
calcul matriciel et ce standard s'est imposé depuis. Comme *MATLAB* est
un logiciel payant, des équivalents open source et gratuits ont été
développés. Ils proposent tous le calcul matriciel, la possibilité de
visualiser, un environnement de développement. Ils différent pas des
performances différentes et des éventails d'extensions différentes.
-  `R <http://www.r-project.org/>`__ : la référence pour les
   statisticiens, il est utilisé par tous les chercheurs dans ce
   domaine.
-  `SciLab <http://www.scilab.org/fr>`__ : développé par
   l'\ `INRIA <http://www.inria.fr/>`__.
-  `Octave <http://www.gnu.org/software/octave/>`__ : clone open source
   de *MATLAB*, il n'inclut pas autant de librairies mais il est
   gratuit.
-  `Julia <http://julialang.org/>`__ : c'est le plus jeune, il est plus
   rapide mais ses librairies sont moins nombreuses.

Ils sont tous performants en qui concerne le calcul numérique, ils le
sont beaucoup moins lorsqu'il s'agit de faire des traitements qui ne
sont pas numériques (traiter du texte par exemple) car ils n'ont pas été
prévus pour cela à la base (à l'exception de Julia peut être qui est
plus jeune `Python v. Clojure v.
Julia <http://matthewrocklin.com/blog/work/2014/01/13/Text-Benchmarks>`__).
Le langage Python est devenu depuis 2012 une alternative intéressante
pour ces raisons (voir également `Why
Python? <http://www.xavierdupre.fr/blog/2014-07-11_nojs.html>`__) :
-  Il propose les même fonctionnalités de base (calcul matriciel,
   graphiques, environnement).
-  Python est plus pratique pour tout ce qui n'est pas numérique
   (fichiers, web, server web, SQL, ...).
-  La plupart des librairies connues et écrites en C++ ont été portée
   sous Python.
-  Il est plus facile de changer un composant important en Python (numpy
   par exemple) si le nouveau est plus efficace.

Un inconvénient peut-être est qu'il faut installer plusieurs extensions
avant de pouvoir commencer à travailler. Vous pouvez soit utiliser la
distribution `WinPython <http://winpython.sourceforge.net/>`__ ou
installer les modules suivants (avant leurs dépendances) :
-  `numpy <http://www.numpy.org/>`__ : calcul matriciel
-  `pandas <http://pandas.pydata.org/>`__ : DataFrame
-  `ipython <http://ipython.org/>`__ : notebooks (comme celui-ci)
-  `matplotlib <http://matplotlib.org/>`__ : graphiques
-  `scikit-learn <http://scikit-learn.org/stable/>`__ : machine
   learning, statistique descriptive

Optionnels :
-  `ggplot <http://ggplot.yhathq.com/>`__ : extension très populaire sur
   *R* et portée sur Python
-  `Spyder <https://code.google.com/p/spyderlib/>`__ : environnement
   type R, MATLAB, ...
-  `scipy <http://www.scipy.org/>`__ : autres traitements numériques
   (voir `NumPy vs. SciPy vs. other
   packages <http://www.scipy.org/scipylib/faq.html#what-is-the-difference-between-numpy-and-scipy>`__)
-  `cvxopt <http://cvxopt.org/>`__ : optimisation quadratique sous
   contrainte
-  `Pillow <https://pypi.python.org/pypi/Pillow>`__ : traitement d'image
-  `PyQt4 <https://wiki.python.org/moin/PyQt4>`__ : interface graphique
-  `openpyxl <http://pythonhosted.org/openpyxl/>`__ : lecture/écriture
   de fichir Excel

Les environnements Python évoluent très vite, les modules mentionnés ici
sont tous maintenus mais il eut en surgir de nouveau très rapidement.
Quelques environnements à suivre :
-  `PyTools <http://pytools.codeplex.com/>`__ : environnement de
   développement pour Visual Studio
-  `PyCharm <http://www.jetbrains.com/pycharm/>`__ : n'inclut pas les
   graphiques mais est assez agréable pour programmer
-  `IEP <http://www.iep-project.org/index.html>`__ : écrit en Python
-  `PyDev <http://pydev.org/>`__ : extension pour
   `Eclipse <http://www.eclipse.org/>`__

Si vous ne voulez pas programmer, il existe des alternatives. C'est
assez performant sur de petits jeux de données mais cela devient plus
complexe dès qu'on veut programmer car le code doit tenir compte des
spécificités de l'outil.
-  `Orange <http://orange.biolab.si/>`__ : écrit en Python
-  `Weka <http://www.cs.waikato.ac.nz/ml/weka/>`__ : écrit en Java (le
   pionnier)
-  `RapidMiner <http://rapidminer.com/>`__ : version gratuite et payante

C'est parfois plus pratique pour commencer mais mal commode si on veut
automatiser un traitrment pour répéter la même tâche de façon régulière.
Pour les travaux pratiques à l'ENSAE, jai choisi les
`notebook <http://ipython.org/notebook.html>`__ : c'est une page blanche
où on peut mélanger texte, équations, graphiques, code et exécution de
code.

.. raw:: html

   <h2 id="df">

DataFrame (pandas)

.. raw:: html

   </h2>

Un `Data Frame <http://en.wikipedia.org/wiki/Data_frame>`__ est un objet
qui est présent dans la plupart des logiciels de traitements de données,
c'est une **matrice**, chaque colonne est de même type (nombre, dates,
texte), elle peut contenir des valeurs manquantes. On peut considérer
chaque colonne comme les variables d'une table
(`pandas.Dataframe <http://pandas.pydata.org/pandas-docs/dev/generated/pandas.DataFrame.html>`__)

::

    import pandas

    l = [ { "date":"2014-06-22", "prix":220.0, "devise":"euros" },
          { "date":"2014-06-23", "prix":221.0, "devise":"euros" },]

    df = pandas.DataFrame(l)
    df

.. raw:: html

    <div style="max-height:1000px;max-width:1500px;overflow:auto;">

    <table border="1" class="dataframe">
      <thead>

        <tr style="text-align: right;">
          <th></th>

          <th>date</th>
          <th>devise</th>

          <th>prix</th>
        </tr>

      </thead>
      <tbody>

        <tr>
          <th>0</th>

          <td> 2014-06-22</td>
          <td> euros</td>

          <td> 220</td>
        </tr>

        <tr>
          <th>1</th>

          <td> 2014-06-23</td>
          <td> euros</td>

          <td> 221</td>
        </tr>

      </tbody>
    </table>

    <p>2 rows × 3 columns</p>
    </div>

Avec une valeur manquante :

::

    l = [ { "date":"2014-06-22", "prix":220.0, "devise":"euros" },

          { "date":"2014-06-23", "devise":"euros"  },]
    df = pandas.DataFrame(l)

    df

.. raw:: html

    <div style="max-height:1000px;max-width:1500px;overflow:auto;">

    <table border="1" class="dataframe">
      <thead>

        <tr style="text-align: right;">
          <th></th>

          <th>date</th>
          <th>devise</th>

          <th>prix</th>
        </tr>

      </thead>
      <tbody>

        <tr>
          <th>0</th>

          <td> 2014-06-22</td>
          <td> euros</td>

          <td> 220</td>
        </tr>

        <tr>
          <th>1</th>

          <td> 2014-06-23</td>
          <td> euros</td>

          <td> NaN</td>
        </tr>

      </tbody>
    </table>

    <p>2 rows × 3 columns</p>
    </div>

`NaN <http://docs.scipy.org/doc/numpy/reference/generated/numpy.isnan.html#numpy.isnan>`__
est une convention pour une valeur manquante. On extrait la variable
``prix`` :

::

    df.prix

.. parsed-literal::

    0    220

    1    NaN
    Name: prix, dtype: float64

Ou :

::

    df["prix"]

.. parsed-literal::

    0    220

    1    NaN
    Name: prix, dtype: float64

Pour extraire plusieurs colonnes :

::

    df [["date","prix"]]

.. raw:: html

    <div style="max-height:1000px;max-width:1500px;overflow:auto;">

    <table border="1" class="dataframe">
      <thead>

        <tr style="text-align: right;">
          <th></th>

          <th>date</th>
          <th>prix</th>

        </tr>
      </thead>

      <tbody>
        <tr>

          <th>0</th>
          <td> 2014-06-22</td>

          <td> 220</td>
        </tr>

        <tr>
          <th>1</th>

          <td> 2014-06-23</td>
          <td> NaN</td>

        </tr>
      </tbody>

    </table>
    <p>2 rows × 2 columns</p>

    </div>

.. raw:: html

   <h3 id="io">

Lecture et écriture de DataFrame

.. raw:: html

   </h3>

Aujourd'hui, on n'a plus besoin de réécrire soi-même une fonction de
lecture ou d'écriture de données présentées sous forme de tables. Il
existe des fonctions plus génériques qui gère un grand nombre de cas.
Cette section présente brièvement les fonctions qui permettent de
lire/écrire un DataFrame aux formats texte/Excel. On reprend l'exemple
de section précédente. L'instruction ``encoding=utf-8`` n'est pas
obligatoire mais conseillée lorsque les données contiennent des accents
(voir
`read\_csv <http://pandas.pydata.org/pandas-docs/stable/generated/pandas.io.parsers.read_csv.html>`__).

::

    import pandas

    l = [ { "date":"2014-06-22", "prix":220.0, "devise":"euros" },
          { "date":"2014-06-23", "prix":221.0, "devise":"euros" },]

    df = pandas.DataFrame(l)

    # écriture au format texte
    df.to_csv("exemple.txt",sep="\t",encoding="utf-8", index=False)

    # on regarde ce qui a été enregistré

    with open("exemple.txt", "r", encoding="utf-8") as f : text = f.read()
    print(text)

    # on enregistre au format Excel

    df.to_excel("exemple.xlsx", index=False)

    # on ouvre Excel sur ce fichier (sous Windows)
    from pyquickhelper import run_cmd

    out,err = run_cmd("exemple.xlsx", wait = False)

.. parsed-literal::

    date	devise	prix

    2014-06-22	euros	220.0
    2014-06-23	euros	221.0

On peut récupérer des données directement depuis Internet ou une chaîne
de caractères et afficher le début
(`head <pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.head.html>`__)
ou la fin
(`tail <pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.tail.html>`__)
:

::

    import pandas, io

    from pyquickhelper import get_url_content
    text = get_url_content("http://www.xavierdupre.fr/enseignement/complements/marathon.txt")

    df = pandas.read_csv(io.StringIO(text), sep="\t",
                            names=["ville", "annee", "temps","secondes"])

    df.head()

.. raw:: html

    <div style="max-height:1000px;max-width:1500px;overflow:auto;">

    <table border="1" class="dataframe">
      <thead>

        <tr style="text-align: right;">
          <th></th>

          <th>ville</th>
          <th>annee</th>

          <th>temps</th>
          <th>secondes</th>

        </tr>
      </thead>

      <tbody>
        <tr>

          <th>0</th>
          <td> PARIS</td>

          <td> 2011</td>
          <td> 02:06:29</td>

          <td> 7589</td>
        </tr>

        <tr>
          <th>1</th>

          <td> PARIS</td>
          <td> 2010</td>

          <td> 02:06:41</td>
          <td> 7601</td>

        </tr>
        <tr>

          <th>2</th>
          <td> PARIS</td>

          <td> 2009</td>
          <td> 02:05:47</td>

          <td> 7547</td>
        </tr>

        <tr>
          <th>3</th>

          <td> PARIS</td>
          <td> 2008</td>

          <td> 02:06:40</td>
          <td> 7600</td>

        </tr>
        <tr>

          <th>4</th>
          <td> PARIS</td>

          <td> 2007</td>
          <td> 02:07:17</td>

          <td> 7637</td>
        </tr>

      </tbody>
    </table>

    <p>5 rows × 4 columns</p>
    </div>

.. raw:: html

   <h3 id="index">

DataFrame et Index

.. raw:: html

   </h3>

On désigne généralement une colonne ou *variable* par son nom. Les
lignes peuvent être désignées par un entier.

::

    import pandas

    l = [ { "date":"2014-06-22", "prix":220.0, "devise":"euros" },
          { "date":"2014-06-23", "prix":221.0, "devise":"euros" },]

    df = pandas.DataFrame(l)
    df

.. raw:: html

    <div style="max-height:1000px;max-width:1500px;overflow:auto;">

    <table border="1" class="dataframe">
      <thead>

        <tr style="text-align: right;">
          <th></th>

          <th>date</th>
          <th>devise</th>

          <th>prix</th>
        </tr>

      </thead>
      <tbody>

        <tr>
          <th>0</th>

          <td> 2014-06-22</td>
          <td> euros</td>

          <td> 220</td>
        </tr>

        <tr>
          <th>1</th>

          <td> 2014-06-23</td>
          <td> euros</td>

          <td> 221</td>
        </tr>

      </tbody>
    </table>

    <p>2 rows × 3 columns</p>
    </div>

On extrait une ligne
(`ix <http://pandas.pydata.org/pandas-docs/dev/generated/pandas.DataFrame.ix.html>`__)
:

::

    df.ix[1]

.. parsed-literal::

    date      2014-06-23

    devise         euros
    prix             221

    Name: 1, dtype: object

Mais il est possible d'utiliser une colonne ou plusieurs colonnes comme
index
(`set\_index <http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.set_index.html>`__)
:

::

    dfi = df.set_index("date")

    dfi

.. raw:: html

    <div style="max-height:1000px;max-width:1500px;overflow:auto;">

    <table border="1" class="dataframe">
      <thead>

        <tr style="text-align: right;">
          <th></th>

          <th>devise</th>
          <th>prix</th>

        </tr>
        <tr>

          <th>date</th>
          <th></th>

          <th></th>
        </tr>

      </thead>
      <tbody>

        <tr>
          <th>2014-06-22</th>

          <td> euros</td>
          <td> 220</td>

        </tr>
        <tr>

          <th>2014-06-23</th>
          <td> euros</td>

          <td> 221</td>
        </tr>

      </tbody>
    </table>

    <p>2 rows × 2 columns</p>
    </div>

On peut maintenant désigner une ligne par une date :

::

    dfi.ix["2014-06-23"]

.. parsed-literal::

    devise    euros

    prix        221
    Name: 2014-06-23, dtype: object

Il est possible d'utiliser plusieurs colonnes comme index :

::

    df = pandas.DataFrame([ {"prénom":"xavier", "nom":"dupré", "arrondissement":18},

           {"prénom":"clémence", "nom":"dupré", "arrondissement":15 } ])
    dfi = df.set_index(["nom","prénom"])

    dfi.ix["dupré","xavier"]

.. parsed-literal::

    arrondissement    18

    Name: (dupré, xavier), dtype: int64

Si on veut changer l'index ou le supprimer
(`reset\_index <http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.reset_index.html>`__)
:

::

    dfi.reset_index(drop=False, inplace=True)

            # le mot-clé drop pour garder ou non les colonnes servant d'index
            # inplace signifie qu'on modifie l'instance et non qu'une copie est modifiée

            # donc on peut aussi écrire dfi2 = dfi.reset_index(drop=False)
    dfi.set_index(["nom", "arrondissement"],inplace=True)

    dfi

.. raw:: html

    <div style="max-height:1000px;max-width:1500px;overflow:auto;">

    <table border="1" class="dataframe">
      <thead>

        <tr style="text-align: right;">
          <th></th>

          <th></th>
          <th>prénom</th>

        </tr>
        <tr>

          <th>nom</th>
          <th>arrondissement</th>

          <th></th>
        </tr>

      </thead>
      <tbody>

        <tr>
          <th rowspan="2" valign="top">dupré</th>

          <th>18</th>
          <td>   xavier</td>

        </tr>
        <tr>

          <th>15</th>
          <td> clémence</td>

        </tr>
      </tbody>

    </table>
    <p>2 rows × 1 columns</p>

    </div>

.. raw:: html

   <h3 id="ix">

Notation avec le symbole ``:``

.. raw:: html

   </h3>

Le symbole ``:`` désigne une plage de valeur.

::

    import pandas, io

    from pyquickhelper import get_url_content
    text = get_url_content("http://www.xavierdupre.fr/enseignement/complements/marathon.txt")

    df = pandas.read_csv(io.StringIO(text), sep="\t",
                            names=["ville", "annee", "temps","secondes"])

    df.head()

.. raw:: html

    <div style="max-height:1000px;max-width:1500px;overflow:auto;">

    <table border="1" class="dataframe">
      <thead>

        <tr style="text-align: right;">
          <th></th>

          <th>ville</th>
          <th>annee</th>

          <th>temps</th>
          <th>secondes</th>

        </tr>
      </thead>

      <tbody>
        <tr>

          <th>0</th>
          <td> PARIS</td>

          <td> 2011</td>
          <td> 02:06:29</td>

          <td> 7589</td>
        </tr>

        <tr>
          <th>1</th>

          <td> PARIS</td>
          <td> 2010</td>

          <td> 02:06:41</td>
          <td> 7601</td>

        </tr>
        <tr>

          <th>2</th>
          <td> PARIS</td>

          <td> 2009</td>
          <td> 02:05:47</td>

          <td> 7547</td>
        </tr>

        <tr>
          <th>3</th>

          <td> PARIS</td>
          <td> 2008</td>

          <td> 02:06:40</td>
          <td> 7600</td>

        </tr>
        <tr>

          <th>4</th>
          <td> PARIS</td>

          <td> 2007</td>
          <td> 02:07:17</td>

          <td> 7637</td>
        </tr>

      </tbody>
    </table>

    <p>5 rows × 4 columns</p>
    </div>

On peut sélectionner un sous-ensemble de lignes :

::

    df[3:6]

.. raw:: html

    <div style="max-height:1000px;max-width:1500px;overflow:auto;">

    <table border="1" class="dataframe">
      <thead>

        <tr style="text-align: right;">
          <th></th>

          <th>ville</th>
          <th>annee</th>

          <th>temps</th>
          <th>secondes</th>

        </tr>
      </thead>

      <tbody>
        <tr>

          <th>3</th>
          <td> PARIS</td>

          <td> 2008</td>
          <td> 02:06:40</td>

          <td> 7600</td>
        </tr>

        <tr>
          <th>4</th>

          <td> PARIS</td>
          <td> 2007</td>

          <td> 02:07:17</td>
          <td> 7637</td>

        </tr>
        <tr>

          <th>5</th>
          <td> PARIS</td>

          <td> 2006</td>
          <td> 02:08:03</td>

          <td> 7683</td>
        </tr>

      </tbody>
    </table>

    <p>3 rows × 4 columns</p>
    </div>

On extrait la même plage mais avec deux colonnes seulement :

::

    df.ix[3:6,["annee","temps"]]

.. raw:: html

    <div style="max-height:1000px;max-width:1500px;overflow:auto;">

    <table border="1" class="dataframe">
      <thead>

        <tr style="text-align: right;">
          <th></th>

          <th>annee</th>
          <th>temps</th>

        </tr>
      </thead>

      <tbody>
        <tr>

          <th>3</th>
          <td> 2008</td>

          <td> 02:06:40</td>
        </tr>

        <tr>
          <th>4</th>

          <td> 2007</td>
          <td> 02:07:17</td>

        </tr>
        <tr>

          <th>5</th>
          <td> 2006</td>

          <td> 02:08:03</td>
        </tr>

        <tr>
          <th>6</th>

          <td> 2005</td>
          <td> 02:08:02</td>

        </tr>
      </tbody>

    </table>
    <p>4 rows × 2 columns</p>

    </div>

Le même code pour lequel on renomme les colonnes extraites :

::

    sub = df.ix[3:6,["annee","temps"]]

    sub.columns = ["year","time"]
    sub

.. raw:: html

    <div style="max-height:1000px;max-width:1500px;overflow:auto;">

    <table border="1" class="dataframe">
      <thead>

        <tr style="text-align: right;">
          <th></th>

          <th>year</th>
          <th>time</th>

        </tr>
      </thead>

      <tbody>
        <tr>

          <th>3</th>
          <td> 2008</td>

          <td> 02:06:40</td>
        </tr>

        <tr>
          <th>4</th>

          <td> 2007</td>
          <td> 02:07:17</td>

        </tr>
        <tr>

          <th>5</th>
          <td> 2006</td>

          <td> 02:08:03</td>
        </tr>

        <tr>
          <th>6</th>

          <td> 2005</td>
          <td> 02:08:02</td>

        </tr>
      </tbody>

    </table>
    <p>4 rows × 2 columns</p>

    </div>

.. raw:: html

   <h3 id="exo1">

Exercice 1 : créer un fichier Excel

.. raw:: html

   </h3>

On souhaite récupérer les données
`marathon.txt <http://www.xavierdupre.fr/enseignement/complements/marathon.txt>`__,
les indexer selon la ville et l'année puis sauve le tout au format
Excel.

::

    import pandas, io

    # ...
.. raw:: html

   <h2 id="df2">

Manipuler un DataFrame

.. raw:: html

   </h2>

Si la structure *DataFrame* s'est imposée, c'est parce qu'on effectue
toujours les mêmes opérations. Chaque fonction cache une boucle ou deux
dont le coût est précisé en fin de ligne :
-  **filter** : on sélectionne un sous-ensemble de lignes qui vérifie
   une condition :math:`\rightarrow O(n)`
-  **union** : concaténation de deux jeux de données
   :math:`\rightarrow O(n_1 + n_2)`
-  **sort** : tri :math:`\rightarrow O(n \ln n)`
-  **group by** : grouper des lignes qui partagent une valeur commune
   :math:`\rightarrow O(n)`
-  **join** : fusionner deux jeux de données en associant les lignes qui
   partagent une valeur commune
   :math:`\rightarrow \in [O(n_1 + n_2), O(n_1 n_2)]`
-  **pivot** : utiliser des valeurs présent dans colonne comme noms de
   colonnes :math:`\rightarrow O(n)`

Les 5 premières opérations sont issues de la logique de manipulation des
données avec le langage
`SQL <http://fr.wikipedia.org/wiki/Structured_Query_Language>`__ (ou le
logiciel `SAS <http://www.sas.com>`__). La dernière correspond à un
`tableau croisé
dynamique <http://fr.wikipedia.org/wiki/Tableau_crois%C3%A9_dynamique>`__.

.. raw:: html

   <h3 id="op">

6 opérations : filtrer, union, sort, group by, join, pivot

.. raw:: html

   </h3>
