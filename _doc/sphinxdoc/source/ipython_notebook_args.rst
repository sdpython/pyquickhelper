
.. _l-ipython_notebook_args:

IPython Notebook Arguments
==========================

.. index:: ipython, notebook, command line

This is the output of command line::

    ipython notebook --help-all
    
These arguments can be specified in :class:`NotebookRunner <pyquickhelper.ipythonhelper.notebook_runner>`.
They were generated with Jupyter 4.0 on 08/18/2015.



The Jupyter HTML Notebook.

This launches a Tornado based HTML Notebook Server that serves up an
HTML5/Javascript Notebook client.

Subcommands-----------
Subcommands are launched as `jupyter-notebook cmd [args]`. For information on
using subcommand 'cmd', do: `jupyter-notebook cmd -h`.

list
    List currently running notebook servers in this profile.

Options-------
Arguments that take values are actually convenience aliases to full
Configurables, whose aliases are listed on the help line. For more information
on full configurables, see '--help-all'.

--generate-config    generate default config file--pylab    DISABLED: use %pylab or %matplotlib in the notebook to enable matplotlib.-y    Answer yes to any questions instead of prompting.--debug    set log level to logging.DEBUG (maximize logging output)--script    DEPRECATED, IGNORED--no-script    DEPRECATED, IGNORED--no-browser    Don't open the notebook in a browser after startup.--no-mathjax
    Disable MathJax    
    MathJax is the javascript library IPython uses to render math/LaTeX. It is
    very large, so you may want to disable it if you have a slow internet
    connection, or for offline use of the notebook.    
    When disabled, equations etc. will appear as their untransformed TeX source.
--certfile=<Unicode> (NotebookApp.certfile)
    Default: ''
    The full path to an SSL/TLS certificate file.
--port-retries=<Int> (NotebookApp.port_retries)
    Default: 50
    The number of additional ports to try if the specified port is not
    available.
--transport=<CaselessStrEnum> (KernelManager.transport)
    Default: 'tcp'
    Choices: ['tcp', 'ipc']
--pylab=<Unicode> (NotebookApp.pylab)
    Default: 'disabled'
    DISABLED: use %pylab or %matplotlib in the notebook to enable matplotlib.
--config=<Unicode> (JupyterApp.config_file)
    Default: ''
    Full path of a config file.
--ip=<Unicode> (NotebookApp.ip)
    Default: 'localhost'
    The IP address the notebook server will listen on.
--browser=<Unicode> (NotebookApp.browser)
    Default: ''
    Specify what command to use to invoke a web browser when opening the    notebook. If not specified, the default browser will be determined by the    `webbrowser` standard library module, which allows setting of the BROWSER    environment variable to override it.--port=<Int> (NotebookApp.port)    Default: 8888    The port the notebook server will listen on.--notebook-dir=<Unicode> (NotebookApp.notebook_dir)    Default: ''    The directory to use for notebooks and kernels.--keyfile=<Unicode> (NotebookApp.keyfile)    Default: ''    The full path to a private key file for usage with SSL/TLS.--log-level=<Enum> (Application.log_level)    Default: 30    Choices: (0, 10, 20, 30, 40, 50, 'DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL')    Set the log level by value or name.

Class parameters
----------------

Parameters are set from command-line arguments of the form:
`--Class.trait=value`. This line is evaluated in Python, so simple expressions
are allowed, e.g.:: `--C.a='range(3)'` For setting C.a=[0,1,2].

NotebookApp options
-------------------

--NotebookApp.allow_credentials=<Bool>
    Default: False
    Set the Access-Control-Allow-Credentials: true header
--NotebookApp.allow_origin=<Unicode>
    Default: ''
    Set the Access-Control-Allow-Origin header
    Use '*' to allow any origin to access your server.
    Takes precedence over allow_origin_pat.
--NotebookApp.allow_origin_pat=<Unicode>
    Default: ''
    Use a regular expression for the Access-Control-Allow-Origin header
    Requests from an origin matching the expression will get replies with:
        Access-Control-Allow-Origin: origin
    where `origin` is the origin of the request.
    Ignored if allow_origin is set.
