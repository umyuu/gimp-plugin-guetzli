# -*- coding: utf-8 -*-
# License: MIT License
import os
import time
from collections import OrderedDict
import subprocess
import json
import glob
import sys

try:
    from gimpfu import *
    isGIMP = True
except ImportError:
    isGIMP = False


class ProgressBar(object):
    def __init__(self):
        self.value = 0
        self.step = 1
        if isGIMP:
            gimp.progress_init("Save guetzli ...")

    def perform_step(self):
        self.value += self.step
        if isGIMP:
            gimp.progress_update(self.value)


class Plugin(object):
    JSON = None

    def __init__(self):
        self.base_dir = os.path.dirname(__file__)
        Plugin.load_setting()
        node = Plugin.JSON['COMMAND']
        self.cmd = self.search_command(node['FILE']['PREFIX'], node['FILE']['LOWER_LIMIT'])
        self.params = OrderedDict()
        self.is_verbose = node['PARAMS']['-verbose'].upper() == 'TRUE'

    def search_command(self, target, lower_limit):
        """ search guetzli
        :param target:
        :param lower_limit:
        :return:file name
                order by find first
        """
        for file in glob.glob(os.path.join(self.base_dir, target)):
            # skip plugin file
            if os.path.getsize(file) >= int(lower_limit):
                return file
        raise Exception('File Not Found\n{0}\n{1}'.format(self.base_dir, target[:-1]))

    @staticmethod
    def load_setting():
        """
        load json
        :return:json data
        """
        if Plugin.JSON is None:
            # .py => .json
            file_name = Plugin.with_suffix(__file__, '.json')
            try:
                with open(file_name, 'r') as file:
                    Plugin.JSON = json.load(file)
            except:
                raise Exception('File Not Found\n{0}'.format(file_name))
        return Plugin.JSON

    @staticmethod
    def with_suffix(file, suffix):
        return os.path.splitext(file)[0] + suffix

    def set_quality(self, quality):
        self.params['-quality'] = int(quality)
        return self

    def get_args(self):
        """
            guetzli | params | in | out
        :return:
        """
        args = [self.cmd]
        # add command line parameter
        for k in self.params.keys():
            args.append(k)
            args.append(str(self.params[k]))
        if self.is_verbose:
            args.append('-verbose')
        input_file = Plugin.get_input_filename()
        output_file = Plugin.with_suffix(input_file, '.jpeg')
        args.append(input_file)
        args.append(output_file)
        return args

    def run(self):
        cmd = self.get_args()
        if not isGIMP:
            print(' '.join(cmd))
        try:
            subprocess.call(cmd)
        except Exception as ex:
            raise

    @staticmethod
    def get_input_filename():
        """

        :return: unicode filename
        """
        name = ''
        if isGIMP:
            image = gimp.image_list()[0]
            name = image.filename
        else:
            name = '.\\test.png'
        # suffix check
        supported = tuple(Plugin.JSON['COMMAND']['SUFFIX'])
        if not name.endswith(supported):
            raise Exception('UnSupported File Type\n{0}'.format(name))
        if isGIMP:
            name = r'{0}'.format(name)
        else:
            name = '{0}'.format(name)
        return name

    @staticmethod
    def main(quality):
        plugin = Plugin()
        plugin.set_quality(quality)
        plugin.run()

if isGIMP:
    register(
        proc_name="python_fu_guetzli_export",
        blurb="",
        help="",
        author="umyu",
        copyright="umyu",
        date="2017/3/20",
        label="Save guetzli ...",
        imagetypes="*",
        params=[
            (PF_SLIDER, "quality", "quality", 95, (85, 100, 1))
        ],
        results=[],
        function=Plugin.main,
        menu="<Image>/File/Export/"
    )
    main()
else:
    Plugin.main(95)
