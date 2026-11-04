from playwright.sync_api import sync_playwright
import json,uuid,re,sys
S=str(__import__('pathlib').Path(__file__).resolve().parent/'out')
LIB=str(__import__('pathlib').Path(__file__).resolve().parent.parent/'node_modules/@supabase/supabase-js/dist/umd/supabase.js')
__import__('pathlib').Path(S).mkdir(exist_ok=True)
W=lambda i,pl,en,s=None:{'id':i,'pl':pl,'en':en,'sentence':s,'trap':None}
cats=[{'id':1,'name':'Zwierzęta','emoji':'🐶','level':'A1','no_hint':False,'is_public':True,'owner':None,'sort':0,'words':[W(1,'pies','dog','I walk my ___.'),W(2,'kot','cat'),W(3,'ptak','bird'),W(4,'ryba','fish'),W(5,'koń','horse')]}]
users={};profiles={};nid=[100];wid=[1000];CODE='WL-TEST'
STUDENTS={}
log=[]
CORS={'access-control-allow-origin':'*','access-control-allow-headers':'*','access-control-allow-methods':'*','access-control-expose-headers':'*'}
def jr(route,obj,st=200):route.fulfill(status=st,headers={'content-type':'application/json',**CORS},body=json.dumps(obj))
def sess(u):return {'access_token':'tok_'+u['id'],'token_type':'bearer','expires_in':3600,'expires_at':9999999999,'refresh_token':'r','user':{'id':u['id'],'aud':'authenticated','role':'authenticated','email':u['email'],'user_metadata':{'nickname':u['nick']},'app_metadata':{},'created_at':'2026-11-04T00:00:00Z'}}
def uid(req):
    m=re.match(r'Bearer tok_(.+)',req.headers.get('authorization',''));return m.group(1) if m else None
def idsin(url):
    from urllib.parse import unquote;url=unquote(url)
    m=re.search(r'id=in\.\(([^)]*)\)',url);return [int(x) for x in m.group(1).split(',')] if m else []
def eqid(url,col='id'):
    m=re.search(col+r'=eq\.(\d+)',url);return int(m.group(1)) if m else None
def handle(route):
    r=route.request;url=r.url;m=r.method;p=url.split('.supabase.co')[1]
    if m=='OPTIONS':return route.fulfill(status=204,headers=CORS)
    try:b=json.loads(r.post_data) if r.post_data else None
    except:b=None
    u_=uid(r)
    if p.startswith('/auth/v1/signup'):
        n=b['data']['nickname'];u={'id':str(uuid.uuid4()),'pw':b['password'],'nick':n,'email':b['email']};users[n]=u;profiles[u['id']]={'role':'student','nickname':n};return jr(route,sess(u))
    if p.startswith('/auth/v1/token'):
        n=b['email'].split('@')[0];u=users.get(n)
        return jr(route,sess(u)) if u and u['pw']==b['password'] else jr(route,{'error_code':'invalid_credentials','msg':'Invalid login credentials'},400)
    if p.startswith('/auth/v1/logout'):return route.fulfill(status=204,headers=CORS)
    if p.startswith('/rest/v1/rpc/claim_teacher'):
        ok=b['code']==CODE
        if ok and u_:profiles[u_]['role']='teacher'
        log.append('claim '+str(ok));return jr(route,ok)
    if p.startswith('/rest/v1/profiles'):return jr(route,[profiles[u_]] if u_ in profiles else [])
    if p.startswith('/rest/v1/categories'):
        if m=='GET':
            vis=[c for c in cats if c['is_public'] or c['owner']==u_];return jr(route,vis)
        if m=='POST':
            nid[0]+=1;c={'id':nid[0],'name':b['name'],'emoji':b['emoji'],'level':b.get('level'),'no_hint':b['no_hint'],'is_public':b['is_public'],'owner':b['owner'],'sort':100,'words':[]};cats.append(c);log.append('cat+ '+b['name']);return jr(route,{'id':c['id']},201)
        i=eqid(url);c=next((c for c in cats if c['id']==i and c['owner']==u_),None)
        if m=='PATCH' and c:c.update({k:v for k,v in b.items()});log.append('cat~ '+json.dumps(b,ensure_ascii=False));return route.fulfill(status=204,headers=CORS)
        if m=='DELETE':
            if c:cats.remove(c);log.append('cat-')
            return route.fulfill(status=204,headers=CORS)
    if p.startswith('/rest/v1/words'):
        if m=='POST':
            for x in (b if isinstance(b,list) else [b]):
                c=next((c for c in cats if c['id']==x['category_id'] and c['owner']==u_),None)
                if c:wid[0]+=1;c['words'].append({'id':wid[0],'pl':x['pl'],'en':x['en'],'sentence':x.get('sentence'),'trap':x.get('trap')})
            log.append('words+%d'%len(b));return route.fulfill(status=201,headers=CORS)
        if m=='DELETE':
            ids=idsin(url)
            for c in cats:
                if c['owner']==u_:c['words']=[w for w in c['words'] if w['id'] not in ids]
            log.append('words- %s'%ids);return route.fulfill(status=204,headers=CORS)
        if m=='PATCH':
            i=eqid(url)
            for c in cats:
                for w in c['words']:
                    if w['id']==i and c['owner']==u_:w.update(b)
            log.append('words~');return route.fulfill(status=204,headers=CORS)
    if p.startswith('/functions/v1/reset-student-password'):
        role=profiles.get(u_,{}).get('role');nk=(b or {}).get('nick');pw=(b or {}).get('password','')
        if role!='teacher':return jr(route,{'error':'forbidden'},403)
        u=users.get(nk)
        if not u:return jr(route,{'error':'not_found'},404)
        if profiles[u['id']]['role']=='teacher':return jr(route,{'error':'teacher_account'},403)
        if len(pw)<6:return jr(route,{'error':'password'},400)
        u['pw']=pw;log.append('reset '+nk);return jr(route,{'ok':True})
    return jr(route,[])
