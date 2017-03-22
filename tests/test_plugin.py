# -*- coding: utf-8 -*-
import pytest
import decimal
import conftest
from guetzli_export_plugin import *

class TestPlugin(object):
    def test_calc_best_step(self):
        plugin = Plugin(Canvas(None))
        dec = plugin.calc_best_step().quantize(Decimal('.0000000'), rounding=decimal.ROUND_HALF_UP)
        assert Decimal(0.00822) == dec

if __name__ == '__main__':
    pytest.main("--capture=sys")
