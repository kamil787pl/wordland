from playwright.sync_api import sync_playwright
import json,uuid,re,sys
S=str(__import__('pathlib').Path(__file__).resolve().parent/'out')
LIB=str(__import__('pathlib').Path(__file__).resolve().parent.parent/'node_modules/@supabase/supabase-js/dist/umd/supabase.js')
__import__('pathlib').Path(S).mkdir(exist_ok=True)
W=lambda i,pl,en,s=None:{'id':i,'pl':pl,'en':en,'sentence':s,'trap':None}
cats=[{'id':1,'name':'Zwierzęta','emoji':'🐶','level':'A1','no_hint':False,'is_public':True,'owner':None,'sort':0,'words':[W(1,'pies','dog','I walk my ___.'),W(2,'kot','cat'),W(3,'ptak','bird'),W(4,'ryba','fish'),W(5,'koń','horse')]},
 {'id':2,'name':'Jedzenie','emoji':'🍎','level':'A1','no_hint':False,'is_public':True,'owner':None,'sort':1,'words':[W(11,'chleb','bread'),W(12,'mleko','milk'),W(13,'ser','cheese'),W(14,'jajko','egg')]},
 {'id':3,'name':'Dom','emoji':'🏠','level':'A1','no_hint':False,'is_public':True,'owner':None,'sort':2,'words':[W(21,'okno','window'),W(22,'drzwi','door'),W(23,'stół','table'),W(24,'łóżko','bed')]},
 {'id':4,'name':'Kolory','emoji':'🎨','level':'A1','no_hint':False,'is_public':True,'owner':None,'sort':3,'words':[W(31,'czerwony','red'),W(32,'niebieski','blue'),W(33,'zielony','green'),W(34,'żółty','yellow')]}]
