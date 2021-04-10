"""
Defines additional setup commands.
"""
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
