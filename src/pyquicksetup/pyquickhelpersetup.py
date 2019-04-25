"""
@file
@brief  Defines setup commands.
"""
import re
import os
import pprint
from distutils.core import Command


class SetupCommandDisplay(Command):
    description = "Displays information about the setup."

    user_options = [
        ('disp=', None, "Available options '__dict__'"),
    ]

    def initialize_options(self):
        self.disp = "__dict__"

    def finalize_options(self):
        valid = (None, '__dict__')
        if self.disp not in valid:
            raise ValueError("Option disp must be in {}.".format(valid))

    def run(self):
        module_name = self.distribution.packages[0]
        location = os.path.normpath(os.path.join(os.path.abspath(
            self.distribution.package_dir[module_name]), '..'))
        if os.path.split(location)[-1] == 'src':
            location = os.path.normpath(os.path.join(location, '..'))

        parameters = dict(
            project_var_name=self.distribution.get_name(),
            module_name=module_name,
            file_or_folder=location,
            argv=[],
            fLOG=print
        )
        print('---------- PARAMETERS ----------')
        pprint.pprint(parameters)
        print('---------- METADATA ------------')
        pprint.pprint(self.distribution.metadata.__dict__)
        print('---------- DISTRIBUTION --------')
        pprint.pprint(self.distribution.__dict__)


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


class SetupCommandHistory(_SetupCommand):
    description = "Show history (solved issues)."

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
