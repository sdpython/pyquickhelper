if exist c:\Python34_x64 goto py64:
set pythonexe=c:\Python34
goto nextn:

:py64:
set pythonexe=c:\Python34_x64

:nextn:
set path=%path%;%pythonexe%;%pythonexe%\Scripts
ipython3 notebook --notebook-dir=_doc\notebooks