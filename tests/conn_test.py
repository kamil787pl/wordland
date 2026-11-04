"""Połączenia: generowanie łamigłówki, zasady, wygrana/przegrana, codzienna, udostępnianie."""
import json,pathlib
from playwright.sync_api import sync_playwright
URL='file://'+str(pathlib.Path(__file__).resolve().parent.parent/'index.html')
res={};errs=[]
with sync_playwright() as pw:
    br=pw.chromium.launch();pg=br.new_page(viewport={'width':420,'height':900});pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(500);pg.evaluate("sessionStorage.clear();localStorage.clear()");pg.reload();pg.wait_for_timeout(500)
    res['karta na stronie glownej']='Połączenia' in pg.inner_text('#v-home')
    pg.evaluate("show('conn')");pg.wait_for_timeout(300)
    res['16 kafelkow']=pg.locator('.cn-t').count()==16
    res['unikalne slowa']=pg.evaluate("new Set(CN.tiles.map(t=>t.w.toLowerCase())).size")==16
    res['4 kategorie po 4']=pg.evaluate("CN.groups.length==4&&CN.groups.every(g=>g.w.length==4)")
    res['kolory 4 rozne']=pg.evaluate("new Set(CN.groups.map(g=>g.c)).size")==4
    # codzienna jest powtarzalna
    a=pg.evaluate("CN.tiles.map(t=>t.w).join()");pg.evaluate("CN=null;renderConn()");b=pg.evaluate("CN.tiles.map(t=>t.w).join()")
    res['codzienna powtarzalna']=a==b
    # zły ruch: 4 kafelki z różnych grup
    pg.evaluate("CN.sel=[];[0,1,2,3].forEach(k=>{});")
    pick="(()=>{const used={};const idx=[];CN.tiles.forEach((t,i)=>{if(!used[t.g]&&idx.length<4){used[t.g]=1;idx.push(i)}});CN.sel=idx;renderConn()})()"
    pg.evaluate(pick);res['zatwierdz aktywny przy 4']=not pg.is_disabled('text=Zatwierdź')
    pg.click('text=Zatwierdź');pg.wait_for_timeout(200)
    res['blad liczy sie']=pg.evaluate("CN.miss")==1;res['komunikat']=pg.inner_text('.cn-msg')
    # dobry ruch
    pg.evaluate("(()=>{const g=CN.tiles[0].g;CN.sel=CN.tiles.map((t,i)=>t.g===g?i:-1).filter(i=>i>=0);renderConn()})()");pg.click('text=Zatwierdź');pg.wait_for_timeout(200)
    res['grupa rozwiazana']=pg.evaluate("CN.solved.length")==1 and pg.locator('.cn-row').count()==1 and pg.locator('.cn-t').count()==12
    # wygrana: rozwiąż resztę
    for _ in range(3):
        pg.evaluate("(()=>{const g=CN.tiles[0].g;CN.sel=CN.tiles.map((t,i)=>t.g===g?i:-1).filter(i=>i>=0);renderConn()})()");pg.click('text=Zatwierdź');pg.wait_for_timeout(120)
    res['wygrana']=pg.evaluate("[CN.over,CN.won]")==[1,1]
    res['statystyki zapisane']=pg.evaluate("SV.cn.p==1&&SV.cn.w==1&&SV.cn.s==1")
    res['share ma kwadraciki']='🟨' in pg.evaluate("cnShareText()") or '🟩' in pg.evaluate("cnShareText()")
    # po odświeżeniu codzienna jest ukończona
    pg.reload();pg.wait_for_timeout(400);pg.evaluate("show('conn')");pg.wait_for_timeout(200)
    res['codzienna zapamietana']=pg.evaluate("[CN.over,CN.won]")==[1,1] and pg.locator('.cn-row').count()==4
    # losowa: przegrana po 4 błędach ujawnia grupy
    pg.evaluate("cnNew()");pg.wait_for_timeout(200)
    for _ in range(4):
        pg.evaluate(pick);pg.click('text=Zatwierdź');pg.wait_for_timeout(100)
    res['przegrana ujawnia grupy']=pg.evaluate("[CN.over,CN.won,CN.solved.length]")==[1,0,4]
    res['losowa nie zmienia serii dziennej']=pg.evaluate("SV.cn.p")==1
    pg.set_viewport_size({'width':360,'height':740});pg.evaluate("cnNew()");pg.wait_for_timeout(300)
    res['mobile: brak poziomego przewijania']=pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth")
    # poziomy
    pg.evaluate("cnLvl('A2')");res['poziom A2']=pg.evaluate("CN.groups.length")==4
    res['errors']=errs
print(json.dumps(res,ensure_ascii=False,indent=1))
bad=[k for k,v in res.items() if v is False]
print('FAIL' if bad or errs else 'OK',bad)
