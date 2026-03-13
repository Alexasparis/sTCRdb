import pandas as pd
import sqlite3

def load_data():
    """Load data from SQLite"""
    conn = sqlite3.connect('stcrdb.db', check_same_thread=False)
    try:
        df = pd.read_sql("SELECT * FROM models", conn)
    finally:
        conn.close()
    
    rename_map = {
        'pdb_id': 'TCR ID', 'model_number': 'Model Number', 'plddt': 'Complex pLDDT',
        'cdr1a_plddt': 'CDR1α pLDDT', 'cdr1b_plddt': 'CDR1β pLDDT', 'cdr2a_plddt': 'CDR2α pLDDT',
        'cdr2b_plddt': 'CDR2β pLDDT', 'cdr3a_plddt': 'CDR3α pLDDT', 'cdr3b_plddt': 'CDR3β pLDDT',
        'iptm_mean': 'iPTM Mean', 'iptm_tcrpmhc': 'iPTM TCR-pMHC', 'pdockq': 'pDockQ',
        'avgipae': 'iPAE', 'avgipde': 'iPDE', 'pdockq2': 'pDockQ2', 'ipsae': 'ipSAE',
        'lis': 'LIS', 'ranking_score': 'Ranking Score AF3', 'pdb_url': 'PDB URL'
    }
    
    cols_to_use = [c for c in rename_map.keys() if c in df.columns]
    df_clean = df[cols_to_use].rename(columns=rename_map)
    return df_clean

def apply_filters(df: pd.DataFrame, model_numbers=None, filters=None):
    if model_numbers is None: model_numbers = [0, 1, 2, 3, 4]
    if filters is None: filters = {}
    
    df_filtered = df[df['Model Number'].isin(model_numbers)].copy()
    for col, min_val in filters.items():
        if col in df_filtered.columns:
            df_filtered = df_filtered[df_filtered[col] >= min_val]
    return df_filtered

# Global cache
df_display = load_data()
