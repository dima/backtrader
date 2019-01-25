#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Copyright (C) 2015, 2016 Daniel Rodriguez
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


import argparse
import collections
import datetime
import io
import logging
import sys
import itertools
import os

import backtrader as bt

# Supported Alpaca timeframe combos
# (TimeFrame.Seconds, 5): 'S5',
# (TimeFrame.Seconds, 10): 'S10',
# (TimeFrame.Seconds, 15): 'S15',
# (TimeFrame.Seconds, 30): 'S30',
# (TimeFrame.Minutes, 1): 'M1',
# (TimeFrame.Minutes, 2): 'M3',
# (TimeFrame.Minutes, 3): 'M3',
# (TimeFrame.Minutes, 4): 'M4',
# (TimeFrame.Minutes, 5): 'M5',
# (TimeFrame.Minutes, 10): 'M10',
# (TimeFrame.Minutes, 15): 'M15',
# (TimeFrame.Minutes, 30): 'M30',
# (TimeFrame.Minutes, 60): 'H1',
# (TimeFrame.Minutes, 120): 'H2',
# (TimeFrame.Minutes, 180): 'H3',
# (TimeFrame.Minutes, 240): 'H4',
# (TimeFrame.Minutes, 360): 'H6',
# (TimeFrame.Minutes, 480): 'H8',
# (TimeFrame.Days, 1): 'D',
# (TimeFrame.Weeks, 1): 'W',
# (TimeFrame.Months, 1): 'M',

TIMEFRAMES = dict(
    seconds=bt.TimeFrame.Seconds,
    minutes=bt.TimeFrame.Minutes,
    days=bt.TimeFrame.Days,
    weeks=bt.TimeFrame.Weeks,
    months=bt.TimeFrame.Months
)

logging.basicConfig(
    format='%(levelname)s: %(message)s',
    level=logging.INFO)

class DownloadStrategy(bt.Strategy):
    params = (
        ('separator', ','),
        ('outfile', None),
    )

    def start(self):
        if self.p.outfile is None:
            self.f = sys.stdout
        else:
            self.f = open(self.p.outfile, 'w')
            logging.info('opened file {}'.format(self.p.outfile))

        headers = 'date,open,high,low,close,volume,openinterest\n'
        self.f.write(headers)

    def stop(self):
        if self.p.outfile:
            logging.info('closing file {}'.format(self.p.outfile))
            self.f.close()

    def next(self):
        fields = list()
        if self.data._timeframe < bt.TimeFrame.Days:
            dt = self.data.datetime.date(0).strftime('%Y-%m-%d')
            tm = self.data.datetime.time(0).strftime('%H:%M:%S')
            fields.append('{} {}'.format(dt, tm))
        else:
            dt = self.data.datetime.date(0).strftime('%Y-%m-%d')
            fields.append(dt)

        o = self.data.open[0]
        fields.append(o)
        h = self.data.high[0]
        fields.append(h)
        l = self.data.low[0]
        fields.append(l)
        c = self.data.close[0]
        fields.append(c)
        v = int(self.data.volume[0])
        fields.append(v)
        oi = int(self.data.openinterest[0])
        fields.append(oi)

        txt = self.p.separator.join(str(x) for x in fields)
        txt += '\n'
        self.f.write(txt)

def alpacadownload():
    args = parse_args()

    logging.debug('Processing input parameters')
    logging.debug('Processing fromdate')
    try:
        fromdate = datetime.datetime.strptime(args.fromdate, '%Y-%m-%d')
    except Exception as e:
        logging.error('Converting fromdate failed')
        logging.error(str(e))
        sys.exit(1)

    logging.debug('Processing todate')
    todate = datetime.datetime.today()
    if args.todate:
        try:
            todate = datetime.datetime.strptime(args.todate, '%Y-%m-%d')
        except Exception as e:
            logging.error('Converting todate failed')
            logging.error(str(e))
            sys.exit(1)

    outfile = '{}_{}-{}-{}.csv'.format(args.timeframe[0].capitalize(), args.ticker, fromdate.strftime('%Y-%m-%d'), todate.strftime('%Y-%m-%d'))
    if args.outfile:
        outfile = args.outfile

    if os.environ.get('ALPACA_KEY') is None or os.environ.get('ALPACA_SECRET_KEY') is None:
        logging.error('ALPACA_KEY and ALPACA_SECRET_KEY environment variables must be set before using this tool.')
        sys.exit(1)

    logging.info('Downloading from Alpaca')
    try:
        cerebro = bt.Cerebro(tz=0)
        astore = bt.stores.AlpacaStore(key_id=os.environ.get('ALPACA_KEY'), secret_key=os.environ.get('ALPACA_SECRET_KEY'), paper=True)
        data = astore.getdata(dataname=args.ticker, timeframe=TIMEFRAMES[args.timeframe], 
            compression=int(args.compression), historical=True, fromdate=fromdate, todate=todate)

        cerebro.adddata(data)

        cerebro.addstrategy(DownloadStrategy, outfile=outfile)
        cerebro.run(stdstats=False)

    except Exception as e:
        logging.error('Downloading data from Alpaca failed')
        logging.error(str(e))
        sys.exit(1)

    logging.info('All operations completed successfully')
    sys.exit(0)

def parse_args():
    parser = argparse.ArgumentParser(
        description='Download Aplaca Finance Data in CSV')

    parser.add_argument('--ticker', required=True,
                        help='Ticker to be downloaded')

    parser.add_argument('--fromdate', required=True,
                        help='Starting date in YYYY-MM-DD format')

    parser.add_argument('--todate', required=False,
                        help='Ending date in YYYY-MM-DD format')

    parser.add_argument('--timeframe', required=False, default='minutes',
                       choices=TIMEFRAMES.keys(),
                       help='What data resolution to use. Can be one of the above choices.')

    parser.add_argument('--compression', required=False, default=1,
                       type=int,
                       help='How to compress the data. Integer')

    parser.add_argument('--outfile', required=False, help='Output file name')

    return parser.parse_args()


