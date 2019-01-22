import backtrader as bt
from typing import Dict, Optional, List, Union
import math
import numbers
from datetime import datetime
import logging

try:
    import pandas
except ImportError:
    raise ImportError(
        'Pandas seems to be missing. Needed for bokeh plotting support')

_logger = logging.getLogger(__name__)


def get_nondefault_params(params: object) -> Dict[str, object]:
    return {key: params._get(key) for key in params._getkeys() if not params.isdefault(key) and key != 'plotname'}


def get_params_str(params: Optional[bt.AutoInfoClass], number_format) -> str:
    user_params = get_nondefault_params(params)

    def get_value_str(name, value, number_format):
        if name == "timeframe":
            return bt.TimeFrame.getname(value, 1)
        elif isinstance(value, str):
            return value
        elif isinstance(value, int):
            return str(value)
        elif isinstance(value, list):
            return ','.join(value)
        else:
            format_str = number_format.split('.')
            if len(format_str) == 2:
                decimal_points = len(format_str[1])
            else:
                decimal_points = 2
            if isinstance(value, numbers.Number):
                return "{:.{}f}".format(value, decimal_points)
            else:
                return "{}".format(value)

    plabs = ["{}: {}".format(x, get_value_str(x, y, number_format)) for x, y in user_params.items()]
    plabs = ', '.join(plabs)
    return plabs


def get_strategy_label(strategycls, params, number_format):
    if strategycls is None:
        return get_params_str(params, number_format)
    else:
        label = strategycls.__name__
        plabs = get_params_str(params, number_format)
        return "{} [{}]".format(label, plabs)


def nanfilt(x: List) -> List:
    """filters all NaN values from a list"""
    return [value for value in x if not math.isnan(value)]


def resample_line(line, line_clk, new_clk):
    """Resamples data line to a new clock. Missing values will be filled with NaN."""
    if new_clk is None:
        return line

    new_line = []
    next_idx = len(line_clk) - 1
    for sc in new_clk:
        for i in range(next_idx, 0, -1):
            v = line_clk[-i]
            if sc == v:
                # exact hit
                new_line.append(line[-i])
                next_idx = i
                break
        else:
            new_line.append(float('nan'))
    return new_line


def convert_to_pandas(strat_clk, obj: bt.LineSeries, start: datetime=None, end: datetime=None, name_prefix: str="") -> pandas.DataFrame:
    df = pandas.DataFrame()
    for lineidx in range(obj.size()):
        line = obj.lines[lineidx]
        linealias = obj.lines._getlinealias(lineidx)
        if linealias == 'datetime':
            continue
        data = line.plotrange(start, end)

        ndata = resample_line(data, obj.lines.datetime.plotrange(start, end), strat_clk)
        logging.info("Filled_line: {}: {}".format(linealias, str(ndata)))

        df[name_prefix + linealias] = ndata

    df[name_prefix + 'datetime'] = [bt.num2date(x) for x in strat_clk]
    return df


def get_data_obj(ind: Union[bt.Indicator, bt.LineSeriesStub]):
    """obj can be a data object or just a single line (in case indicator was created with an explicit line)"""
    while True:
        if isinstance(ind, bt.LineSeriesStub):
            return ind.owner
        elif isinstance(ind, bt.Indicator):
            ind = ind.data
        else:
            return ind