import numpy as np
import pandas as pd
import requests
import yfinance as yf


def get_yfinance_data(start_year, tickers):
    """
    queries yfinance and keeps tickers from S&P that existed and remained from start year to end 2023
    computes returns and stores them as csv files: 
    d = daily, m = monthly
    stocks = universe, spx = benchmark

    start_year: starting year
    """

    
    prices = yf.download(tickers, start=f"{start_year}-01-01", end='2022-12-31')['Adj Close'].dropna(axis=1)
    prices.index = pd.to_datetime(prices.index)

    d_stocks = np.log(prices/prices.shift(1)).dropna()
    m_stocks = d_stocks.resample('M').sum()
 
    d_spx = d_stocks.iloc[:,-1]
    m_spx = m_stocks.iloc[:,-1]
 
    d_stocks = d_stocks.iloc[:,:-1]
    m_stocks = m_stocks.iloc[:,:-1]

    d_stocks.to_csv(f'data/d_stocks_{start_year}.csv')
    m_stocks.to_csv(f'data/m_stocks_{start_year}.csv')


def get_weights_slickcharts():
    df = pd.read_html(requests.get('https://www.slickcharts.com/sp500',
                        headers={'User-agent': 'Mozilla/5.0'}).text)[0]

    df['weights'] = df['Portfolio%'].str.replace('%', '').astype(float)
    df = df[['Symbol','weights']].rename(columns={"Symbol":"ticker"})
    df.set_index('ticker', inplace=True)

    df.to_csv('data/sp_weights_2023.csv')



def calc_alphas(excess, vol, breadth, ir=1.5):
    """
    calculates alphas cross-sectionally according to formula given in paper, from Grinold & Kahn 1971.

    excess: sequence: excess returns
    vol: sequence: a pd.Series of realized annualized vol of excess returns. Is this an expanding or rolling window?
    breadth: scalar: number of bets
    ir: scalar: desired ex-ante information ratio
    """
    # z-score and add noise
    excess = excess.sub(excess.mean()).div(excess.std())
    raw = excess + np.random.standard_normal()
    # calculate information coeff
    ic = ir * np.sqrt(12 * breadth)
    # alphas
    alphas = ic * raw * vol

    return alphas