res={}
with sync_playwright() as pw:
    br=pw.chromium.launch();pg=br.new_context(viewport={'width':1000,'height':900}).new_page();errs=[]
    pg.on('pageerror',lambda e:errs.append('PAGEERROR '+str(e)));pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None)
    pg.route('**/cdn.jsdelivr.net/**',lambda r:r.fulfill(status=200,headers={'content-type':'application/javascript',**CORS},body=open(LIB,encoding='utf-8').read()))
    pg.route('**/*.supabase.co/**',handle)
    pg.goto('file://'+str(__import__('pathlib').Path(__file__).resolve().parent.parent/'index.html'));pg.wait_for_timeout(900)
    res['gosc: przycisk Nauczyciel ukryty']=pg.is_hidden('#nb-teach')
    res['gosc: home bez bloku nauczyciela']='Dla nauczyciela' not in pg.inner_text('#v-home')
    pg.evaluate("show('teach')");res['gosc: komunikat']=pg.inner_text('#v-teach')[:70]
    # rejestracja ucznia
    pg.evaluate("goAuth(1)");pg.fill('#au-n','anna_nauczycielka');pg.fill('#au-p','haslo123');pg.fill('#au-p2','haslo123');pg.check('#au-ok');pg.click('#au-go');pg.wait_for_timeout(900)
    res['uczen: przycisk ukryty']=pg.is_hidden('#nb-teach')
    pg.evaluate("show('home')");res['uczen: home bez bloku nauczyciela']='Dla nauczyciela' not in pg.inner_text('#v-home')
    pg.evaluate("show('prof')");res['uczen: profil ma link z kodem']='mam kod' in pg.inner_text('#v-prof')
    pg.evaluate("show('teach')");res['uczen: widzi pole kodu']=pg.is_visible('#tc-code')
    pg.fill('#tc-code','ZLY');pg.click('text=Aktywuj');pg.wait_for_timeout(400);res['zly kod']=pg.inner_text('#tc-m')
    pg.fill('#tc-code',CODE);pg.click('text=Aktywuj');pg.wait_for_timeout(600)
    res['po dobrym kodzie']={'rola':pg.evaluate('ROLE'),'przycisk':pg.is_visible('#nb-teach'),'formularz':pg.is_visible('#tc-w')}
    pg.evaluate("show('home')");res['nauczyciel: home ma blok']='Dla nauczyciela' in pg.inner_text('#v-home')
    pg.evaluate("show('prof')");res['nauczyciel: profil bez linku']='mam kod' not in pg.inner_text('#v-prof')
    pg.evaluate("show('teach')")
    # nowa kategoria (kreator)
    res['kreator: 4 puste wiersze']=pg.locator('#tc-rows .wr').count()
    pg.fill('#tc-n','Sport');pg.click('.emo button >> nth=10');res['ikona z listy']=pg.input_value('#tc-e')
    pg.click('#tc-seg button[data-v="A2"]');res['opis poziomu']=pg.inner_text('#tc-lvd')
    pg.click('button:has-text("Zapisz kategorię")');pg.wait_for_timeout(200);res['pusta lista']=pg.inner_text('#tc-m')
    rows=pg.locator('#tc-rows .wr')
    def fill(i,a,b,c=''):
        r=pg.locator('#tc-rows .wr').nth(i);r.locator('.p').fill(a);r.locator('.e').fill(b);r.locator('.s').fill(c)
    fill(0,'piłka','ball','I kick the ___.');fill(1,'bramka','goal')
    pg.locator('#tc-rows .wr').nth(1).locator('.s').fill('Brak luki w zdaniu')
    pg.click('button:has-text("Zapisz kategorię")');pg.wait_for_timeout(200);res['zdanie bez luki']=pg.inner_text('#tc-m')
    fill(1,'bramka','goal','The ___ is big.')
    # Enter w ostatnim wierszu dodaje nowy, wklejanie z Excela
    pg.locator('#tc-rows .wr').nth(3).locator('.s').press('Enter');res['enter dodaje wiersz']=pg.locator('#tc-rows .wr').count()
    pg.click('button:has-text("Wklej z Excela")');pg.fill('#tc-w','boisko\tpitch\tThey play on the ___.\ndrużyna;team\nzła linia\nbramka=goal');pg.click('button:has-text("Dodaj do listy")');pg.wait_for_timeout(200)
    res['po wklejeniu']={'wiersze':pg.locator('#tc-rows .wr').count(),'licznik':pg.inner_text('#tc-cnt'),'msg':pg.inner_text('#tc-m')}
    pg.screenshot(path=S+'/wiz.png',full_page=True)
    pg.click('button:has-text("Zapisz kategorię")');pg.wait_for_timeout(900)
    res['po zapisie']={'komunikat':pg.inner_text('#tc-m'),'w_bazie':[(c['name'],c['emoji'],c['level'],[w['en'] for w in c['words']]) for c in cats if c['owner']],'w_grze':pg.evaluate("CATS.filter(c=>c.own).map(c=>c.n+':'+c.w.length)")}
    # edycja: usuń wiersz, zmień zdanie
    pg.click('button:has-text("Edytuj")');pg.wait_for_timeout(300)
    res['edycja: wypelnione']={'nazwa':pg.input_value('#tc-n'),'ikona':pg.input_value('#tc-e'),'poziom_on':pg.inner_text('#tc-seg button.on'),'wiersze':pg.locator('#tc-rows .wr').count(),'pierwszy':pg.locator('#tc-rows .wr .p').first.input_value()}
    pg.click('#tc-rows .wr >> nth=3 >> button.x');res['po usunieciu wiersza']=pg.locator('#tc-rows .wr').count()
    pg.locator('#tc-rows .wr').nth(0).locator('.s').fill('I kick the red ___.')
    pg.click('button:has-text("Zapisz zmiany")');pg.wait_for_timeout(300);res['za malo po usunieciu']=pg.inner_text('#tc-m')
    pg.click('button:has-text("Dodaj słówko")');r=pg.locator('#tc-rows .wr').last;r.locator('.p').fill('sędzia');r.locator('.e').fill('referee')
    pg.click('button:has-text("Zapisz zmiany")');pg.wait_for_timeout(900)
    mine=[c for c in cats if c['owner']][0]
    res['po edycji']=[(w['en'],w['sentence']) for w in mine['words']]
    # reset hasła ucznia
    users['uczen1']={'id':'u-stu','pw':'stare12','nick':'uczen1','email':'uczen1@x'};profiles['u-stu']={'role':'student','nickname':'uczen1'}
    pg.fill('#rp-n','nieistnieje');pg.fill('#rp-p','nowe1234');pg.click('button:has-text("Zmień hasło")');pg.wait_for_timeout(400);res['reset: brak ucznia']=pg.inner_text('#rp-m')
    pg.fill('#rp-n','uczen1');pg.fill('#rp-p','abc');pg.click('button:has-text("Zmień hasło")');pg.wait_for_timeout(200);res['reset: krotkie haslo']=pg.inner_text('#rp-m')
    pg.fill('#rp-n','anna_nauczycielka');pg.fill('#rp-p','nowe1234');pg.click('button:has-text("Zmień hasło")');pg.wait_for_timeout(400);res['reset: konto nauczyciela']=pg.inner_text('#rp-m')
    pg.fill('#rp-n','uczen1');pg.fill('#rp-p','nowe1234');pg.click('button:has-text("Zmień hasło")');pg.wait_for_timeout(400);res['reset: ok']={'msg':pg.inner_text('#rp-m'),'haslo_w_atrapie':users['uczen1']['pw'],'pole_wyczyszczone':pg.input_value('#rp-p')==''}
    # ukryj/pokaż, widok ucznia
    pg.click('button:has-text("Ukryj")');pg.wait_for_timeout(500);res['ukryta']=mine['is_public']
    pg.click('button:has-text("Pokaż uczniom")');pg.wait_for_timeout(500);res['pokazana']=mine['is_public']
    # menu gry bez przycisków admina
    pg.evaluate("openGame()");pg.wait_for_timeout(300);html=pg.inner_html('#ov');res['gra: brak admin/kod']=('Admin' not in html and 'Wczytaj kategorię' not in html)
    res['gra: kategoria nauczyciela w menu']='Sport' in html or 'Własne' in html
    # usuń (2 kliknięcia)
    pg.evaluate("show('teach')");pg.click('button.dng');pg.wait_for_timeout(200);first=pg.is_visible('text=Na pewno usunąć')
    pg.click('text=Na pewno usunąć');pg.wait_for_timeout(600);res['usuwanie']={'potwierdzenie':first,'zostalo':len([c for c in cats if c['owner']])}
    res['log']=log;res['errors']=errs
    pg.evaluate("show('teach')");pg.screenshot(path=S+'/teach.png',full_page=True)
    br.close()
print(json.dumps(res,ensure_ascii=False,indent=1))
