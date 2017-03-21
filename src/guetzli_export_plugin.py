# -*- coding: utf-8 -*-
# License: MIT License

import glob
import json
import locale
import os
import subprocess
from collections import OrderedDict
import threading

try:
    from gimpfu import *
    isGIMP = True
except ImportError:
    isGIMP = False


class ProgressBar(object):
    def __init__(self):
        self.value = 0
        self.step = 0.1
        self.minimum = 0
        self.maximum = 1
        if isGIMP:
            gimp.progress_init("Save guetzli ...")

    def perform_step(self):
        self.value += self.step
        if isGIMP:
            gimp.progress_update(self.value)
        if self.value >= self.maximum:
            self.value = self.minimum
class Plugin(object):
    JSON = None

    def __init__(self):
        self.base_dir = os.path.dirname(__file__)
        Plugin.load_setting()
        node = Plugin.JSON['COMMAND']
        self.cmd = self.search_command(node['FILE']['PREFIX'], node['FILE']['LOWER_LIMIT'])
        self.params = OrderedDict()
        self.is_verbose = node['PARAMS']['-verbose'].upper() == 'TRUE'
        self.is_new_shell = node['NEW_SHELL'].upper() == 'TRUE'
        self.output_extension = '.jpeg'
        self.input_file = None
        self.output_file = None
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
                with open(file_name, 'r') as infile:
                    Plugin.JSON = json.load(infile)
            except:
                raise Exception('File Not Found\n{0}'.format(file_name))
        return Plugin.JSON

    @staticmethod
    def with_suffix(file_name, suffix):
        return os.path.splitext(file_name)[0] + suffix

    def set_quality(self, quality):
        self.params['-quality'] = int(quality)
        return self
    def set_extension(self, extension):
        self.output_extension = extension
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
        self.set_filename()
        args.append(self.input_file)
        args.append(self.output_file)
        return args

    def run(self):
        cmd = self.get_args()
        if not isGIMP:
            print(' '.join(cmd))
        cmd = u' '.join(cmd)
        # fix: python 2.7 unicode file bug
        # http://stackoverflow.com/questions/9941064/subprocess-popen-with-a-unicode-path
        cmd = cmd.encode(locale.getpreferredencoding())
        try:
            progress = ProgressBar()
            t = threading.Thread(target=Plugin.run_thread, args=(cmd, self.is_new_shell))
            t.start()
            while t.is_alive():
                t.join(timeout=1)
                progress.perform_step()
        except Exception as ex:
            raise
    @staticmethod
    def run_thread(cmd, is_new_shell):
        try:
            subprocess.call(cmd, shell=is_new_shell)
        except Exception:
            pass
    def set_filename(self):
        """

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
            name = '{0}'.format(name)
        else:
            name = '{0}'.format(name)
        self.input_file = '"{0}"'.format(name)
        self.output_file = '"{0}"'.format(Plugin.with_suffix(name, self.output_extension))

    @staticmethod
    def main(ext, quality):
        plugin = Plugin()
        plugin.set_extension(ext)
        plugin.set_quality(quality)
        plugin.run()


if isGIMP:
    register(
        proc_name="python_fu_guetzli_export",
        blurb="Please click the OK button\n after saving the image",
        help="",
        author="umyu",
        copyright="umyu",
        date="2017/3/20",
        label="Save guetzli ...",
        imagetypes="*",
        params=[
            (PF_STRING, "extension", "File extension", '.jpeg'),
            (PF_SLIDER, "quality", "quality", 95, (85, 100, 1)),
        ],
        results=[],
        function=Plugin.main,
        menu="<Image>/File/Export/"
    )
    main()
else:
    Plugin.main('.jpeg', 95)
