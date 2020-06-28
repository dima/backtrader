#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Copyright (C) 2015-2020 Daniel Rodriguez

#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt

def is_btresult(result):
    return isinstance(result, list) and isinstance(result[0], bt.Strategy) and len(result) > 0

def is_optresult(result):
    return isinstance(result, list) and \
           isinstance(result[0], list) and \
           len(result[0]) > 0 and \
           isinstance(result[0][0], (bt.OptReturn, bt.Strategy)) and \
           len(result) > 0

def is_ordered_optresult(result):
    return isinstance(result, bt.OrderedOptResult)