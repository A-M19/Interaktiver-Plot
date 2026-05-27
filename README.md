# Interaktiver-Plot
# Interaktive Aktivitäts- & Leistungsanalyse

Dieses Streamlit-Projekt dient der sportwissenschaftlichen Auswertung von Leistungsdaten (in Watt) und der Herzfrequenz (in bpm) aus einem Belastungstest. Die Daten werden sekündlich eingelesen, in fünf physiologische Belastungszonen eingeteilt und interaktiv visualisiert.

# Funktionen
* Duale Y-Achsen-Visualisierung: Leistung (Watt) und Herzfrequenz (bpm) sauber getrennt in einem Plotly-Diagramm.
* Dynamische Zonenbänder: Farbliche Hinterlegung der 5 Herzfrequenz-Zonen basierend auf der individuellen $\text{HF}_{\max}$ des Nutzers.
* Zonenspezifische Auswertung: Tabellarische Übersicht über die exakte Verweildauer (in Sekunden) und die durchschnittliche erbrachte Leistung pro Zone.

# Installation & Start

Das Projekt verwendet das PDM-Paketmanagementsystem.

1. Abhängigkeiten installieren:
   Bash
   pdm install

2. Streamlit App starten:
    Bash
    streamlit run main.py