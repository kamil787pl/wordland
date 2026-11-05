"""WordElf: lista, półka, pakowanie, błąd, wygrana, rekord."""
import pathlib
from playwright.sync_api import sync_playwright
URL='file://'+str(pathlib.Path(__file__).resolve().parent.parent/'index.html')
res={};errs=[]
with sync_playwright() as pw:
    br=pw.chromium.launch();pg=br.new_page(viewport={'width':420,'height':900});pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(400);pg.evaluate("localStorage.clear()");pg.reload();pg.wait_for_timeout(400)
    res['karta']='WordElf' in pg.inner_text('#v-home')
    for lvl,n in (('A1',4),('A2',3),('B1',4)):
        pg.evaluate("show('elf');elLvl('%s')"%lvl);pg.wait_for_timeout(150)
        res[lvl+' przed startem polka ukryta']=pg.locator('button.el-it').count()==0 and pg.locator('.el-start').count()==1
        pg.click('.el-start .pri');pg.wait_for_timeout(150)
        res[lvl+' lista']=pg.locator('.el-list>div').count()==n
        res[lvl+' polka>=lista']=pg.locator('button.el-it').count()>=n
        # błąd: kliknij przedmiot spoza listy
        bad=pg.evaluate("EL.shelf.findIndex(s=>!EL.list.some(e=>e.k===s.k))")
        pg.locator('button.el-it').nth(bad).click();pg.wait_for_timeout(100)
        res[lvl+' blad +5s']=pg.evaluate("EL.miss")==1 and pg.evaluate("elTotal()")>=5000
        res[lvl+' pierwszy blad nie konczy']=pg.evaluate("EL.round")==0
        for rd in range(3):
            for _ in range(80):
                i=pg.evaluate("EL.over||EL.between?-1:EL.shelf.findIndex(s=>!s.used&&EL.list.some(e=>e.k===s.k&&e.got<e.need))")
                if i<0:break
                pg.locator('button.el-it').nth(i).click(force=True);pg.wait_for_timeout(30)
            if rd<2:
                res[lvl+' przerwa po rundzie %d'%(rd+1)]=pg.evaluate("EL.between")==1 and pg.locator('.el-start .pri').count()==1
                t=pg.evaluate("elTotal()");pg.wait_for_timeout(300);res[lvl+' czas stoi w przerwie %d'%rd]=pg.evaluate("elTotal()")==t
                pg.click('.el-start .pri');pg.wait_for_timeout(100)
                res[lvl+' runda %d'%(rd+2)]=pg.evaluate("EL.round")==rd+1 and pg.locator('.el-list>div').count()==pg.evaluate("ELN['%s'][%d]"%(lvl,rd+1))
        res[lvl+' wygrana']=pg.evaluate("EL.over")==1
        pg.wait_for_timeout(3900)
        res[lvl+' ekran koncowy']='Sanie odleciały' in pg.inner_text('#v-elf')
    res['rekordy zapisane']=pg.evaluate("Object.keys(SV.elf.r3).length")==3
    pg.evaluate("show('prof')");res['profil']='WordElf' in pg.inner_text('#v-prof')
    pg.evaluate("show('elf');elNewR()");pg.click('.el-start .pri');pg.screenshot(path=str(pathlib.Path(__file__).parent/'out'/'elf.png'))
    print({k:v for k,v in res.items() if v is not True});print('OK',errs)
