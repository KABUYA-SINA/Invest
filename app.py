import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

st.title('Invest Portolio')

assets = st.text_input("Fournissez vos actifs (séparés par une virgule - 3 actifs)", "AAPL, MSFT, GOOGL")
start = st.date_input("Définissez une date de début pour votre analyse", value = pd.to_datetime('2022-06-01 00:00:00+00:00'))
data = yf.download(assets, start=start)['Adj Close']

if assets:
    data_list = [item.strip() for item in assets.split(",")]
    try:
        if len(data_list) <3:
            raise ValueError("You need at least 3 actifs")
    except Exception:
        st.error('Something went wrong. Please enter 3 actifs')


taux_journalier = data.pct_change()
cumul_du_taux_journalier = (taux_journalier + 1).cumprod() - 1
cumul_du_taux_portfolio_par_jour = cumul_du_taux_journalier.mean(axis=1)

analyse_comparative = yf.download("^GSPC", start=start)['Adj Close']
analyse_comparative_taux = analyse_comparative.pct_change()
cumul_analyse_comparative = (analyse_comparative_taux + 1).cumprod() - 1

calcul_risque = (np.ones(len(taux_journalier.cov()))/len(taux_journalier.cov()))
portolio_risque = (calcul_risque.dot(taux_journalier.cov()).dot(calcul_risque)) ** (1/2)

st.subheader("Analyse comparative du portefeuille et de l'évolution de l'indice")

cumul_analyse_comparative = cumul_analyse_comparative.tz_localize('Etc/UCT')

creation_courbe = pd.concat([cumul_analyse_comparative, cumul_du_taux_portfolio_par_jour], axis=1)
creation_courbe.columns = ['S&P500 Performance', 'Portfolio Performance']

st.line_chart(data=creation_courbe)
st.subheader("Risque Porfolio")
portolio_risque

st.subheader("Risque d'Analyse comparative")
analyse_risques = analyse_comparative_taux.std()
analyse_risques

st.subheader("Composition du Portfolio")
fig, ax = plt.subplots()
myexplode = [0.01, 0.01, 0.02]
colors = ["#edcc6f","#99dde7", "#CFFFE5"]
ax.pie(calcul_risque, labels=data.columns, autopct="%1.1f%%", textprops={"color" : "black"}, explode = myexplode, colors = colors)
plt.legend(title = "Portfolio", loc="upper left")

st.pyplot(fig)
