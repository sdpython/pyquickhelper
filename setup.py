# -*- coding: utf-8 -*-
import sys
import os
from setuptools import setup, Extension, find_packages
from pyquicksetup import read_version, read_readme, default_cmdclass

#########
# settings
#########

project_var_name = "pyquickhelper"
github_owner = "sdpython"
versionPython = "%s.%s" % (sys.version_info.major, sys.version_info.minor)
path = "Lib/site-packages/" + project_var_name
readme = 'README.rst'
history = "HISTORY.rst"
requirements = None

KEYWORDS = project_var_name + (
    ', synchronization, files, documentation, Xavier Dupré, sphinx, '
    'extension, notebooks, rst, builder, cli, setup, unit tests')
DESCRIPTION = (
    "Various functionalities: folder synchronization, simple logging function, "
    "helpers to generate documentation with sphinx, sphinx extension, "
    "to run a command line, to run a notebook...")
CLASSIFIERS = [
    'Programming Language :: Python :: 3',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Development Status :: 5 - Production/Stable'
]

#######
# data
#######

packages = find_packages('src', exclude='src')
package_dir = {k: "src/" + k.replace(".", "/") for k in packages}
package_data = {
    project_var_name + ".sphinxext": ["*.png"],
    project_var_name + ".ipythonhelper": ["*.png"],
    project_var_name + ".filehelper": ["*.js", "*.css"],
    project_var_name + ".helpgen": ["*.js", "*.tpl"],
    project_var_name + ".sphinxext.bokeh": ["*.txt"],
    project_var_name + ".sphinxext.sphinximages.sphinxtrib": ["*.png"],
    project_var_name + ".sphinxext.revealjs.templates.revealjs": ["*.conf", "*.html", "*.txt"],
    project_var_name + ".sphinxext.revealjs.templates.revealjs.static": ["LICENSE", "*.json", "*.css_t"],
    project_var_name + ".sphinxext.revealjs.templates.revealjs.static.css": ["*.css", "*.scss"],
    project_var_name + ".sphinxext.revealjs.templates.revealjs.static.css.print": ["*.css"],
    project_var_name + ".sphinxext.revealjs.templates.revealjs.static.css.theme": ["*.css", "*.md"],
    project_var_name + ".sphinxext.revealjs.templates.revealjs.static.css.theme.source": ["*.scss"],
    project_var_name + ".sphinxext.revealjs.templates.revealjs.static.css.theme.template": ["*.scss"],
    project_var_name + ".sphinxext.revealjs.templates.revealjs.static.js": ["*.js"],
    project_var_name + ".sphinxext.revealjs.templates.revealjs.static.lib.css": ["*.css"],
    project_var_name + ".sphinxext.revealjs.templates.revealjs.static.lib.font": [
        "league-gothic/*.*", "source-sans-pro/*.*"],
    project_var_name + ".sphinxext.revealjs.templates.revealjs.static.lib.js": ["*.js"],
    project_var_name + ".sphinxext.revealjs.templates.revealjs.static.lib.plugin": [
        "highlight/*.js", "markdown/*.*", "math/*.js", "multiplex/*.*",
        "notes/*.*", "notes-server/*.*", "print-pdf/*.js", "search/*js", "zoom-js/*.js"],
    project_var_name + ".sphinxext.sphinximages.sphinxcontrib_images_lightbox2.lightbox2_customize": ["*.js"],
    project_var_name + ".sphinxext.sphinximages.sphinxcontrib_images_lightbox2.lightbox2.css": ["*.css"],
    project_var_name + ".sphinxext.sphinximages.sphinxcontrib_images_lightbox2.lightbox2.img": ["*.png", "*.gif"],
    project_var_name + ".sphinxext.sphinximages.sphinxcontrib_images_lightbox2.lightbox2.js": ["*.js", "*.map"],
    project_var_name + ".sphinxext.sphinximages.sphinxcontrib_images_lightbox2.lightbox2.sass": ["*.sass"],
    project_var_name + ".sphinxext.sphinximages.sphinxtrib": ["*.png"],
    project_var_name + ".sphinxext.templates": ["*.txt"],
}

#######
# data
#######

setup(
    name=project_var_name,
    version=read_version(__file__, "pyquickhelper", subfolder='src'),
    author='Xavier Dupré',
    author_email='xavier.dupre@gmail.com',
    license="MIT",
    url="http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/index.html",
    download_url="https://github.com/sdpython/pyquickhelper",
    description=DESCRIPTION,
    long_description=read_readme(__file__),
    keywords=KEYWORDS,
    classifiers=CLASSIFIERS,
    packages=packages,
    package_dir=package_dir,
    package_data=package_data,
    ext_modules=[],
    cmdclass=default_cmdclass(),
    setup_requires=['pyquicksetup>=0.2'],
    install_requires=[
        'fire',
        'numpy>=1.16.0',
        'pyquicksetup>=0.2',
    ],
    extras_require={
        'cli': ['tkinterquickhelper', 'pysftp', 'fire'],
        # cryptography
        'filehelper': ['cffi', 'cryptography', 'pylzma', 'pysftp',
                       'keyrings.cryptfile'],
        'jenkinshelper': ['python-jenkins>=1.0.0', 'pyyaml'],
        'loghelper': ['psutil'],
        'server': ['fastapi'],
        'all': [
            "autopep8",     # part of the minimal list
            'cffi',
            "coverage>=5.0",
            'cryptography',
            "docformatter",
            "docutils",
            'flake8',
            'fastapi',
            'fire',
            "IPython>=5.0.0",
            "jupyter",
            "jupyter_client",
            "jupyter_sphinx",
            "jyquickhelper",
            "keyring",
            "keyrings.cryptfile",
            "matplotlib",
            "metakernel",
            "multi_key_dict",
            "nbconvert>=6.0.2",
            "notebook>=4.2.0",
            "numpy>=1.16.0",
            "numpydoc",
            "pandas>=1.0.0",
            'psutil',
            "pylint",
            'python-jenkins>=1.0.0',
            'pyyaml',
            'pylzma',
            'pysftp',
            "requests",
            "semantic_version",
            "sphinx>=3.0,<4.0",
            "sphinx-gallery",
            "sphinxcontrib-imagesvg",
            "traitlets>=5.0",
        ],
    },
    entry_points={
        'console_scripts': [
            'encrypt = pyquickhelper.cli.encryption_cli:encrypt',
            'decrypt = pyquickhelper.cli.encryption_cli:decrypt',
            'encrypt_file = pyquickhelper.cli.encryption_file_cli:encrypt_file',
            'decrypt_file = pyquickhelper.cli.encryption_file_cli:decrypt_file',
            'pyq-sync = pyquickhelper.cli.pyq_sync_cli:pyq_sync',
        ]}
)
