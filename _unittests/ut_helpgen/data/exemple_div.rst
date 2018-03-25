
.. _exemplevideodevoxx2018rst:

========================================
Quelques exemples pour traiter une vidéo
========================================

.. only:: html

    **Links:** :download:`notebook <exemple_video_devoxx_2018.ipynb>`, `html <../_downloads/exemple_video_devoxx_2018.html>`_ :download:`. <exemple_video_devoxx_2018.html>`, :download:`PDF <exemple_video_devoxx_2018.pdf>`, :download:`python <exemple_video_devoxx_2018.py>`, `slides <../_downloads/exemple_video_devoxx_2018.slides.html>`_ :download:`. <exemple_video_devoxx_2018.slides.html>`, `presentation <../_downloads/exemple_video_devoxx_2018.slides2p.html>`_ :download:`. <exemple_video_devoxx_2018.slides2p.html>`, :githublink:`GitHub|_doc/notebooks/ateliers/devoxx2018/exemple_video_devoxx_2018.ipynb|*`

.. code:: ipython3

    from jyquickhelper import add_notebook_menu
    add_notebook_menu()

.. contents::
    :local:

Télécharger une vidéo
---------------------

`outils <http://lesenfantscodaient.fr//api/video.html#youtube>`__

.. code:: ipython3

    from code_beatrix.art.video import *

.. code:: ipython3

    download_youtube_video('Htaj3o3JD8I', '.', res=None)

.. parsed-literal::
    'Harry Potter Theme Song.mp4'

La librairie
`librosa <https://librosa.github.io/librosa_gallery/index.html>`__
permet de retraiter le son comme de séparer les voix du fond sonore.

Extraire le son
---------------

.. code:: ipython3

    son = video_extract_audio('Harry Potter Theme Song.mp4')

.. code:: ipython3

    son30 = audio_extract_audio(son, '00:00:00', '00:00:30')

Jouer le son
------------

.. code:: ipython3

    son30.ipython_display()

.. parsed-literal::
    100%|███████████████████████████████████████████████████████████████████████████████| 662/662 [00:01<00:00, 580.64it/s]

<div align=middle><audio controls><source   src='data:audio/mp3;base64,SUQzBAAAAAAAI1RTU0qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq'>Sorry, seems like your browser doesn't support HTML5 audio/video</audio></div>

Liste des vidéos filmées
------------------------

.. code:: ipython3

    import os
    [_ for _ in os.listdir(r'.') if 'mp4' in _ and ('Harry' in _ or "WIN_20180113_16" in _)]

.. parsed-literal::
    ['Harry Potter Theme Song.mp4',
     'WIN_20180113_16_40_32_Pro.mp4',
     'WIN_20180113_16_40_40_Pro.mp4',
     'WIN_20180113_16_42_41_Pro.mp4',
     'WIN_20180113_16_43_33_Pro.mp4',
     'WIN_20180113_16_43_42_Pro.mp4',
     'WIN_20180113_16_44_31_Pro.mp4',
     'WIN_20180113_16_45_39_Pro.mp4',
     'WIN_20180113_16_46_26_Pro.mp4',
     'WIN_20180113_16_47_17_Pro.mp4',
     'WIN_20180113_16_47_28_Pro.mp4',
     'WIN_20180113_16_47_39_Pro.mp4',
     'WIN_20180113_16_58_37_Pro.mp4']

Extraire un bout de la video
----------------------------

.. code:: ipython3

    vid = video_extract_video('WIN_20180113_16_40_40_Pro.mp4', '00:00:06', '00:00:22')

Accélérer une vidéo
-------------------

.. code:: ipython3

    vid2 = video_modification(vid, speed=2.)

Mettre des vidéos bout à bout
-----------------------------

.. code:: ipython3

    video_mur = video_concatenate([vid2, vid])

Mettre des sons bout à bout
---------------------------

.. code:: ipython3

    son3 = audio_concatenate([son30, son30])

Remplacer le son d'une vidéo
----------------------------

.. code:: ipython3

    video_truquee = video_replace_audio(video_mur, son_tout)

Sauver une vidéo sur disque
---------------------------

.. code:: ipython3

    video_save(video_truquee, 'rapide_crash2_truquee2.mp4', verbose=True)

.. parsed-literal::
    [MoviePy] >>>> Building video rapide_crash2_truquee2.mp4
    [MoviePy] Writing audio in rapide_crash2_truquee2TEMP_MPY_wvf_snd.mp3

.. parsed-literal::

    100%|███████████████████████████████████████████████████████████████████████████████| 192/192 [00:00<00:00, 691.81it/s]

.. parsed-literal::
    [MoviePy] Done.
    [MoviePy] Writing video rapide_crash2_truquee2.mp4

.. parsed-literal::

    100%|████████████████████████████████████████████████████████████████████████████████| 289/289 [00:33<00:00,  8.57it/s]

.. parsed-literal::
    [MoviePy] Done.
    [MoviePy] >>>> Video ready: rapide_crash2_truquee2.mp4
