from fastapi import Query, HTTPException, APIRouter
from fastapi.responses import StreamingResponse, Response
import io
import requests
from datetime import datetime
from ..database import df_display, apply_filters

router = APIRouter()

@router.get("/data")
async def get_data(
    model_numbers: str = Query("0,1,2,3,4"), 
    complex_plddt: float = Query(0.0), 
    iptm_mean: float = Query(0.0), 
    pdockq: float = Query(0.0)
):
    model_numbers_list = [int(x) for x in model_numbers.split(',')]
    filters = {'Complex pLDDT': complex_plddt, 'iPTM Mean': iptm_mean, 'pDockQ': pdockq}
    df_filtered = apply_filters(df_display, model_numbers_list, filters)
    return {
        "total_count": len(df_filtered), 
        "data": df_filtered.drop(columns=['PDB URL'], errors='ignore').to_dict('records')
    }

@router.get("/model/{index}")
async def get_model(index: int):
    if index >= len(df_display): 
        raise HTTPException(status_code=404, detail="Model not found")
    selected_row = df_display.iloc[index]
    return {
        "data": selected_row.to_dict(),
        "display_name": f"{selected_row['TCR ID']}_{int(selected_row['Model Number'])}"
    }

@router.get("/pdb/{index}")
async def get_pdb(index: int):
    if index >= len(df_display): 
        raise HTTPException(status_code=404, detail="Model not found")
    selected_row = df_display.iloc[index]
    pdb_url = selected_row['PDB URL']
    response = requests.get(str(pdb_url).strip(), timeout=10)
    response.raise_for_status()
    filename = f"{selected_row['TCR ID']}_{int(selected_row['Model Number'])}.pdb"
    return StreamingResponse(
        io.BytesIO(response.content), 
        media_type="chemical/x-pdb",
        headers={{"Content-Disposition": f"attachment; filename={filename}"}}
    )

@router.get("/export")
async def export_data(
    model_numbers: str = Query("0,1,2,3,4"), 
    complex_plddt: float = Query(0.0), 
    iptm_mean: float = Query(0.0), 
    pdockq: float = Query(0.0)
):
    model_numbers_list = [int(x) for x in model_numbers.split(',')]
    filters = {'Complex pLDDT': complex_plddt, 'iPTM Mean': iptm_mean, 'pDockQ': pdockq}
    df_filtered = apply_filters(df_display, model_numbers_list, filters)
    output = io.StringIO()
    df_filtered.to_csv(output, index=False)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()), 
        media_type="text/csv",
        headers={{"Content-Disposition": f"attachment; filename=stcrdb_{datetime.now().strftime('%Y%m%d')}.csv"}}
    )

@router.get("/molstar/{index}")
async def molstar_proxy(index: str):
    idx = int(index)
    selected_row = df_display.iloc[idx]
    pdb_url = str(selected_row['PDB URL']).strip()
    
    response = requests.get(pdb_url, timeout=30)
    response.raise_for_status()
    pdb_full = response.text.rstrip() + '\nEND'
    
    return Response(
        content=pdb_full.encode('utf-8'),
        media_type="chemical/x-pdb",
        headers={"Access-Control-Allow-Origin": "*"}
    )
