import streamlit as st
import pandas as pd
from pathlib import Path
import numpy as np
import math
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import streamlit.components.v1 as components

def scroll_to_top():
    # Piccolo snippet JS che forza lo scroll all'inizio della pagina
    components.html(
        """
        <script>
        const main = window.parent.document.querySelector('section.main');
        if (main) { main.scrollTo(0, 0); }
        </script>
        """,
        height=0,
    )


# --------------------------------------------------------------------
# CONFIGURAZIONE GENERALE DELLA PAGINA
# --------------------------------------------------------------------
st.set_page_config(
    page_title="Modello di Costruzione del Portafoglio",
    layout="centered"
)

# --------------------------------------------------------------------
# STILE GRAFICO – VERSIONE "WOW"
# --------------------------------------------------------------------
st.markdown(
    """
    <style>
        /* Font generale */
        html, body, [class*="css"]  {
            font-family: "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Sfondo generale con leggero gradiente */
        .main {
            background: radial-gradient(circle at 0% 0%, #eef3ff 0, #f7f9fc 45%, #ffffff 100%);
        }

        /* Contenitore centrale più "pulito" e centrato */
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2.5rem;
            max-width: 1150px;
        }

        /* Titolo degli step */
        .step-title {
            font-size: 30px;
            font-weight: 800;
            margin: 0.2rem 0 0.8rem 0;
            color: #003366;
            letter-spacing: 0.5px;
        }

        /* Sottotitolo */
        .step-subtitle {
            font-size: 17px;
            color: #4c5a70;
            margin-bottom: 1.4rem;
        }

        /* Pulsanti Avanti / Indietro */
        .stButton>button {
            background: linear-gradient(135deg, #f2f2f2 0%, #e0e0e0 100%);
            color: #222222;
            border: 1px solid #c2c2c2;
            border-radius: 999px;
            padding: 0.45rem 1.4rem;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            box-shadow: 0 1px 2px rgba(0,0,0,0.10);
            transition: all 0.15s ease-in-out;
        }

        .stButton>button:hover {
            background: linear-gradient(135deg, #ffffff 0%, #e7e7e7 100%);
            box-shadow: 0 3px 6px rgba(0,0,0,0.16);
            transform: translateY(-1px);
        }

        .stButton>button:active {
            box-shadow: 0 1px 2px rgba(0,0,0,0.18);
            transform: translateY(0px);
        }

/* Sidebar più chiara e leggibile */
[data-testid="stSidebar"] {
    background: #f4f5fb;
    color: #111827 !important;
    border-right: 1px solid #d1d5db;
}

/* Titoli nella sidebar */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4 {
    color: #111827 !important;
}

/* Label (radio, select, ecc.) nella sidebar */
[data-testid="stSidebar"] label {
    color: #111827 !important;
}

        /* Radio nella sidebar (step) */
        [data-testid="stSidebar"] .stRadio > label {
            font-weight: 600;
        }

        /* Tabella "tipo card": leggera pulizia generale */
        table {
            font-size: 13px;
        }

        th {
            font-weight: 700;
        }

        /* Dataframe / data_editor leggibili */
        .stDataFrame table, .stDataFrame thead tr th {
            font-size: 12px;
        }

        /* Titolini di sezione (usati come sottotitoli blu) */
        .section-header {
            font-size: 18px;
            font-weight: 700;
            color: #005b96;
            margin-top: 1.2rem;
            margin-bottom: 0.6rem;
        }

        /* Piccole "card" informative azzurre/rosse (riutilizzabili) */
        .info-box {
            background-color: #d7ecff;
            padding: 14px 16px;
            border-radius: 10px;
            color: #000000;
            font-size: 14px;
            line-height: 1.5;
            margin-bottom: 0.8rem;
        }

        .warning-box {
            background-color: #ffe0e0;
            padding: 14px 16px;
            border-radius: 10px;
            color: #7f1d1d;
            font-size: 14px;
            line-height: 1.5;
            margin-bottom: 0.8rem;
        }

        /* Piccolo sottolineato sotto il titolo di step */
        .step-title::after {
            content: "";
            display: block;
            width: 70px;
            height: 3px;
            margin-top: 6px;
            border-radius: 999px;
            background: linear-gradient(90deg, #005b96 0%, #38bdf8 100%);
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------------------------
# FUNZIONE PER MOSTRARE IMMAGINE IN FORMATO RIDOTTO
# --------------------------------------------------------------------
def mostra_immagine(nome_file: str, didascalia: str = ""):
    path = Path(nome_file)
    if path.exists():
        st.image(str(path), caption=didascalia, width=250)


# --------------------------------------------------------------------
# STATO DI SESSIONE
# --------------------------------------------------------------------
if "step_index" not in st.session_state:
    st.session_state.step_index = 0

if "importo" not in st.session_state:
    st.session_state.importo = 0.0

if "orizzonte" not in st.session_state:
    st.session_state.orizzonte = 0.0

if "tolleranza" not in st.session_state:
    st.session_state.tolleranza = "Bassa"

if "canale_prodotti" not in st.session_state:
    st.session_state.canale_prodotti = "Gestioni Patrimoniali"

if "equity_raccomandata" not in st.session_state:
    st.session_state.equity_raccomandata = "0%"

if "equity_scelta" not in st.session_state:
    st.session_state.equity_scelta = "0%"

# Per la selezione dei fondi nello Step 10
if "fondi_step10" not in st.session_state:
    # dict: chiave = nome asset class, valore = DataFrame con fondi + colonne Seleziona / Peso %
    st.session_state.fondi_step10 = {}


if "asset_class_selezionate" not in st.session_state:
    st.session_state.asset_class_selezionate = []


if "equity_scelta_definita" not in st.session_state:
    # False = prima volta che entro nello Step 5
    st.session_state.equity_scelta_definita = False

if "pesi_asset_class" not in st.session_state:
    st.session_state.pesi_asset_class = {}

if "importi_asset_class" not in st.session_state:
    st.session_state.importi_asset_class = {}

if "fondi_step10" not in st.session_state:
    st.session_state.fondi_step10 = {}

lista_step = ["Intro", "Step 1", "Step 2", "Step 3", "Step 4", "Step 5", "GP (stop)", "Step 6", "Focus","Step 7","Step 8","Step 9","Step 10","Step 11","Step 12","Step 13","Step 14"]


# --------------------------------------------------------------------
# CLASSIFICAZIONE ORIZZONTE
# --------------------------------------------------------------------
def classifica_orizzonte(anni: float) -> str:
    anni = float(anni)
    if anni <= 3:
        return "Brevissimo (0-3 Y)"
    if anni <= 5:
        return "Breve (3-5 Y)"
    if anni <= 8:
        return "Medio-Lungo (5-8 Y)"
    if anni <= 10:
        return "Lungo (8-10 Y)"
    return "Molto Lungo (>10 Y)"


# --------------------------------------------------------------------
# TABELLE % AZIONARIO PER LO STEP 5
# --------------------------------------------------------------------
righe_orizzonte = [
    "Brevissimo (0-3 Y)",
    "Breve (3-5 Y)",
    "Medio-Lungo (5-8 Y)",
    "Lungo (8-10 Y)",
    "Molto Lungo (>10 Y)"
]

colonne_tolleranza = ["Bassa", "Medio-Bassa", "Medio-Alta", "Alta"]

# (a) Portafogli prudenti
TABELLA_A = {
    "Brevissimo (0-3 Y)": {"Bassa": "0%",  "Medio-Bassa": "5%",  "Medio-Alta": "10%", "Alta": "15%"},
    "Breve (3-5 Y)":      {"Bassa": "5%",  "Medio-Bassa": "10%", "Medio-Alta": "15%", "Alta": "20%"},
    "Medio-Lungo (5-8 Y)":{"Bassa": "10%", "Medio-Bassa": "15%", "Medio-Alta": "20%", "Alta": "30%"},
    "Lungo (8-10 Y)":     {"Bassa": "15%", "Medio-Bassa": "20%", "Medio-Alta": "30%", "Alta": "40%"},
    "Molto Lungo (>10 Y)":{"Bassa": "20%", "Medio-Bassa": "30%", "Medio-Alta": "40%", "Alta": "60%"},
}

# (b) Approccio “nel mezzo”
TABELLA_B = {
    "Brevissimo (0-3 Y)": {"Bassa": "5%",  "Medio-Bassa": "5%",  "Medio-Alta": "10%", "Alta": "15%"},
    "Breve (3-5 Y)":      {"Bassa": "10%", "Medio-Bassa": "15%", "Medio-Alta": "20%", "Alta": "30%"},
    "Medio-Lungo (5-8 Y)":{"Bassa": "15%", "Medio-Bassa": "20%", "Medio-Alta": "30%", "Alta": "40%"},
    "Lungo (8-10 Y)":     {"Bassa": "20%", "Medio-Bassa": "30%", "Medio-Alta": "40%", "Alta": "50%"},
    "Molto Lungo (>10 Y)":{"Bassa": "30%", "Medio-Bassa": "40%", "Medio-Alta": "50%", "Alta": "60%"},
}

# (c) Portafogli sfidanti
TABELLA_C = {
    "Brevissimo (0-3 Y)": {"Bassa": "10%", "Medio-Bassa": "10%", "Medio-Alta": "15%", "Alta": "20%"},
    "Breve (3-5 Y)":      {"Bassa": "15%", "Medio-Bassa": "20%", "Medio-Alta": "30%", "Alta": "30%"},
    "Medio-Lungo (5-8 Y)":{"Bassa": "20%", "Medio-Bassa": "30%", "Medio-Alta": "40%", "Alta": "50%"},
    "Lungo (8-10 Y)":     {"Bassa": "30%", "Medio-Bassa": "40%", "Medio-Alta": "50%", "Alta": "60%"},
    "Molto Lungo (>10 Y)":{"Bassa": "40%", "Medio-Bassa": "50%", "Medio-Alta": "60%", "Alta": "80%"},
}


import math
import matplotlib.pyplot as plt

# --------------------------------------------------------------------
# DATI DI BASE PER LA COSTRUZIONE DELL'ASSET ALLOCATION (STEP 7)
# --------------------------------------------------------------------
ASSET_CLASSI_AA = [
    "Obbligazionario Euro BT",
    "Obbligazionario Euro MLT",
    "Obbligazionario Euro Corporate",
    "Obbligazionario Globale",
    "Obbligazionario Paesi Emergenti",
    "Obbligazionario Globale High Yield",
    "Azionario Europa/Euro",
    "Azionario Nord America",
    "Azionario Pacifico",
    "Azionario Paesi Emergenti",
    "Azionario Internazionale",
    "Best Ideas",
]

# 13 portafogli di riferimento (0%, 5%, ..., 100% di Equity)
EQUITY_LEVELS = [0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 1.00]

BASE_WEIGHTS = {
    "Obbligazionario Euro BT":            [0.28, 0.27, 0.25, 0.24, 0.23, 0.22, 0.21, 0.18, 0.14, 0.10, 0.08, 0.03, 0.00],
    "Obbligazionario Euro MLT":           [0.36, 0.34, 0.32, 0.30, 0.28, 0.26, 0.25, 0.21, 0.17, 0.13, 0.09, 0.04, 0.00],
    "Obbligazionario Euro Corporate":     [0.21, 0.20, 0.19, 0.16, 0.15, 0.13, 0.12, 0.09, 0.08, 0.06, 0.03, 0.03, 0.00],
    "Obbligazionario Globale":            [0.15, 0.14, 0.14, 0.13, 0.12, 0.12, 0.10, 0.08, 0.07, 0.05, 0.04, 0.03, 0.00],
    "Obbligazionario Paesi Emergenti":    [0.00, 0.00, 0.00, 0.01, 0.01, 0.01, 0.01, 0.02, 0.02, 0.03, 0.03, 0.04, 0.00],
    "Obbligazionario Globale High Yield": [0.00, 0.00, 0.00, 0.01, 0.01, 0.01, 0.01, 0.02, 0.02, 0.03, 0.03, 0.03, 0.00],
    "Azionario Europa/Euro":              [0.00, 0.01, 0.02, 0.03, 0.04, 0.04, 0.04, 0.07, 0.09, 0.12, 0.14, 0.16, 0.20],
    "Azionario Nord America":             [0.00, 0.02, 0.03, 0.04, 0.06, 0.07, 0.08, 0.11, 0.14, 0.17, 0.19, 0.22, 0.26],
    "Azionario Pacifico":                 [0.00, 0.00, 0.00, 0.00, 0.01, 0.01, 0.02, 0.03, 0.04, 0.04, 0.05, 0.06, 0.10],
    "Azionario Paesi Emergenti":          [0.00, 0.00, 0.01, 0.02, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.12],
    "Azionario Internazionale":           [0.00, 0.02, 0.02, 0.04, 0.05, 0.07, 0.08, 0.10, 0.12, 0.15, 0.18, 0.20, 0.24],
    "Best Ideas":                         [0.00, 0.00, 0.02, 0.02, 0.02, 0.03, 0.04, 0.04, 0.05, 0.05, 0.06, 0.07, 0.08],
}

INDICI_BOND = [0, 1, 2, 3, 4, 5]
INDICI_EQUITY = [6, 7, 8, 9, 10, 11]

MACRO_GROUPS = {
    "Obbligazionario in €": [
        "Obbligazionario Euro BT",
        "Obbligazionario Euro MLT",
        "Obbligazionario Euro Corporate",
    ],
    "Obbligazionario in valuta": [
        "Obbligazionario Globale",
    ],
    "Obbligazionario Alto Rischio": [
        "Obbligazionario Paesi Emergenti",
        "Obbligazionario Globale High Yield",
    ],
    "Azionario in senso stretto": [
        "Azionario Europa/Euro",
        "Azionario Nord America",
        "Azionario Pacifico",
        "Azionario Paesi Emergenti",
        "Azionario Internazionale",
    ],
    "Best Ideas/Inv. Alternativi": [
        "Best Ideas",
    ],
}

COLORI_MACRO = {
    "Obbligazionario in €": "#a8d08d",            # verde
    "Obbligazionario in valuta": "#c6e0b4",       # verde chiaro
    "Obbligazionario Alto Rischio": "#ffe699",    # arancione chiaro
    "Azionario in senso stretto": "#ff6666",      # rosso
    "Best Ideas/Inv. Alternativi": "#00b0f0",     # azzurro
}


def _costruisci_portafoglio(importo: float, equity_pct: int, selezionate: list[str]):
    """
    Restituisce:
    - lista di tuple (asset, peso_% intero, importo)
    - lista di tuple macro (macro, peso_% intero, importo)
    """
    target_equity = equity_pct / 100.0

    # scelta del portafoglio base in funzione della % di equity
    if target_equity in EQUITY_LEVELS:
        j = EQUITY_LEVELS.index(target_equity)
    else:
        j = min(range(len(EQUITY_LEVELS)), key=lambda k: abs(EQUITY_LEVELS[k] - target_equity))

    base = [BASE_WEIGHTS[n][j] for n in ASSET_CLASSI_AA]

    selezionate_set = set(selezionate)
    sel_mask = [1.0 if n in selezionate_set else 0.0 for n in ASSET_CLASSI_AA]

    pesi_float = [0.0] * len(ASSET_CLASSI_AA)

    # --- obbligazionario ---
    sel_bond = [sel_mask[i] for i in INDICI_BOND]
    base_bond = [base[i] for i in INDICI_BOND]
    bond_target = 1.0 - target_equity

    if sum(sel_bond) > 0 and bond_target > 0:
        base_sel = [b * s for b, s in zip(base_bond, sel_bond)]
        somma = sum(base_sel)
        if somma == 0:
            base_sel = [s / sum(sel_bond) for s in sel_bond]
        else:
            base_sel = [b / somma for b in base_sel]
        for idx_loc, w in zip(INDICI_BOND, base_sel):
            pesi_float[idx_loc] = w * bond_target

    # --- azionario + Best Ideas ---
    sel_eq = [sel_mask[i] for i in INDICI_EQUITY]
    base_eq = [base[i] for i in INDICI_EQUITY]
    eq_target = target_equity

    if sum(sel_eq) > 0 and eq_target > 0:
        base_sel = [b * s for b, s in zip(base_eq, sel_eq)]
        somma = sum(base_sel)
        if somma == 0:
            base_sel = [s / sum(sel_eq) for s in sel_eq]
        else:
            base_sel = [b / somma for b in base_sel]
        for idx_loc, w in zip(INDICI_EQUITY, base_sel):
            pesi_float[idx_loc] = w * eq_target

    # funzione di arrotondamento intero a somma prefissata
    def round_group(indici, target_pct):
        if target_pct <= 0:
            return [0] * len(indici)
        raw = [pesi_float[i] * 100 for i in indici]
        floors = [int(math.floor(x)) for x in raw]
        rema = [x - f for x, f in zip(raw, floors)]
        diff = target_pct - sum(floors)
        order = sorted(range(len(indici)), key=lambda k: rema[k], reverse=True)
        res = floors[:]
        for k in range(diff):
            if k < len(order):
                res[order[k]] += 1
        return res

    eq_int = int(round(equity_pct))
    bond_int = 100 - eq_int

    pesi_int = [0] * len(ASSET_CLASSI_AA)
    bond_rounded = round_group(INDICI_BOND, bond_int)
    for idx_loc, v in zip(INDICI_BOND, bond_rounded):
        pesi_int[idx_loc] = v
    eq_rounded = round_group(INDICI_EQUITY, eq_int)
    for idx_loc, v in zip(INDICI_EQUITY, eq_rounded):
        pesi_int[idx_loc] = v

    # azzeriamo comunque le asset class non selezionate
    for i, nome in enumerate(ASSET_CLASSI_AA):
        if nome not in selezionate_set:
            pesi_int[i] = 0

    # costruzione lista micro
    dettagli = []
    for nome, pct in zip(ASSET_CLASSI_AA, pesi_int):
        if pct > 0:
            importo_i = importo * pct / 100.0
            dettagli.append((nome, pct, importo_i))

    # aggregazione macro
    macro = []
    for macro_nome, componenti in MACRO_GROUPS.items():
        pct = sum(p for n, p, _ in dettagli if n in componenti)
        if pct > 0:
            imp = sum(imp for n, _, imp in dettagli if n in componenti)
            macro.append((macro_nome, pct, imp))

    return dettagli, macro


# --------------------------------------------------------------------
# SIDEBAR
# --------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Navigazione")
    scelta = st.radio("Vai allo step:", lista_step, index=st.session_state.step_index)
    st.session_state.step_index = lista_step.index(scelta)
    st.markdown("---")
    st.markdown(f"**Step corrente:** {lista_step[st.session_state.step_index]}")


# --------------------------------------------------------------------
# PULSANTI NAVIGAZIONE – VERSIONE GRAFICA MIGLIORATA
# --------------------------------------------------------------------
def mostra_pulsanti_navigazione():
    totale_step = len(lista_step)
    idx_corrente = st.session_state.step_index

    col1, col2, col3 = st.columns([1.2, 1.6, 1.2])

    # Pulsante INDIETRO
    with col1:
        if idx_corrente > 0:
            if st.button("◀ Indietro", use_container_width=True):
                st.session_state.step_index -= 1
                st.rerun()

    # Indicatore centrale dello step corrente
    with col2:
        st.markdown(
            f"""
            <div style="
                text-align:center;
                font-size:14px;
                color:#4b5563;
                padding-top:0.3rem;
            ">
                Step <b>{idx_corrente + 1}</b> di <b>{totale_step}</b>
                <br>
                <span style="font-size:12px; color:#6b7280;">
                    ({lista_step[idx_corrente]})
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Pulsante AVANTI
    with col3:
        if idx_corrente < totale_step - 1:
            if st.button("Avanti ▶", use_container_width=True):
                st.session_state.step_index += 1
                st.rerun()


# --------------------------------------------------------------------
# CONTENUTI STEP
# --------------------------------------------------------------------
step_corrente = lista_step[st.session_state.step_index]
scroll_to_top()


# --------------------------------------------------------------------
# INTRO
# --------------------------------------------------------------------
if step_corrente == "Intro":
    # Immagine per prima
    mostra_immagine("intro.png", "Modello di costruzione del portafoglio")

    # Titolo e sottotitolo sotto l'immagine
    st.markdown('<div class="step-title">Intro</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step-subtitle">'
        "Questa App propone un modello di costruzione del portafoglio basato su due step."
        "</div>",
        unsafe_allow_html=True
    )

    st.write("- **(A)** Creazione dell'Asset Allocation")
    st.write("- **(B)** Selezione dei Prodotti")
    st.markdown("<span style='color:red'>Nella parte finale sarà anche possibile applicare una logica Life Cycle ed ipotizzare dei conferimenti periodici in una logica PAC</span>", unsafe_allow_html=True)

    mostra_pulsanti_navigazione()


# --------------------------------------------------------------------
# STEP 1 – DATI DI BASE
# --------------------------------------------------------------------
elif step_corrente == "Step 1":
    mostra_immagine("step1.png", "Dati dell’investimento")
    st.markdown('<div class="step-title">Step 1 – Info Cliente</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # -------------------------------------------------------
    # IMPORTO DA INVESTIRE con separatore delle migliaia
    # -------------------------------------------------------
    with col1:
        # Valore di default formattato (es. 150.000)
        if st.session_state.importo == 0:
            importo_default = ""
        else:
            importo_default = (
                f"{st.session_state.importo:,.0f}"
                .replace(",", ".")        # 150,000 -> 150.000
            )

        importo_raw = st.text_input(
            "Importo da investire inizialmente",
            value=importo_default
        )

        # Conversione robusta del testo in numero
        try:
            importo_clean = (
                importo_raw.replace(".", "")
                           .replace(",", "")
                           .replace("€", "")
                           .replace(" ", "")
            )
            st.session_state.importo = float(importo_clean) if importo_clean != "" else 0.0
        except ValueError:
            st.session_state.importo = 0.0

        # Visualizzazione conferma formattata
        importo_formattato = (
            f"{st.session_state.importo:,.0f}"
            .replace(",", ".")
        )
        st.write(f"Importo selezionato: **€ {importo_formattato}**")

    # -------------------------------------------------------
    # ORIZZONTE TEMPORALE (resta number_input)
    # -------------------------------------------------------
    with col2:
        st.session_state.orizzonte = st.number_input(
            "Orizzonte temporale (in anni)",
            value=float(st.session_state.orizzonte),
            step=1.0,
            format="%.1f"
        )

    # -------------------------------------------------------
    # TOLLERANZA AL RISCHIO (come prima)
    # -------------------------------------------------------
    st.session_state.tolleranza = st.selectbox(
        "Tolleranza al rischio",
        ["Bassa", "Medio-Bassa", "Medio-Alta", "Alta"],
        index=["Bassa", "Medio-Bassa", "Medio-Alta", "Alta"].index(st.session_state.tolleranza)
    )

    mostra_pulsanti_navigazione()

# --------------------------------------------------------------------
# STEP 2 – MATRICE ORIZZONTE × TOLLERANZA
# --------------------------------------------------------------------
elif step_corrente == "Step 2":
    mostra_immagine("step2.png", "Mappa rischio / orizzonte")
    st.markdown('<div class="step-title">Step 2 – Matrice Orizzonte Temporale / Tolleranza al Rischio</div>', unsafe_allow_html=True)

    colonne_tolleranza_loc = colonne_tolleranza
    righe_orizzonte_loc = righe_orizzonte

    riga_sel = classifica_orizzonte(st.session_state.orizzonte)

    df = pd.DataFrame("", index=righe_orizzonte_loc, columns=colonne_tolleranza_loc)

    # Inseriamo l'importo investito nella cella selezionata
    df.loc[riga_sel, st.session_state.tolleranza] = f"{st.session_state.importo:,.0f} €"

    def evidenzia(val):
        if val != "":
            return "background-color: #ffd54f; font-weight: bold; text-align:center;"
        return "text-align:center;"

    stile = (
        df.style
        .applymap(evidenzia)
        .set_properties(
        **{
            "width": "100px",
            "height": "50px",
            "text-align": "center",
            "font-size": "11px"
        }
        )
        .set_table_styles([
        # intestazioni di colonna (Bassa, Medio-Bassa, ecc.)
        {
            "selector": "th.col_heading",
            "props": [
                ("background-color", "#e0e0e0"),
                ("text-align", "center"),
                ("font-size", "15px"),
                ("padding", "4px 6px")
            ]
        },
        # intestazioni di riga (Brevissimo, Breve, ecc.) → colonna stretta
        {
            "selector": "th.row_heading",
            "props": [
                ("min-width", "50px"),
                ("max-width", "50px"),
                ("font-size", "12px"),
                ("text-align", "left"),
                ("white-space", "normal"),
                ("padding", "4px 4px"),
                ("background-color", "#e0e0e0")
            ]
        }
        ])
        )


    st.table(stile)

    mostra_pulsanti_navigazione()


# --------------------------------------------------------------------
# STEP 3 – CANALE PRODOTTI
# --------------------------------------------------------------------
elif step_corrente == "Step 3":
    mostra_immagine("step3.png", "Tipologia di soluzioni")

    st.markdown(
        '<div class="step-title">Step 3 – Perimetro di investimento</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="step-subtitle">In questa fase sei chiamato ad identificare il tuo perimetro di investimento: i prodotti nei quali investire.</div>',
        unsafe_allow_html=True
    )

    opzioni = ["Gestioni Patrimoniali", "Solo Fondi NEF", "Fondi NEF e Funds Partner"]

    st.session_state.canale_prodotti = st.selectbox(
        "Tipologia di prodotti",
        opzioni,
        index=opzioni.index(st.session_state.canale_prodotti)
    )

    st.write(f"Hai selezionato: **{st.session_state.canale_prodotti}**")

    # Testo esplicativo su sfondo azzurro in funzione del perimetro scelto
    if st.session_state.canale_prodotti == "Gestioni Patrimoniali":
        testo = (
            "Dato il Perimetro selezionato, l'asset allocation del portafoglio sarà "
            "implicitamente quella della Gestione Patrimoniale selezionata. Pertanto, "
            "la tua decisione è quella di dedicare pienamente al gestore della GP sia "
            "le scelte di asset allocation che quelle di selezione dei prodotti (con la sola "
            "eventuale eccezione della selezione delle \"Best Ideas\"). "
            "Procedi nei fogli successivi in coerenza con il Perimetro da te selezionato."
        )
    elif st.session_state.canale_prodotti == "Solo Fondi NEF":
        testo = (
            "Dato il Perimetro selezionato, l'asset allocation del portafoglio sarà in parte "
            "vincolata dal fatto che i fondi NEF coprono un numero limitato di mercati. Pertanto, "
            "nello step successivo sarai chiamato a scegliere tra un numero di asset class inferiore "
            "a quello potenzialmente utilizzabile includendo anche Fondi Funds Partner. "
            "La fase di selezione dei gestori sarà anch'essa semplificata. "
            "Una scelta del genere è comunque molto efficace per una clientela non molto sofisticata "
            "e non abituata alla logica del \"supermercato\" dei fondi. "
            "Procedi nei fogli successivi in coerenza con il Perimetro da te selezionato."
        )
    else:  # "Fondi NEF e Funds Partner"
        testo = (
            "Dato il Perimetro selezionato, l'asset allocation del portafoglio sarà la più ampia possibile: "
            "i fondi Funds Partner coprono infatti l'intero spettro dei mercati nei quali investire. Pertanto, "
            "nello step successivo sarai chiamato a scegliere tra un numero di asset class molto ampio. "
            "La fase di selezione dei gestori sarà però più articolata, dovendo tu pescare da un paniere di "
            "centinaia di prodotti. Una scelta del genere è efficace soprattutto per una clientela sofisticata, "
            "abituata alla logica del \"supermercato\" dei fondi e che pretende quindi di poter fare "
            "\"Cherry Picking\" (scelta delle \"ciliegie\" migliori) tra i migliori gestori presenti sul mercato. "
            "Procedi nei fogli successivi in coerenza con il Perimetro da te selezionato."
        )

    st.markdown(
        f"""
        <div style="
            background-color: #d7ecff;
            padding: 16px;
            border-radius: 8px;
            color: #000000;
            font-size: 15px;
            line-height: 1.5;
            margin-top: 10px;
        ">
        {testo}
        </div>
        """,
        unsafe_allow_html=True
    )

    mostra_pulsanti_navigazione()


# --------------------------------------------------------------------
# STEP 4 – INTRODUZIONE ALLA SCELTA DEL PESO AZIONARIO
# --------------------------------------------------------------------
elif step_corrente == "Step 4":
    mostra_immagine("step4.png", "Introduzione alla scelta del peso azionario")

    st.markdown(
        '<div class="step-title">Step 4 – Peso dell’Azionario</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="
            background-color: #d7ecff;
            padding: 20px;
            border-radius: 8px;
            color: #000000;
            font-size: 16px;
            line-height: 1.5;
        ">
        Nelle successive sezioni sei chiamato a definire una delle variabili più rilevanti
        della costruzione del portafoglio, ovvero il peso da attribuire all'Azionario.
        La percentuale di Equity in portafoglio è infatti la più intuitiva modalità di catturare
        il rischio di un investimento.<br><br>

        Rammenta che la tolleranza al rischio e la diversificazione temporale sono fattori tali
        che giustificano un incremento del peso dell'azionario mano a mano che il cliente
        si colloca più in basso ed a destra nella griglia "Tolleranza al Rischio / Orizzonte Temporale".<br><br>

        Sperando di essere di aiuto ti supporteremo nella scelta.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<span style='color:red'>N.B: Nel caso in cui dovessi optare per una logica Life Cycle, il peso della componente azionaria si modificherà nel tempo.</span>", unsafe_allow_html=True)


    mostra_pulsanti_navigazione()

# STEP 5 – SUGGERIMENTO % AZIONARIO IN FUNZIONE DELLO STILE DI CONSULENTE
# --------------------------------------------------------------------
elif step_corrente == "Step 5":
    # immagine in alto
    mostra_immagine("step5.png", "Suggerimento percentuale di Azionario")

    st.markdown(
        '<div class="step-title">Step 5 – Suggerimento % di Azionario</div>',
        unsafe_allow_html=True
    )


    # Testo su sfondo grigio
    st.markdown(
        """
        <div style="
            background-color: #e0e0e0;
            padding: 12px;
            border-radius: 6px;
            color: #000000;
            font-size: 15px;
        ">
        Come forma di supporto nella scelta della % di Azionario in portafoglio,
        rispondi al seguente quesito:
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")
    st.markdown("**Che tipo di consulente sei?**")

    opzione_a = "(a) Preferisco che i miei clienti abbiano dei portafogli prudenti. Sono tranquillo io e anche loro"
    opzione_b = "(b) Il mio approccio sta nel mezzo: non esageriamo con il rischio dei portafogli ma assumiamolo"
    opzione_c = "(c) Per i miei clienti prediligo portafogli sfidanti"

    scelta_stile = st.selectbox(
        "",
        [opzione_a, opzione_b, opzione_c],
        key="step5_stile"
    )

    # Selezione tabella in funzione della risposta
    if scelta_stile == opzione_a:
        tabella = TABELLA_A
    elif scelta_stile == opzione_b:
        tabella = TABELLA_B
    else:
        tabella = TABELLA_C

    # Posizione nella griglia (stessa logica Step 2)
    riga_sel = classifica_orizzonte(st.session_state.orizzonte)
    col_sel = st.session_state.tolleranza

    # Valore raccomandato
    valore_raccomandato = tabella[riga_sel][col_sel]
    st.session_state.equity_raccomandata = valore_raccomandato

    # Se è la PRIMA volta che entro nello Step 5,
    # inizializzo equity_scelta al valore raccomandato.
    if not st.session_state.equity_scelta_definita:
        st.session_state.equity_scelta = valore_raccomandato
        st.session_state.equity_scelta_definita = True

    # ----------------- GRIGLIA IN ALTO (valore raccomandato) -----------------
    df = pd.DataFrame("", index=righe_orizzonte, columns=colonne_tolleranza)
    df.loc[riga_sel, col_sel] = valore_raccomandato

    def evidenzia_step5(val):
        if val != "":
            return "background-color: #ffd54f; font-weight: bold; text-align:center;"
        return "text-align:center;"

    stile5 = (
    df.style
    .applymap(evidenzia_step5)
    .set_properties(
        **{
            "width": "90px",
            "height": "32px",
            "text-align": "center",
            "font-size": "11px"
        }
    )
    .set_table_styles([
        # intestazioni di colonna (Bassa, Medio-Bassa, ecc.)
        {
            "selector": "th.col_heading",
            "props": [
                ("background-color", "#e0e0e0"),
                ("text-align", "center"),
                ("font-size", "11px"),
                ("padding", "4px 6px")
            ]
        },
        # intestazioni di riga (Brevissimo, Breve, ecc.) → colonna stretta
        {
            "selector": "th.row_heading",
            "props": [
                ("min-width", "110px"),
                ("max-width", "110px"),
                ("font-size", "11px"),
                ("text-align", "left"),
                ("white-space", "normal"),
                ("padding", "4px 4px"),
                ("background-color", "#e0e0e0")
            ]
        }
    ])
    )

    st.write("")
    st.markdown("#### Griglia di supporto: suggerimento % di Azionario")
    st.table(stile5)

    # ----------------- MENU DI SCELTA FINALE -----------------
    st.write("")
    st.markdown(
        "<div style='text-align:center; font-weight:bold;'>"
        "Se lo ritieni opportuno fissa una % diversa di Azionario"
        "</div>",
        unsafe_allow_html=True
    )

    opzioni_equity = [
        "0%", "5%", "10%", "15%", "20%", "25%", "30%",
        "40%", "50%", "60%", "70%", "80%", "100%"
    ]

    # default = ultima scelta dell'utente (persistente)
    if st.session_state.equity_scelta in opzioni_equity:
        idx_default = opzioni_equity.index(st.session_state.equity_scelta)
    else:
        idx_default = 0

    colA, colB, colC = st.columns([2, 1, 2])
    with colB:
        scelta_equity = st.selectbox(
            "",
            opzioni_equity,
            index=idx_default,
            key="step5_equity_select"
        )

    # aggiorno in modo permanente la scelta
    st.session_state.equity_scelta = scelta_equity

    # Griglia finale con la % effettiva scelta
    df2 = pd.DataFrame("", index=righe_orizzonte, columns=colonne_tolleranza)
    df2.loc[riga_sel, col_sel] = st.session_state.equity_scelta

    stile6 = (
        df2.style
        .applymap(evidenzia_step5)
        .set_properties(
        **{
            "width": "90px",
            "height": "32px",
            "text-align": "center",
            "font-size": "11px"
        }
        )
        .set_table_styles([
        # intestazioni di colonna
        {
            "selector": "th.col_heading",
            "props": [
                ("background-color", "#e0e0e0"),
                ("text-align", "center"),
                ("font-size", "11px"),
                ("padding", "4px 6px")
            ]
        },
        # intestazioni di riga → colonna stretta
        {
            "selector": "th.row_heading",
            "props": [
                ("min-width", "110px"),
                ("max-width", "110px"),
                ("font-size", "11px"),
                ("text-align", "left"),
                ("white-space", "normal"),
                ("padding", "4px 4px"),
                ("background-color", "#e0e0e0")
            ]
        }
        ])
        )

    st.write("")
    st.markdown("#### Griglia aggiornata: Ecco la % di Azionario definitiva")
    st.table(stile6)

    mostra_pulsanti_navigazione()


# --------------------------------------------------------------------
# GP (stop) – BLOCCO FINALE LEGATO AL PERIMETRO "GESTIONI PATRIMONIALI"
# --------------------------------------------------------------------
elif step_corrente == "GP (stop)":
    mostra_immagine("gp_stop.png", "Gestione Patrimoniale")

    st.markdown(
        '<div class="step-title">GP (stop)</div>',
        unsafe_allow_html=True
    )

    # Caso 1: nello Step 3 è stata scelta "Gestioni Patrimoniali"
    if st.session_state.canale_prodotti == "Gestioni Patrimoniali":
        testo = (
            "L'uso del File per te finisce qui. Dato il perimetro scelto, non devi fare "
            "scelte personalizzate di asset allocation e di selezione dei fondi. Dovrai "
            "scegliere una Gestione Patrimoniale con un livello di Azionario in linea con "
            "quello da te prima indicato."
        )

        st.markdown(
            f"""
            <div style="
                background-color: #ffcccc;
                padding: 20px;
                border-radius: 8px;
                color: #000000;
                font-size: 16px;
                line-height: 1.5;
                margin-top: 10px;
            ">
            {testo}
            </div>
            """,
            unsafe_allow_html=True
        )

    # Caso 2: nello Step 3 è stata scelta una delle altre opzioni
    else:
        testo = (
            "Salta questa sezione perchè riguarda le Gestioni Patrimoniali e NON è quindi "
            "coerente con il Perimetro di Prodotti che hai selezionato."
        )

        st.markdown(
            f"""
            <div style="
                background-color: #ccffcc;
                padding: 20px;
                border-radius: 8px;
                color: #000000;
                font-size: 16px;
                line-height: 1.5;
                margin-top: 10px;
            ">
            {testo}
            </div>
            """,
            unsafe_allow_html=True
        )

    mostra_pulsanti_navigazione()

# --------------------------------------------------------------------
# STEP 6 – SELEZIONE DELLE ASSET CLASS
# --------------------------------------------------------------------
elif step_corrente == "Step 6":
    mostra_immagine("step6.png", "Selezione delle asset class")

    st.markdown(
        '<div class="step-title">Step 6 – Selezione delle asset class</div>',
        unsafe_allow_html=True
    )

    # Importo formattato con separatore delle migliaia
    importo_form = f"{st.session_state.importo:,.0f}".replace(",", ".")
    importo_testo = f"€ {importo_form}"

    # Box introduttivo su sfondo azzurro
    st.markdown(
        f"""
        <div style="
            background-color: #d7ecff;
            padding: 16px;
            border-radius: 8px;
            color: #000000;
            font-size: 15px;
            line-height: 1.5;
        ">
        In questa sezione sei chiamato a selezionare le asset class con le quali comporre
        l'Asset Allocation del portafoglio del cliente.<br>
        Essendo il portafoglio pari a: <b>{importo_testo}</b>, dovrai selezionare un numero
        di asset class che rispecchi la dimensione del portafoglio.<br><br>
        Come indicazione utile ai fini di una scelta efficace, il suggerimento è quello di
        utilizzare almeno le seguenti tre asset class:<br>
        (a) Obbligazionario € Breve Termine;<br>
        (b) Obbligazionario € Medio Lungo Termine;<br>
        (c) Mercato Azionario.
        </div>
        """,
        unsafe_allow_html=True
    )



    st.write("")

    # Elenco asset class e suggerimenti
    asset_classi = [
        "Obbligazionario Euro BT",
        "Obbligazionario Euro MLT",
        "Obbligazionario Euro Corporate",
        "Obbligazionario Globale",
        "Obbligazionario Paesi Emergenti",
        "Obbligazionario Globale High Yield",
        "Azionario Europa/Euro",
        "Azionario Nord America",
        "Azionario Pacifico",
        "Azionario Paesi Emergenti",
        "Azionario Internazionale",
        "Best Ideas",
    ]

    suggerimenti = [
        "* selezione SEMPRE raccomandata",
        "* selezione SEMPRE raccomandata",
        "* selezione raccomandata se il portafoglio > 100.000€",
        "* selezione raccomandata se il portafoglio > 50.000€",
        "* selezione per portafogli importanti",
        "* selezione per portafogli importanti",
        "* selezione quando portaf. >100.000€, insieme alle altre asset class geografiche",
        "* selezione quando portaf. >100.000€, insieme alle altre asset class geografiche",
        "* selezione quando portaf. >100.000€, insieme alle altre asset class geografiche",
        "* selezione quando portaf. >100.000€, insieme alle altre asset class geografiche",
        "* selezione per portafogli piccoli al fine di coprire tutto il segmento azionario",
        "* selezione per portafogli importanti e per finalità di Story Telling",
    ]

    st.markdown("#### Seleziona le asset class da includere")

    # Recupero le selezioni precedenti (se presenti)
    pre_sel = set(st.session_state.asset_class_selezionate)

    selezionate = []

    for nome, hint in zip(asset_classi, suggerimenti):
        col_a, col_b = st.columns([2, 3])

        with col_a:
            # La checkbox è spuntata se l'asset class era già stata selezionata
            checked = st.checkbox(
                nome,
                value=(nome in pre_sel)
            )

        with col_b:
            st.markdown(
                f"<span style='font-size:13px; color:#0066aa;'>{hint}</span>",
                unsafe_allow_html=True
            )

        if checked:
            selezionate.append(nome)

    # Aggiorno lo stato di sessione con le scelte correnti
    st.session_state.asset_class_selezionate = selezionate

    # ---------------------------
    # RAGGRUPPO PER TIPOLOGIA
    # ---------------------------
    obbligazionari_list = [
        "Obbligazionario Euro BT",
        "Obbligazionario Euro MLT",
        "Obbligazionario Euro Corporate",
        "Obbligazionario Globale",
        "Obbligazionario Paesi Emergenti",
        "Obbligazionario Globale High Yield",
    ]

    azionari_list = [
        "Azionario Europa/Euro",
        "Azionario Nord America",
        "Azionario Pacifico",
        "Azionario Paesi Emergenti",
        "Azionario Internazionale",
    ]

    obbligazionari_sel = [ac for ac in selezionate if ac in obbligazionari_list]
    azionari_sel = [ac for ac in selezionate if ac in azionari_list]
    altro_sel = ["Best Ideas"] if "Best Ideas" in selezionate else []

    st.write("")
    st.markdown("#### Asset class selezionate (per macro-categoria)")

    col_obbl, col_az, col_alt = st.columns(3)

    # Colonna Obbligazionari – sfondo azzurro
    with col_obbl:
        items = "<br>".join(obbligazionari_sel) if obbligazionari_sel else ""
        st.markdown(
            f"""
            <div style="
                background-color: #d7ecff;
                padding: 12px;
                border-radius: 8px;
                color: #000000;
                font-size: 14px;
                line-height: 1.4;
                min-height: 120px;
            ">
            <b>Obbligazionari</b><br>
            {items}
            </div>
            """,
            unsafe_allow_html=True
        )

    # Colonna Azionari – sfondo rosato/rosso chiaro
    with col_az:
        items = "<br>".join(azionari_sel) if azionari_sel else ""
        st.markdown(
            f"""
            <div style="
                background-color: #ffd7d7;
                padding: 12px;
                border-radius: 8px;
                color: #000000;
                font-size: 14px;
                line-height: 1.4;
                min-height: 120px;
            ">
            <b>Azionari</b><br>
            {items}
            </div>
            """,
            unsafe_allow_html=True
        )

    # Colonna Altro – sfondo verde chiaro
    with col_alt:
        items = "<br>".join(altro_sel) if altro_sel else ""
        st.markdown(
            f"""
            <div style="
                background-color: #d7ffd7;
                padding: 12px;
                border-radius: 8px;
                color: #000000;
                font-size: 14px;
                line-height: 1.4;
                min-height: 120px;
            ">
            <b>Altro</b><br>
            {items}
            </div>
            """,
            unsafe_allow_html=True
        )

    mostra_pulsanti_navigazione()

# --------------------------------------------------------------------
# FOCUS – WARNING SULLA SELEZIONE DELLE ASSET CLASS
# --------------------------------------------------------------------
elif step_corrente == "Focus":
    mostra_immagine("focus.png", "Warning nella selezione dei mercati")
    st.markdown(
        '<div class="step-title">Focus – Controllo di coerenza della selezione dei mercati</div>',
        unsafe_allow_html=True
    )

    # Box introduttivo su sfondo azzurro
    st.markdown(
        """
        <div style="
            background-color: #d7ecff;
            padding: 16px;
            border-radius: 8px;
            color: #000000;
            font-size: 15px;
            line-height: 1.5;
        ">
        In questa sezione troverai dei consigli relativi alla selezione delle asset class che hai effettuato.
        Qualche indicazione utile per ripensare eventualmente la selezione ed affinarla.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<span style='color:red'>N.B: Nel caso in cui tu voglia implementare una logica PAC le indicazioni qui di seguito fornite potranno in buona parte essere trascurate alla luce della peculiarità di un investimento ad Accumulo periodico e della necessità di limitare il numero di prodotti oggetto di investimento.</span>", unsafe_allow_html=True)


    st.write("")

    # -------------------------------
    # MESSAGGI (copiati da FOCUS.xlsx)
    # -------------------------------
    MSG_R5  = (
        "Valuta l'inserimento dell'Obbligazionario Euro BT: la sua selezione è "
        "necessaria per gestire il rischio tasso di interesse in portafoglio."
    )
    MSG_R6  = (
        "Valuta l'inserimento dell'Obbligazionario Euro MLT: la sua selezione è "
        "necessaria per assicurare la presenza in portafoglio di uno 'zoccolo duro' "
        "obbligazionario a basso rischio."
    )
    MSG_R7  = (
        "Valuta l'inserimento dell'Obbligazionario Euro Corporate: si tratta di una "
        "asset class a rischio relativamente basso che aiuta a diversificare il "
        "rischio di credito."
    )
    MSG_R8  = (
        "Valuta l'inserimento dell'Obbligazionario Globale: ti aiuta a diversificare "
        "il rischio di credito ed aggiunge una esposizione in valute estere forti "
        "utile nelle fasi di panico sui mercati."
    )
    MSG_R9  = (
        "Valuta l'inserimento di altre asset class Azionarie: la scelta di investire "
        "nella sola componente Azionaria Domestica (Europa/Euro) non è ottimale ai "
        "fini della diversificazione geografica e settoriale"
    )
    MSG_R10 = (
        "Stai investendo solo nel'azionario domestico e quello USA: valuta "
        "l'investimento anche nelle altre asset class geografiche, oppure "
        "sostituisci l'azionario USA con quello Internazionale"
    )
    MSG_R11 = (
        "Stai investendo solo nel'azionario domestico e quello Emergente: valuta "
        "l'investimento anche nelle altre asset class geografiche, oppure "
        "sostituisci l'azionario Emergente con quello Internazionale"
    )
    MSG_R12 = (
        "Stai investendo solo nel'azionario domestico e quello Pacifico: valuta "
        "l'investimento anche nelle altre asset class geografiche, oppure "
        "sostituisci l'azionario Pacifico con quello Internazionale"
    )
    MSG_R13 = (
        "Devi selezionare delle Asset class azionarie, altrimenti l'asset allocation "
        "non può essere creata."
    )
    # R14: 5 possibili messaggi a seconda di importo e numerosità
    MSG_R14_1 = (
        "Valuta se ridurre il numero delle Asset Class selezionate dato l'importo "
        "limitato da investire."
    )
    MSG_R14_2 = (
        "Valuta se ridurre il numero delle Asset Class selezionate dato l'importo "
        "non elevato da investire."
    )
    MSG_R14_3 = (
        "Valuta se aumentare il numero delle Asset Class selezionate dato l'importo "
        "importante da investire."
    )
    MSG_R14_4 = (
        "Valuta se aumentare il numero delle Asset Class selezionate dato l'importo "
        "elevato da investire."
    )
    MSG_R14_5 = (
        "Valuta se aumentare il numero delle Asset Class selezionate al fine di "
        "creare una diversificazione sufficiente."
    )
    MSG_R15 = (
        "Valuta l'inserimento della Asset Class 'Best Ideas' per accrescere "
        "l'interesse per la soluzione di investimento proposta."
    )
    MSG_R16 = (
        "Poiché stai già investendo nelle 4 area azionarie geografiche (Europa/Euro, "
        "Nord America, Pacifico e Emergenti) valuta l'eliminazione dell'Azionario "
        "Internazionale Internazionale"
    )
    MSG_R17 = (
        "Valuta l'inserimento dell'Azionario Europa/Euro, poiché ti stai limitando "
        "ad investire solo nei mercati azionari esteri"
    )
    MSG_R18 = (
        "Stai investendo solo nel'azionario domestico, USA e Pacifico: valuta "
        "l'investimento anche nell'Azionario Emergente, oppure sostituisci "
        "l'azionario USA e Pacifico con quello Internazionale"
    )
    MSG_R19 = (
        "Stai investendo solo nel'azionario domestico, USA e Emergente: valuta "
        "l'investimento anche nell'Azionario Pacifico oppure sostituisci "
        "l'azionario USA e Pacifico con quello Internazionale"
    )
    MSG_R20 = (
        "Stai investendo solo nel'azionario domestico, Pacifico e Emergente: valuta "
        "l'investimento anche nell'Azionario USA oppure sostituisci l'azionario "
        "Pacifico e Emergente con quello Internazionale"
    )
    MSG_R21 = (
        "E' opportuno che tu faccia una scelta precisa: (a) investire nel solo "
        "mercato Azionario Internazionale, oppure (b) comprare i singoli mercati "
        "geografici esteri"
    )

    # -------------------------------
    # DATI DI BASE – equivalenti a R1, R2 e O5:O16
    # -------------------------------
    selezionate = set(st.session_state.asset_class_selezionate)

    def sel(nome):
        return 1 if nome in selezionate else 0

    obbl_bt   = sel("Obbligazionario Euro BT")            # O5
    obbl_mlt  = sel("Obbligazionario Euro MLT")           # O6
    obbl_corp = sel("Obbligazionario Euro Corporate")     # O7
    obbl_glob = sel("Obbligazionario Globale")            # O8
    obbl_em   = sel("Obbligazionario Paesi Emergenti")    # O9
    obbl_hy   = sel("Obbligazionario Globale High Yield") # O10

    az_eu     = sel("Azionario Europa/Euro")              # O11
    az_usa    = sel("Azionario Nord America")             # O12
    az_pac    = sel("Azionario Pacifico")                 # O13
    az_em     = sel("Azionario Paesi Emergenti")          # O14
    az_intl   = sel("Azionario Internazionale")           # O15

    best      = sel("Best Ideas")                         # O16

    # P5:P16 in Excel (0/1 in base alla selezione)
    P5, P6, P7, P8, P9, P10 = obbl_bt, obbl_mlt, obbl_corp, obbl_glob, obbl_em, obbl_hy
    P11, P12, P13, P14, P15 = az_eu, az_usa, az_pac, az_em, az_intl

    # Importo (R2) e % equity (R1) – qui lavoro con valori numerici
    importo = float(st.session_state.importo) if st.session_state.importo else 0.0

    try:
        # equity_scelta es. "40%"
        equity_raw = st.session_state.equity_scelta.replace("%", "").replace(",", ".")
        equity_pct = float(equity_raw)   # es. 40.0
    except Exception:
        equity_pct = 0.0

    warnings = []

    # -------------------------------
    # TRADUZIONE PUNTUALE DELLE FORMULE R5:R21
    # -------------------------------

    # R5: IF(O5>0,"", MSG_R5)
    if obbl_bt == 0:
        warnings.append(MSG_R5)

    # R6: IF(O6>0,"", MSG_R6)
    if obbl_mlt == 0:
        warnings.append(MSG_R6)

    # R7: IF(OR(O7>0, R2<100000),"", MSG_R7)
    if obbl_corp == 0 and importo >= 100000:
        warnings.append(MSG_R7)

    # R8: IF(OR(O8>0, R2<50000),"", MSG_R8)
    if obbl_glob == 0 and importo >= 50000:
        warnings.append(MSG_R8)

    # R9: IF(AND(O11>0, SUM(O12:O15)<1), MSG_R9, "")
    if az_eu > 0 and (az_usa + az_pac + az_em + az_intl) < 1:
        warnings.append(MSG_R9)

    # R10: IF(AND((P11+P12)=2, SUM(O13:O15)<1), MSG_R10, "")
    if (P11 + P12) == 2 and (az_pac + az_em + az_intl) < 1:
        warnings.append(MSG_R10)

    # R11: IF(AND((P11+P14)=2, SUM(O12,O13,O15)<1), MSG_R11, "")
    if (P11 + P14) == 2 and (az_usa + az_pac + az_intl) < 1:
        warnings.append(MSG_R11)

    # R12: IF(AND((P11+P13)=2, SUM(O12,O14,O15)<1), MSG_R12, "")
    if (P11 + P13) == 2 and (az_usa + az_em + az_intl) < 1:
        warnings.append(MSG_R12)

    # R13: IF(AND(SUM(O11:O15)<1,R1>0), MSG_R13, "")
    if (az_eu + az_usa + az_pac + az_em + az_intl) < 1 and equity_pct > 0:
        warnings.append(MSG_R13)

    # R14: IF nidificati su R2 e SUM(P5:P16)
    num_sel_tot = P5 + P6 + P7 + P8 + P9 + P10 + P11 + P12 + P13 + P14 + P15 + best

    if importo < 50000 and num_sel_tot > 5:
        warnings.append(MSG_R14_1)
    elif importo < 100000 and num_sel_tot > 7:
        warnings.append(MSG_R14_2)
    elif importo > 250000 and num_sel_tot < 7:
        warnings.append(MSG_R14_3)
    elif importo > 500000 and num_sel_tot < 9:
        warnings.append(MSG_R14_4)
    elif num_sel_tot < 4:
        warnings.append(MSG_R14_5)

    # R15: IF(AND(O16<1,R2>250000), MSG_R15, "")
    if best < 1 and importo > 250000:
        warnings.append(MSG_R15)

    # R16: IF(AND(SUM(P11:P14)=4, O15>0), MSG_R16, "")
    if (P11 + P12 + P13 + P14) == 4 and az_intl > 0:
        warnings.append(MSG_R16)

    # R17: IF(AND(SUM(P12:P14)>1, O11<1), MSG_R17, "")
    if (P12 + P13 + P14) > 1 and az_eu < 1:
        warnings.append(MSG_R17)

    # R18: IF(AND((P11+P12+P13)=3, SUM(O14:O15)<1), MSG_R18, "")
    if (P11 + P12 + P13) == 3 and (az_em + az_intl) < 1:
        warnings.append(MSG_R18)

    # R19: IF(AND((P11+P12+P14)=3, SUM(O13,O15)<1), MSG_R19, "")
    if (P11 + P12 + P14) == 3 and (az_pac + az_intl) < 1:
        warnings.append(MSG_R19)

    # R20: IF(AND((P11+P13+P14)=3, SUM(O12,O15)<1), MSG_R20, "")
    if (P11 + P13 + P14) == 3 and (az_usa + az_intl) < 1:
        warnings.append(MSG_R20)

    # R21: IF(AND((P12+P13+P14)>0, O15>0, P11=0), MSG_R21, "")
    if (P12 + P13 + P14) > 0 and az_intl > 0 and P11 == 0:
        warnings.append(MSG_R21)

    # -------------------------------
    # OUTPUT – SOLO WARNING ATTIVI
    # -------------------------------
    st.markdown("#### Warning attivi sulla selezione delle asset class")

    if not warnings:
        st.success("Al momento non emergono warning particolari sulla selezione effettuata.")
    else:
        for msg in warnings:
            st.markdown(
                f"""
                <div style="
                    background-color: #ffe0e0;
                    padding: 10px;
                    border-radius: 6px;
                    margin-bottom: 8px;
                    font-size: 14px;
                ">
                {msg}
                </div>
                """,
                unsafe_allow_html=True
            )

    mostra_pulsanti_navigazione()

# --------------------------------------------------------------------
# STEP 7 – COMPOSIZIONE DEL PORTAFOGLIO
# --------------------------------------------------------------------
elif step_corrente == "Step 7":
    # immagine in alto
    mostra_immagine("step7.png", "Composizione del portafoglio")


    st.markdown('<div class="step-title">Step 7 – Composizione del portafoglio</div>', unsafe_allow_html=True)

    
    # testo esplicativo su sfondo azzurro
    st.markdown(
        """
        <div style="
            background-color: #d7ecff;
            padding: 16px;
            border-radius: 8px;
            color: #000000;
            font-size: 15px;
            line-height: 1.5;
            margin-top: 10px;
        ">
        Questa è la composizione del portafoglio che si ottiene sulla base delle scelte da te effettuate.
        Osserva attentamente la composizione e verifica:
        <br>(a) se la soluzione ti pare ragionevole;
        <br>(b) se il portafoglio ti pare adeguato alle caratteristiche dell'investitore;
        <br>(c) se la soluzione ha elementi di complessità in linea con il profilo del cliente e con la
        dimensione del portafoglio investito.
        <br><br>
        Alla luce di queste considerazioni potrai:
        <br>(A) decidere di tornare indietro ed apportare modifiche radicali alla soluzione di investimento
        (livello azionario – asset class utilizzate);
        <br>(B) scegliere questa soluzione.
        </div>
        """,
        unsafe_allow_html=True,
    )



    importo = float(st.session_state.importo)
    equity_str = st.session_state.equity_scelta  # es. "15%"
    equity_pct = int(equity_str.replace("%", "")) if equity_str else 0

    # asset class selezionate nello Step 6
    selezionate = st.session_state.get("asset_class_selezionate", [])

    if not selezionate:
        st.warning("Nello Step 6 non è stata selezionata alcuna asset class.")
        mostra_pulsanti_navigazione()
        st.stop()

    dettagli, macro = _costruisci_portafoglio(importo, equity_pct, selezionate)

    # ------------------ TABELLA MICRO + PIE CHART ------------------
    df = pd.DataFrame(dettagli, columns=["Asset class", "Pesi", "Importo"])
    totale_pesi = df["Pesi"].sum()
    totale_importo = df["Importo"].sum()

    df_tot = pd.DataFrame(
        [["TOTALE", totale_pesi, totale_importo]],
        columns=["Asset class", "Pesi", "Importo"]
    )
    df = pd.concat([df, df_tot], ignore_index=True)

    df["Pesi"] = df["Pesi"].astype(str) + "%"
    df["Importo"] = df["Importo"].map(lambda x: f"{x:,.0f} €".replace(",", "."))

    # colori per riga in funzione della macro asset class
    def colore_riga(asset_name: str) -> str:
        for macro_nome, componenti in MACRO_GROUPS.items():
            if asset_name in componenti:
                return COLORI_MACRO.get(macro_nome, "")
        if asset_name == "TOTALE":
            return "#b0c4de"  # grigio/azzurro per il totale
        return ""

    def style_righe(row):
        col = colore_riga(row["Asset class"])
        if not col:
            return ["" for _ in row]
        return [f"background-color: {col};" for _ in row]

    col1, col2 = st.columns(2)

    df_no_index = df.reset_index(drop=True)

    styled = (
        df_no_index.style
        .apply(style_righe, axis=1)
        .set_properties(**{"text-align": "left"})
        .set_properties(subset=["Importo"], **{"width": "160px"})
        .set_table_styles([
            {"selector": "th", "props": "background-color: #4f81bd; color: white; text-align: center;"}
        ])
    )

    st.dataframe(styled, use_container_width=True)




    with col2:
        # pie chart per asset class (escludendo il totale)
        labels = [a for a, _, _ in dettagli]
        values = [p for _, p, _ in dettagli]

        colors = []
        for nome in labels:
            for macro_nome, comp in MACRO_GROUPS.items():
                if nome in comp:
                    colors.append(COLORI_MACRO.get(macro_nome, None))
                    break
            else:
                colors.append(None)

        fig, ax = plt.subplots()
        ax.pie(values, labels=labels, autopct="%1.0f%%", startangle=90, colors=colors)
        ax.set_title("Asset allocation per asset class")
        st.pyplot(fig)

    # ------------------ TABELLA MACRO + PIE CHART ------------------
    if macro:
        df_macro = pd.DataFrame(macro, columns=["Macro Asset Class", "Pesi", "Importo"])
        tot_pesi_macro = df_macro["Pesi"].sum()
        tot_imp_macro = df_macro["Importo"].sum()

        df_macro_tot = pd.DataFrame(
            [["TOTALE", tot_pesi_macro, tot_imp_macro]],
            columns=["Macro Asset Class", "Pesi", "Importo"]
        )
        df_macro = pd.concat([df_macro, df_macro_tot], ignore_index=True)

        df_macro["Pesi"] = df_macro["Pesi"].astype(str) + "%"
        df_macro["Importo"] = df_macro["Importo"].map(lambda x: f"{x:,.0f} €".replace(",", "."))

        def style_righe_macro(row):
            nome = row["Macro Asset Class"]
            col = COLORI_MACRO.get(nome, "#b0c4de" if nome == "TOTALE" else "")
            if not col:
                return ["" for _ in row]
            return [f"background-color: {col};" for _ in row]

        st.markdown("### Sintesi per Macro Asset Class")

        col3, col4 = st.columns(2)

        with col3:
            df_macro_no_index = df_macro.reset_index(drop=True)

            styled_macro = (
                df_macro_no_index.style
                .apply(style_righe_macro, axis=1)
                .set_properties(**{"text-align": "left"})
                .set_properties(subset=["Importo"], **{"width": "160px"})
                .set_table_styles([
                    {"selector": "th", "props": "background-color: #4f81bd; color: white; text-align: center;"}
                ])
            )

            st.dataframe(styled_macro, use_container_width=True)



    with col4:
            labels_m = [n for n, _, _ in macro]
            values_m = [p for _, p, _ in macro]
            colors_m = [COLORI_MACRO.get(n, None) for n in labels_m]

            fig2, ax2 = plt.subplots()
            ax2.pie(values_m, labels=labels_m, autopct="%1.0f%%", startangle=90, colors=colors_m)
            ax2.set_title("Asset allocation per Macro Asset Class")
            st.pyplot(fig2)

    mostra_pulsanti_navigazione()


# --------------------------------------------------------------------
# STEP 8 – ANALISI STORICA DEL PORTAFOGLIO
# --------------------------------------------------------------------
elif step_corrente == "Step 8":
    # immagine in alto, se presente
    mostra_immagine("step8.png", "Analisi storica del portafoglio")


    st.markdown(
        '<div class="step-title">Step 8 – Analisi storica e prospettica del portafoglio</div>',
        unsafe_allow_html=True
    )


    st.markdown(
        "<div class='step-subtitle'>In questa sezione è possibile esplorare le caratteristiche salienti dell'asset allocation selezionata.</div>",
        unsafe_allow_html=True
    )

    # ------------------------------------------------------------------
    # Lettura INPUT_AC e costruzione del portafoglio (come in Step 7)
    # ------------------------------------------------------------------
    input_path = Path("INPUT_AC.xlsx")
    if not input_path.exists():
        st.error("Il file 'INPUT_AC.xlsx' deve trovarsi nella stessa cartella di 'app_portafoglio.py'.")
        mostra_pulsanti_navigazione()
        st.stop()

    df_input = pd.read_excel(input_path, sheet_name=0, header=None)

    # Nomi asset class, rendimenti attesi e matrice var-cov
    nomi_ac = df_input.iloc[4:16, 0].tolist()
    mu_ac = df_input.iloc[4:16, 1].astype(float).values       # E(R)
    cov_ac = df_input.iloc[4:16, 4:16].astype(float).values   # matrice var-cov

    # Serie storiche (date + 12 asset class)
    date_series = pd.to_datetime(df_input.iloc[2:, 19])
    returns_ac = df_input.iloc[2:, 20:32].astype(float)
    returns_ac.columns = nomi_ac
    returns_ac.index = date_series

    # Portafoglio coerente con Step 7
    importo = float(st.session_state.importo)
    equity_str = st.session_state.equity_scelta
    equity_pct = int(equity_str.replace("%", "")) if equity_str else 0
    selezionate = st.session_state.get("asset_class_selezionate", [])

    if not selezionate:
        st.warning("Per effettuare l'analisi storica è necessario aver selezionato almeno una asset class nello Step 6.")
        mostra_pulsanti_navigazione()
        st.stop()

    dettagli, macro = _costruisci_portafoglio(importo, equity_pct, selezionate)

    # Salvo in sessione i pesi e gli importi per ogni asset class,
    # così Step10 può recuperare esattamente gli stessi valori
    st.session_state.pesi_asset_class = {
        nome: float(pct) for (nome, pct, _) in dettagli
    }
    st.session_state.importi_asset_class = {
        nome: float(imp) for (nome, _, imp) in dettagli
    }


    # vettore pesi ordinato come in INPUT_AC
    import numpy as np
    import math
    import matplotlib.pyplot as plt

    w = np.zeros(len(nomi_ac))
    for nome, pct, _ in dettagli:
        if nome in nomi_ac:
            idx = nomi_ac.index(nome)
            w[idx] = pct / 100.0

    if w.sum() == 0:
        st.warning("Non è stato possibile associare i pesi del portafoglio alle asset class dell'INPUT_AC.")
        mostra_pulsanti_navigazione()
        st.stop()

    w = w / w.sum()

    # ------------------------------------------------------------------
    # Indicatori sintetici: rendimento atteso, rischio, pesi bond/equity
    # ------------------------------------------------------------------
    def fmt_pct(x: float) -> str:
        return f"{x*100:.1f}%".replace(".", ",")

    port_er = float(np.dot(w, mu_ac))
    port_var = float(w @ cov_ac @ w)
    port_sd = math.sqrt(port_var) if port_var > 0 else 0.0

    peso_bond = 100.0 * sum(w[i] for i in INDICI_BOND if i < len(w))
    peso_eq   = 100.0 * sum(w[i] for i in INDICI_EQUITY if i < len(w))

    # Box Rendimento / Rischio (grigio)
    st.markdown(
        f"""
        <div style="display:inline-block;border:1px solid #000000;font-size:16px;">
          <div style="background-color:#f2f2f2;padding:4px 14px;min-width:320px;">
            <span>Rendimento Atteso</span>
            <span style="float:right;">{fmt_pct(port_er)}</span>
          </div>
          <div style="background-color:#f2f2f2;padding:4px 14px;min-width:320px;">
            <span>Rischio</span>
            <span style="float:right;">{fmt_pct(port_sd)}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Box Peso Obbligazionario / Peso Azionario (verde e fucsia)
    st.markdown(
        f"""
        <div style="margin-top:8px;display:inline-block;border:1px solid #000000;font-size:16px;">
          <div style="background-color:#00b050;color:#000000;padding:4px 14px;min-width:320px;">
            <span>Peso Obbligazionario</span>
            <span style="float:right;">{peso_bond:.0f}%</span>
          </div>
          <div style="background-color:#ff0066;color:#000000;padding:4px 14px;min-width:320px;">
            <span>Peso Azionario(+Best Ideas)</span>
            <span style="float:right;">{peso_eq:.0f}%</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Titolo sezione Orso–Toro
    st.markdown(
        """
        <div style="margin-top:18px;text-align:center;font-weight:bold;
                    border-top:1px solid #000000;border-bottom:1px solid #000000;
                    padding:4px 0;">
        Comportamento della Asse Allocation nelle fasi Orso-Toro
        </div>
        """,
        unsafe_allow_html=True
    )

    # ------------------------------------------------------------------
    # Serie giornaliera del portafoglio
    # ------------------------------------------------------------------
    port_daily = (returns_ac * w).sum(axis=1)
    port_cum = (1.0 + port_daily).cumprod()

    # ------------------------------------------------------------------
    # Scenari "Orso" (peggiori) – tabella fucsia
    # ------------------------------------------------------------------
    SCENARI_ORSO = [
        ("La crisi russa dell'agosto 1998", "1998-08-19", "1998-09-02"),
        ("L'aumento dei tassi di interesse del '99", "1998-12-30", "1999-12-29"),
        ('La crisi delle ".com"', "2000-03-29", "2003-04-02"),
        ("L'attacco terroristico alle torri gemelle", "2001-09-05", "2001-09-21"),
        ("Il tracollo dell'equity del 2002", "2002-01-02", "2002-12-31"),
        ('La crisi dei "subprime"', "2007-07-24", "2009-03-09"),
        ('Il "Default" di Lehman Brothers', "2008-09-03", "2008-09-17"),
        ("L'Ottobre Nero del 2008", "2008-09-22", "2008-11-06"),
        ('Il picco della crisi del debito € "periferico"', "2011-08-18", "2011-11-10"),
        ("La crisi Covid di inizio 2020", "2020-02-18", "2020-03-23"),
        ("Il rialzo dei tassi del 2022", "2021-12-07", "2022-12-31"),
    ]

    righe_orso = []
    for nome, d_start, d_end in SCENARI_ORSO:
        start = pd.to_datetime(d_start)
        end = pd.to_datetime(d_end)
        mask = (port_daily.index >= start) & (port_daily.index <= end)
        if mask.sum() == 0:
            rend = None
        else:
            rend = (1.0 + port_daily[mask]).prod() - 1.0

        if rend is None:
            rend_str = "n.d."
        elif rend >= 0:
            rend_str = "POSITIVO"
        else:
            rend_str = fmt_pct(rend)
        righe_orso.append(
            (nome, start.strftime("%d/%m/%Y"), end.strftime("%d/%m/%Y"), rend_str)
        )

    rows_html = ""
    for nome, dal, al, rend_str in righe_orso:
        rows_html += f"""
        <tr style="background-color:#ffd6e5;">
          <td style="padding:3px 6px;">{nome}</td>
          <td style="padding:3px 6px;text-align:center;">{dal}</td>
          <td style="padding:3px 6px;text-align:center;">{al}</td>
          <td style="padding:3px 6px;text-align:right;background-color:#ffe699;font-weight:bold;">
            {rend_str}
          </td>
        </tr>
        """

    st.markdown(
        f"""
        <table style="width:100%;border-collapse:collapse;margin-top:10px;font-size:13px;">
          <tr style="background-color:#ff0066;color:#ffffff;font-weight:bold;">
            <th style="padding:4px 6px;text-align:left;">Peggiori scenari</th>
            <th style="padding:4px 6px;text-align:center;">Dal:</th>
            <th style="padding:4px 6px;text-align:center;">Al:</th>
            <th style="padding:4px 6px;text-align:right;">Rend %</th>
          </tr>
          {rows_html}
        </table>
        """,
        unsafe_allow_html=True
    )

    # ------------------------------------------------------------------
    # Scenari "Toro" (migliori) – tabella verde
    # ------------------------------------------------------------------
    SCENARI_TORO = [
        ('Il "Boom" delle ".com"', "1998-10-09", "2000-03-29"),
        ("Lo straordinario 1999 dell'Azionario", "1998-12-31", "1999-12-31"),
        ('La ripresa dopo la crisi delle ".com"', "2003-04-01", "2006-01-09"),
        ('Il rimbalzo dopo la crisi dei "subprime"', "2009-03-10", "2010-01-19"),
        ("L'eccellente 2021", "2020-12-31", "2021-12-31"),
        ("L'eccellente 2023", "2022-12-31", "2023-12-29"),
    ]

    righe_toro = []
    for nome, d_start, d_end in SCENARI_TORO:
        start = pd.to_datetime(d_start)
        end = pd.to_datetime(d_end)
        mask = (port_daily.index >= start) & (port_daily.index <= end)
        if mask.sum() == 0:
            rend = None
        else:
            rend = (1.0 + port_daily[mask]).prod() - 1.0

        if rend is None:
            rend_str = "n.d."
        else:
            rend_str = fmt_pct(rend)
        righe_toro.append(
            (nome, start.strftime("%d/%m/%Y"), end.strftime("%d/%m/%Y"), rend_str)
        )

    rows_html_toro = ""
    for nome, dal, al, rend_str in righe_toro:
        rows_html_toro += f"""
        <tr style="background-color:#e6ffe6;">
          <td style="padding:3px 6px;">{nome}</td>
          <td style="padding:3px 6px;text-align:center;">{dal}</td>
          <td style="padding:3px 6px;text-align:center;">{al}</td>
          <td style="padding:3px 6px;text-align:right;background-color:#c6efce;font-weight:bold;">
            {rend_str}
          </td>
        </tr>
        """

    st.markdown(
        f"""
        <table style="width:100%;border-collapse:collapse;margin-top:10px;font-size:13px;">
          <tr style="background-color:#00b050;color:#ffffff;font-weight:bold;">
            <th style="padding:4px 6px;text-align:left;">Migliori scenari</th>
            <th style="padding:4px 6px;text-align:center;">Dal:</th>
            <th style="padding:4px 6px;text-align:center;">Al:</th>
            <th style="padding:4px 6px;text-align:right;">Rend %</th>
          </tr>
          {rows_html_toro}
        </table>
        """,
        unsafe_allow_html=True
    )

    # ------------------------------------------------------------------
    # Cosa potrebbe accadere in 1 anno? (stima parametrica)
    # ------------------------------------------------------------------
    # port_er e port_sd sono già calcolati sopra come rendimento atteso annuo
    # e deviazione standard annua

    scen_neg1 = port_er - 1.645 * port_sd
    scen_neg2 = port_er - 2.326 * port_sd
    scen_pos1 = port_er + 1.645 * port_sd
    scen_pos2 = port_er + 2.326 * port_sd

    st.markdown(
        f"""
        <div style="margin-top:14px;">
          <div style="background-color:#ff0066;color:#ffffff;padding:4px 10px;font-size:13px;">
            <span>Cosa potrebbe accadere in 1 anno particolarmente negativo</span>
            <span style="float:right;font-weight:bold;">{fmt_pct(scen_neg1)}</span>
          </div>
          <div style="background-color:#ff0066;color:#ffffff;padding:4px 10px;font-size:13px;margin-top:2px;">
            <span>Cosa potrebbe accadere in 1 anno MOLTO negativo</span>
            <span style="float:right;font-weight:bold;">{fmt_pct(scen_neg2)}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div style="margin-top:8px;">
          <div style="background-color:#00b050;color:#ffffff;padding:4px 10px;font-size:13px;">
            <span>Cosa potrebbe accadere in 1 anno particolarmente positivo</span>
            <span style="float:right;font-weight:bold;">{fmt_pct(scen_pos1)}</span>
          </div>
          <div style="background-color:#00b050;color:#ffffff;padding:4px 10px;font-size:13px;margin-top:2px;">
            <span>Cosa potrebbe accadere in 1 anno MOLTO positivo</span>
            <span style="float:right;font-weight:bold;">{fmt_pct(scen_pos2)}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )


    # ------------------------------------------------------------------
    # Miglior / Peggior mese, trimestre, anno
    # (finestre mobili: 21, 63, 262 giorni)
    # ------------------------------------------------------------------
    def best_worst_window(serie: pd.Series, window: int):
        """
        Calcola tutti i rendimenti cumulati di lunghezza 'window' giorni
        secondo logica di concatenazione geometrica, e restituisce:
        - data di inizio del miglior periodo
        - rendimento del miglior periodo
        - data di inizio del peggior periodo
        - rendimento del peggior periodo
        """
        import numpy as np

        if serie.empty or len(serie) < window:
            return None, None, None, None

        # vettore dei rendimenti giornalieri
        r = serie.values.astype(float)

        # indice cumulato: cum[0] = 1, cum[k] = ∏_{i=0}^{k-1} (1 + r_i)
        cum = np.empty(len(r) + 1, dtype=float)
        cum[0] = 1.0
        cum[1:] = np.cumprod(1.0 + r)

        best_ret = -1e9
        worst_ret = 1e9
        best_k = None
        worst_k = None

        # per ogni possibile finestra di ampiezza "window"
        # rendimento da giorno k (incluso) a k+window (escluso):
        # (cum[k+window]/cum[k]) - 1
        for k in range(0, len(r) - window + 1):
            ret = cum[k + window] / cum[k] - 1.0
            if ret > best_ret:
                best_ret = ret
                best_k = k
            if ret < worst_ret:
                worst_ret = ret
                worst_k = k

        if best_k is None or worst_k is None:
            return None, None, None, None

        start_best = serie.index[best_k].date()
        start_worst = serie.index[worst_k].date()

        return start_best, float(best_ret), start_worst, float(worst_ret)


    # finestre: 21 gg (mese), 63 gg (trimestre), 262 gg (anno)
    best_m_d, best_m_r, worst_m_d, worst_m_r = best_worst_window(port_daily, 21)
    best_q_d, best_q_r, worst_q_d, worst_q_r = best_worst_window(port_daily, 63)
    best_y_d, best_y_r, worst_y_d, worst_y_r = best_worst_window(port_daily, 262)

    def box_best(titolo, data, rend):
        if data is None:
            return ""
        return f"""
        <div style="background-color:#00b050;color:#000000;padding:6px 10px;
                    margin-top:6px;font-size:13px;border:1px solid #000000;">
          <div style="font-weight:bold;text-align:center;">{titolo}</div>
          <div><i>Dal:</i> {data.strftime("%d/%m/%Y")}</div>
          <div style="text-align:right;font-weight:bold;">{fmt_pct(rend)}</div>
        </div>
        """

    def box_worst(titolo, data, rend):
        if data is None:
            return ""
        return f"""
        <div style="background-color:#ff0066;color:#ffffff;padding:6px 10px;
                    margin-top:6px;font-size:13px;border:1px solid #000000;">
          <div style="font-weight:bold;text-align:center;">{titolo}</div>
          <div><i>Dal:</i> {data.strftime("%d/%m/%Y")}</div>
          <div style="text-align:right;font-weight:bold;">{fmt_pct(rend)}</div>
        </div>
        """

    blocco_best = (
        box_best("Miglior mese (nella storia):", best_m_d, best_m_r) +
        box_best("Miglior trimestre (nella storia):", best_q_d, best_q_r) +
        box_best("Miglior anno (nella storia):", best_y_d, best_y_r)
    )
    blocco_worst = (
        box_worst("Peggior mese (nella storia):", worst_m_d, worst_m_r) +
        box_worst("Peggior trimestre (nella storia):", worst_q_d, worst_q_r) +
        box_worst("Peggior anno (nella storia):", worst_y_d, worst_y_r)
    )

    st.markdown(
        f"""
        <div style="display:flex;gap:20px;margin-top:16px;">
          <div style="flex:1;">{blocco_best}</div>
          <div style="flex:1;">{blocco_worst}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ------------------------------------------------------------------
    # Fissa tu il periodo da analizzare
    # ------------------------------------------------------------------
    st.markdown(
        """
        <div style="margin-top:16px;background-color:#4f81bd;color:#ffffff;
                    padding:4px 8px;font-size:13px;font-weight:bold;">
            Fissa tu il periodo da analizzare (dal 16 marzo 1998 in poi):
        </div>
        """,
        unsafe_allow_html=True
    )

    min_date = port_daily.index.min().date()
    max_date = port_daily.index.max().date()
    c1, c2 = st.columns(2)
    with c1:
        data_inizio = st.date_input(
            "Dal (gg/mm/aaaa):",
            value=min_date,
            min_value=min_date,
            max_value=max_date,
            key="step8_dal"
        )
    with c2:
        data_fine = st.date_input(
            "Al (gg/mm/aaaa):",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
            key="step8_al"
        )

    risultato_custom = ""
    if data_inizio <= data_fine:
        mask = (
            port_daily.index >= pd.to_datetime(data_inizio)
        ) & (
            port_daily.index <= pd.to_datetime(data_fine)
        )
        if mask.sum() > 0:
            rend_pers = (1.0 + port_daily[mask]).prod() - 1.0
            risultato_custom = fmt_pct(rend_pers)

    if risultato_custom:
        st.markdown(
            f"""
            <div style="background-color:#000000;color:#ffffff;
                        padding:4px 8px;font-size:13px;">
                <span><i>Giorni lavorativi</i></span>
                <span style="float:right;background-color:#c6efce;color:#000000;
                             padding:2px 6px;font-weight:bold;">
                    {risultato_custom}
                </span>
                <br>
                <span>Dal: {data_inizio.strftime("%d/%m/%Y")} &nbsp;&nbsp;
                      Al: {data_fine.strftime("%d/%m/%Y")}</span>
            </div>
            """,
            unsafe_allow_html=True
        )


    # ------------------------------------------------------------------
    # Grafico dell'andamento storico (periodo selezionato dall'utente)
    # base 100, stile "area" e asse Y non ancorato a 0
    # ------------------------------------------------------------------
    if data_inizio <= data_fine:
        mask = (
            port_cum.index >= pd.to_datetime(data_inizio)
        ) & (
            port_cum.index <= pd.to_datetime(data_fine)
        )
        serie_plot = port_cum[mask]
    else:
        serie_plot = port_cum

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Andamento storico del portafoglio", unsafe_allow_html=True)

    if not serie_plot.empty:
        # normalizzazione a base 100
        serie_plot_norm = serie_plot / serie_plot.iloc[0] * 100.0

        y_min = float(serie_plot_norm.min())
        y_max = float(serie_plot_norm.max())

        # piccolo margine sopra e sotto
        y_lower = y_min * 0.98
        y_upper = y_max * 1.02

        fig, ax = plt.subplots(figsize=(12, 4))

        # area: tra serie e livello minimo
        ax.fill_between(
            serie_plot_norm.index,
            serie_plot_norm.values,
            y_lower,
            alpha=0.25,
            color="#fddf9f"
        )

        # linea del montante
        ax.plot(
            serie_plot_norm.index,
            serie_plot_norm.values,
            linewidth=2.5,
            color="#e69100"
        )

        ax.set_title("Evoluzione del montante nel tempo", fontsize=18, pad=10)
        ax.set_ylabel("Valore del portafoglio (base 100)")
        ax.set_xlabel("Data")

        ax.grid(True, alpha=0.3)

        # limiti dell'asse Y in modo che la curva riempia il grafico
        ax.set_ylim(y_lower, y_upper)

        # gestione date asse X (pochi tick, formato italiano)
        locator = mdates.AutoDateLocator(minticks=4, maxticks=8)
        formatter = mdates.DateFormatter("%d/%m/%Y")
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        fig.autofmt_xdate(rotation=30, ha="right")

        st.pyplot(fig)
    else:
        st.write("Nessun dato disponibile per il periodo selezionato.")

    mostra_pulsanti_navigazione()

# --------------------------------------------------------------------
# STEP 9 – INTRODUZIONE ALLA SELEZIONE DEI GESTORI
# --------------------------------------------------------------------
elif step_corrente == "Step 9":
    st.markdown(
        '<div class="step-title">Step 9 – Introduzione alla selezione dei gestori</div>',
        unsafe_allow_html=True
    )

    # Immagine (se esiste un file "step9.png")
    mostra_immagine("step9.png", "Selezione dei gestori")

    testo_step9 = (
        "Nei successivi fogli di lavoro procederai alla selezione dei gestori "
        "per la creazione del portafoglio di fondi da proporre alla clientela. "
        "Procederai step by step, selezionando i prodotti per ciascuna delle "
        "asset class che hai deciso di inserire nell'asset allocation. Avrai la "
        "possibilità di inserire per ogni asset class uno o anche più prodotti. "
        "La logica è chiaramente quella di utilizzare più prodotti solo quando "
        "l'ammontare da investire nell'asset class lo giustifica."
    )

    st.markdown(
        f"""
        <div style="
            background-color: #d7ecff;
            padding: 16px;
            border-radius: 8px;
            color: #000000;
            font-size: 15px;
            line-height: 1.5;
        ">
        {testo_step9}
        </div>
        """,
        unsafe_allow_html=True
    )

    mostra_pulsanti_navigazione()

# --------------------------------------------------------------------
# STEP 10 – SELEZIONE DEI FONDI PER SINGOLA ASSET CLASS
# --------------------------------------------------------------------
elif step_corrente == "Step 10":
    st.markdown(
        '<div class="step-title">Step 10 – Selezione dei fondi per singola asset class</div>',
        unsafe_allow_html=True
    )

    mostra_immagine("step10.png", "Selezione dei fondi per asset class")

    # Elenco delle 12 asset class gestite in questo step
    asset_class_list = [
        "Obbligazionario Euro BT",
        "Obbligazionario Euro MLT",
        "Obbligazionario Euro Corporate",
        "Obbligazionario Globale",
        "Obbligazionario Paesi Emergenti",
        "Obbligazionario Globale High Yield",
        "Azionario Europa/Euro",
        "Azionario Nord America",
        "Azionario Pacifico",
        "Azionario Paesi Emergenti",
        "Azionario Internazionale",
        "Best Ideas",
    ]

    # Dizionari provenienti dallo Step 7
    pesi_asset = st.session_state.get("pesi_asset_class", {})
    importi_asset = st.session_state.get("importi_asset_class", {})

    # Lettura DB dei fondi
    fondi_path = Path("DB_FONDI.xlsx")
    if not fondi_path.exists():
        st.error("File 'DB_FONDI.xlsx' non trovato nella stessa cartella di 'app_portafoglio.py'.")
        mostra_pulsanti_navigazione()
        st.stop()

    df_all = pd.read_excel(fondi_path)

    # Colonne chiave del DB
    if "Asset Class" in df_all.columns:
        col_ac = "Asset Class"
    elif "AssetClass" in df_all.columns:
        col_ac = "AssetClass"
    else:
        st.error("Nel file DB_FONDI.xlsx non trovo la colonna 'Asset Class'.")
        mostra_pulsanti_navigazione()
        st.stop()

    # Colonna società di gestione (per evidenziare NEF)
    if "Società di Gestione" in df_all.columns:
        col_sg = "Società di Gestione"
    elif "Societa di Gestione" in df_all.columns:
        col_sg = "Societa di Gestione"
    else:
        col_sg = None

    # Una tab per ciascuna asset class
    tabs = st.tabs(asset_class_list)

    for asset_name, tab in zip(asset_class_list, tabs):
        with tab:
            st.markdown(f"### {asset_name}")

            # Leggo peso e importo calcolati in Step 7
            peso = float(pesi_asset.get(asset_name, 0.0))
            importo_ac = float(importi_asset.get(asset_name, 0.0))

            # Header come da immagine (nome, importo, peso)
            st.markdown(
                f"""
                <table style="border-collapse:collapse; width:100%; font-size:14px;">
                    <tr style="background-color:#f0f0f0; font-weight:bold; text-align:center;">
                        <td style="border:1px solid #000; width:50%;">Asset Class</td>
                        <td style="border:1px solid #000; width:25%;">Importo da investire:</td>
                        <td style="border:1px solid #000; width:25%;">Peso in portafoglio</td>
                    </tr>
                    <tr style="background-color:#ffffff;">
                        <td style="border:1px solid #000; color:#008000; font-weight:bold; padding-left:6px;">
                            {asset_name}
                        </td>
                        <td style="border:1px solid #000; text-align:right; padding-right:6px;">
                            {importo_ac:,.0f} €
                        </td>
                        <td style="border:1px solid #000; text-align:center; background-color:#dddddd;">
                            {peso:.1f}%
                        </td>
                    </tr>
                </table>
                """,
                unsafe_allow_html=True
            )

            st.write("")

            # Se l'asset class NON è stata selezionata nello Step 6 → avviso rosso
            if asset_name not in st.session_state.asset_class_selezionate:
                st.markdown(
                    """
                    <div style="
                        background-color:#ff4d4d;
                        color:#ffffff;
                        padding:12px;
                        border-radius:6px;
                        font-weight:bold;
                    ">
                    Questa Asset Class non è stata selezionata nello Step 6.
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                continue

            # Filtra i fondi per l'asset class corrente
            df_ac = df_all[df_all[col_ac] == asset_name].copy()
            if df_ac.empty:
                st.warning("Nel file DB_FONDI.xlsx non risultano fondi per questa asset class.")
                continue

            # Recupero eventuali scelte già fatte in passato
            if asset_name in st.session_state.fondi_step10:
                df_editor = st.session_state.fondi_step10[asset_name].copy()
            else:
                df_editor = df_ac.copy()
                # colonne per l'utente (se non esistono)
                if "Seleziona" not in df_editor.columns:
                    df_editor.insert(0, "Seleziona", False)
                if "Peso %" not in df_editor.columns:
                    df_editor.insert(1, "Peso %", 0.0)

            # Colonne disabilitate alla modifica (ma tutte ordinabili cliccando sul titolo)
            colonne_disabilitate = [
                c for c in df_editor.columns if c not in ["Seleziona", "Peso %"]
            ]

            # Evidenzio i NEF con una colonna testuale aggiuntiva (opzionale)
            if col_sg is not None and col_sg in df_editor.columns:
                if "NEF" not in df_editor.columns:
                    df_editor.insert(
                        2,
                        "NEF",
                        df_editor[col_sg].apply(
                            lambda x: "NEF" if str(x).strip() == "Nord Est Asset Management SA" else ""
                        ),
                    )
                if "NEF" not in colonne_disabilitate:
                    colonne_disabilitate.append("NEF")

            col_config = {
                "Seleziona": st.column_config.CheckboxColumn(
                    "Seleziona",
                    help="Spunta i fondi che vuoi inserire in portafoglio."
                ),
                "Peso %": st.column_config.NumberColumn(
                    "Peso %",
                    help="Peso percentuale del fondo all'interno dell'asset class.",
                    min_value=0.0,
                    max_value=100.0,
                    step=1.0,
                    format="%.1f",
                ),
            }

            st.markdown("#### Seleziona i fondi e attribuisci i pesi (la somma deve fare 100%)")

            # QUI usiamo st.data_editor → tutte le colonne sono ordinabili cliccando sul titolo
            df_editato = st.data_editor(
                df_editor,
                use_container_width=True,
                column_config=col_config,
                disabled=colonne_disabilitate,
                num_rows="fixed",
                key=f"editor_{asset_name.replace(' ', '_')}",
            )

            # Salvo le scelte in sessione
            st.session_state.fondi_step10[asset_name] = df_editato

            # Controllo somma dei pesi
            if "Seleziona" in df_editato.columns and "Peso %" in df_editato.columns:
                selezionati = df_editato[df_editato["Seleziona"] == True]
                somma_pesi = float(selezionati["Peso %"].sum())

                if abs(somma_pesi - 100.0) > 1e-6:
                    st.markdown(
                        f"""
                        <div style="
                            background-color:#ffcccc;
                            color:#990000;
                            padding:10px;
                            border-radius:6px;
                            font-weight:bold;
                        ">
                        Attenzione: la somma dei pesi dei fondi selezionati è pari a {somma_pesi:.1f}%.
                        Deve essere pari a 100%.
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        """
                        <div style="
                            background-color:#d8f5d0;
                            color:#006600;
                            padding:10px;
                            border-radius:6px;
                            font-weight:bold;
                        ">
                        La somma dei pesi dei fondi selezionati è correttamente pari a 100%.
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    mostra_pulsanti_navigazione()

# --------------------------------------------------------------------
# STEP 11 – RIEPILOGO DEI FONDI E VALORI MEDI DI PORTAFOGLIO
# --------------------------------------------------------------------
elif step_corrente == "Step 11":
    st.markdown(
        '<div class="step-title">Step 11 – Riepilogo dei fondi selezionati</div>',
        unsafe_allow_html=True
    )

    mostra_immagine("step11.png", "Riepilogo complessivo dei fondi")

    pesi_asset = st.session_state.get("pesi_asset_class", {})
    importi_asset = st.session_state.get("importi_asset_class", {})
    fondi_dict = st.session_state.get("fondi_step10", {})

    if not fondi_dict:
        st.warning("Non risultano fondi selezionati nello Step 10.")
        mostra_pulsanti_navigazione()
        st.stop()

    righe = []

    # ------------------------------------------------------------
    # COSTRUISCO DATAFRAME COMPLESSIVO DEI FONDI SELEZIONATI
    # ------------------------------------------------------------
    for asset_name, df_fondi in fondi_dict.items():
        if asset_name not in pesi_asset or asset_name not in importi_asset:
            continue

        peso_ac = float(pesi_asset.get(asset_name, 0.0))       # % della asset class
        importo_ac = float(importi_asset.get(asset_name, 0.0)) # € nella asset class

        if "Seleziona" not in df_fondi.columns or "Peso %" not in df_fondi.columns:
            continue

        selezionati = df_fondi[df_fondi["Seleziona"] == True].copy()
        if selezionati.empty:
            continue

        for _, r in selezionati.iterrows():
            peso_fondo_ac = float(r["Peso %"])   # % all'interno della AC
            peso_portafoglio = peso_ac * peso_fondo_ac / 100.0
            importo_fondo = importo_ac * (peso_fondo_ac / 100.0)

            nome_fondo = r.get("Nome Fondo", "")
            isin = r.get("ISIN", r.get("Isin", ""))
            rating_fp = r.get("Rating Fund Partners", r.get("RatingFundPartners", None))
            rating_q = r.get("Rating Quantalys", r.get("RatingQuantalys", None))
            perf_ytd = r.get("Perf YTD", r.get("PerfYTD", None))
            perf_3y = r.get("Perf annua su triennio", r.get("PerfAnnuaSuTriennio", None))
            rischio_3y = r.get("Rischio su triennio", r.get("RischioSuTriennio", None))
            sharpe_3y = r.get("Sharpe su Triennio", r.get("SharpeSuTriennio", None))
            spese_corr = r.get("Spese correnti", r.get("SpeseCorrenti", None))
            comm_max_retr = r.get("Comm. Gestione MAX Retrocessa", r.get("CommGestioneMAXRetrocessa", None))

            righe.append({
                "Asset Class": asset_name,
                "Nome Fondo": nome_fondo,
                "ISIN": isin,
                "Peso nella AC %": peso_fondo_ac,
                "Peso in Portafoglio %": peso_portafoglio,
                "Importo": importo_fondo,
                "Rating Fund Partners": rating_fp,
                "Rating Quantalys": rating_q,
                "Perf YTD": perf_ytd,
                "Perf annua su triennio": perf_3y,
                "Rischio su triennio": rischio_3y,
                "Sharpe su Triennio": sharpe_3y,
                "Spese correnti": spese_corr,
                "Comm. Gestione MAX Retrocessa": comm_max_retr,
            })

    if not righe:
        st.warning("Non è stato selezionato alcun fondo con peso > 0%.")
        mostra_pulsanti_navigazione()
        st.stop()

    df_riep_raw = pd.DataFrame(righe)

    # ------------------------------------------------------------
    # TABELLA RIEPILOGATIVA DETTAGLIATA
    # ------------------------------------------------------------
    colonne_ordine = [
        "Nome Fondo",
        "ISIN",
        "Importo",
        "Peso nella AC %",
        "Peso in Portafoglio %",
        "Asset Class",
        "Rating Fund Partners",
        "Rating Quantalys",
        "Perf YTD",
        "Perf annua su triennio",
        "Rischio su triennio",
        "Sharpe su Triennio",
        "Spese correnti",
        "Comm. Gestione MAX Retrocessa",
    ]
    colonne_presenti = [c for c in colonne_ordine if c in df_riep_raw.columns]
    df_riep = df_riep_raw[colonne_presenti].copy()

    def _fmt_importo(x):
        return f"{x:,.0f} €".replace(",", ".")

    def _fmt_pct(x):
        return f"{x:.1f}%"

    if "Importo" in df_riep.columns:
        df_riep["Importo"] = df_riep["Importo"].apply(_fmt_importo)
    for col in ["Peso nella AC %", "Peso in Portafoglio %"]:
        if col in df_riep.columns:
            df_riep[col] = df_riep[col].apply(_fmt_pct)

    st.markdown(
        """
        <div style="
            background-color:#005b96;
            color:#ffffff;
            padding:6px;
            font-weight:bold;
            font-size:14px;
        ">
        I Fondi selezionati:
        </div>
        """,
        unsafe_allow_html=True
    )
    st.dataframe(df_riep, use_container_width=True)

    # ------------------------------------------------------------
    # VALORI MEDI A LIVELLO DI PORTAFOGLIO (MEDIE PONDERATE)
    # ------------------------------------------------------------
    st.write("")
    st.write("")

    pesi_port = df_riep_raw["Peso in Portafoglio %"].astype(float)  # es. 7.5, 12.0, ...

    def _to_num(series, is_percent):
        """
        Converte una colonna in numerico, gestendo:
        - valori già numerici (es. 0.0345, 4.5)
        - stringhe in formato italiano: '3,45', '3,45%', '1.234,56'
        - se is_percent=True e i dati sono numerici (0.0345) li porta in % moltiplicando per 100.
        """
        import pandas.api.types as ptypes

        # Caso 1: la colonna è già numerica (come avviene di solito quando l'Excel ha formattazione %)
        if ptypes.is_numeric_dtype(series):
            arr = series.astype(float)
            if is_percent:
                # da 0.0345 → 3.45
                arr = arr * 100.0
            return arr

        # Caso 2: stringhe
        s = series.astype(str).str.replace("%", "", regex=False).str.strip()

        # Se c'è sia "." che "," assumo "." come separatore delle migliaia e "," come decimale
        mask_both = s.str.contains(",", regex=False) & s.str.contains(".", regex=False)

        s1 = s.copy()
        s1[mask_both] = (
            s1[mask_both]
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
        )

        # Solo virgola → decimale italiano
        mask_comma_only = s.str.contains(",", regex=False) & ~mask_both
        s1[mask_comma_only] = s1[mask_comma_only].str.replace(",", ".", regex=False)

        # Altri casi (solo punto o solo numeri) li lascio così
        vals = pd.to_numeric(s1, errors="coerce")
        return vals  # qui NON moltiplico per 100: le stringhe sono già in unità "percento"

    metriche = [
        ("Rating Fund Partners", False),
        ("Rating Quantalys", False),
        ("Perf YTD", True),
        ("Perf annua su triennio", True),
        ("Rischio su triennio", True),
        ("Sharpe su Triennio", False),
        ("Spese correnti", True),
        ("Comm. Gestione MAX Retrocessa", True),
    ]

    risultati = {}
    for col, is_percent in metriche:
        if col not in df_riep_raw.columns:
            risultati[col] = None
            continue

        valori = _to_num(df_riep_raw[col], is_percent)
        mask = valori.notna() & pesi_port.notna()

        if not mask.any():
            risultati[col] = None
            continue

        w_eff = pesi_port[mask]
        v_eff = valori[mask]

        media = (v_eff * w_eff).sum() / w_eff.sum()
        risultati[col] = (media, is_percent)

    headers = [
        "Rating Fund Partners",
        "Rating Quantalys",
        "Perf YTD",
        "Perf annua su triennio",
        "Rischio su triennio",
        "Sharpe su Triennio",
        "Spese correnti",
        "Comm. Gestione MAX Retrocessa",
    ]

    valori_formattati = []
    for h in headers:
        if h not in risultati or risultati[h] is None:
            if h in ["Rating Fund Partners", "Rating Quantalys", "Sharpe su Triennio"]:
                valori_formattati.append("0,0")
            else:
                valori_formattati.append("0,00%")
        else:
            val, is_percent = risultati[h]
            if is_percent:
                valori_formattati.append(f"{val:.2f}%".replace(".", ","))
            else:
                valori_formattati.append(f"{val:.1f}".replace(".", ","))

    cells_header = "".join(
        f'<td style="border:1px solid #000; padding:4px 8px; text-align:center;">{h}</td>'
        for h in headers
    )
    cells_values = "".join(
        f'<td style="border:1px solid #000; padding:6px 8px; text-align:center; font-weight:bold;">{v}</td>'
        for v in valori_formattati
    )

    st.markdown(
        f"""
        <table style="border-collapse:collapse; width:100%; font-size:13px; margin-top:16px;">
            <tr>
                <td colspan="{len(headers)}" style="
                    border:1px solid #000;
                    background-color:#005b96;
                    color:#ffffff;
                    font-weight:bold;
                    text-align:center;
                    padding:4px;
                ">
                    VALORI MEDI A LIVELLO DI PORTAFOGLIO COMPLESSIVO
                </td>
            </tr>
            <tr style="background-color:#d7ecff; color:#004080; font-weight:bold;">
                {cells_header}
            </tr>
            <tr style="background-color:#e9f4ff;">
                {cells_values}
            </tr>
        </table>
        """,
        unsafe_allow_html=True
    )

    # ------------------------------------------------------------
    # GRAFICO A TORTA – COMPOSIZIONE PER PRODOTTO
    # ------------------------------------------------------------
    st.write("")
    st.write("")
    st.markdown("#### Composizione del portafoglio per prodotto")

    try:
        labels = df_riep_raw["Nome Fondo"].astype(str).tolist()
        sizes = df_riep_raw["Peso in Portafoglio %"].astype(float).tolist()

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct="%1.0f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)
    except Exception as e:
        st.warning(f"Impossibile creare il grafico a torta: {e}")



    mostra_pulsanti_navigazione()


# --------------------------------------------------------------------
# STEP 12 – Gestione PAC
# --------------------------------------------------------------------
elif step_corrente == "Step 12":
    mostra_immagine("step12.png", "Investimenti ricorrenti")
    

    st.markdown(
        "<div class='step-subtitle'>In questa sezione potrai ipotizzare degli investimenti ricorrenti, così da realizzare un PAC. "
        "Ti verranno qui di seguito richieste una serie di informazioni che dovrai fornire dettagliatamente.</div>",
        unsafe_allow_html=True
    )



    st.markdown(
        "<div style='color:#005b96; font-weight:bold; font-size:30px; margin-top:12px;'>"
        "Informazioni relative agli eventuali conferimenti periodici"
        "</div>",
        unsafe_allow_html=True
    )

    col_a, col_b = st.columns(2)
    with col_a:
        st.write(f"**Importo iniziale investito:** {st.session_state.importo:,.0f} €".replace(",", "."))
    with col_b:
        st.write(f"**Orizzonte temporale:** {st.session_state.orizzonte:.1f} anni")

    st.write("")

    if "usa_pac" not in st.session_state:
        st.session_state.usa_pac = "No"
    if "frequenza_pac" not in st.session_state:
        st.session_state.frequenza_pac = "Mensile"
    if "importo_pac" not in st.session_state:
        st.session_state.importo_pac = 0.0

    st.session_state.usa_pac = st.selectbox(
        "Vuoi ipotizzare degli investimenti periodici?",
        ["No", "Sì"],
        index=["No", "Sì"].index(st.session_state.usa_pac)
    )

    frequenza = None
    importo_pac = 0.0

    if st.session_state.usa_pac == "Sì":
        st.session_state.frequenza_pac = st.selectbox(
            "Con quale frequenza verranno effettuati i conferimenti?",
            ["Mensile", "Bimestrale", "Trimestrale", "Semestrale", "Annuale"],
            index=["Mensile", "Bimestrale", "Trimestrale", "Semestrale", "Annuale"].index(st.session_state.frequenza_pac)
        )
        st.session_state.importo_pac = st.number_input(
            "Importo di ciascun conferimento",
            min_value=0.0,
            value=float(st.session_state.importo_pac),
            step=100.0,
            format="%.0f"
        )
        frequenza = st.session_state.frequenza_pac
        importo_pac = st.session_state.importo_pac
    else:
        frequenza = None
        importo_pac = 0.0

    st.write("")
    st.markdown("#### Dinamica temporale dei flussi investiti")

    orizzonte_anni = float(st.session_state.orizzonte)
    importo_iniziale = float(st.session_state.importo)

    if orizzonte_anni <= 0 or importo_iniziale <= 0:
        st.info("Per visualizzare il grafico, assicurati di aver inserito un importo iniziale e un orizzonte temporale positivi nello Step 1.")
        mostra_pulsanti_navigazione()
    else:
    # Costruzione dei flussi e dei tempi in ANNI
        valori = []
        tempi_anni = []

    # Investimento iniziale al tempo 0
    valori.append(importo_iniziale)
    tempi_anni.append(0.0)

    if st.session_state.usa_pac == "Sì" and importo_pac > 0:
        freq_to_mesi = {
            "Mensile": 1,
            "Bimestrale": 2,
            "Trimestrale": 3,
            "Semestrale": 6,
            "Annuale": 12,
        }
        mesi_totali = orizzonte_anni * 12
        passo = freq_to_mesi.get(frequenza, 1)
        n_periodi = int(mesi_totali // passo)

        # Aggiungo i conferimenti periodici con il relativo tempo in anni
        for i in range(1, n_periodi + 1):
            valori.append(importo_pac)
            tempi_anni.append(i * passo / 12.0)  # tempo in anni

    # Grafico a barre con asse delle x in anni (e pochi tick per evitare sovrapposizioni)
    import numpy as np

    x = np.arange(len(valori))  # posizioni delle barre

    fig, ax = plt.subplots()
    ax.bar(x, valori, color="#ff9900")

    # Riduzione del numero di tick sull'asse x
    max_ticks = 8
    if len(x) <= max_ticks:
        tick_idx = x
    else:
        tick_idx = np.linspace(0, len(x) - 1, max_ticks, dtype=int)
        tick_idx = np.unique(tick_idx)  # elimina eventuali duplicati

    tick_labels = [f"{tempi_anni[i]:.1f}" for i in tick_idx]

    ax.set_xticks(tick_idx)
    ax.set_xticklabels(tick_labels, fontsize=8)
    ax.set_ylabel("Importo del flusso (€)")
    ax.set_xlabel("Tempo (anni)")
    ax.set_title("Flussi di investimento nel tempo")

    st.pyplot(fig)

    mostra_pulsanti_navigazione()

# --------------------------------------------------------------------
# STEP 13 – Life Cycle
# --------------------------------------------------------------------
elif step_corrente == "Step 13":
    mostra_immagine("step13.png", "Life Cycle")

    # Testo introduttivo
    st.markdown(
        """
        <div style="font-size:16px; font-weight:bold;">
        In questa sezione potrai implementare una logica Life Cycle, consistente nel cambiare la composizione del portafoglio
        nella parte finale del periodo di investimento, allo scopo di non essere più sensibilmente esposti all'andamento
        negativo dei mercati. Ti verranno qui di seguito richieste una serie di informazioni che dovrai fornire dettagliatamente.
        </div>
        """,
        unsafe_allow_html=True
    )

    # Titolo blu
    st.markdown(
        "<div style='color:#004c99; font-size:18px; font-weight:bold; margin-top:15px;'>"
        "Informazioni relative alla dinamica di composizione del portafoglio"
        "</div>",
        unsafe_allow_html=True
    )

    # -----------------------------------------------------------------
    # Recupero dei dati di base
    # -----------------------------------------------------------------
    orizzonte = float(st.session_state.get("orizzonte", 0.0))
    pesi_ac_originali = st.session_state.get("pesi_asset_class", {})

    if not pesi_ac_originali:
        st.warning("Per utilizzare la logica Life Cycle occorre prima definire l'asset allocation nello Step 7.")
        mostra_pulsanti_navigazione()
        st.stop()

    # -----------------------------------------------------------------
    # 1) Menu: vuoi ipotizzare Life Cycle? (valore persistente)
    # -----------------------------------------------------------------
    default_flag = st.session_state.get("life_cycle_flag", "No")
    if default_flag not in ["No", "Sì"]:
        default_flag = "No"

    risposta_lc = st.selectbox(
        "Vuoi ipotizzare un investimento Life Cycle?",
        ["No", "Sì"],
        index=["No", "Sì"].index(default_flag)
    )
    st.session_state.life_cycle_flag = risposta_lc

    import numpy as np
    import matplotlib.pyplot as plt

    # -----------------------------------------------------------------
    # Caso: Life Cycle NON attivato → grafico con pesi costanti
    # -----------------------------------------------------------------
    if risposta_lc == "No":
        st.info("Non hai attivato la logica Life Cycle. Il portafoglio rimarrà costante nel tempo.")

        anni = np.linspace(0, orizzonte, 30)

        labels = list(pesi_ac_originali.keys())
        values = np.array([pesi_ac_originali[k] for k in labels], dtype=float)
        # normalizzazione di sicurezza
        if values.sum() != 0:
            values = values * (100.0 / values.sum())
        repeated = np.tile(values, (len(anni), 1))

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.stackplot(anni, repeated.T, labels=labels)
        ax.legend(loc="upper left", fontsize=7)
        ax.set_xlabel("Anni")
        ax.set_ylabel("Peso %")
        ax.set_title("Evoluzione dell'asset allocation (senza Life Cycle)")

        st.pyplot(fig)
        mostra_pulsanti_navigazione()
        st.stop()

    # -----------------------------------------------------------------
    # Caso: Life Cycle attivato
    # -----------------------------------------------------------------

    # Opzioni possibili: anni prima della fine, < orizzonte
    possibili_anni = [i for i in range(3, 11) if i < orizzonte]
    if not possibili_anni:
        st.warning("L'orizzonte temporale è troppo breve per applicare una logica Life Cycle con almeno 3 anni di transizione.")
        mostra_pulsanti_navigazione()
        st.stop()

    # valore di default per gli anni (se già scelto in passato)
    default_anni = st.session_state.get("life_cycle_anni_inizio", possibili_anni[0])
    if default_anni not in possibili_anni:
        default_anni = possibili_anni[0]

    anni_inizio = st.selectbox(
        "Quanti anni prima della fine del periodo di investimento vuoi che inizi la riduzione della componente rischiosa?",
        possibili_anni,
        index=possibili_anni.index(default_anni)
    )
    st.session_state.life_cycle_anni_inizio = int(anni_inizio)

    # Istante (in anni) in cui parte la fase di transizione
    anno_start = orizzonte - anni_inizio

    # -----------------------------------------------------------------
    # Costruzione dei pesi nel tempo con migrazione verso 100% Obbl. Euro BT
    # -----------------------------------------------------------------
    # Copia dei pesi originali e forzo la presenza di "Obbligazionario Euro BT"
    pesi_ac = pesi_ac_originali.copy()
    if "Obbligazionario Euro BT" not in pesi_ac:
        pesi_ac["Obbligazionario Euro BT"] = 0.0

    labels = list(pesi_ac.keys())
    pesi_iniziali = np.array([pesi_ac[k] for k in labels], dtype=float)

    somma_init = pesi_iniziali.sum()
    if somma_init != 0:
        pesi_iniziali = pesi_iniziali * (100.0 / somma_init)

    # Indice dell'Obbligazionario Euro BT
    if "Obbligazionario Euro BT" in labels:
        idx_bt = labels.index("Obbligazionario Euro BT")
    else:
        labels.append("Obbligazionario Euro BT")
        pesi_iniziali = np.append(pesi_iniziali, 0.0)
        idx_bt = len(labels) - 1

    # Grid temporale
    anni = np.linspace(0, orizzonte, 40)
    matrice_pesi = []

    for t in anni:
        if t <= anno_start:
            # Prima del Life Cycle: portafoglio costante
            matrice_pesi.append(pesi_iniziali.copy())
        else:
            # Fase di transizione verso 100% Obbligazionario Euro BT
            if orizzonte == anno_start:
                progresso = 1.0
            else:
                progresso = (t - anno_start) / (orizzonte - anno_start)
                progresso = min(max(progresso, 0.0), 1.0)

            pesi_non_bt = pesi_iniziali.copy()
            pesi_non_bt[idx_bt] = 0.0

            pesi_non_bt_t = pesi_non_bt * (1.0 - progresso)
            somma_non_bt_t = pesi_non_bt_t.sum()

            pesi_t = pesi_non_bt_t
            pesi_t[idx_bt] = 100.0 - somma_non_bt_t

            somma_t = pesi_t.sum()
            if somma_t != 0:
                pesi_t = pesi_t * (100.0 / somma_t)

            matrice_pesi.append(pesi_t)

    matrice_pesi = np.array(matrice_pesi)

    # -----------------------------------------------------------------
    # Grafico ad area dell'evoluzione dell'asset allocation
    # -----------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.stackplot(anni, matrice_pesi.T, labels=labels)
    ax.legend(loc="upper left", fontsize=7)
    ax.set_xlabel("Anni")
    ax.set_ylabel("Peso %")
    ax.set_title("Evoluzione dell'asset allocation con Life Cycle\n(confluenza finale in Obbligazionario Euro BT)")

    st.pyplot(fig)

    mostra_pulsanti_navigazione()

# --------------------------------------------------------------------
# STEP 14 – Simulazione Monte Carlo del montante
# --------------------------------------------------------------------
elif step_corrente == "Step 14":
    mostra_immagine("step14.png", "Simulazioni Monte Carlo del montante")

        # Box introduttivo su sfondo azzurro
    st.markdown(
        f"""
        <div style="
            background-color: #d7ecff;
            padding: 16px;
            border-radius: 8px;
            color: #000000;
            font-size: 15px;
            line-height: 1.5;
        ">
        In questa sezione vengono simulate 1.000 possibili evoluzioni temporali del montante del portafoglio,
        tenendo conto di:<br>
        
        (a) rendimento atteso, rischi e correlazioni delle asset class;<br>
        (b) importo inizialmente investito;<br>
        (c) orizzonte temporale complessivo;<br>
        (d) eventuali conferimenti periodici (Step 12);<br>
        (e) eventuale logica Life Cycle (Step 13).<br><br>
        Nel Grafico le linee grigie identificano l'evoluzione temporale del montante di ogni singola simulazione, la linea verde rappresenta lo scenario ottimistico corrispondente al novantesimo percentile, la linea rossa rappresenta lo scenario pessimistico corrispondente al decimo percentile e la linea blu rappresenta lo scenario atteso.<br>
        La Tabella mostra per ciascuno degli anni che compongono il periodo di investimento il Montante Ottimistico, quello Atteso ed infine quello Pessimistico.
        </div>
        """,
        unsafe_allow_html=True
    )


    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt

    # Avvolgo la parte "delicata" in un try/except così, se c'è un problema,
    # Streamlit mostra l'errore invece di fermarsi in silenzio.
    try:
        # --------------------------------------------------------------
        # 1. Lettura dei dati dal file INPUT_AC.xlsx
        # --------------------------------------------------------------
        df_in = pd.read_excel("INPUT_AC.xlsx", sheet_name=0, header=None)

        # Nomi delle asset class (A5:A16)
        asset_names = df_in.iloc[4:16, 0].astype(str).tolist()

        # Rendimenti attesi annuali (B5:B16)
        mu_ann = df_in.iloc[4:16, 1].astype(float).to_numpy()

        # Matrice varianze-covarianze annuale (E5:P16)
        Sigma_ann = df_in.iloc[4:16, 4:16].astype(float).to_numpy()

        # Passo mensile
        mu_m = mu_ann / 12.0
        Sigma_m = Sigma_ann / 12.0

        n_assets = len(asset_names)
        name_to_idx = {n: i for i, n in enumerate(asset_names)}

        # --------------------------------------------------------------
        # 2. Recupero informazioni dagli step precedenti
        # --------------------------------------------------------------
        importo_iniziale = float(st.session_state.get("importo", 0.0))
        T_years = float(st.session_state.get("orizzonte", 0.0))

        usa_pac = st.session_state.get("usa_pac", "No")
        freq_pac = st.session_state.get("frequenza_pac", "Annuale")
        importo_pac = float(st.session_state.get("importo_pac", 0.0))

        life_cycle_flag = st.session_state.get("life_cycle_flag", "No")
        anni_inizio_lc = int(st.session_state.get("life_cycle_anni_inizio", 0))

        pesi_ac = st.session_state.get("pesi_asset_class", {})
        if not pesi_ac:
            st.error("Per eseguire la simulazione occorre aver definito l'asset allocation nello Step 7.")
            mostra_pulsanti_navigazione()
            st.stop()

        # L'asset class Obbligazionario Euro BT deve sempre esistere
        if "Obbligazionario Euro BT" not in pesi_ac:
            pesi_ac["Obbligazionario Euro BT"] = 0.0

        # --------------------------------------------------------------
        # 3. Costruzione dei pesi per anno (con o senza Life Cycle)
        # --------------------------------------------------------------
        anni_tot_int = int(round(T_years))
        if anni_tot_int <= 0:
            st.error("L'orizzonte temporale deve essere positivo per eseguire le simulazioni.")
            mostra_pulsanti_navigazione()
            st.stop()

        # Vettore di pesi iniziali (decimali) allineato alle asset del file INPUT_AC
        w0 = np.zeros(n_assets)
        for nome, peso_perc in pesi_ac.items():
            if nome in name_to_idx:
                w0[name_to_idx[nome]] = float(peso_perc) / 100.0

        if w0.sum() == 0:
            st.error("I pesi iniziali risultano nulli. Controllare lo Step 7 e la coerenza dei nomi delle asset class.")
            mostra_pulsanti_navigazione()
            st.stop()

        w0 = w0 / w0.sum()

        # Indice Obbligazionario Euro BT
        idx_bt = name_to_idx.get("Obbligazionario Euro BT", None)
        if idx_bt is None:
            st.error("L'asset class 'Obbligazionario Euro BT' non è presente nel file INPUT_AC.")
            mostra_pulsanti_navigazione()
            st.stop()

        # Matrice pesi per anno (0..anni_tot_int-1)
        weights_year = np.zeros((anni_tot_int, n_assets))

        if life_cycle_flag != "Sì" or anni_inizio_lc <= 0 or anni_inizio_lc >= T_years:
            # Nessun Life Cycle: pesi costanti
            for y in range(anni_tot_int):
                weights_year[y, :] = w0
        else:
            # Life Cycle: migrazione verso 100% Obbligazionario Euro BT
            start_year = T_years - anni_inizio_lc
            for y in range(anni_tot_int):
                t = y + 0.5  # punto medio dell'anno
                if t <= start_year:
                    weights_year[y, :] = w0
                else:
                    progresso = (t - start_year) / (T_years - start_year)
                    progresso = min(max(progresso, 0.0), 1.0)

                    w_non_bt = w0.copy()
                    w_non_bt[idx_bt] = 0.0
                    w_non_bt_t = w_non_bt * (1.0 - progresso)
                    somma_non_bt_t = w_non_bt_t.sum()

                    w_t = w_non_bt_t
                    w_t[idx_bt] = max(0.0, 1.0 - somma_non_bt_t)

                    if w_t.sum() > 0:
                        w_t = w_t / w_t.sum()

                    weights_year[y, :] = w_t

        # --------------------------------------------------------------
        # 4. Simulazioni Monte Carlo (passo mensile)
        # --------------------------------------------------------------
        n_steps = anni_tot_int * 12
        n_scen = 1000

        # Rendimenti multivariati mensili simulati
        R = np.random.multivariate_normal(mu_m, Sigma_m, size=(n_steps, n_scen))

        # Gestione PAC
        freq_to_mesi = {
            "Mensile": 1,
            "Bimestrale": 2,
            "Trimestrale": 3,
            "Semestrale": 6,
            "Annuale": 12,
        }
        passo_pac = freq_to_mesi.get(freq_pac, 12)
        usa_pac_bool = (usa_pac == "Sì" and importo_pac > 0)

        # Matrice dei montanti
        wealth = np.zeros((n_steps + 1, n_scen))
        wealth[0, :] = importo_iniziale

        for s in range(n_steps):
            year_idx = min(int(s / 12), anni_tot_int - 1)
            w = weights_year[year_idx, :]

            contributo = 0.0
            if usa_pac_bool and s > 0 and (s % passo_pac == 0):
                contributo = importo_pac

            r_step = R[s] @ w  # rendimento di portafoglio
            wealth[s + 1, :] = (wealth[s, :] + contributo) * (1.0 + r_step)

        # Asse dei tempi in anni
        t_years = np.linspace(0, anni_tot_int, n_steps + 1)

        # --------------------------------------------------------------
        # 5. Percentili 10 / 50 / 90
        # --------------------------------------------------------------
        percs = np.percentile(wealth, [10, 50, 90], axis=1)
        pess = percs[0, :]
        med  = percs[1, :]
        ott  = percs[2, :]

        # --------------------------------------------------------------
        # 6. Grafico a ventaglio
        # --------------------------------------------------------------
        fig, ax = plt.subplots(figsize=(8, 5))

        max_tracce_grigie = 300
        for j in range(min(n_scen, max_tracce_grigie)):
            ax.plot(t_years, wealth[:, j], color="lightgray", linewidth=0.7, alpha=0.4)

        ax.plot(t_years, ott, color="green", linewidth=2.0, label="Scenario ottimistico (90° p.)")
        ax.plot(t_years, med, color="blue", linewidth=2.0, label="Scenario atteso (50° p.)")
        ax.plot(t_years, pess, color="red", linewidth=2.0, label="Scenario pessimistico (10° p.)")

        ax.set_xlabel("Anni")
        ax.set_ylabel("Montante")
        ax.set_title("Simulazioni Monte Carlo del montante dell'investimento")
        ax.legend(loc="upper left", fontsize=8)

        st.pyplot(fig)

        # --------------------------------------------------------------
        # 7. Tabella riepilogativa anno per anno
        # --------------------------------------------------------------
        righe = []
        for anno in range(anni_tot_int + 1):
            idx = min(anno * 12, n_steps)
            righe.append({
                "Anno": anno,
                "Montante Ottimistico (90° p.)": ott[idx],
                "Montante Atteso (50° p.)": med[idx],
                "Montante Pessimistico (10° p.)": pess[idx],
            })

        df_tab = pd.DataFrame(righe)

        st.markdown("### Evoluzione del montante – scenari percentili")
        st.dataframe(
            df_tab.style.format({
                "Montante Ottimistico (90° p.)": "€{:,.0f}".format,
                "Montante Atteso (50° p.)":      "€{:,.0f}".format,
                "Montante Pessimistico (10° p.)": "€{:,.0f}".format,
            }),
            use_container_width=True
        )

    except Exception as e:
        # Se qualcosa va storto, lo vediamo chiaramente nello Step 14
        st.error("Si è verificato un errore durante la simulazione Monte Carlo:")
        st.exception(e)

    mostra_pulsanti_navigazione()
