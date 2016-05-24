import plotly
import pandas
import numpy as np

from datetime import datetime
from datetime import time as dt_tm
from datetime import date as dt_date

import plotly.tools as plotly_tools
from plotly.graph_objs import *

import os
import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()
from matplotlib.finance import quotes_historical_yahoo
import matplotlib.pyplot as plt

from scipy.stats import gaussian_kde

from IPython.display import HTML

plotly.sign_in("jackp", "XXXX")


date1 = dt_date(2014, 1, 1)
date2 = dt_date(2014, 12, 12)

tickers = ['AAPL', 'GE', 'IBM', 'KO', 'MSFT', 'PEP']
prices = []
for ticker in tickers:
    quotes = quotes_historical_yahoo(ticker, date1, date2)
    prices.append( [q[1] for q in quotes] )


# We have all the stock prices in a list of lists - use the code snippet below to convert this into a Pandas dataframe.
df = pandas.DataFrame( prices ).transpose()
df.columns = tickers
df.head()