users={};profiles={};nid=[100];wid=[1000];CODE='WL-TEST'
CL=[];MEM={};ASG=[];RES=[];AW=[]
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
            vis=[c for c in cats if c['is_public'] or c['owner']==u_ or any(a['category_id']==c['id'] and u_ in MEM.get(a['class_id'],[]) for a in ASG)];return jr(route,vis)
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
    if p.startswith('/rest/v1/rpc/'):
        fn=p.split('/rpc/')[1].split('?')[0];b=b or {}
        def mine(cid):return next((c for c in CL if c['id']==cid and c['teacher_id']==u_),None)
        if fn=='class_create':
            cid='c%d'%(len(CL)+1);c={'id':cid,'teacher_id':u_,'name':b['p_name'],'code':'ABC%03d'%len(CL),'archived':False};CL.append(c);MEM[cid]=[];return jr(route,[{'id':cid,'code':c['code']}])
        if fn=='class_update':
            c=mine(b['p_class']);c['name']=b['p_name'];c['archived']=b['p_archived'];return jr(route,None)
        if fn=='class_new_code':
            c=mine(b['p_class']);c['code']='NEW999';return jr(route,'NEW999')
        if fn=='class_delete':
            c=mine(b['p_class']);CL.remove(c);return jr(route,None)
        if fn=='class_remove_student':
            MEM[b['p_class']].remove(b['p_user']);return jr(route,None)
        if fn=='class_students':
            return jr(route,[{'user_id':i,'nick':profiles[i]['nickname'],'joined_at':'2026-11-05T08:00:00Z','last_day':'2026-11-05' if profiles[i]['nickname']!='leniwy' else None,'answers':40,'correct':30,'answers_7d':12 if profiles[i]['nickname']!='leniwy' else 0,'mastered':5,'stars':3,'wl_best':95000,'done':len([r for r in RES if r['user']==i])} for i in MEM.get(b['p_class'],[])])
        if fn=='class_hard_words':return jr(route,[{'pl':'ryba','en':'fish','wrong':7,'hit':3},{'pl':'kot','en':'cat','wrong':5,'hit':3},{'pl':'pies','en':'dog','wrong':4,'hit':2},{'pl':'ptak','en':'bird','wrong':3,'hit':1},{'pl':'koń','en':'horse','wrong':2,'hit':1}])
        if fn=='class_activity':return jr(route,[{'day':'2026-11-04','answers':20,'active':2},{'day':'2026-11-05','answers':50,'active':3}])
        if fn=='student_detail':return jr(route,{'cats':[{'name':'Zwierzęta','emoji':'🐶','stars':2,'hard':1}],'hard':[{'pl':'kot','en':'cat','wrong':4,'right':1}],'days':[{'day':'2026-11-05','answers':12,'correct':9}],'wl':{'bt':95000}})
        if fn=='assignment_create':
            a={'id':'a%d'%(len(ASG)+1),'class_id':b['p_class'],'kind':b['p_kind'],'title':b['p_title'],'category_id':b['p_category'],'groups':b['p_groups'],'due':b['p_due'],'targets':b.get('p_targets'),'created_at':'2026-11-05T09:00:00Z'};ASG.append(a);return jr(route,a['id'])
        if fn=='assignment_delete':
            ASG[:]=[a for a in ASG if a['id']!=b['p_id']];return jr(route,None)
        if fn=='assignment_status':
            a=next(a for a in ASG if a['id']==b['p_id'])
            return jr(route,[{'user_id':i,'nick':profiles[i]['nickname'],'done':any(r['user']==i and r['a']==a['id'] for r in RES),'won':True,'ms':70000,'miss':1,'stars':0,'done_at':'2026-11-05T10:00:00Z'} for i in MEM[a['class_id']] if not a.get('targets') or i in a['targets']])
        if fn=='join_class':
            c=next((c for c in CL if c['code']==b['p_code'].upper()),None)
            if not c:return jr(route,{'message':'code'},400)
            MEM[c['id']].append(u_);return jr(route,[{'class_id':c['id'],'name':c['name']}])
        if fn=='wl_award':AW.append(b['p_pts']);return jr(route,b['p_pts'])
        if fn=='wl_my_points':return jr(route,40)
        if fn=='wl_pts_board':return jr(route,[{'nick':'lacznik','pts':900,'rk':1,'me':False},{'nick':'ola_u','pts':340,'rk':2,'me':True}])
        if fn=='wc_board':return jr(route,[{'nick':'mistrz','pts':1200,'rk':1,'me':False},{'nick':'ola_u','pts':340,'rk':2,'me':True}])
        if fn=='leave_class':MEM[b['p_class']].remove(u_);return jr(route,None)
        if fn=='my_classes':return jr(route,[{'class_id':c['id'],'name':c['name'],'teacher':'anna'} for c in CL if u_ in MEM[c['id']]])
        if fn=='my_assignments':
            return jr(route,[{'id':a['id'],'class_name':'5b','kind':a['kind'],'title':a['title'],'category_id':a['category_id'],'groups':a['groups'],'due':a['due'],'done':any(r['user']==u_ and r['a']==a['id'] for r in RES),'won':True,'ms':80000} for a in ASG if u_ in MEM[a['class_id']] and (not a.get('targets') or u_ in a['targets'])])
        if fn=='submit_assignment':RES.append({'user':u_,'a':b['p_id'],'ms':b['p_ms'],'miss':b['p_miss'],'won':b['p_won']});return jr(route,None)
    if p.startswith('/rest/v1/classes'):return jr(route,[c for c in CL if c['teacher_id']==u_])
    if p.startswith('/rest/v1/assignments'):
        i=re.search(r'class_id=eq\.([^&]+)',url);return jr(route,[a for a in ASG if i and a['class_id']==i.group(1)][::-1])
    if p.startswith('/functions/v1/create-students'):
        out=[]
        for st in b['students']:
            if st['nick'] in users:out.append({'nick':st['nick'],'ok':False,'error':'taken'});continue
            u={'id':str(uuid.uuid4()),'pw':st['password'],'nick':st['nick'],'email':st['nick']+'@x'};users[st['nick']]=u;profiles[u['id']]={'role':'student','nickname':st['nick']};MEM[b['class_id']].append(u['id']);out.append({'nick':st['nick'],'ok':True})
        return jr(route,{'results':out})
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
import atexit
atexit.register(lambda:print(json.dumps(res,ensure_ascii=False,indent=1)) if 'DONE' not in res else None)
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
    pg.evaluate("show('teach')");pg.wait_for_timeout(300)
    res['panel: 4 zakladki']=pg.locator('.tp-tabs button').all_inner_texts();pg.click('.tp-tabs button:has-text("Kategorie")')
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
    # ukryj/pokaż, widok ucznia
    pg.click('button:has-text("Ukryj")');pg.wait_for_timeout(500);res['ukryta']=mine['is_public']
    pg.click('button:has-text("Pokaż uczniom")');pg.wait_for_timeout(500);res['pokazana']=mine['is_public']
    # menu gry bez przycisków admina
    pg.evaluate("openGame()");pg.wait_for_timeout(300);html=pg.inner_html('#ov');res['gra: brak admin/kod']=('Admin' not in html and 'Wczytaj kategorię' not in html)
    res['gra: kategoria nauczyciela w menu']='Sport' in html or 'Własne' in html
    # usuń (2 kliknięcia)
    pg.evaluate("show('teach')");pg.click('button.dng');pg.wait_for_timeout(200);first=pg.is_visible('text=Na pewno usunąć')
    pg.click('text=Na pewno usunąć');pg.wait_for_timeout(600);res['usuwanie']={'potwierdzenie':first,'zostalo':len([c for c in cats if c['owner']])}

    # ===== panel: klasy, uczniowie, zadania =====
    pg.evaluate("show('teach')");pg.click('.tp-tabs button:has-text("Dziś")');pg.wait_for_timeout(500)
    res['klasa: formularz gdy brak klas']=pg.is_visible('#tp-nn')
    pg.fill('#tp-nn','5b angielski');pg.click('button:has-text("Utwórz klasę")');pg.wait_for_timeout(700)
    res['klasa: utworzona']={'kod':pg.inner_text('#tp-code'),'w_bazie':[c['name'] for c in CL],'kafelki':pg.locator('.tp-t').count()}
    pg.click('.tp-tabs button:has-text("Uczniowie")');pg.wait_for_timeout(200)
    pg.click('button:has-text("Dodaj uczniów")');pg.fill('#tp-nl','ania_k\njan_n;haslo123\nZLY NICK');pg.click('button:has-text("Utwórz konta")');pg.wait_for_timeout(200)
    res['dodawanie: zly nick']=pg.inner_text('#tp-m')
    pg.fill('#tp-nl','ania_k\njan_n;haslo123\nleniwy\nania_k');pg.click('button:has-text("Utwórz konta")');pg.wait_for_timeout(800)
    t=pg.inner_text('.tp-add');res['dodawanie: wynik']={'utworzono':t.count('utworzono'),'ma_haslo_jan':'haslo123' in t,'wygenerowane_8':all(len(u['pw'])==8 for n,u in users.items() if n in('ania_k','leniwy'))}
    pg.click('button:has-text("Gotowe")');pg.wait_for_timeout(200)
    res['uczniowie: wiersze']=pg.locator('.tp-st').count()
    pg.click('.tp-st .tp-nm >> nth=0');pg.wait_for_timeout(500)
    res['szczegoly']={'kat':'Zwierzęta' in pg.inner_text('#tp-det'),'trudne':'cat' in pg.inner_text('#tp-det'),'wl':'1:35' in pg.inner_text('#tp-det')}
    pg.fill('#tp-pw','abc');pg.click('#tp-det button:has-text("Zmień hasło")');pg.wait_for_timeout(150);res['reset: krotkie']=pg.inner_text('#tp-m')
    pg.fill('#tp-pw','nowe1234');pg.click('#tp-det button:has-text("Zmień hasło")');pg.wait_for_timeout(500);res['reset: ok']={'msg':pg.inner_text('#tp-m'),'haslo':users['ania_k']['pw']}
    pg.click('#tp-det button:has-text("Usuń z klasy")');pg.wait_for_timeout(150);pot=pg.is_visible('text=Kliknij jeszcze raz');pg.click('#tp-det button.dng');pg.wait_for_timeout(700)
    res['usuniecie ucznia']={'potwierdzenie':pot,'zostalo':pg.locator('.tp-st').count()}
    pg.click('.tp-tabs button:has-text("Dziś")');pg.wait_for_timeout(300)
    ov=pg.inner_text('#t-body');res['przeglad']={'trudne':'fish' in ov,'uwaga':'leniwy' in ov.split('Wymaga uwagi')[1].split('Aktywność klasy')[0] and 'jeszcze nie zaczął' in ov,'slupki':pg.locator('.tp-bars i').count(),'kod':pg.inner_text('#tp-code')}
    pg.click('#tp-hard');pg.wait_for_timeout(900)
    hc=[c for c in cats if c['name'].startswith('Trudne')]
    res['trudne: zadanie']={'kat_prywatna':[(c['is_public'],len(c['words'])) for c in hc],'zadanie':[(a['title'],a['category_id']==hc[0]['id'],a['targets']) for a in ASG],'zakladka':pg.locator('.tp-tabs button.on').inner_text()}
    pg.click('.tp-tabs button:has-text("Uczniowie")');pg.wait_for_timeout(200)
    pg.fill('#tp-q','jan');res['szukaj']=pg.locator('.tp-st').count();pg.fill('#tp-q','')
    pg.select_option('#tp-so','last');res['sort po aktywnosci: pierwszy']=pg.locator('.tp-st .tp-nm').first.inner_text().split(' ')[0]
    pg.click('.tp-flt button:has-text("Nieaktywni")');res['filtr nieaktywni']=pg.locator('.tp-st').count();pg.click('.tp-flt button:has-text("Wszyscy")')
    pg.check('.tp-st:has-text("jan_n") input');res['pasek akcji']=pg.is_visible('.tp-bulk')
    pg.click('button:has-text("Zadaj zadanie wybranym")');pg.wait_for_timeout(200);res['formularz dla wybranych']='jan_n' in pg.inner_text('.tp-add')
    pg.fill('#ta-t','Tylko Jan');pg.click('button:has-text("Zadaj wybranym")');pg.wait_for_timeout(700)
    res['zadanie celowane']=[(a['title'],a['targets']==[next(u['id'] for n,u in users.items() if n=='jan_n')]) for a in ASG if a['title']=='Tylko Jan']
    pg.click('.tp-tabs button:has-text("Zadania")');pg.wait_for_timeout(200);res['lista zadan: podsumowanie']=pg.inner_text('.tp-a >> nth=0')[:140]
    pg.click('.tp-tabs button:has-text("Uczniowie")');pg.wait_for_timeout(200)
    pg.check('.tp-st:has-text("leniwy") input');pg.click('.tp-bulk button.dng');pg.wait_for_timeout(150);pot2=pg.is_visible('text=Kliknij jeszcze raz: usunąć');pg.click('.tp-bulk button.dng');pg.wait_for_timeout(700)
    res['usuniecie zaznaczonych']={'potwierdzenie':pot2,'zostalo':pg.locator('.tp-st').count()}
    pg.click('.tp-tabs button:has-text("Dziś")');pg.wait_for_timeout(200)
    pg.screenshot(path=S+'/panel-ov.png',full_page=True)
    # zadania
    pg.click('.tp-tabs button:has-text("Zadania")');pg.click('button:has-text("Nowe zadanie")');pg.fill('#ta-t','Zwierzaki');pg.click('button:has-text("Zadaj klasie")');pg.wait_for_timeout(700)
    res['zadanie kategoria']=[(a['kind'],a['title'],a['category_id']) for a in ASG]
    pg.click('button:has-text("Nowe zadanie")');pg.click('button:has-text("Łamigłówka WordLinks")');pg.fill('#ta-t','Puzzle');pg.click('button:has-text("Zadaj klasie")');pg.wait_for_timeout(200)
    res['wl: te same kategorie']=pg.inner_text('#tp-m')
    ncat=pg.locator('#ta-c0 option').count();res['wl: liczba kategorii w liscie']=ncat
    for i in range(4):pg.select_option('#ta-c%d'%i,index=min(i,ncat-1))
    pg.fill('#ta-d','2099-01-31');pg.click('button:has-text("Zadaj klasie")');pg.wait_for_timeout(700)
    res['zadanie wordlinks']=[(a['kind'],a['title'],len(a['groups'] or []),a['due']) for a in ASG]
    pg.click('.tp-a >> nth=0 >> button:has-text("Wyniki")');pg.wait_for_timeout(500);res['status zadania']=pg.inner_text('.tp-a >> nth=0')[:160]
    pg.screenshot(path=S+'/panel-asg.png',full_page=True)
    # uczen: dolacza, widzi i robi zadanie
    pg.evaluate("logout()");pg.wait_for_timeout(600)
    pg.evaluate("goAuth(1)");pg.fill('#au-n','ola_u');pg.fill('#au-p','haslo123');pg.fill('#au-p2','haslo123');pg.check('#au-ok');pg.click('#au-go');pg.wait_for_timeout(900)
    pg.evaluate("show('prof')");pg.fill('#my-code','zzzzzz');pg.click('button:has-text("Dołącz")');pg.wait_for_timeout(400);res['uczen: zly kod']=pg.inner_text('#my-m')
    pg.fill('#my-code','abc000');pg.click('button:has-text("Dołącz")');pg.wait_for_timeout(700)
    res['uczen: w klasie']='5b angielski' in pg.inner_text('#v-prof')
    pg.evaluate("show('home')");pg.wait_for_timeout(300);hm=pg.inner_text('#v-home .my-asg');res['uczen: zadania na home']={'tekst':hm[:140],'przyciski':pg.locator('#v-home .my-asg .gbtn').count()}
    pg.screenshot(path=S+'/panel-home.png',full_page=True)
    pg.locator('#v-home .my-asg .crow').filter(has_text='Puzzle').locator('.gbtn').click();pg.wait_for_timeout(500)
    res['uczen: tryb zadania']={'widok':pg.evaluate('view'),'tryb':pg.evaluate('CN.mode'),'etykieta':'Zadanie: Puzzle' in pg.inner_text('#v-conn')}
    pg.click('.cn-start .pri');pg.wait_for_timeout(200)
    pg.evaluate("CN.t0=Date.now()-30000;for(let g=0;g<4;g++){CN.sel=CN.tiles.map((t,i)=>t.g===g?i:-1).filter(i=>i>=0);cnSubmit()}");pg.wait_for_timeout(500)
    res['uczen: wynik wyslany']=[(r['won'],r['miss'],r['ms']>=30000) for r in RES]
    pg.evaluate("show('home')");pg.wait_for_timeout(300);res['uczen: po zadaniu']=pg.inner_text('#v-home .my-asg')[:200]
    pg.locator('#v-home .my-asg .crow').filter(has_text='Zwierzaki').locator('.gbtn').click();pg.wait_for_timeout(400);res['uczen: zadanie kategoria otwiera gre']=pg.evaluate('view')
    pg.evaluate("show('home')");pg.wait_for_timeout(500);hb=pg.inner_text('#v-home .cn-lbp');res['ranking: home']={'wiersze':pg.locator('#v-home .cn-lbp li').count(),'ja':pg.locator('#v-home .cn-lbp li.me b').inner_text(),'pkt':'1\xa0200 pkt' in hb}
    pg.click('#v-home .cn-lbp button:has-text("Ogółem")');pg.wait_for_timeout(400);res['ranking: zakladka']=pg.locator('#v-home .cn-lbp button.on').all_inner_texts()
    pg.evaluate("show('game')");pg.evaluate("touchDay(true)");pg.wait_for_timeout(100);res['punkty: efekt +10']=pg.locator('.ptsfx').count()
    pg.evaluate("show('conn');cnMode('random')");pg.wait_for_timeout(300);pg.click('.cn-start .pri');pg.evaluate("CN.t0=Date.now()-70000;for(let g=0;g<4;g++){CN.sel=CN.tiles.map((t,i)=>t.g===g?i:-1).filter(i=>i>=0);cnSubmit()}");pg.wait_for_timeout(600)
    res['wl: punkty wyslane na serwer']=AW
    res['wl: ranking w widoku gry']={'wiersze':pg.locator('#v-conn .cn-lbp li').count(),'ja':'ola_u' in pg.inner_text('#v-conn .cn-lbp'),'tytul':'Ranking punktów WordLinks' in pg.inner_text('#v-conn')}
    pg.screenshot(path=S+'/wl-rank.png',full_page=True)
    pg.evaluate("show('home')");pg.wait_for_timeout(300);pg.click('#v-home .cn-lbp button:has-text("WordLinks")');pg.wait_for_timeout(500);res['home: przelacznik gier']=pg.inner_text('#v-home .cn-lbp').count('lacznik')
    pg.evaluate("show('prof')");pg.wait_for_timeout(500);res['profil: punkty i ranga']={'ranga':'Ranga:' in pg.inner_text('#v-prof'),'ranking':pg.locator('#v-prof .cn-lbp li').count()}
    pg.screenshot(path=S+'/panel-rank.png',full_page=True)
    pg.evaluate("show('prof')");res['uczen: zadania w profilu']=pg.locator('#v-prof .my-asg .crow').count();pg.click('button:has-text("Opuść klasę")');pg.click('button:has-text("Na pewno opuścić")');pg.wait_for_timeout(500);res['uczen: opuscil']=len(MEM['c1'])
    res['DONE']=1;res['log']=log;res['errors']=errs
    pg.evaluate("show('teach')");pg.screenshot(path=S+'/teach.png',full_page=True)
    br.close()
print(json.dumps(res,ensure_ascii=False,indent=1))
