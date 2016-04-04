# -*- coding: utf-8 -*-
"""
@file
@brief  quelques fonctions à propos de la première séance

"""


def commentaire_accentues():
    """
    L'aide de cette fonction contient assuréments des accents.

    @FAQ(Python n'accepte pas les accents)
    Le langage Python a été conçu en langage anglais. Dès qu'on on ajoute un caractère
    qui ne fait pas partie de l'alphabet anglais (ponctuation comprise), il déclenche une erreur :

    @code
    File "faq_cvxopt.py", line 3
    SyntaxError: Non-UTF-8 code starting with '\xe8' in file faq_cvxopt.py on line 4, but no encoding declared;
                 see http://python.org/dev/peps/pep-0263/ for details
    @endcode

    Pour la résoudre, il faut dire à l'interpréteur que des caractères non anglais peuvent apparaître
    et écrire sur la première ligne du programme :

    @code
    # -*- coding: latin-1 -*-
    @endcode

    Ou pour tout caractère y compris chinois :

    @code
    # -*- coding: utf-8 -*-
    @endcode

    Si vous utilisez l'éditeur `SciTE <http://www.scintilla.org/SciTE.html>`_ sous Windows,
    après avoir ajouté cette ligne avec l'encoding `utf-8`,
    il est conseillé de fermer le fichier puis de le réouvrir.
    SciTE le traitera différemment.

    @endFAQ
    """
    pass
