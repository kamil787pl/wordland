"""Telefon: układ pionowy i poziomy, przyciski dotykowe (wymusza ekran dotykowy flagą Chromium)."""
import json,pathlib
from playwright.sync_api import sync_playwright
URL='file://'+str(pathlib.Path(__file__).resolve().parent.parent/'index.html')
ARGS=['--blink-settings=primaryPointerType=4,availablePointerTypes=4,primaryHoverType=1,availableHoverTypes=1']
res={};errs=[]
with sync_playwright() as pw:
    br=pw.chromium.launch(args=ARGS)
    for name,vp in (('pion',{'width':390,'height':844}),('poziom',{'width':844,'height':390})):
        ctx=br.new_context(viewport=vp,is_mobile=True,has_touch=True);pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto(URL);pg.wait_for_timeout(500);pg.evaluate("show('game')");pg.wait_for_timeout(300);pg.evaluate("start(0)");pg.wait_for_timeout(400)
        r={}
        r['dotyk']=pg.evaluate("matchMedia('(pointer:coarse)').matches")
        r['podpowiedzi klawiszy ukryte']=pg.is_hidden('#keys')
        r['pelny ekran tylko w poziomie']=pg.evaluate("document.getElementById('wrap').classList.contains('px')")==(name=='poziom')
        r['skok >=48px']=min(pg.locator('#bj').bounding_box()['width'],pg.locator('#bj').bounding_box()['height'])>=48
        c=pg.locator('#c').bounding_box();r['plansza w ekranie']=c['x']>=0 and c['x']+c['width']<=vp['width']+1 and c['y']+c['height']<=vp['height']+1
        r['plansza px']=[round(c['width']),round(c['height'])]
        pg.evaluate("ask(3,3)");pg.wait_for_timeout(200)
        r['przyciski ukryte w pytaniu (poziom)']=pg.is_hidden('#bj') if name=='poziom' else None
        pg.evaluate("show('home')");pg.wait_for_timeout(200)
        r['po wyjsciu z gry brak pelnego ekranu']=not pg.evaluate("document.getElementById('wrap').classList.contains('px')")
        res[name]=r;ctx.close()
print(json.dumps(res,ensure_ascii=False,indent=1));print('errors',errs)
bad=[(n,k) for n,r in res.items() for k,v in r.items() if v is False]
print('FAIL' if bad or errs else 'OK',bad)