--NotebookApp.answer_yes=<Bool>
    Default: False
    Answer yes to any prompts.
--NotebookApp.base_project_url=<Unicode>
    Default: '/'
    DEPRECATED use base_url
--NotebookApp.base_url=<Unicode>
    Default: '/'
    The base URL for the notebook server.
    Leading and trailing slashes can be omitted, and will automatically be
    added.
--NotebookApp.browser=<Unicode>
    Default: ''
    Specify what command to use to invoke a web browser when opening the
    notebook. If not specified, the default browser will be determined by the
    `webbrowser` standard library module, which allows setting of the BROWSER
    environment variable to override it.
--NotebookApp.certfile=<Unicode>
    Default: ''
    The full path to an SSL/TLS certificate file.
--NotebookApp.config_file=<Unicode>
    Default: ''
    Full path of a config file.
--NotebookApp.config_file_name=<Unicode>
    Default: ''
    Specify a config file to load.
--NotebookApp.config_manager_class=<Type>
    Default: <class 'notebook.services.config.manager.ConfigManager'>
    The config manager class to use
--NotebookApp.contents_manager_class=<Type>
    Default: <class 'notebook.services.contents.filemanager.FileContentsMa...
    The notebook manager class to use.
--NotebookApp.cookie_secret=<Bytes>
    Default: b''
    The random bytes used to secure cookies. By default this is a new random
    number every time you start the Notebook. Set it to a value in a config file
    to enable logins to persist across server sessions.
    Note: Cookie secrets should be kept private, do not share config files with
    cookie_secret stored in plaintext (you can read the value from a file).
--NotebookApp.cookie_secret_file=<Unicode>
    Default: ''
    The file where the cookie secret is stored.
--NotebookApp.default_url=<Unicode>
    Default: '/tree'
    The default URL to redirect to from `/`
--NotebookApp.enable_mathjax=<Bool>
    Default: True
    Whether to enable MathJax for typesetting math/TeX
    MathJax is the javascript library IPython uses to render math/LaTeX. It is
    very large, so you may want to disable it if you have a slow internet
    connection, or for offline use of the notebook.
    When disabled, equations etc. will appear as their untransformed TeX source.
--NotebookApp.extra_nbextensions_path=<List>
    Default: traitlets.Undefined
    extra paths to look for Javascript notebook extensions
--NotebookApp.extra_static_paths=<List>
    Default: traitlets.Undefined
    Extra paths to search for serving static files.
    This allows adding javascript/css to be available from the notebook server
    machine, or overriding individual files in the IPython
--NotebookApp.extra_template_paths=<List>
    Default: traitlets.Undefined
    Extra paths to search for serving jinja templates.
    Can be used to override templates from notebook.templates.
--NotebookApp.file_to_run=<Unicode>
    Default: ''
--NotebookApp.generate_config=<Bool>
    Default: False
    Generate default config file.
--NotebookApp.ip=<Unicode>
    Default: 'localhost'
    The IP address the notebook server will listen on.
--NotebookApp.jinja_environment_options=<Dict>
    Default: traitlets.Undefined
    Supply extra arguments that will be passed to Jinja environment.
--NotebookApp.jinja_template_vars=<Dict>
    Default: traitlets.Undefined
    Extra variables to supply to jinja templates when rendering.
--NotebookApp.kernel_manager_class=<Type>
    Default: <class 'notebook.services.kernels.kernelmanager.MappingKernel...
    The kernel manager class to use.
--NotebookApp.kernel_spec_manager_class=<Type>
    Default: <class 'jupyter_client.kernelspec.KernelSpecManager'>
    The kernel spec manager class to use. Should be a subclass of
    `jupyter_client.kernelspec.KernelSpecManager`.
    The Api of KernelSpecManager is provisional and might change without warning
    between this version of IPython and the next stable one.
