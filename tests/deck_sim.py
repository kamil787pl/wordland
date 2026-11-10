"""Symulacja balansu WordDeck: gracz-bot (skutecznosc odpowiedzi pP) kontra bot gry; wypisuje procenty zwyciestw.
Uzycie: python3 tests/deck_sim.py [liczba_pojedynkow_na_ustawienie]"""
import sys
from playwright.sync_api import sync_playwright
N=int(sys.argv[1]) if len(sys.argv)>1 else 300
JS="""([lvl,pP,n])=>{
  window.setTimeout=f=>{f();return 0};window.renderDeck=()=>{};window.beep=()=>{};window.save=()=>{};
  const oT=dkTurnP;
  function sim(){
    if(DK.over)return;
    for(let g=0;g<12;g++){
      const pl=dkPlan(0);if(!pl)break;
      dkPlay(DK.hand.indexOf(pl.c));if(!DK.task)break;
      const T=DK.task.t,w=()=>T.opts.map((_,j)=>j).find(j=>j!==T.ok&&!T.dis[j]);
      if(Math.random()<pP)dkAns(T.ok);else{dkAns(w());if(Math.random()<.5)dkAns(T.ok);else dkAns(w())}
      if(DK.place)dkPut(pl.s);
      if(DK.over)return
    }
    dkEnd()
  }
  window.dkTurnP=function(){oT();sim()};
  const r={w:0,l:0,d:0,fw:0,fn:0,sw:0,sn:0,hp:0,hb:0};
  for(let i=0;i<n;i++){
    dkNew(lvl);DK.first=i%2;dkStart();
    const x=DK.res;r[x]++;r.hp+=DK.hero[0];r.hb+=DK.hero[1];
    if(DK.first===0){r.fn++;if(x==='w')r.fw++}else{r.sn++;if(x==='w')r.sw++}
  }
  return r
}"""
BAL=sys.argv[2] if len(sys.argv)>2 else ''
with sync_playwright() as pw:
    b=pw.chromium.launch()
    print('poziom  pP   wygr%  rem%  przegr%  | wygr% gdy zaczyna gracz / rywal | srednie serca gracz:rywal')
    for lvl,pb in(('A1',.7),('A2',.8),('B1',.9)):
        for pP in (.6,.8,.95,pb):
            p=b.new_page();p.goto('file:///home/claude/wordland/index.html');p.wait_for_timeout(600)
            if BAL:p.evaluate("Object.assign(DKBAL,%s)"%BAL)
            r=p.evaluate(JS,[lvl,pP,N]);p.close()
            pc=lambda a,t:round(100*a/max(t,1))
            print(f"{lvl}   {pP:.2f}  {pc(r['w'],N):4}  {pc(r['d'],N):4}  {pc(r['l'],N):5}   | {pc(r['fw'],r['fn']):4} / {pc(r['sw'],r['sn']):4}   | {r['hp']/N:.1f}:{r['hb']/N:.1f}"+('   <- rowne umiejetnosci (test uczciwosci)' if pP==pb else ''))
