

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def load_and_analyze_data(filepath, max_hr):
    # 1. Daten aus der echten Datei laden
    df = pd.read_csv(filepath)

    # TRICK: Da 'Duration' immer 1 ist, erstellen wir eine fortlaufende Sekunden-Spalte
    # range(len(df)) zählt einfach von 0 bis zur Gesamtzahl der Zeilen hoch
    df["Zeit_Sekunden"] = range(len(df))

    # Da 'PowerOriginal' manchmal NaN/leere Werte am Anfang hat, füllen wir sie mit 0
    df["PowerOriginal"] = df["PowerOriginal"].fillna(0)

    # 2. Basis-Statistiken berechnen
    mean_power = df["PowerOriginal"].mean()
    max_power = df["PowerOriginal"].max()

    # 3. Herzfrequenz-Zonen definieren (nach % der eingegebenen max. HF)
    zones = {
        "Zone 1 (Regeneration)": (0, 0.60 * max_hr),
        "Zone 2 (Grundlagenausdauer 1)": (0.60 * max_hr, 0.70 * max_hr),
        "Zone 3 (Grundlagenausdauer 2)": (0.70 * max_hr, 0.80 * max_hr),
        "Zone 4 (Entwicklungsbereich)": (0.80 * max_hr, 0.90 * max_hr),
        "Zone 5 (Spitzenbereich)": (0.90 * max_hr, float("inf")),
    }

    # Funktion zur Zuweisung der Zone pro Zeile
    def get_zone(hr):
        if pd.isna(hr):
            return "Keine HF-Daten"
        for zone_name, (low, high) in zones.items():
            if low <= hr < high:
                return zone_name
        return "Unbekannt"

    df["Zone"] = df["HeartRate"].apply(get_zone)

    # 4. Zeit in den Zonen berechnen
    zone_counts = df["Zone"].value_counts()

    # 5. Durchschnittliche Leistung pro Zone
    zone_power = df.groupby("Zone")["PowerOriginal"].mean()

    return df, mean_power, max_power, zone_counts, zone_power, zones

# --- INTERFACE (Streamlit) ---
st.title(" Aktivitäts- & Leistungsanalyse")

# Dynamische Eingabe der maximalen Herzfrequenz durch den Nutzer
max_hr_input = st.number_input(
    "Bitte maximale Herzfrequenz (max HF) eingeben:",
    min_value=100,
    max_value=250,
    value=190,  # Standardwert
)

try:
    # Daten verarbeiten
    df, mean_p, max_p, z_counts, z_power, zones_dict = load_and_analyze_data(
        "data/activity(1).csv", max_hr_input
    )

    # Kennzahlen oben anzeigen
    col1, col2 = st.columns(2)
    col1.metric("Mittelwert Leistung", f"{mean_p:.1f} W")
    col2.metric("Maximalwert Leistung", f"{max_p:.1f} W")

    # --- INTERAKTIVER PLOT (Plotly) ---
    st.subheader("Leistung und Herzfrequenz über die Zeit")

    fig = go.Figure()

    # 1. Linie: Leistung (Linke Y-Achse) -> Nutzt 'Duration' als X-Achse
    fig.add_trace(
        go.Scatter(
            x=df["Duration"],
            y=df["PowerOriginal"],
            name="Leistung (Watt)",
            line=dict(color="rgba(28, 115, 232, 0.7)", width=1.5),
            yaxis="y1",
        )
    )

    # 2. Linie: Herzfrequenz (Rechte Y-Achse)
    fig.add_trace(
        go.Scatter(
            x=df["Duration"],
            y=df["HeartRate"],
            name="Herzfrequenz (bpm)",
            line=dict(color="rgba(232, 28, 28, 0.8)", width=2),
            yaxis="y2",
        )
    )

    # Achsen-Layout konfigurieren
    fig.update_layout(
    xaxis=dict(title="Dauer (in Sekunden)"),
    yaxis=dict(
        title=dict(text="Leistung (Watt)", font=dict(color="#1c73e8")),
    ),
    yaxis2=dict(
        title=dict(text="Herzfrequenz (bpm)", font=dict(color="#e81c1c")),
        overlaying="y",
        side="right",
    ),
    legend=dict(x=0, y=1.1, orientation="h"),
    template="plotly_white",
)
    # HF-Zonen als farbige Hintergründe (Shapes) hinterlegen
    colors = [
        "rgba(200, 200, 200, 0.08)",  # Grau
        "rgba(0, 255, 0, 0.08)",  # Grün
        "rgba(255, 255, 0, 0.08)",  # Gelb
        "rgba(255, 165, 0, 0.08)",  # Orange
        "rgba(255, 0, 0, 0.08)",  # Rot
    ]
    shapes = []
    for (zone_name, (low, high)), color in zip(zones_dict.items(), colors):
        if high == float("inf"):
            high = df["HeartRate"].max() + 10 if pd.notna(df["HeartRate"].max()) else 220
        shapes.append(
            dict(
                type="rect",
                xref="x",
                yref="y2",
                x0=df["Duration"].min(),
                x1=df["Duration"].max(),
                y0=low,
                y1=high,
                fillcolor=color,
                layer="below",
                line=dict(width=0),
            )
        )

    fig.update_layout(shapes=shapes)
    st.plotly_chart(fig, use_container_width=True)

    # --- TABELLARISCHE AUSWERTUNG ---
    st.subheader(" Zonen-Auswertung")

    # Tabelle für die Abgabe hübsch zusammenbauen
    summary_df = pd.DataFrame(
        {
            "Zeit in Zone (Sekunden)": z_counts,
            "Ø Leistung in Zone (Watt)": z_power,
        }
    )

    # Index-Reihenfolge sortieren, damit Zone 1 oben steht
    expected_order = [
        "Zone 1 (Regeneration)",
        "Zone 2 (Grundlagenausdauer 1)",
        "Zone 3 (Grundlagenausdauer 2)",
        "Zone 4 (Entwicklungsbereich)",
        "Zone 5 (Spitzenbereich)",
    ]
    summary_df = summary_df.reindex(expected_order).fillna(0)

    # Formatierung für die Anzeige im Webinterface
    st.dataframe(
        summary_df.style.format(
            {
                "Zeit in Zone (Sekunden)": "{:,.0f}",
                "Ø Leistung in Zone (Watt)": "{:.1f} W",
            }
        )
    )

except FileNotFoundError:
    st.error(
        "Die Datei 'activity(1).csv' wurde nicht im Ordner gefunden. Bitte platziere sie genau hier."
    )