--NotebookApp.keyfile=<Unicode>
    Default: ''
    The full path to a private key file for usage with SSL/TLS.
--NotebookApp.log_datefmt=<Unicode>
    Default: '%Y-%m-%d %H:%M:%S'
    The date format used by logging formatters for %(asctime)s
--NotebookApp.log_format=<Unicode>
    Default: '[%(name)s]%(highlevel)s %(message)s'
    The Logging format template
--NotebookApp.log_level=<Enum>
    Default: 30
    Choices: (0, 10, 20, 30, 40, 50, 'DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL')
    Set the log level by value or name.
--NotebookApp.login_handler_class=<Type>
    Default: <class 'notebook.auth.login.LoginHandler'>
    The login handler class to use.
--NotebookApp.logout_handler_class=<Type>
    Default: <class 'notebook.auth.logout.LogoutHandler'>
    The logout handler class to use.
--NotebookApp.mathjax_url=<Unicode>
    Default: ''
    The url for MathJax.js.
--NotebookApp.notebook_dir=<Unicode>
    Default: ''
    The directory to use for notebooks and kernels.
--NotebookApp.open_browser=<Bool>
    Default: True
    Whether to open in a browser after starting. The specific browser used is
    platform dependent and determined by the python standard library
    `webbrowser` module, unless it is overridden using the --browser
    (NotebookApp.browser) configuration option.
--NotebookApp.password=<Unicode>
    Default: ''
    Hashed password to use for web authentication.
    To generate, type in a python/IPython shell:
      from notebook.auth import passwd; passwd()
    The string should be of the form type:salt:hashed-password.
--NotebookApp.port=<Int>
    Default: 8888
    The port the notebook server will listen on.
--NotebookApp.port_retries=<Int>
    Default: 50
    The number of additional ports to try if the specified port is not
    available.
--NotebookApp.pylab=<Unicode>
    Default: 'disabled'
    DISABLED: use %pylab or %matplotlib in the notebook to enable matplotlib.
--NotebookApp.reraise_server_extension_failures=<Bool>
    Default: False
    Reraise exceptions encountered loading server extensions?
--NotebookApp.server_extensions=<List>
    Default: traitlets.Undefined
    Python modules to load as notebook server extensions. This is an
    experimental API, and may change in future releases.
--NotebookApp.session_manager_class=<Type>
    Default: <class 'notebook.services.sessions.sessionmanager.SessionMana...
    The session manager class to use.
--NotebookApp.ssl_options=<Dict>
    Default: traitlets.Undefined
    Supply SSL options for the tornado HTTPServer. See the tornado docs for
    details.
--NotebookApp.tornado_settings=<Dict>
    Default: traitlets.Undefined
    Supply overrides for the tornado.web.Application that the IPython notebook
    uses.
--NotebookApp.trust_xheaders=<Bool>
    Default: False
    Whether to trust or not X-Scheme/X-Forwarded-Proto and X-Real-Ip/X
    -Forwarded-For headerssent by the upstream reverse proxy. Necessary if the
    proxy handles SSL
--NotebookApp.webapp_settings=<Dict>
    Default: traitlets.Undefined
    DEPRECATED, use tornado_settings
