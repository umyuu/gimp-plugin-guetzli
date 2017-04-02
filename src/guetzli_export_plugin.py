# -*- coding: utf-8 -*-
# License: MIT License
# Plugin EntryPoint: Plugin.main
# Python 2.7.10
import glob
import json
import locale
import os
import subprocess
from collections import OrderedDict
import threading
from decimal import Decimal

try:
    from gimpfu import *
    gettext.install("gimp20-python", gimp.locale_directory, unicode=True)
    isGIMP = True
except ImportError:
    isGIMP = False


class ProgressBar(object):
    def __init__(self, step=0.01):
        """
            Cyclic ProgressBar
            GIMP GUI Update
        """
        self.value = Decimal(0)
        self._step = Decimal(step)
        # <blockquote cite="https://developer.gimp.org/api/2.0/libgimp/libgimp-gimpprogress.html">
        # gimp_progress_update
        # percentage :Percentage of progress completed (in the range from 0.0 to 1.0).
        # </blockquote>
        self.minimum = Decimal(0)
        self.maximum = Decimal(1)
    @property
    def step(self):
        return self._step
    @step.setter
    def step(self, value):
        self._step = value
    def perform_step(self):
        """
            value increment
        :return: None
        """
        self.value += self.step
        if isGIMP:
            gimp.progress_update(self.value)
        else:
            print(self.value)
        if self.value >= self.maximum:
            self.value = self.minimum

class Canvas(object):
    """
        Canvas Class Adapter
        Gimp Image Class / Script Debugging interface
        @pattern Adapter
    """
    def __init__(self, image, filename=None, width=0, height=0, dirty=False):
        """
        :param image: is None Script Debugging
        :param filename:
        :param width:
        :param height:
        :param dirty: True…Unsaved, False…Saved
        """
        if image is not None:
            self.filename = image.filename
            self.width = image.width
            self.height = image.height
            self.dirty = image.dirty
        else:
            self.filename = filename
            self.width = width
            self.height = height
            self.dirty = dirty
    @property
    def size(self):
        return self.width * self.height
class Resources(object):
    @staticmethod
    def load():
        """
        load json file
        :return:json data
        """
        # .py => .json
        file_name = Plugin.with_suffix(__file__, '.json')
        try:
            with open(file_name, 'r') as infile:
                return json.load(infile)
        except:
            raise
