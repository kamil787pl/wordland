from playwright.sync_api import sync_playwright
import json
URL='file:///'+__import__('pathlib').Path(__file__).resolve().parent.parent.joinpath('index.html').as_posix().lstrip('/')
res={};errs=[]
SOLVE="for(let g=0;g<4;g++){CN.sel=CN.tiles.map((t,i)=>t.g===g?i:-1).filter(i=>i>=0);cnSubmit()}"
with sync_playwright() as pw:
    br=pw.chromium.launch();pg=br.new_page(viewport={'width':420,'height':900});pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(500);pg.evaluate("sessionStorage.clear();localStorage.clear()");pg.reload();pg.wait_for_timeout(500)
    pg.evaluate("show('conn');cnMode('random')");pg.wait_for_timeout(200)
    res['przed startem 0']=pg.inner_text('.gs-s').count('⭐ 0')==1
    pg.click('.cn-start .pri');pg.evaluate("CN.t0=Date.now()-60000;CN.sel=CN.tiles.map((t,i)=>t.g===0?i:-1).filter(i=>i>=0);cnSubmit()");pg.wait_for_timeout(100)
    res['po grupie: 25']=pg.evaluate("CNP")==25 and '⭐ 25' in pg.inner_text('.gs-s')
    pg.evaluate("for(let g=1;g<4;g++){CN.sel=CN.tiles.map((t,i)=>t.g===g?i:-1).filter(i=>i>=0);cnSubmit()}");pg.wait_for_timeout(200)
    res['wygrana bez bledow ~1:00 -> 100+100+100']=pg.evaluate("[CN.pts,SV.cn.pts,CN.won,CN.miss]")
    res['karta wyniku']='Punkty: 300' in pg.inner_text('#v-conn')
    # nowa gra: licznik od zera
    pg.evaluate("cnNew()");pg.click('.cn-start .pri');res['nowa gra: reset']=pg.evaluate("CNP")==0
    # porazka: 4 bledy -> punkty tylko za grupy
    pg.evaluate("CN.sel=CN.tiles.map((t,i)=>t.g===0?i:-1).filter(i=>i>=0);cnSubmit()")
    pg.evaluate("for(let k=0;k<4&&!CN.over;k++){const a=CN.tiles.map((t,i)=>[t.g,i]),g0=a.filter(x=>x[0]===CN.tiles[0].g).slice(0,2),g1=a.filter(x=>x[0]!==CN.tiles[0].g).slice(0,2);CN.sel=[...g0,...g1].map(x=>x[1]);cnSubmit()}")
    res['porazka']=pg.evaluate("[CN.over,CN.won,CN.pts]")
    res['suma lokalna rosnie']=pg.evaluate("SV.cn.pts")
    pg.evaluate("show('prof')");res['profil: ranga i punkty']='Ranga WordLinks' in pg.inner_text('#v-prof') and 'punkty' in pg.inner_text('#v-prof')
    pg.evaluate("show('conn')");res['ranking: gosc proszony o logowanie']='Zaloguj się' in pg.inner_text('#v-conn')
    res['errors']=errs;br.close()
ok=[k for k,v in res.items() if v is False]
print(json.dumps(res,ensure_ascii=False,indent=1));print('OK',ok)
