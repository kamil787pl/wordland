"""tests/out/help-*.png -> assets/help/*.webp (szerokość max 900, wysokość max 1100)."""
import pathlib
from PIL import Image
T=pathlib.Path(__file__).resolve().parent;D=T.parent/'assets'/'help';D.mkdir(parents=True,exist_ok=True)
for f in sorted((T/'out').glob('help-*.png')):
    im=Image.open(f).convert('RGB');w,h=im.size;k=min(1,900/w);im=im.resize((int(w*k),int(h*k)),Image.LANCZOS)
    if im.height>1100:im=im.crop((0,0,im.width,1100))
    n=f.stem[5:];im.save(D/(n+'.webp'),quality=78);print(n,im.size,(D/(n+'.webp')).stat().st_size//1024,'kB')