class Plugin(object):
    JSON = None

    def __init__(self, canvas):
        self.canvas = canvas
        self.progress = ProgressBar()
        self.progress.step = self.calc_best_step()
        self.base_dir = os.path.dirname(__file__)
        Plugin.JSON = Resources.load()
        node = Plugin.JSON['COMMAND']
        self.cmd = self.search_command(node['FILE'])
        self.params = OrderedDict(node['PARAMS'])
        self.is_new_shell = node['NEW_SHELL'].upper() == 'TRUE'
        self.output_extension = '.jpeg'
    def search_command(self, node):
        """ search guetzli
        :param node:
        :return:file name
                order by find first
        """
        target = node['PREFIX']
        lower_limit = int(node['LOWER_LIMIT'])
        link = node['DOWNLOAD']['LINK']
        for exe_file in glob.glob(os.path.join(self.base_dir, target)):
            # skip plugin file
            if os.path.getsize(exe_file) > lower_limit:
                return exe_file
        raise Exception('File Not Found\n{0}\nPlease download {1}\n{2}'.format(self.base_dir, target[:-1], link))

    @staticmethod
    def with_suffix(file_name, suffix):
        return os.path.splitext(file_name)[0] + suffix
    def set_quality(self, quality):
        self.params['--quality'] = int(quality)
        return self
    def set_extension(self, extension):
        self.output_extension = extension
        return self
    def get_args(self):
        """
            command line arguments
        :return: guetzli , params , in , out
        """
        args = [self.cmd]
        # add command line parameter
        for k in self.params.keys():
            args.append(k)
            args.append(str(self.params[k]))
        input_file = '"{0}"'.format(self.canvas.filename)
        output_file = '"{0}"'.format(Plugin.with_suffix(self.canvas.filename, self.output_extension))
        args.append(input_file)
        args.append(output_file)
        return args
    def calc_best_step(self):
        """
          ProgressBar step calc
          <blockquote cite="https://github.com/google/guetzli">
          Guetzli uses a significant amount of CPU time. You should count on using about 1 minute of CPU per 1 MPix of input image.
          </blockquote>
        :return: ProgressBar#maximum / Per second
        """
        # 1 minute => Thread#join timeout elapsed
        seconds = Decimal(self.canvas.size) / Decimal(1000000) * Decimal(60)
        return self.progress.maximum / seconds
    def validation(self):
        name = self.canvas.filename
        # New Image => filename:None
        if self.canvas.dirty:
            raise Exception('Please save the image\n{0}'.format(name))
        # suffix check
        supported = tuple(Plugin.JSON['COMMAND']['SUFFIX'])
        if not name.endswith(supported):
            raise Exception('UnSupported File Type\n{0}'.format(name))

    def run(self):
        """
        Thread#start & join
        GIMP GUI Update
        :return: None
        """
        self.validation()
        cmd = self.get_args()
        if not isGIMP:
            print(' '.join(cmd))
        cmd = u' '.join(cmd)
        # fix: python 2.7 unicode file bug
        # http://stackoverflow.com/questions/9941064/subprocess-popen-with-a-unicode-path
        cmd = cmd.encode(locale.getpreferredencoding())
        in_params = [cmd, self.is_new_shell]
        out_params = [None, '']
        if isGIMP:
            gimp.progress_init("Save guetzli ...")
            #gimp.message(in_params[0])
        lock = threading.RLock()
        t = threading.Thread(target=Plugin.run_thread, args=(in_params, lock, out_params))
        t.start()
        while t.is_alive():
            t.join(timeout=1)
            self.progress.perform_step()
        with lock:
            # not Success
            if out_params[0] != 0:
                raise Exception(out_params[1])
    @staticmethod
    def run_thread(in_params, lock, out_params):
        """
        :param in_params: cmd , is_new_shell
        :param lock:
        :param out_params: return code , message
        :return:None
        """
        exception = None
        try:
            subprocess.check_output(in_params[0], shell=in_params[1], stderr=subprocess.STDOUT)
            return_code = 0
        except subprocess.CalledProcessError as ex:
            return_code = ex.returncode
            exception = ex.output
        with lock:
            out_params[0] = return_code
            if exception is not None:
                out_params[1] = exception
    @staticmethod
    def main(image, drawable, ext, quality):
        """
        plugin entry point
        :param image:Selected Image      GIMP menu<Image> required
        :param drawable:drawable Image   GIMP menu<Image> required
        :param ext: output file extension
        :param quality:output file quality
        :return:
        """
        try:
            plugin = Plugin(Canvas(image))
            plugin.set_extension(ext)
            plugin.set_quality(quality)
            plugin.run()
        except Exception as ex:
            raise
            #if isGIMP:
            #    gimp.message(ex.message)


if isGIMP:
    register(
        proc_name="python_fu_guetzli_export",
        blurb="Please click the OK button\n after saving the image",
        help="",
        author="umyu",
        copyright="umyu",
        date="2017/3/25",
        label="Save guetzli ...",
        imagetypes="RGB",
        params=[
            (PF_IMAGE, "image", "Input image", None),
            (PF_DRAWABLE, "drawable", "Input drawable", None),
            (PF_STRING, "extension", "File extension", '.jpeg'),
            (PF_SLIDER, "quality", "quality", 95, (84, 100, 1)),
        ],
        results=[],
        function=Plugin.main,
        menu="<Image>/File/Export/",
        domain=("gimp20-python", gimp.locale_directory)
    )
    main()
else:
    if __name__ == '__main__':
        plugin = Plugin(Canvas(None, '.\\test.png', 800, 617))
        plugin.run()
