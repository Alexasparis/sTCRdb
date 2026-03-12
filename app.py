import streamlit as st
import pandas as pd
import os
from streamlit_molstar import st_molstar
from datetime import datetime

st.set_page_config(page_title="sTCRdb", layout="wide")

st.title("🧬 sTCRdb - Synthetic TCR Database")

@st.cache_data
def load_data():
    df = pd.read_csv('metadata.csv')
    df['display_id'] = df['pdb_id'].astype(str) + '_' + df['model_number'].astype(str)
    df['pdb_path'] = df['pdb_id'] + '_' + df['model_number'].astype(str) + '.pdb'
    
    df['avgipde'] = (df['avgipde_a'] + df['avgipde_b']) / 2
    df['avgipae'] = (df['avgipae_a'] + df['avgipae_b']) / 2
    df['pdockq2'] = (df['pdockq2_a'] + df['pdockq2_b']) / 2
    
    rename_map = {
        'pdb_id': 'TCR ID',
        'model_number': 'Model Number',
        'plddt': 'Complex pLDDT',
        'cdr1a_plddt': 'CDR1α pLDDT',
        'cdr1b_plddt': 'CDR1β pLDDT',
        'cdr2a_plddt': 'CDR2α pLDDT',
        'cdr2b_plddt': 'CDR2β pLDDT',
        'cdr3a_plddt': 'CDR3α pLDDT',
        'cdr3b_plddt': 'CDR3β pLDDT',
        'iptm_mean': 'iPTM Mean',
        'iptm_tcrpmhc': 'iPTM TCR-pMHC',
        'pdockq': 'pDockQ',
        'avgipae': 'iPAE',
        'avgipde': 'iPDE',
        'pdockq2': 'pDockQ2',
        'ipsae': 'ipSAE',
        'lis': 'LIS',
        'ranking_score': 'Ranking Score AF3'
    }
    
    df_clean = df[list(rename_map.keys())].rename(columns=rename_map)
    return df_clean, df[['display_id', 'pdb_path']]

df_display, df_meta = load_data()

# SIDEBAR: FILTROS
st.sidebar.header("🔍 Filters")

# 1. Selector para Model Number (0-4)
selected_models = st.sidebar.multiselect(
    "Select Model Numbers", 
    options=[0, 1, 2, 3, 4], 
    default=[0, 1, 2, 3, 4]
)

# 2. Filtros para el resto de métricas (excluyendo Model Number)
filters = {}
numeric_cols = [c for c in df_display.select_dtypes(include=['float64', 'int64']).columns if c != 'Model Number']

for col in numeric_cols:
    filters[col] = st.sidebar.slider(
        f"Min {col}", 
        float(df_display[col].min()), 
        float(df_display[col].max()), 
        float(df_display[col].min())
    )

# APLICAR FILTROS
df_filtered = df_display[df_display['Model Number'].isin(selected_models)].copy()
for col, min_val in filters.items():
    df_filtered = df_filtered[df_filtered[col] >= min_val]

# 
# TABLA Y VISUALIZACIÓN
st.header(f"📊 Displaying {len(df_filtered)} Models")
event = st.dataframe(df_filtered, use_container_width=True, selection_mode="single-row", on_select="rerun")

if len(event.selection["rows"]) > 0:
    idx = event.selection["rows"][0]
    selected_row = df_filtered.iloc[idx]
    
    display_name = f"{selected_row['TCR ID']}_{int(selected_row['Model Number'])}"
    pdb_path = f"pdb_files/{display_name}.pdb"
    
    st.divider()
    st.subheader(f"🎯 3D Structure: {display_name}")
    
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.write("### Model Metrics")
        st.dataframe(selected_row.T, use_container_width=True)
    with col_b:
        if os.path.exists(pdb_path):
            st_molstar(pdb_path, height=500)
        else:
            st.error(f"PDB file not found: {pdb_path}")

file_name = f"stcrdb_data_{datetime.now().strftime('%Y-%m-%d')}.csv"

st.download_button(
    label="Export Data as CSV", 
    data=df_filtered.to_csv(index=False), 
    file_name=file_name,
    mime="text/csv"
)


