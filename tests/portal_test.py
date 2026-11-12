"""Portal: strona glowna (siatka kart, Kontynuuj), nawigacja w jednym wierszu, profil z zakladkami, ekrany startowe gier."""
import pathlib
from playwright.sync_api import sync_playwright
URL='file://'+str(pathlib.Path(__file__).resolve().parent.parent/'index.html')
res={};errs=[]
with sync_playwright() as pw:
    br=pw.chromium.launch();pg=br.new_page(viewport={'width':1280,'height':900});pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(400);pg.evaluate("localStorage.clear()");pg.reload();pg.wait_for_timeout(400)
    res['home: 5 kart gier + 1 karta Wkrotce w siatce']=pg.locator('#v-home .cards .gc.feat').count()==5 and pg.locator('#v-home .cards .gc.soonc').count()==1
    res['home: karty maja obrazek 5:3 i nie sa na pelna szerokosc']=pg.evaluate("(()=>{const c=document.querySelector('#v-home .cards .gc.feat'),i=c.querySelector('.gimg'),r=i.getBoundingClientRect();return Math.abs(r.width/r.height-5/3)<.05&&c.getBoundingClientRect().width<500})()")
    res['home: bez ostatniej gry brak kafla Kontynuuj']=pg.locator('#v-home .gcont').count()==0
    pg.evaluate("show('elf')");pg.evaluate("show('home')");pg.wait_for_timeout(200)
    res['home: po wejsciu do gry jest Kontynuuj z ta gra']=pg.locator('#v-home .gcont h4').inner_text()=='WordElf'
    res['nawigacja: w jednym wierszu (Zaloguj nie spada nizej)']=pg.evaluate("(()=>{const a=document.querySelector('#pt .brand').getBoundingClientRect().top,b=document.querySelector('#nb-user').getBoundingClientRect().top;return Math.abs(a-b)<30})()")
    res['nawigacja: etykieta tylko przy aktywnej grze, reszta ma podpowiedz']=pg.evaluate("(()=>{show('climb');const on=document.querySelector('#nb-climb .t').offsetWidth>0,off=document.querySelector('#nb-elf .t').offsetWidth===0&&!!document.querySelector('#nb-elf').title;return on&&off})()")
    for v,sel in [('conn','.cn-start'),('elf','.el-start'),('climb','.cl-ov'),('heist','.cn-start')]:
        pg.evaluate("v=>{show(v)}",v);pg.wait_for_timeout(250)
        res['start '+v+': przycisk Start >=50px, wyjscie bez obramowania']=pg.evaluate("s=>{const o=document.querySelector(s),b=o.querySelector('button:not(.xit):not(.g)'),x=o.querySelector('button.xit');return !!b&&b.getBoundingClientRect().height>=48&&!!x&&getComputedStyle(x).borderTopWidth==='0px'}",sel)
    pg.evaluate("openGame()");pg.wait_for_timeout(300)
    res['start WordCraft: ciemna karta z Start i Wyjscie']=pg.locator('#ov .card.wc-intro button.pri').count()==1 and pg.locator('#ov .card.wc-intro button.xit').count()==1
    pg.evaluate("show('prof')");pg.wait_for_timeout(300)
    res['profil: zakladki Przeglad + 5 gier']=pg.locator('#v-prof .ptabs button').count()==6
    res['profil: domyslnie widoczny tylko Przeglad']=pg.evaluate("[...document.querySelectorAll('#v-prof .ptab')].filter(e=>!e.hidden).map(e=>e.dataset.t).join()")=='all'
    for k in ['wc','wl','el','cl','hs']:
        pg.evaluate("k=>profTab(k)",k)
        res['profil '+k+': panel gry + ranga w jednej zakladce']=pg.evaluate("k=>{const e=document.querySelector('#v-prof .ptab[data-t=\"'+k+'\"]');return !e.hidden&&!!e.querySelector('.gpn')&&!!e.querySelector('.rkp')&&document.querySelectorAll('#v-prof .ptab:not([hidden])').length===1}",k)
    res['profil: ranking punktow (wbHtml) w Przegladzie']=pg.evaluate("!!document.querySelector('#v-prof .ptab[data-t=all] .bbw')")
    pg.set_viewport_size({'width':390,'height':800});pg.evaluate("show('home')");pg.wait_for_timeout(300)
    res['telefon: home bez przewijania poziomego, karty w 1 kolumnie']=pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1&&document.querySelector('#v-home .cards .gc.feat').getBoundingClientRect().width>300")
    pg.evaluate("show('prof')");pg.wait_for_timeout(200)
    res['telefon: profil bez przewijania poziomego']=pg.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
    print({k:v for k,v in res.items() if v is not True});print('OK' if not errs else 'BLEDY',errs)
