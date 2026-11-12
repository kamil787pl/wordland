"""Zrzuty do zakładki Poradnik (gry, pokój, strona główna) -> tests/out/help-*.png, potem make_help_assets.py."""
import pathlib
from playwright.sync_api import sync_playwright
URL='file://'+str(pathlib.Path(__file__).resolve().parent.parent/'index.html');O=str(pathlib.Path(__file__).resolve().parent/'out')+'/'
with sync_playwright() as pw:
    br=pw.chromium.launch();pg=br.new_page(viewport={'width':1000,'height':900},device_scale_factor=1.5);errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(3500)
    pg.evaluate("localStorage.clear()");pg.reload();pg.wait_for_timeout(3500)
    hide="document.getElementById('pt').style.visibility='hidden'"
    pg.evaluate("SV.cn={p:3,w:3,s:2,b:2,last:'',bt:0,br:{},pts:1250};SV.elf={p:2,perf:1,pts:620,r3:{A1:95000}};SV.climb={p:3,perf:1,pts:840,st:{A1:3,A2:2}};SV.heist={p:2,perf:1,fast:1,st:3,pts:380};SV.deck={m:{},g:6,w:3,pts:410};SV.ok=120;SV.s=[3,2,1,0,0,0,0,0,0,0,0,0];show('home')");pg.wait_for_timeout(600)
    pg.evaluate(hide);pg.locator('#v-home .hero').screenshot(path=O+'help-home-hero.png')
    pg.locator('#v-home .cards').screenshot(path=O+'help-home-gry.png')
    pg.evaluate("show('conn');cnMode('random')");pg.wait_for_timeout(300);pg.click('.cn-start .pri');pg.wait_for_timeout(200)
    pg.evaluate("CN.sel=CN.tiles.map((t,i)=>t.g===CN.tiles[0].g?i:-1).filter(i=>i>=0);cnSubmit()");pg.wait_for_timeout(700)
    pg.evaluate("CN.t0=Date.now()-41000;document.getElementById('cn-time').textContent=cnFmt(41000)");pg.locator('#v-conn .gstage').screenshot(path=O+'help-wl.png')
    pg.evaluate("show('elf');elLvl('A2')");pg.click('.el-start .pri');pg.wait_for_timeout(200)
    for _ in range(2):
        i=pg.evaluate("EL.shelf.findIndex(s=>!s.used&&EL.list.some(e=>e.k===s.k&&e.got<e.need))");pg.locator('button.el-it').nth(i).click();pg.wait_for_timeout(700)
    pg.locator('#v-elf .gstage').screenshot(path=O+'help-elf.png')
    pg.evaluate("show('climb');clLvl('A2');clStart()");pg.wait_for_timeout(200)
    for _ in range(5):
        pg.evaluate("CL.between&&clNext();clTap(CL.cur.ok)");pg.wait_for_timeout(800)
    pg.evaluate("CL.between&&clNext()");pg.wait_for_timeout(600);pg.locator('#v-climb .gstage').screenshot(path=O+'help-climb.png')
    pg.evaluate("show('heist');hsNewR(0);hsStart();hsOpen(1);hsPick(HSI[0].a);hsBack();hsOpen(3);hsPick(HSI[2].a);hsBack()");pg.wait_for_timeout(400);pg.locator('#v-heist .gstage').screenshot(path=O+'help-heist.png')
    pg.evaluate("dkNew('A2');DK.first=0;show('deck')");pg.wait_for_timeout(300);pg.click('.dk-start .pri,.dk-start .dk-go');pg.wait_for_timeout(300)
    for k in range(2):
        pg.evaluate("DK.hand[0]=DKCARDS.find(c=>c.cost===1&&c.t==='f'&&!DK.field[0].some(x=>x&&x.c.id===c.id));dkPlay(0)");pg.wait_for_timeout(100)
        pg.evaluate("dkAns(DK.task.t.ok)");pg.wait_for_timeout(1000);pg.evaluate("dkPut(DK.field[0].findIndex(x=>!x))");pg.wait_for_timeout(300)
    pg.locator('#v-deck .gstage').screenshot(path=O+'help-deck.png')
    pg.evaluate("show('prof');document.querySelector('.pgroom').open=true");pg.wait_for_timeout(500);pg.locator('#v-prof .room').screenshot(path=O+'help-pokoj.png')
    pg.evaluate("show('game');openGame()");pg.wait_for_timeout(800);pg.locator('#v-game').screenshot(path=O+'help-wc.png')
    print('OK',errs)
