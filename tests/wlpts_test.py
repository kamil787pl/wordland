from playwright.sync_api import sync_playwright
import json
URL='file:///'+__import__('pathlib').Path(__file__).resolve().parent.parent.joinpath('index.html').as_posix().lstrip('/')
res={};errs=[]
with sync_playwright() as pw:
    br=pw.chromium.launch();pg=br.new_page(viewport={'width':420,'height':900});pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(500);pg.evaluate("sessionStorage.clear();localStorage.clear()");pg.reload();pg.wait_for_timeout(500)
    pg.evaluate("show('conn');cnMode('random')");pg.wait_for_timeout(200)
    res['przed startem: max 300']=pg.inner_text('#cn-pts')=='300'
    pg.click('.cn-start .pri');pg.evaluate("CN.t0=Date.now()-120000");pg.wait_for_timeout(400)
    res['w trakcie maleje (po 2:00 ok 180)']=170<=int(pg.inner_text('#cn-pts'))<=181
    SOLVE="for(let g=0;g<4;g++){CN.sel=CN.tiles.map((t,i)=>t.g===g?i:-1).filter(i=>i>=0);cnSubmit()}CN.rev=0;renderConn()"
    pg.evaluate(SOLVE);pg.wait_for_timeout(300)
    r=pg.evaluate("[CN.pts,CN.gain,SV.cn.pts,CN.won]");res['gra 1 (ok 2:00): pkt, zysk, suma']=r;res['gra 1 ok']=170<=r[0]<=181 and r[1]==r[0] and r[2]==r[0]
    res['karta']='do rankingu dziś' in pg.inner_text('#v-conn')
    # druga gra szybsza -> zysk tylko roznica
    pg.evaluate("cnNew()");pg.click('.cn-start .pri');pg.evaluate("CN.t0=Date.now()-30000");pg.evaluate(SOLVE);pg.wait_for_timeout(300)
    r2=pg.evaluate("[CN.pts,CN.gain,SV.cn.pts]");res['gra 2 (ok 0:30)']=r2;res['gra 2 ok']=r2[0]>=265 and r2[1]==r2[0]-r[0] and r2[2]==r2[0]
    # trzecia wolniejsza -> zero zysku
    pg.evaluate("cnNew()");pg.click('.cn-start .pri');pg.evaluate("CN.t0=Date.now()-200000");pg.evaluate(SOLVE);pg.wait_for_timeout(300)
    r3=pg.evaluate("[CN.pts,CN.gain,SV.cn.pts]");res['gra 3 (wolniej): zysk 0']=r3;res['gra 3 ok']=r3[1]==0 and r3[2]==r2[0]
    res['karta: lepszy wynik dzis']='lepszy wynik' in pg.inner_text('#v-conn')
    # porazka: 0 pkt
    pg.evaluate("cnNew()");pg.click('.cn-start .pri')
    pg.evaluate("for(let k=0;k<4&&!CN.over;k++){const a=CN.tiles.map((t,i)=>[t.g,i]),g0=a.filter(x=>x[0]===CN.tiles[0].g).slice(0,2),g1=a.filter(x=>x[0]!==CN.tiles[0].g).slice(0,2);CN.sel=[...g0,...g1].map(x=>x[1]);cnSubmit()}CN.rev=0;renderConn()")
    res['porazka: 0 pkt']=pg.evaluate("[CN.over,CN.won,CN.pts]")==[1,0,0]
    # wyzwanie nie daje punktow
    pg.evaluate("CN=cnFromObj({g:CN.groups.map(g=>[g.n,g.e,g.w,g.pl]),t:0,f:''});CN.mode='chal';CNmode='chal';renderConn()");pg.click('.cn-start .pri');pg.evaluate(SOLVE);pg.wait_for_timeout(200)
    res['wyzwanie: brak punktow']=pg.evaluate("CN.pts")is None
    pg.evaluate("show('prof')");res['profil']='Ranga WordLinks' in pg.inner_text('#v-prof')
    res['errors']=errs;br.close()
bad=[k for k,v in res.items() if v is False]
print(json.dumps(res,ensure_ascii=False,indent=1));print('OK',bad)
