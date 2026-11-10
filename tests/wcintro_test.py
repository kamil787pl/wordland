"""WordCraft: ekran startowy (postac, opis, Start) przed wyborem kategorii."""
import pathlib
from playwright.sync_api import sync_playwright
URL='file://'+str(pathlib.Path(__file__).resolve().parent.parent/'index.html')
res={};errs=[]
with sync_playwright() as pw:
    br=pw.chromium.launch();pg=br.new_page(viewport={'width':1000,'height':900});pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(400);pg.evaluate("localStorage.clear()");pg.reload();pg.wait_for_timeout(400)
    pg.evaluate("show('game')");pg.wait_for_timeout(300)
    res['intro: postac, opis, Start']=pg.locator('#ov .wc-cast img').count()==1 and 'Do dzieła' in pg.inner_text('#ov') and pg.locator('#ov .lv').count()==0
    pg.click('#ov .pri');pg.wait_for_timeout(200)
    res['Start otwiera wybor kategorii']=pg.locator('#ov .lv').count()>0
    pg.evaluate("show('home');show('game')");pg.wait_for_timeout(200)
    res['powrot do gry bez ponownego intro']=pg.locator('#ov .lv').count()>0 and pg.locator('#ov .wc-cast').count()==0
    print({k:v for k,v in res.items() if v is not True});print('OK' if not errs else 'BLEDY',errs)
