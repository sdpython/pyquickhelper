# -*- coding: utf-8 -*-
import sys
import os
from setuptools import setup, Extension, find_packages

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

KEYWORDS = project_var_name + \
    ', synchronization, files, documentation, Xavier Dupré, sphinx, ' + \
    'extension, notebooks, rst, builder, cli, setup, unit tests'
DESCRIPTION = "Various functionalities: folder synchronization, simple logging function, " + \
              "helpers to generate documentation with sphinx, sphinx extension, " + \
              "to run a command line, to run a notebook..."
CLASSIFIERS = [
    'Programming Language :: Python :: 3',
    'Intended Audience :: Developers',
    'Topic :: Scientific/Engineering',
    'Topic :: Education',
    'License :: OSI Approved :: MIT License',
    'Development Status :: 5 - Production/Stable'
]

#######
# data
#######

packages = find_packages('src', exclude='src')
package_dir = {k: "src/" + k.replace(".", "/") for k in packages}
package_data = {project_var_name + ".sphinxext": ["*.png"],
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

############
# functions
############

if False:

    def is_local():
        file = os.path.abspath(__file__).replace("\\", "/").lower()
        if "/temp/" in file and "pip-" in file:
            return False
        for cname in {"bdist_msi", "build27", "build_script", "build_sphinx", "build_ext",
                      "bdist_wheel", "bdist_egg", "bdist_wininst", "clean_pyd", "clean_space",
                      "copy27", "copy_dist", "local_pypi", "notebook", "publish", "publish_doc",
                      "register", "unittests", "unittests_LONG", "unittests_SKIP", "unittests_GUI",
                      "run27", "sdist", "setupdep", "test_local_pypi", "upload_docs", "setup_hook",
                      "copy_sphinx", "write_version", "lab", "history", "run_pylint", "local_jenkins"}:
            if cname in sys.argv:
                try:
                    import_pyquickhelper()
                except ImportError:
                    return False
                return True
        else:
            return False
        return False

    def ask_help():
        return "--help" in sys.argv or "--help-commands" in sys.argv

    def import_pyquickhelper():
        try:
            import pyquickhelper
        except ImportError:
            p = os.path.normpath(
                os.path.abspath(
                    os.path.join(
                        os.path.dirname(__file__),
                        "src")))
            sys.path.append(p)
            try:
                import pyquickhelper
            except ImportError:
                message = "Module pyquickhelper is needed to build the documentation "
                message += "({0}), not found in path {1} - current {2}".format(
                    sys.executable, sys.path[-1], os.getcwd())
                raise ImportError(message)

        try:
            from pyquickhelpersetup import SetupCommandDisplay
        except ImportError:
            sys.path.append(os.path.join(os.path.dirname(
                pyquickhelper.__file__), '..', 'pyquicksetup'))
            try:
                from pyquickhelpersetup import SetupCommandDisplay
            except ImportError:
                SetupCommandDisplay = None
                pass

        return pyquickhelper

    def verbose():
        print("---------------------------------")
        print("package_dir =", package_dir)
        print("packages    =", packages)
        print("package_data=", package_data)
        print("current     =", os.path.abspath(os.getcwd()))
        print("---------------------------------")

    ##########
    # version
    ##########

    if is_local() and not ask_help():
        def write_version():
            pyquickhelper = import_pyquickhelper()
            from pyquickhelper.pycode import write_version_for_setup
            return write_version_for_setup(__file__)

        write_version()

        versiontxt = os.path.join(os.path.dirname(__file__), "version.txt")
        if os.path.exists(versiontxt):
            with open(versiontxt, "r") as f:
                lines = f.readlines()
            subversion = "." + lines[0].strip("\r\n ")
            if subversion == ".0":
                raise Exception(
                    "Git version is wrong: '{0}'.".format(subversion))
        else:
            raise FileNotFoundError(versiontxt)
    else:
        # when the module is installed, no commit number is displayed
        subversion = ""

    if "upload" in sys.argv and not subversion and not ask_help():
        # avoid uploading with a wrong subversion number
        try:
            import pyquickhelper
            pyq = True
        except ImportError:
            pyq = False
        raise Exception(
            "Git version is empty, cannot upload, is_local()={0}, pyquickhelper={1}".format(is_local(), pyq))

    ##############
    # common part
    ##############

    if os.path.exists(readme):
        with open(readme, "r", encoding='utf-8-sig') as f:
            long_description = f.read()
    else:
        long_description = ""
    if os.path.exists(history):
        with open(history, "r", encoding='utf-8-sig') as f:
            long_description += f.read()

    if "--verbose" in sys.argv:
        verbose()

    if is_local() and not ({"history"} & set(sys.argv)):
        pyquickhelper = import_pyquickhelper()
        logging_function = pyquickhelper.get_fLOG()
        logging_function(OutputPrint=True)
        from pyquickhelper.pycode import process_standard_options_for_setup
        r = process_standard_options_for_setup(
            sys.argv, __file__, project_var_name, port=8067,
            requirements=requirements, blog_list=pyquickhelper.__blog__,
            layout=["rst", "html"], additional_notebook_path=["jyquickhelper"],
            fLOG=logging_function, covtoken=(
                "69193a28-dc79-4a24-98ed-aedf441a8249", "'_UT_39_std' in outfile"),
            github_owner=github_owner)

        if not r and not ({"bdist_msi", "sdist",
                           "bdist_wheel", "publish", "publish_doc", "register",
                           "upload_docs", "bdist_wininst", "build_ext"} & set(sys.argv)):
            raise Exception(
                "unable to interpret command line: " + str(sys.argv))
    else:
        r = False

    if ask_help():
        pyquickhelper = import_pyquickhelper()
        from pyquickhelper.pycode import process_standard_options_for_setup_help
        process_standard_options_for_setup_help(sys.argv)

    if not r:
        if len(sys.argv) in (1, 2) and sys.argv[-1] in ("--help-commands",):
            pyquickhelper = import_pyquickhelper()
            from pyquickhelper.pycode import process_standard_options_for_setup_help
            process_standard_options_for_setup_help(sys.argv)
        else:
            pyquickhelper = import_pyquickhelper()
        try:
            from pyquickhelper.pycode import clean_readme
        except ImportError:
            clean_readme = lambda v: v
        from pyquickhelper import __version__ as sversion
        long_description = clean_readme(long_description)

        cmdclass = {}
        try:
            from pyquickhelpersetup import SetupCommandDisplay, SetupCommandHistory
            cmdclass.update({'display': SetupCommandDisplay,
                             'history': SetupCommandHistory})
        except ImportError:
            pass

        setup(
            name=project_var_name,
            version=sversion,
            author='Xavier Dupré',
            author_email='xavier.dupre@gmail.com',
            license="MIT",
            url="http://www.xavierdupre.fr/app/pyquickhelper/helpsphinx/index.html",
            download_url="https://github.com/sdpython/pyquickhelper",
            description=DESCRIPTION,
            long_description=long_description,
            keywords=KEYWORDS,
            classifiers=CLASSIFIERS,
            packages=packages,
            package_dir=package_dir,
            package_data=package_data,
            ext_modules=[],
            cmdclass=cmdclass,
            install_requires=[
                'fire',
                'numpy>=1.16.0',
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
                    "sphinx>=2.1",
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

from pyquicksetup import read_version, read_readme, default_cmdclass


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
            "sphinx>=2.1",
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
