"""Build a self-contained static site (except public ONNX Runtime CDN)."""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
WEB = ROOT / 'web'
MODEL = ROOT / '_out' / 'model'
for name in ('model.onnx','config.json'):
    if not (MODEL/name).is_file():
        raise SystemExit(f'Model bulunamadı: {name}')
if DIST.exists():shutil.rmtree(DIST)
DIST.mkdir()
for name in ('index.html','style.css','app.js'):
    shutil.copy2(WEB/name,DIST/name)
html=(DIST/'index.html').read_text(encoding='utf-8')
html=html.replace('content="../_out/model/"','content="./model/"')
(DIST/'index.html').write_text(html,encoding='utf-8')
(DIST/'model').mkdir()
for name in ('model.onnx','config.json'):
    shutil.copy2(MODEL/name,DIST/'model'/name)
(DIST/'.nojekyll').write_text('',encoding='utf-8')
print('Static site ready:',DIST)
print('Note: runtime JS is fetched from jsDelivr; first load requires internet.')