--NotebookApp.websocket_url=<Unicode>
    Default: ''
    The base URL for websockets, if it differs from the HTTP server (hint: it
    almost certainly doesn't).
    Should be in the form of an HTTP origin: ws[s]://hostname[:port]

KernelManager options
---------------------

--KernelManager.autorestart=<Bool>
    Default: False
    Should we autorestart the kernel if it dies.
--KernelManager.connection_file=<Unicode>
    Default: ''
    JSON file in which to store connection info [default: kernel-<pid>.json]
    This file will contain the IP, ports, and authentication key needed to
    connect clients to this kernel. By default, this file will be created in the
    security dir of the current profile, but can be specified by absolute path.
--KernelManager.control_port=<Int>
    Default: 0
    set the control (ROUTER) port [default: random]
--KernelManager.hb_port=<Int>
    Default: 0
    set the heartbeat port [default: random]
--KernelManager.iopub_port=<Int>
    Default: 0
    set the iopub (PUB) port [default: random]
--KernelManager.ip=<Unicode>
    Default: ''
    Set the kernel's IP address [default localhost]. If the IP address is
    something other than localhost, then Consoles on other machines will be able
    to connect to the Kernel, so be careful!
--KernelManager.kernel_cmd=<List>
    Default: traitlets.Undefined
    DEPRECATED: Use kernel_name instead.
    The Popen Command to launch the kernel. Override this if you have a custom
    kernel. If kernel_cmd is specified in a configuration file, Jupyter does not
    pass any arguments to the kernel, because it cannot make any assumptions
    about the arguments that the kernel understands. In particular, this means
    that the kernel does not receive the option --debug if it given on the
    Jupyter command line.
--KernelManager.shell_port=<Int>
    Default: 0
    set the shell (ROUTER) port [default: random]
--KernelManager.stdin_port=<Int>
    Default: 0
    set the stdin (ROUTER) port [default: random]
--KernelManager.transport=<CaselessStrEnum>
    Default: 'tcp'
    Choices: ['tcp', 'ipc']

Session options
---------------

--Session.buffer_threshold=<Int>
    Default: 1024
    Threshold (in bytes) beyond which an object's buffer should be extracted to
    avoid pickling.
--Session.copy_threshold=<Int>
    Default: 65536
    Threshold (in bytes) beyond which a buffer should be sent without copying.
--Session.debug=<Bool>
    Default: False
    Debug output in the Session
--Session.digest_history_size=<Int>
    Default: 65536
    The maximum number of digests to remember.
    The digest history will be culled when it exceeds this value.
--Session.item_threshold=<Int>
    Default: 64
    The maximum number of items for a container to be introspected for custom
    serialization. Containers larger than this are pickled outright.
--Session.key=<CBytes>
    Default: b''
    execution key, for signing messages.
--Session.keyfile=<Unicode>
    Default: ''
    path to file containing execution key.
--Session.metadata=<Dict>
    Default: traitlets.Undefined
    Metadata dictionary, which serves as the default top-level metadata dict for
    each message.
--Session.packer=<DottedObjectName>
    Default: 'json'
    The name of the packer for serializing messages. Should be one of 'json',
    'pickle', or an import name for a custom callable serializer.
--Session.session=<CUnicode>
    Default: ''
    The UUID identifying this session.
--Session.signature_scheme=<Unicode>
    Default: 'hmac-sha256'
    The digest scheme used to construct the message signatures. Must have the
    form 'hmac-HASH'.
--Session.unpacker=<DottedObjectName>
    Default: 'json'
    The name of the unpacker for unserializing messages. Only used with custom
    functions for `packer`.
--Session.username=<Unicode>
    Default: 'username'
    Username for the Session. Default is your system username.

MappingKernelManager options
----------------------------

--MappingKernelManager.default_kernel_name=<Unicode>
    Default: 'python3'
    The name of the default kernel to start
--MappingKernelManager.kernel_manager_class=<DottedObjectName>
    Default: 'jupyter_client.ioloop.IOLoopKernelManager'
    The kernel manager class.  This is configurable to allow subclassing of the
    KernelManager for customized behavior.
--MappingKernelManager.root_dir=<Unicode>
    Default: ''

ContentsManager options
-----------------------

--ContentsManager.checkpoints=<Instance>
    Default: traitlets.Undefined
--ContentsManager.checkpoints_class=<Type>
    Default: <class 'notebook.services.contents.checkpoints.Checkpoints'>
--ContentsManager.checkpoints_kwargs=<Dict>
    Default: traitlets.Undefined
--ContentsManager.hide_globs=<List>
    Default: traitlets.Undefined
    Glob patterns to hide in file and directory listings.
--ContentsManager.pre_save_hook=<Any>
    Default: None
    Python callable or importstring thereof
    To be called on a contents model prior to save.
    This can be used to process the structure, such as removing notebook outputs
    or other side effects that should not be saved.
    It will be called as (all arguments passed by keyword)::
        hook(path=path, model=model, contents_manager=self)
    - model: the model to be saved. Includes file contents.
      Modifying this dict will affect the file that is stored.
    - path: the API path of the save destination
    - contents_manager: this ContentsManager instance
--ContentsManager.untitled_directory=<Unicode>
    Default: 'Untitled Folder'
    The base name used when creating untitled directories.
--ContentsManager.untitled_file=<Unicode>
    Default: 'untitled'
    The base name used when creating untitled files.
--ContentsManager.untitled_notebook=<Unicode>
    Default: 'Untitled'
    The base name used when creating untitled notebooks.

FileContentsManager options
---------------------------

--FileContentsManager.checkpoints=<Instance>
    Default: traitlets.Undefined
--FileContentsManager.checkpoints_class=<Type>
    Default: <class 'notebook.services.contents.checkpoints.Checkpoints'>
--FileContentsManager.checkpoints_kwargs=<Dict>
    Default: traitlets.Undefined
--FileContentsManager.hide_globs=<List>
    Default: traitlets.Undefined
    Glob patterns to hide in file and directory listings.
--FileContentsManager.post_save_hook=<Any>
    Default: None
    Python callable or importstring thereof
    to be called on the path of a file just saved.
    This can be used to process the file on disk, such as converting the
    notebook to a script or HTML via nbconvert.
    It will be called as (all arguments passed by keyword)::
        hook(os_path=os_path, model=model, contents_manager=instance)
    - path: the filesystem path to the file just written - model: the model
    representing the file - contents_manager: this ContentsManager instance
--FileContentsManager.pre_save_hook=<Any>
    Default: None
    Python callable or importstring thereof
    To be called on a contents model prior to save.
    This can be used to process the structure, such as removing notebook outputs
    or other side effects that should not be saved.
    It will be called as (all arguments passed by keyword)::
        hook(path=path, model=model, contents_manager=self)
    - model: the model to be saved. Includes file contents.
      Modifying this dict will affect the file that is stored.
    - path: the API path of the save destination
    - contents_manager: this ContentsManager instance
--FileContentsManager.root_dir=<Unicode>
    Default: ''
--FileContentsManager.save_script=<Bool>
    Default: False
    DEPRECATED, use post_save_hook
--FileContentsManager.untitled_directory=<Unicode>
    Default: 'Untitled Folder'
    The base name used when creating untitled directories.
--FileContentsManager.untitled_file=<Unicode>
    Default: 'untitled'
    The base name used when creating untitled files.
--FileContentsManager.untitled_notebook=<Unicode>
    Default: 'Untitled'
    The base name used when creating untitled notebooks.

NotebookNotary options
----------------------

--NotebookNotary.algorithm=<Enum>
    Default: 'sha256'
    Choices: {'sha512', 'md5', 'sha256', 'sha224', 'sha1', 'sha384'}
    The hashing algorithm used to sign notebooks.
--NotebookNotary.cache_size=<Int>
    Default: 65535
    The number of notebook signatures to cache. When the number of signatures
    exceeds this value, the oldest 25% of signatures will be culled.
--NotebookNotary.db_file=<Unicode>
    Default: ''
    The sqlite file in which to store notebook signatures. By default, this will
    be in your Jupyter runtime directory. You can set it to ':memory:' to
    disable sqlite writing to the filesystem.
--NotebookNotary.secret=<Bytes>
    Default: b''
    The secret key with which notebooks are signed.
--NotebookNotary.secret_file=<Unicode>
    Default: ''
    The file where the secret key is stored.

KernelSpecManager options
-------------------------

--KernelSpecManager.whitelist=<Set>
    Default: traitlets.Undefined
    Whitelist of allowed kernel names.
    By default, all installed kernels are allowed.

Examples
--------

    ipython notebook                       # start the notebook
    ipython notebook --profile=sympy       # use the sympy profile
    ipython notebook --certfile=mycert.pem # use SSL/TLS certificate

