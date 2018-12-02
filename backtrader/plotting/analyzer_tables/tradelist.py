from backtrader.plotting.bokeh.datatable import ColummDataType

# ('ref', 'size', 'pricein', 'priceout', 'chng%', 'pnl', 'pnl%', 'cumpnl', 'nbars', 'mfe%', 'mae%')),

def datatable(self):
    cols = [['Ref', ColummDataType.INT],
            ['Ticker', ColummDataType.STRING],
            ['Size', ColummDataType.INT],
            ['Bars', ColummDataType.INT],
            ['PriceIn', ColummDataType.FLOAT],
            ['PriceOut', ColummDataType.FLOAT],
            ['Chng%', ColummDataType.FLOAT],
            ['PNL', ColummDataType.FLOAT],
            ['PNL%', ColummDataType.FLOAT],
            ['MFE%', ColummDataType.FLOAT],
            ['MAE%', ColummDataType.FLOAT],
            ]

    # size, price, i, dname, -size * price
    for k, v in self.get_analysis().items():
        cols[0].append(k)
        cols[1].append(v[0][0])
        cols[2].append(v[0][1])
        cols[3].append(v[0][2])
        cols[4].append(v[0][3])
        cols[5].append(v[0][4])
        cols[6].append(v[0][5])
        cols[7].append(v[0][6])
        cols[8].append(v[0][7])
        cols[9].append(v[0][8])
        cols[10].append(v[0][9])

    return "Trades", [cols]