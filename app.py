import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt

st.title('Invest Portfolio')

assets = st.text_input("Fournissez vos actifs (séparés par une virgule - 3 actifs)", "AAPL, MSFT, GOOGL")
start = st.date_input("Définissez une date de début pour votre analyse", value=pd.to_datetime('2022-06-01'))

if assets:
    data_list = [item.strip() for item in assets.split(",") if item.strip()]
    if len(data_list) != 3:
        if len(data_list) < 3:
            st.error("Vous devez entrer au moins 3 actifs.")
        else:
            st.error("Vous ne pouvez pas entrer plus de 3 actifs.")
    else:
        try:
            # Download data
            data = yf.download(data_list, start=start)['Adj Close']
            taux_journalier = data.pct_change()
            if taux_journalier is not None:
                cumul_du_taux_journalier = (taux_journalier + 1).cumprod() - 1
                cumul_du_taux_portfolio_par_jour = cumul_du_taux_journalier.mean(axis=1)

                analyse_comparative = yf.download("^GSPC", start=start)['Adj Close']
                analyse_comparative_taux = analyse_comparative.pct_change()
                cumul_analyse_comparative = (analyse_comparative_taux + 1).cumprod() - 1

                calcul_risque = (np.ones(len(taux_journalier.columns)) / len(taux_journalier.columns))

                portolio_risque = np.sqrt(taux_journalier.cov().dot(np.ones(len(data.columns))) / len(data.columns))

                # Visualization
                st.subheader("Analyse comparative du portefeuille et de l'évolution de l'indice")
                creation_courbe = pd.concat([cumul_analyse_comparative.tz_localize('Etc/UCT'), cumul_du_taux_portfolio_par_jour], axis=1)
                creation_courbe.columns = ['S&P500 Performance', 'Portfolio Performance']
                st.line_chart(data=creation_courbe)

                st.subheader("Risque Portfolio")
                st.write(portolio_risque)

                # Portfolio Composition
                fig, ax = plt.subplots()
                myexplode = [0.01] * len(data.columns)
                colors = ["#edcc6f", "#99dde7", "#CFFFE5"]
                ax.pie(calcul_risque, labels=data.columns, autopct="%1.1f%%", textprops={"color": "black"}, explode=myexplode, colors=colors)
                plt.legend(title="Portfolio", loc="upper left")
                st.pyplot(fig)
        except Exception as e:
            st.error(f"Une erreur s'est produite : {e}")
