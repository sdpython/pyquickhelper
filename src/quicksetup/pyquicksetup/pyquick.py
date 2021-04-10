"""
Defines setup commands.
* build_script
* build_sphinx
* history
* lab
* local_jenkins
* local_pypi
* notebook
* unittests *
* unittests_LONG *
* unittests_SKIP *
* unittests_GUI *
* setup_hook
* write_version
"""
import os
import re
import sys
from distutils.core import Command


class _SetupCommand(Command):

    def get_parameters(self):
        module_name = self.distribution.packages[0]
        location = os.path.normpath(os.path.join(os.path.abspath(
            self.distribution.package_dir[module_name]), '..'))
        if os.path.split(location)[-1] == 'src':
            location = os.path.normpath(os.path.join(location, '..'))

        parameters = dict(
            project_var_name=self.distribution.get_name(),
            module_name=module_name,
            file_or_folder=location,
            fLOG=print
        )

        durl = self.distribution.metadata.download_url
        reg = re.compile("github[.]com/(.+)/")
        owner = reg.findall(durl)
        if owner:
            parameters['github_owner'] = owner[0]
        return parameters


class SetupCommandBuildScript(_SetupCommand):
    description = "Builds short cut scripts, bat or sh."

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from pyquickhelper.pycode import process_standard_options_for_setup
        parameters = self.get_parameters()
        parameters['argv'] = ['build_script']
        process_standard_options_for_setup(**parameters)


class SetupCommandCleanSpace(_SetupCommand):
    description = "Improves code quality, applies autopep8 on all files."

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from pyquickhelper.pycode import process_standard_options_for_setup
        parameters = self.get_parameters()
        parameters['argv'] = ['clean_space']
        process_standard_options_for_setup(**parameters)


class SetupCommandHistory(_SetupCommand):
    description = "Shows history (solved issues)."

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from pyquickhelper.pycode import process_standard_options_for_setup
        parameters = self.get_parameters()
        parameters['argv'] = ['history']
        process_standard_options_for_setup(**parameters)


class SetupCommandLab(_SetupCommand):
    description = (
        "Opens jupyter-lab pointing on the notebook from the documentation")

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from pyquickhelper.loghelper import run_cmd
        parameters = self.get_parameters()
        location = parameters['file_or_folder']
        folder = os.path.join(location, "_doc", "notebooks")
        if not os.path.exists(folder):
            folder = location
        cmd = ["jupyter-lab", "--notebook-dir=%s" % folder,
               "--NotebookApp.token=", "--NotebookApp.password="]
        run_cmd(" ".join(cmd), wait=True, fLOG=print, communicate=False)


class SetupCommandLocalJenkins(_SetupCommand):
    description = "Submits a job to a jenkins server."

    user_options = [
        ('user=', None, 'user'),
        ('password=', None, 'password'),
        ('location=', None,
            'workspace location of the jenkins server, '
            'default is /var/lib/jenkins/workspace'),
        ('url=', None,
            'url of the Jenkins server, '
            'default is http://localhost:8080/'),
    ]

    def initialize_options(self):
        self.user = None
        self.password = None
        self.location = "/var/lib/jenkins/workspace"
        self.url = "http://localhost:8080/"

    def finalize_options(self):
        pass

    def run(self):
        if self.user is None:
            raise ValueError("user cannot be None")
        if self.password is None:
            raise ValueError("password cannot be None")
        from pyquickhelper.pycode import process_standard_options_for_setup
        parameters = self.get_parameters()
        parameters['argv'] = [
            'local_jenkins', self.user, self.password, self.location, self.url]
        parameters['argv'] = [_ for _ in parameters['argv'] if _]
        process_standard_options_for_setup(**parameters)


class SetupCommandNotebook(_SetupCommand):
    description = (
        "Opens jupyter-notebook pointing on the notebook "
        "from the documentation")

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from pyquickhelper.loghelper import run_cmd
        parameters = self.get_parameters()
        location = parameters['file_or_folder']
        folder = os.path.join(location, "_doc", "notebooks")
        if not os.path.exists(folder):
            folder = location
        cmd = ["jupyter-notebook", "--notebook-dir=%s" % folder,
               "--NotebookApp.token=", "--NotebookApp.password="]
        run_cmd(" ".join(cmd), wait=True, fLOG=print, communicate=False)


class SetupCommandSphinx(_SetupCommand):
    description = "Builds documentation."

    user_options = [
        ('layout=', None, 'format generation, default is html,rst.'),
    ]

    def initialize_options(self):
        self.layout = "html,rst"

    def finalize_options(self):
        pass

    def run(self):
        from pyquickhelper.pycode import process_standard_options_for_setup
        parameters = self.get_parameters()
        parameters['argv'] = ['build_sphinx']
        parameters['layout'] = self.layout.split(',')
        process_standard_options_for_setup(**parameters)


class SetupCommandUnitTests(_SetupCommand):
    description = "Runs unit tests."

    user_options = [
        ('covtoken=', None, 'coverage token'),
        ('covcond=', None,
            'only publishes the coverage if this substring is part '
            'of the job name, example: _UT_39_std'),
        ('d=', 'd', 'run only unit under that duration'),
        ('e=', 'e', 'regular expression to select files to run'),
        ('g=', 'g', 'regular expression to exclude files'),
    ]

    def initialize_options(self):
        self.covtoken = None
        self.covcond = '_UT_%d%d_std' % sys.version_info[:2]
        self.d = None
        self.e = None
        self.g = None

    def finalize_options(self):
        pass

    def run(self):
        from pyquickhelper.pycode import process_standard_options_for_setup
        parameters = self.get_parameters()
        parameters['argv'] = ['unittests']
        if self.covtoken is not None:
            parameters['covtoken'] = self.covtoken
        if self.covtoken is not None:
            parameters['covtoken'] = (
                self.covtoken, "'%s' in outfile" % self.covcond)
        if self.d is not None:
            parameters['argv'].extend(['-d', '%s' % self.d])
        if self.e is not None:
            parameters['argv'].extend(['-e', '"%s"' % self.e])
        if self.g is not None:
            parameters['argv'].extend(['-g', '"%s"' % self.g])
        process_standard_options_for_setup(**parameters)


class SetupCommandUnitTestGUI(_SetupCommand):
    description = "Runs all unit tests whose name include substring GUI."

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from pyquickhelper.pycode import process_standard_options_for_setup
        parameters = self.get_parameters()
        parameters['argv'] = ['unittests_GUI']
        process_standard_options_for_setup(**parameters)


class SetupCommandUnitTestLONG(_SetupCommand):
    description = "Runs all unit tests whose name include substring LONG."

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from pyquickhelper.pycode import process_standard_options_for_setup
        parameters = self.get_parameters()
        parameters['argv'] = ['unittests_LONG']
        process_standard_options_for_setup(**parameters)


class SetupCommandUnitTestSKIP(_SetupCommand):
    description = "Runs all unit tests whose name include substring SKIP."

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from pyquickhelper.pycode import process_standard_options_for_setup
        parameters = self.get_parameters()
        parameters['argv'] = ['unittests_SKIP']
        process_standard_options_for_setup(**parameters)


class SetupCommandVersion(_SetupCommand):
    description = (
        "Retrieves the commit number from git and writes it "
        "in version.txt.")

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from pyquickhelper.pycode import process_standard_options_for_setup
        parameters = self.get_parameters()
        parameters['argv'] = ['write_version']
        process_standard_options_for_setup(**parameters)
