
================================
File d'attente, un petit exemple
================================

*Psychokinèse, les ampoules grillent à distance*

.. contents::
    :local:

Petite histoire
===============

Cet énoncé s'inspire du livre
`Devenez sorciers, devenez savants <https://fr.wikipedia.org/wiki/Devenez_sorciers,_devenez_savants>`_
de Georges Charpak et Henri Broch dont est tiré l'extrait suivant.

    Le présentateur se tourne vers la caméra principale, et d'un air
    très sérieux et enjôleur, regarde le téléspectateur droit dans les
    yeux en déclarant : *Allez-y ! Allumez cinq ou six lampes à côté de vous.*
    Puis il se tourne vers le médium et demande :
    *Vous pensez réellement pouvoir le faire ?*
    Après quelques moments d'hésitation, le mage se prononce :
    *J'espère avoir suffisamment de concentration ce soir, mais je ne suis pas
    dans les conditions vraiment idéales ; pour produire ce genre de phénomène
    à distance, d'habitude, je me retire pendant plusieurs jours
    dans une solitude totale et une profonde obscurité, après un jeûne strict.*

    Si jamais il échoue, le public le mettra au compte des
    circonstances et non pas de ces compétences. Et, pourtant,
    le médium n'échoue pas. Des ampoules grillent chez les téléspectateurs
    qui regardent cette émission. Ils font part au standard téléphonique
    de la chaîne qui diffuse en direct cet extraordinaire moment de culture.
    Le médium a donc bien réussi - comme il le prétendait -, en concentrant sa
    puissance spirituelle sur la matière, à griller des ampoules électriques à distance.

    Supposons que cette émission soit suivie par environ un million de
    téléspectateurs et qu'elle dure une heure ou plus. Cela signifie
    qu'environ cinq à six millions d'ampoules ont été allumées pendant
    une heure ou plus. Supposons que ce nombre soit de deux millions.

    La durée de vie moyenne d'une ampoule à incandescence est de
    mille heures. Ce qui signifie que, pendant la durée de l'émission,
    il y aura environ deux milles lampes grillées.

Un peu de théorie
=================

