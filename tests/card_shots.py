"""Obrazki kafli gier na stronie głównej -> assets/card-<gra>.webp (800x480, 5:3, wycinek planszy gry bez ramki).
Każda nowa gra: dopisz tu zrzut jej planszy (.gstage) i użyj assets/card-<gra>.webp w GAMES[].img."""
import pathlib,io
from playwright.sync_api import sync_playwright
from PIL import Image
R=pathlib.Path(__file__).resolve().parent.parent;URL='file://'+str(R/'index.html');A=R/'assets'
def save(png,name,inset=3,top=None):
    im=Image.open(io.BytesIO(png)).convert('RGB');w,h=im.size;im=im.crop((inset,inset,w-inset,h-inset));w,h=im.size
    k=min(w/5,h/3);cw,ch=int(5*k),int(3*k);x,y=(w-cw)//2,(h-ch)//2 if top is None else top;im=im.crop((x,y,x+cw,y+ch)).resize((800,480),Image.LANCZOS)
    im.save(A/('card-'+name+'.webp'),'WEBP',quality=84,method=6);print(name,(A/('card-'+name+'.webp')).stat().st_size//1024,'kB')
HF="document.querySelectorAll('.gs-foot button,.gbar').forEach(b=>b.style.display='none')"
with sync_playwright() as pw:
    br=pw.chromium.launch();pg=br.new_page(viewport={'width':1000,'height':900},device_scale_factor=1.6);errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(2500);pg.evaluate("localStorage.clear()");pg.reload();pg.wait_for_timeout(2500)
    pg.evaluate("document.getElementById('pt').style.visibility='hidden'")
    pg.evaluate("show('game');openGame();start(0)");pg.wait_for_timeout(1200);pg.keyboard.press('t');pg.wait_for_timeout(1800)
    save(pg.locator('#cv').screenshot(),'wc',0)
    pg.evaluate("show('conn');cnMode('random')");pg.wait_for_timeout(300);pg.click('.cn-start .pri');pg.wait_for_timeout(200)
    pg.evaluate("CN.sel=CN.tiles.map((t,i)=>t.g===CN.tiles[0].g?i:-1).filter(i=>i>=0);cnSubmit()");pg.wait_for_timeout(700)
    pg.evaluate("CN.t0=Date.now()-41000;document.getElementById('cn-time').textContent=cnFmt(41000)")
    pg.evaluate(HF);save(pg.locator('#v-conn .gstage').screenshot(),'wl')
    pg.evaluate("show('elf');elLvl('A2')");pg.click('.el-start .pri');pg.wait_for_timeout(200)
    for _ in range(2):
        i=pg.evaluate("EL.shelf.findIndex(s=>!s.used&&EL.list.some(e=>e.k===s.k&&e.got<e.need))");pg.locator('button.el-it').nth(i).click();pg.wait_for_timeout(700)
    pg.evaluate(HF);save(pg.locator('#v-elf .gstage').screenshot(),'el')
    pg.evaluate("show('climb');clLvl('A2');clStart()");pg.wait_for_timeout(200)
    for _ in range(5):
        pg.evaluate("CL.between&&clNext();clTap(CL.cur.ok)");pg.wait_for_timeout(800)
    pg.evaluate("CL.between&&clNext()");pg.wait_for_timeout(600);pg.evaluate(HF);save(pg.locator('#v-climb .gstage').screenshot(),'cl')
    pg.evaluate("show('heist');hsNewR(0);hsStart();hsOpen(1);hsPick(HSI[0].a);hsBack();hsOpen(3);hsPick(HSI[2].a);hsBack();hsOpen(4);hsPick(HSI[3].a);hsBack()");pg.wait_for_timeout(400)
    pg.set_viewport_size({'width':760,'height':900});pg.wait_for_timeout(300)
    pg.evaluate(HF);save(pg.locator('#v-heist .gstage').screenshot(),'hs')
    pg.set_viewport_size({'width':1000,'height':900})
    pg.evaluate("dkNew('A2');DK.first=0;show('deck')");pg.wait_for_timeout(300);pg.click('.dk-start .pri,.dk-start .dk-go');pg.wait_for_timeout(300)
    for k in range(2):
        pg.evaluate("DK.hand[0]=DKCARDS.find(c=>c.cost===1&&c.t==='f'&&!DK.field[0].some(x=>x&&x.c.id===c.id));dkPlay(0)");pg.wait_for_timeout(100)
        pg.evaluate("dkAns(DK.task.t.ok)");pg.wait_for_timeout(1000);pg.evaluate("dkPut(DK.field[0].findIndex(x=>!x))");pg.wait_for_timeout(300)
    pg.evaluate(HF);save(pg.locator('#v-deck .gstage').screenshot(),'dk',top=0)
    print('OK',errs)
