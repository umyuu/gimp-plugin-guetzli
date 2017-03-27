# -*- coding: utf-8 -*-
import pytest
from decimal import *
import conftest
from guetzli_export_plugin import Canvas, Plugin

class TestPlugin(object):
    def test_calc_best_step(self):
        plugin = Plugin(Canvas(None, '.\\test.jpg', 800, 617))
        context = getcontext()
        context.rounding = rounding=ROUND_HALF_UP
        dec1 = plugin.calc_best_step().quantize(Decimal('.0000000'))
        dec2 = Decimal(0.0337655).quantize(Decimal('.0000000'))
        assert dec1 == dec2
    def test_down_sampling_error(self):
        canvas = Canvas(None, '.\\down_sampling_error.jpg', 980, 551)
        plugin = Plugin(canvas)
        with pytest.raises(Exception):
            plugin.run()
if __name__ == '__main__':
    pytest.main("--capture=sys")