Ce problème ressemble à un problème de files d'attente. Ce dernier
consiste à déterminer un nombre adéquat de guichets en fonction de
la vitesse de remplissage d'une file d'attente afin de limiter le
temps d'attente. On désigne souvent cette problématique par un sigle
du type :math:`M/M/S`. Le premier :math:`M` signifie qu'on suppose que la
probabilité que :math:`n` personnes arrivent pendant une durée :math:`t`
suit une loi de Poisson de paramètre :math:`\lambda t`.
Le second :math:`M` signifie qu'on suppose que le temps de
traitement d'une personne par un guichetier suit une loi exponentielle de
paramètre :math:`\mu`. :math:`S` désigne le nombre de guichets. Pour de
tels problèmes, on cherche à déterminer la probabilité que le
système (file d'attente + guichets) contienne :math:`n` personnes.
De cette probabilité, on peut déduire par exemple le temps d'attente
moyen pour une personne qui entre dans la file d'attente. On
suppose que le système est stationnaire, les probabilités ne dépendent
pas du temps.

.. mathdef::
    :title: loi de Poisson et loi exponentielle
    :tag: Définition

    Si une variable :math:`X` suit une loi de Poisson de
    paramète :math:`\lambda t`, elle a pour densité :

    .. math::
        :nowrap:

        \begin{eqnarray}
        \pr{X = n} &=&  \frac{(\lambda t)^n}{n!} \; e^{-\lambda t}
        \end{eqnarray}

    Si une variable :math:`X` suit une loi exponentielle de paramètre :math:`\mu`, elle a pour densité :

    .. math::
        :nowrap:

        \begin{eqnarray}
        f(t) &=& \mu  \; e^{- \mu t} \text{ et } \pr {X \infegal t} =
                    \int_0^t \mu  \; e^{- \mu x} dx = 1 - e^{-\mu t}
        \end{eqnarray}

File d'attente, cas M/M/1
-------------------------

.. index:: M/M/1

On s'intéresse d'abord à un système :math:`M/M/1`. Il n'y a donc qu'un
seul guichet. :math:`\lambda` est le nombre moyen d'arrivée par unité
de temps tandis que :math:`\mu` est le nombre moyen de clients
traités par unité de temps. On suppose également que :math:`\lambda < \mu`.
Dans le cas contraire, la file d'attente devient infinie. On désigne par
:math:`p_n(t)` la probabilité que la file d'attente contiennent
:math:`n` personne. Que vaut cette probabilité à l'instant :math:`t + dt` ?

On considère que pendant la durée :math:`t + dt`, au plus une personne
peut s'ajouter à la file d'attente et au plus une personne peut
être traitée par un guichetier. Les autres cas sont négligeables.
On désigne par :math:`B(x,t,dt)` le fait qu'une personne quitte
un guichet pendant les instants :math:`t` et :math:`t+dt` sachant
qu'elle est arrivée au guichet à l'instant :math:`x`. On cherche à
déterminer la probabilité :math:`\pr{B(x,t,dt)}`. On peut dire aussi
que :math:`\pr{B(x,t,dt}` est la probabilité que le temps de traitement
d'une personne est inférieur à :math:`t+dt-x` sachant qu'il est
supérieur à :math:`t-x`. Si :math:`D` est une variable de durée
suivant une loi exponentielle, alors :

.. math::
    :label: mu_dt_eq
    :nowrap:

    \begin{eqnarray}
    \pr{B(x,t,dt)} &=& \pr{ D \infegal t+dt-x \sac D > t-x }
                                = \frac{ \pr{  t+dt-x \supegal D > t-x } } { \pr{ D > t-x }} \\
                                &=& \frac{ \int_{t-x}^{t+dt-x} \mu e^{-\mu u} du } { \int_{t-x}^{\infty} \mu e^{-\mu u} du }
                                = \frac{ e^{- \mu (t-x) } - e^{- \mu (t-x+dt) } } { e^{-\mu (t-x) }} \\
                                &=& 1 - e^{- \mu dt}   \\
    \pr{B(x,t,dt)}	&=& - \mu dt + o(dt)
    \end{eqnarray}									

Cette probabilité ne dépend ni de :math:`x`, ni de :math:`t`.
En ce qui concerne les arrivées, la probabilité qu'une personne arrive
pendant les instants :math:`t` et :math:`t+dt` ne dépend pas du
passé et suit une loi de Poisson de paramètre :math:`\lambda`.
Cette constation et l'équation (:eq:`mu_dt_eq`) nous permettent d'écrire que :

.. math::
    :label: amp_dt_2
    :nowrap:

    \begin{eqnarray}
    \pr{ \text{une personne arrive pendant } dt } &=& \lambda dt \; e^{-\lambda dt} \sim \lambda dt + o(dt) \\
    \pr{ \text{une personne part pendant } dt } &=& 1 - e^{-\mu dt} \sim \mu dt + o (dt)
    \end{eqnarray}

De plus, pendant la durée :math:`dt`, quatre cas sont possibles :

* Une personne peut arriver sans qu'aucune ne parte d'un guichet.
* Une personne peut partir d'un guichet sans qu'aucune autre n'arrive.
* Une personne peut arriver et une autre partir d'un guichet.
* Aucune personne n'arrive et aucune ne part d'un guichet.

Ces quatre cas permettent d'écrire la relation suivante :

.. math::
    :label: amp_dt_3
    :nowrap:

    \begin{eqnarray}
    p_n(t+dt) &=&  p_{n-1}(t) \; \lambda dt + \\
                            && p_{n+1}(t) \; \mu dt + \\
                            && p_n(t) \pa{  \mu dt \lambda dt} + \\
                            && p_n(t) \pa { 1 - \mu dt} \pa{ 1 - \lambda dt}
    \end{eqnarray}

On néglige les termes du second degré en :math:`(dt)^2` :		
		
.. math::
    :nowrap:

    \begin{eqnarray}
    p_n(t+dt) &=& p_{n-1}(t) \; \lambda dt + p_{n+1}(t) \; \mu dt +
                                p_n(t) \pa { 1 - \mu dt - \lambda dt } \\
    \Longleftrightarrow \frac{ p_n(t+dt) - p_n (t)} {dt} &=& \lambda  p_{n-1}(t) + \mu p_{n+1}(t)   -
                                \pa { \mu  + \lambda  }  p_n(t)
    \end{eqnarray}
		
Cette relation n'est vraie que lorsque :math:`n > 0`, lorsque
:math:`n = 0`, aucune personne déjà présente ne peut
être traitée par un guichetier, on a donc :

.. math::

    \frac{ p_0(t+dt) - p_0 (t)} {dt} &=& \mu p_{1}(t)  - \lambda   p_0(t)

Comme le système est stationnaire, toutes les dérivées sont
nulles. Les probabilités ne dépendent pas du temps. Ceci donne les
relations suivantes :

.. math::
    :nowrap:
    :label: systeme_mm1

    \begin{eqnarray}
    && 	\left \{ \begin{array}{lll}
            \lambda  p_{n-1} + \mu p_{n+1}   - \pa { \mu  + \lambda  }  p_n &=& 0 \\
            \mu p_1  -   \lambda    p_0 &=& 0
            \end{array}\right. \\
    \Longleftrightarrow && 	\left \{ \begin{array}{lll}
             \mu p_{n+1} &=&      \pa { \mu  + \lambda  }  p_n - \lambda \; p_{n-1} \\
            \mu p_1  &=& 	 \lambda    p_0
            \end{array}\right.
    \end{eqnarray}
		
On vérifie par récurrence que :

.. math::
    :nowrap:

    p_n = \pa{\frac{\lambda}{\mu}}^n p_0
		
Il reste à déterminer :math:`p_0`. Or, comme
:math:`\sum_0^{\infty} p_n = 1 = p_0 \; \sum_0^{\infty} \pa{\frac{\lambda}{\mu}}^n`,
on obtient que :

.. math::
    :nowrap:

    \frac{p_0}{ 1 - \frac{\lambda}{\mu}} = 1 \Longleftrightarrow p_0 = 1 - \frac{\lambda}{\mu}
		
*Exemple :*

On suppose qu'un médecin traite en moyenne quatre patients par heure
tandis qu'il accepte trois rendez-vous par heure. Donc
:math:`\lambda = 3` et :math:`\mu = 4`. Le nombre moyen
:math:`\overline{n}` de patients dans sa salle d'attente
est donné par :

.. math::
    :nowrap:

    \begin{eqnarray}
    \overline{n} &=&  \sum_0^{\infty} n p_n =
                     \pa{1 - \frac{\lambda}{\mu} }  \sum_0^{\infty} n \pa{\frac{\lambda}{\mu}}^n
                    =  \frac{ \frac{\lambda}{\mu} } { 1 - \frac{\lambda}{\mu} }= \frac{\lambda}{\mu - \lambda }
    \end{eqnarray}
			
Il y a donc en moyenne trois personnes dans la salle d'attente de ce
médecin. Comme le temps moyen de traitement de chacun est
:math:`\frac{1}{\mu}`, le temps moyen d'attente d'un patient
arrivant dans la salle d'attente est
:math:` \frac{\lambda \mu}{\mu - \lambda } :math:`. Ce temps est égal à
trois quarts d'heure pour cet exemple.
				
File d'attente, cas M/M/S
-------------------------

.. index:: M/M/S
		
Le système contient dorénavant :math:`S` guichets, on suppose que la vitesse
:math:`\mu` de traitement des clients est commune à tous les
guichets. On cherche tout d'abord la probabilité qu'une
personne s'en aille parmi les :math:`k` qui occupent un guichet. On désigne par
:math:`\vecteur{D_1}{D_k}` :math:`k` variables indépendantes suivant une loi
exponentielle de paramètre :math:`\mu`, pendant un temps :math:`dt`,
la probabilité qu'une personne parmi :math:`k` quitte un guichet est :

.. math::
    :nowrap:

    \begin{eqnarray}
    \pr{ \min \ensemble{D_1}{D_k} \infegal dt } &=& 1 - \pr {\min \ensemble{D_1}{D_k} > dt} \\
    &=& 1 - \cro{\prody{n=1}{k} \pr {D_n > dt}} \\
    &=& 1 - \cro{\prody{n=1}{k} 1 - \pr {D_n \infegal dt}} \\
    &=& 1 - \cro{\prody{n=1}{k}  e^{-\mu dt}} \\
    &=& 1 - e^{- k\mu dt} \sim k \mu dt + o(dt)
    \end{eqnarray}

Pour déterminer les probabilités :math:`\pa{p_n}_n`, on applique le
même raisonnement que pour un système :math:`M/M/1` en distinguant
les cas :math:`n \infegal S` et :math:`n > S`. On adapte la récurrence
donnée par le système d'équations (:eq:`systeme_mm1`) au cas :math:`M/M/S` :

.. math::
    :nowrap:
    :label: system_mms

    \begin{eqnarray}
    && 	\left \{ \begin{array}{lll}
            \mu p_1  -   \lambda    p_0 &=& 0  \\
            \lambda  p_{n-1} + \pa{n+1} \mu p_{n+1}   - \pa {n \mu  + \lambda  }  p_n &=& 0 \text{ si } 1 \infegal n < S \\
            \lambda  p_{n-1} + S \mu p_{n+1}   - \pa { S \mu  + \lambda  }  p_n &=& 0 \text{ si } n \supegal S
            \end{array}\right.
    \end{eqnarray}

On suppose que :math:`\frac{\lambda}{S \mu} < 1` afin que la file d'attente
ne devienne infinie. Comme pour un système :math:`M/M/1`, ces formules de
récurrences et le fait que :math:`\sum_0^{\infty} p_n = 1`
permet de déduire que :

.. math::
    :nowrap:
		
    \begin{eqnarray}
    \left\{ \begin{array}{lll}
    p_0 &=&  \dfrac{1}{ \frac{  \pa{\frac{\lambda}{\mu}}^S   }  { S! \pa { 1 - \frac{\lambda}{S \mu}} }
                                            + \summy{k=1}{S-1} \frac{  \pa{ \frac{\lambda}{\mu}}^n }{ n!}
                                    } \\ \\
    p_n &=& \dfrac{1}{n!} \; \pa{\dfrac{\lambda}{\mu}}^n  p_0 \quad \text{ si } n < S \\ \\
    p_n &=& \dfrac{1}{S^{n-S} S!} \; \pa{\dfrac{\lambda}{\mu}}^n  p_0 \quad \text{ si } n \supegal S
                    \end{array} \right.
    \end{eqnarray}

Ces calculs sont utilisés pour optimiser le nombre de guichets.
Chaque guichetier a un coût qui doit être comparé avec le coût associé au
temps d'attente des clients. Ces résultats sont extraits du livre [Faure2000]_.

    La théorie des files d'attente remonte aux premiers travaux de K. Erlang (1917),
    sur le calcul du nombre d'organes de chaque type à installer dans un central téléphonique
    automatique. Développée aussi par Engset (1918), cette théorie s'est amplifiée
    sous l'impulsion de nombreux chercheurs (E. Borel, D. Kendall, A. Kolmogorov,
    Khintchine, LC. Palm, F. Pollaczek, L. Feller, ...). Les informaticiens l'utilisent
    notamment pour l'évaluation de performances, à titre prévisionnel, des systèmes
    ou des réseaux informatiques.

Retour aux ampoules
-------------------

La durée de traitement d'un client fait penser à la durée de vie
d'une ampoule. Les lampes font office de guichets tandis que le rôle des
clients est joué par des lumières. Toutefois, ce n'est pas le temps
d'attente moyen ni la longueur moyenne de la file d'attente qui nous
intéresse mais, en quelque sorte, le nombre de clients qui sont traités
pendant une durée :math:`T`. En fait, plus exactement, c'est le nombre
de guichets qui auront traités au moins un client pendant une durée
:math:`T` qui nous intéresse. Il correspond exactement au nombre d'ampoules
qui vont griller pendant cette même période :math:`T`. Il reste à définir
ce qu'est une file d'attente d'ampoules et surtout son paramètre :math:`\lambda`.

Lorsqu'une ampoule grille, elle est a priori changée dans les plus brefs
délais, comme si la file d'attente des ampoules était infinie. Ceci
signifie que :math:`\lambda >> \mu`, configuration qui sort du champ
d'application des files d'attente :math:`M/M/S`. Le paramètre
:math:`\lambda` n'a a priori aucun rôle à jouer. On peut néanmoins
s'inspirer de la méthode développée dans les paragraphes précédants pour
aborder le problème des ampoules.

On suppose que la durée de vie d'une ampoule suit toujours une loi exponentielle
de paramètre :math:`\mu` et qu'il y en a exactement :math:`S`
qui brillent en même temps. On note :math:`p_n(t)` la probabilité que
:math:`n` ampoules aient grillées à l'instant :math:`t`.
Si :math:`N(t)` est le nombre d'ampoules grillées à l'instant :math:`t` :
:math:`p_n(t) = \pr{ N(t) = n}`. Cette fonction n'est plus stationnaire
et décroît avec le temps à partir d'un certain moment. Plus on avance dans le
temps, plus le nombre d'ampoules grillées augmente. Par conséquent, la
probabilité qu'il y ait :math:`n` ampoules grillées augmente tout d'abord puis,
à partir d'un moment :math:`t`, elle diminue.}. On utilise un raisonnement
similaire à celui qui a permis d'écrire les équations
(:eq:`amp_dt_2`), (:eq:`amp_dt_3`) pour obtenir :

.. math::
    :nowrap:
    :label: ampoule_diff_1

    \begin{eqnarray}
    p_n(t +dt) 													&=& \pa{1 - S \mu dt} p_n(t) + S \mu p_{n-1}(t) dt \\
    \Longleftrightarrow \frac{p_n(t +dt) - p_{n-1}(t)}{dt} 	&=& - S \mu p_n(t) + S \mu p_{n-1}(t) \\
    \Longleftrightarrow p_n'(t) 	&=& - S \mu p_n(t) + S \mu p_{n-1}(t)
    \end{eqnarray}

On connaît la fonction :math:`p_0(t)` puisqu'elle correspond à
la probabilité qu'aucune des :math:`S` ampoules n'ait grillé
depuis l'instant~0 jusqu'à l'instant :math:`t`, par conséquent :

.. math::
    :nowrap:

    \begin{eqnarray}
    p_0(t) &=& \pr{ \text{ durée de vie des } S \text{ ampoules soient toutes supérieures à } t } \\
    \Longrightarrow p_0(t) &=& \cro{ \int_t^{\infty} \mu e^{- \mu u} du } ^S \\
    \Longrightarrow	p_0(t) &=& e^{-S\mu t}
    \end{eqnarray}

L'équation (:eq:`ampoule_diff_1`) permet de définir une suite d'équations
différentielles du premier degré :

.. math::
    :nowrap:
    :label: ampoule_diff_2

    \begin{eqnarray*}
    p_0(t) 	&=& e^{-S\mu t} \\
    p_1'(t)	&=&	- S \mu p_1(t) + S \mu e^{-S\mu t} \\
    p_2'(t)	&=&	- S \mu p_2(t) + p_1(t) \\
    ... && \\
    p_n'(t) 	&=& - S \mu p_n(t) + S \mu p_{n-1}(t)
    \end{eqnarray*}

On peut donc calculer par récurrence la suite de fonction
:math:`\pa{p_n(t)}_n`. La solution de l'équation différentielle
homogène est :math:`e^{-S\mu t}`. On utilise la méthode de la
variation de la constante en posant :math:`p_n(t) = C_n(t) e^{-S \mu t}`.
On aboutit à l'équation :

.. math::
    :nowrap:

    \begin{eqnarray*}
    p_n'(t)   &=& - S \mu p_n(t) + S \mu p_{n-1}(t) = - S \mu p_n(t) + C_n'(t) e^{- S \mu t} \\
    \Longrightarrow		C_n'(t) e^{- S \mu t} &=& S \mu p_{n-1}(t) \\
    \Longrightarrow		C_n'(t)  &=& S \mu p_{n-1}(t) e^{ S \mu t}
    \end{eqnarray*}

Pour :math:`n = 1`, on obtient
:math:`C_1'(t) = S \mu \Longrightarrow C_1'(t) = S \mu t + A_1`.
Par conséquent, :math:`p_1(t) = \pa{S \mu t + A_1} e^{- S \mu t}`.
On sait que :math:`\forall t, \; \sum_0^{\infty} p_n(t) = 1` mais cela
ne permet pas de déterminer la constante :math:`A_1`. Néanmoins, en
faisant tendre :math:`t \longrightarrow 0`, nécessairement :math:`p_1(t) \longrightarrow 0`.
Par conséquent : :math:`A_1 = 0` et :math:`p_1(t) = S \mu t \; e^{- S \mu t}`. On pose maintenant :math:`p_2(t) = C_2(t) e^{- S \mu t}`. La résolution de l'équation différentielle (:eq:`ampoule_diff_2}) pour :math:`n=2` aboutit à :

.. math::
    :nowrap:

    \begin{eqnarray*}
    C_2'(t)  &=& S \mu p_{1}(t) e^{ S \mu t} = \pa{S \mu t}^2 \\
    \Longrightarrow	C_2(t) &=& \frac{1}{2} S^2 \mu^2 t^2 + A_2 \\
    \Longrightarrow	p_2(t) &=& \pa{ \frac{1}{2} S^2 \mu^2 t^2 + A_2} e^{- S \mu t}
    \end{eqnarray*}

De même, en faisant tendre :math:`t \longrightarrow 0`, on démontre que
:math:`A_2 = 0`. En poursuivant ce raisonnement, par récurrence,
on démontre que :

.. math::
    :label: result_poisson_final

    p_n(t)	&=&	\frac{\pa{S \mu t}^n }{n!} \; e^{- S \mu t}

:math:`p_n(t) = \pr{ N(t) = n}` et d'après l'équation
(:eq:`result_poisson_final`), la variable aléatoire :math:`N(t)`
suit une loi de Poisson de paramètre :math:`S \mu t`. :math:`N`
est aussi appelé `processus de Poisson <https://fr.wikipedia.org/wiki/Processus_de_Poisson>`_.
L'espérance de :math:`N` est égale à :math:`\esp{N(t)} = S \mu t`.
Pendant une durée :math:`T`, le nombre moyen d'ampoules grillées est :
		
.. math::

    \esp{N (t) - N (t-T)} = \esp{N (T)} - \esp{N (t-T)} = S \mu T
		
Ce nombre est indépendant du temps :math:`t`.
		
		
Application numérique
---------------------

Pour des ampoules d'une durée de 1000 heures, le paramètre
:math:`\mu = \frac{1}{1000}`, :math:`T = 1`. S'il y a deux millions
d'ampoules, le nombre moyen d'ampoules grillées par heure est
:math:`S \mu T = 2000`. On retrouve le résultat énoncé.

Programme informatique
======================

La durée de vie de chaque ampoule suit une loi exponentielle de paramètre
:math:`\mu`. Il faut donc simuler une telle variable dont la fonction
de répartition est :math:`F_{\mu}(x) = 1 - e^{ \mu x}`.
On utilise pour cela une propriété qui découle de la fonction
de répartition. On note :math:`F_{\mu}^{-1}(x) = - \; \frac{\ln(1-x)}{\mu}`.
Cette fonction vérifie :math:`F_{\mu}^{-1}\pa{F_{\mu}(x)} = 1`.
Or si :math:`U` est une variable aléatoire uniforme sur
:math:`\cro{0,1}`, alors la variable :math:`V = F_{\mu}^{-1}(U)`
suit la loi exponentielle avec :math:`\mu` pour paramètre.
Effectivement, :math:`\pr{ V \infegal t} = \pr{ F_{\mu}^{-1}(U) \infegal t} = \pr{U \infegal F_{\mu}(t)} = F_{\mu}(x)`.
La fonction de répartition de la variable :math:`V` est :math:`F_{\mu}`,
:math:`V` est donc une loi exponentielle de paramètre :math:`\mu`.
La première fonction simule une variable exponentielle de paramètre :math:`\mu` :

.. runpython::
    :showcode:

    import math
    import random
    def generate_expo(mu):
        x = 0
        while x == 0:
            x = random.random()
        y = - math.log(1-x) / mu
        return y

    print(generate_expo(2))

Le module :epkg:`*py:random` propose aussi une fonction
qui simule automatiquement une variable exponentielle.

.. runpython::
    :showcode:

    import random
    def generate_expo (mu):
        return random.expovariate(mu)

    print(generate_expo(2))

Pour réaliser cette simulation, on suppose qu'on a un tableau de
:math:`S` ampoules. Chaque case de ce tableau contient la durée de
vie restante d'une ampoule, simulée selon une loi exponentielle.
Au départ, toutes les durées de vie sont nulles. On considère qu'à
chaque itération, une heure passe. Lors de chaque itération, pour chaque
ampoule, on vérifie sa durée de vie restante. Si celle-ci est nulle, on
la remplace par une autre dont on choisit aléatoirement la durée de vie
(arrondie à l'entier le plus proche). Si la durée de vie n'est pas
nulle, on la diminue d'une heure. A chaque itération, on compte le nombre
d'ampoules grillées pour en faire la moyenne au bout de :math:`n` itérations.
Pour effectuer cette simulation, les valeurs choisies sont :

.. math::

    S = 10000, \mu = \frac{1}{100}, n = 500

Le programme suivant réalise cette simulation.
On calcule la moyenne du nombre d'ampoules grillées par heure sur les
500 itérations excepté la première pour laquelle toutes les ampoules sont grillées
- configuration aberrante ou tout du moins très peu probable -.
La valeur obtenue est proche de :math:`S \mu = 100`.

.. toctree::

    ../notebooks/file_dattente
