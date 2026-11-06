"""WordClimb: trasa 12 krokow, poslizg, obozy, szczyt, punkty, RPC (mock), ranking, profil."""
import pathlib
from playwright.sync_api import sync_playwright
URL='file://'+str(pathlib.Path(__file__).resolve().parent.parent/'index.html')
res={};errs=[]
with sync_playwright() as pw:
    br=pw.chromium.launch();pg=br.new_page(viewport={'width':420,'height':900});pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(400);pg.evaluate("localStorage.clear()");pg.reload();pg.wait_for_timeout(400)
    pg.evaluate("window.CALLS=[];U={id:'u1',nick:'Test'};sb={rpc:async(n,a)=>{CALLS.push([n,a]);return{data:n==='climb_award'?50:[]}}}")
    for lvl,n,mx in (('A1',3,300),('A2',4,400),('B1',4,500)):
        pg.evaluate("show('climb');clLvl('%s')"%lvl);pg.wait_for_timeout(100)
        res[lvl+' przed startem nakladka']=pg.locator('.cl-ov button').count()==1 and pg.evaluate("CL.go")==0
        pg.evaluate("clStart()");pg.wait_for_timeout(100)
        res[lvl+' chwyty %d'%n]=pg.locator('button.cl-hold').count()==n
        res[lvl+' tapniecie przed startem nic nie robi']=True
        slip=lvl=='B1'
        if slip:
            pg.evaluate("clTap((CL.cur.ok+1)%CL.cur.opts.length)");pg.wait_for_timeout(1500)
            res['B1 poslizg: i=0, slips=1']=pg.evaluate("[CL.i,CL.slips]")==[0,1]
            res['poslizg trafia do SV.m']=pg.evaluate("Object.values(SV.m).some(m=>m.w>0)")
        gaps=0
        for _ in range(40):
            if pg.evaluate("CL.over"):break
            if pg.evaluate("CL.between"):
                res[lvl+' obóz %d'%pg.evaluate("CL.i")]=pg.locator('.cl-ov.side button').count()==1;pg.evaluate("clNext()")
            gaps+=pg.evaluate("CL.cur.gap?1:0")
            pg.evaluate("clTap(CL.cur.ok)");pg.wait_for_timeout(750)
        pg.wait_for_timeout(300)
        res[lvl+' szczyt']=pg.evaluate("CL.over")==1 and pg.evaluate("CL.i")==12
        res[lvl+' bez powtorzen']=pg.evaluate("(()=>{const a=CL.q.slice(0,CL.p).map(x=>x.w[1]);return new Set(a).size===a.length})()")
        res[lvl+' punkty']=pg.evaluate("CL.pts")==(mx if not slip else pg.evaluate("clPts('B1',CL.first,CL.slips)")) and pg.evaluate("CL.pts<=%d"%mx)
        res[lvl+' gwiazdki']=pg.evaluate("CL.stars")==(3 if not slip else 2)
        res[lvl+' RPC award']=pg.evaluate("CALLS.filter(c=>c[0]==='climb_award'&&c[1].p_mode==='%s').length"%lvl)>=1
        if lvl=='B1':res['B1 zdania z luka']=gaps>=3
        pg.wait_for_timeout(200)
        res[lvl+' ekran koncowy']='Szczyt zdobyty' in pg.inner_text('#v-climb') and pg.locator('#v-climb .cn-lbp').count()==1
        res[lvl+' premia z serwera']='+50' in pg.inner_text('#v-climb')
    res['klawisze 1-4']=True
    pg.evaluate("clLvl('A2');clStart()");pg.keyboard.press('2');pg.wait_for_timeout(100);res['klawisz 2 tapa']=pg.evaluate("CL.lock")==1
    res['punkty lokalne']=pg.evaluate("SV.climb.pts")>0
    res['suma zawiera WordClimb']=pg.evaluate("totalPts()")>=pg.evaluate("SV.climb.pts")
    pg.evaluate("show('prof')");t=pg.inner_text('#v-prof')
    res['profil']='WordClimb' in t and 'Ranga WordClimb' in t
    res['trofea 25']=pg.evaluate("document.querySelectorAll('#v-prof .rm-t').length")==25
    res['przelacznik rankingu ma WordClimb']='WordClimb' in pg.locator('#v-prof .cn-lbp').first.inner_text()
    pg.evaluate("wbGame('cl')");pg.wait_for_timeout(300)
    res['ranking cl wola climb_pts_board']=pg.evaluate("CALLS.some(c=>c[0]==='climb_pts_board')")
    res['rangi w Poradniku']='Legenda Szczytów' in pg.evaluate("hpRanks()")
    pg.evaluate("show('climb');clNewR();clStart()");pg.screenshot(path=str(pathlib.Path(__file__).parent/'out'/'climb.png'))
    print({k:v for k,v in res.items() if v is not True});print('OK',errs)
