from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.api.data import router
from app.database import df_display

app = FastAPI(title="🧬 sTCRdb - Synthetic TCR Database API")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router, prefix="/api")

@app.get("/viewer/{index}")
def viewer_html(index: str):
    """🎉 3Dmol.js Viewer - SAME EXACT CODE"""
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <script src="https://3dmol.org/build/3Dmol-min.js"></script>
    <style>
        body {{ margin:0; height:100vh; background:#1a1a1a; overflow:hidden; }}
        #viewer {{ width:100%; height:100vh; }}
    </style>
</head>
<body>
    <div id="viewer"></div>
    <script>
        let viewer = $3Dmol.createViewer("viewer");
        fetch('/api/molstar/{index}')
            .then(response => response.text())
            .then(pdb => {{
                viewer.addModel(pdb, "pdb");
                viewer.setStyle({{chain: 'A'}}, {{cartoon: {{color: 'blue'}}}});
                viewer.setStyle({{chain: 'B'}}, {{cartoon: {{color: 'cyan'}}}});
                viewer.setStyle({{chain: 'C'}}, {{licorice: {{color: 'red'}}}});
                viewer.setStyle({{chain: 'D'}}, {{cartoon: {{color: 'darkgreen'}}}});
                viewer.setStyle({{chain: 'E'}}, {{cartoon: {{color: 'orange'}}}});
                viewer.zoomTo();
                viewer.render();
                console.log('✅ TCR-pMHC 3D CARGADO!');
            }})
            .catch(e => console.error('Error:', e));
    </script>
</body>
</html>"""
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/")
async def main_page():
    # **EXACT SAME HTML + JS FROM YOUR CODE**
    with open("staticfiles/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/health")
async def health():
    return {"status": "healthy", "models": len(df_display)}
