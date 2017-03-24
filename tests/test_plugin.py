# -*- coding: utf-8 -*-
import pytest
import decimal
import conftest
from guetzli_export_plugin import *

class TestPlugin(object):
    def test_calc_best_step(self):
        plugin = Plugin(Canvas(None))
        context = decimal.getcontext()
        context.rounding = rounding=decimal.ROUND_HALF_UP
        dec1 = plugin.calc_best_step().quantize(Decimal('.0000000'))
        dec2 = Decimal(0.0337655).quantize(Decimal('.0000000'))
        assert dec1 == dec2

if __name__ == '__main__':
    pytest.main("--capture=sys")
