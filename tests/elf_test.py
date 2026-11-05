"""WordElf: lista, półka, pakowanie, błąd, wygrana, rekord."""
import pathlib
from playwright.sync_api import sync_playwright
URL='file://'+str(pathlib.Path(__file__).resolve().parent.parent/'index.html')
res={};errs=[]
with sync_playwright() as pw:
    br=pw.chromium.launch();pg=br.new_page(viewport={'width':420,'height':900});pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(400);pg.evaluate("localStorage.clear()");pg.reload();pg.wait_for_timeout(400)
    res['karta']='WordElf' in pg.inner_text('#v-home')
    for lvl,n in (('A1',6),('A2',5),('B1',5)):
        pg.evaluate("show('elf');elLvl('%s')"%lvl);pg.wait_for_timeout(150)
        res[lvl+' przed startem polka ukryta']=pg.locator('button.el-it').count()==0 and pg.locator('.el-start').count()==1
        pg.click('.el-start .pri');pg.wait_for_timeout(150)
        res[lvl+' lista']=pg.locator('.el-list>div').count()==n
        res[lvl+' polka>=lista']=pg.locator('button.el-it').count()>=n
        # błąd: kliknij przedmiot spoza listy
        bad=pg.evaluate("EL.shelf.findIndex(s=>!EL.list.some(e=>e.k===s.k))")
        pg.locator('button.el-it').nth(bad).click();pg.wait_for_timeout(100)
        res[lvl+' blad +5s']=pg.evaluate("EL.miss")==1 and pg.evaluate("elTotal()")>=5000
        for _ in range(60):
            i=pg.evaluate("EL.over?-1:EL.shelf.findIndex(s=>!s.used&&EL.list.some(e=>e.k===s.k&&e.got<e.need))")
            if i<0:break
            pg.locator('button.el-it').nth(i).click(force=True);pg.wait_for_timeout(30)
        res[lvl+' wygrana']=pg.evaluate("EL.over")==1
        pg.wait_for_timeout(3900)
        res[lvl+' ekran koncowy']='Sanie odleciały' in pg.inner_text('#v-elf')
    res['rekordy zapisane']=pg.evaluate("Object.keys(SV.elf.br).length")==3
    pg.evaluate("show('prof')");res['profil']='WordElf' in pg.inner_text('#v-prof')
    pg.evaluate("show('elf');elNewR()");pg.click('.el-start .pri');pg.screenshot(path=str(pathlib.Path(__file__).parent/'out'/'elf.png'))
    print({k:v for k,v in res.items() if v is not True});print('OK',errs)
