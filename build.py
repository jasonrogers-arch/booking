#!/usr/bin/env python3
"""Rebuild the booking pages from template.html + customers.json.
Usage:  python3 build.py                      rebuild pages only
        python3 build.py EVENTS_DIR YYYY-MM-DD  also rewrite availability.js from TUBC event JSON files
Outputs: index.html (public page) and <slug>/index.html for every customer in customers.json."""
import json,glob,os,sys
ROOMS=[("r99","99 (KC Conf Room)"),("r102","102 (Conf Room)"),("r107","107"),("r109","109 (Meeting Lounge)"),("r601","601"),("r602","602"),("r612","612"),("studio","Studio")]
here=os.path.dirname(os.path.abspath(__file__))
if len(sys.argv)==3:
    ev_dir,today=sys.argv[1],sys.argv[2]
    ids={r for r,_ in ROOMS};busy={r:[] for r in ids}
    for f in glob.glob(ev_dir+"/*.json"):
        d=json.load(open(f));c=d.get("cal")
        if c not in ids:continue
        s=d.get("start");e=d.get("end") or s
        if not s or e<today:continue
        busy[c].append([s,e,d.get("t1") or "",d.get("t2") or ""])
    for r in busy:busy[r].sort()
    ALL=[]
    for f in glob.glob(ev_dir+"/*.json"):
        d=json.load(open(f));d["_id"]=os.path.basename(f)[:-5]
        if d.get("cal") in ids and (d.get("end") or d.get("start") or "")>=today:ALL.append(d)
    open(here+"/availability.js","w").write("window.AVAIL="+json.dumps({"busy":busy,"built":today},separators=(",",":"))+";\n")
    print({r:len(v) for r,v in busy.items()})
tpl=open(here+"/template.html").read()
rooms=json.dumps([{"id":r,"name":n} for r,n in ROOMS],separators=(",",":"))
tpl=tpl.replace("/*__DATA__*/null","Object.assign({rooms:"+rooms+'},window.AVAIL||{busy:{},built:""})')
i=tpl.index('<div class="wrap">');head,body=tpl[:i],tpl[i:]
def page(prefix,customer):
    pre='<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n<style>:root{color-scheme:light}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n'
    h=head.replace("<title>Book a Room</title>","<title>Book a Room</title>\n"+'<link rel="icon" type="image/png" href="'+prefix+'favicon.png">\n<link rel="apple-touch-icon" href="'+prefix+'apple-touch-icon.png">'+("\n<meta name=\"robots\" content=\"noindex\">" if customer else ""))
    b=body.replace("<script>",'<script src="'+prefix+'availability.js"></script>\n'+("<script>window.CUSTOMER="+json.dumps(customer,separators=(",",":"))+";</script>\n<script src=\"bookings.js\"></script>\n" if customer else "")+"<script>",1)
    return pre+h+"</head>\n<body>\n"+b+"\n</body>\n</html>\n"
open(here+"/index.html","w").write(page("",None))
for slug,c in json.load(open(here+"/customers.json")).items():
    os.makedirs(here+"/"+slug,exist_ok=True)
    cc=dict(c,slug=slug)
    if cc.get("logo"):cc["logo"]="../"+cc["logo"]
    open(here+"/"+slug+"/index.html","w").write(page("../",cc))
    if len(sys.argv)==3 and c.get("match"):
        names=dict(ROOMS);pats=[p.lower() for p in c["match"]];hide=set(c.get("hide",[]))
        mine=[]
        for d in ALL:
            if d["_id"] in hide:continue
            if not any(p in (d.get("title") or "").lower() for p in pats):continue
            mine.append([d["start"],d.get("end") or d["start"],d.get("t1") or "",d.get("t2") or "",names[d["cal"]].split(" ")[0]])
        mine.sort()
        open(here+"/"+slug+"/bookings.js","w").write("window.MINE="+json.dumps(mine,separators=(",",":"))+";\n")
        print(slug,"bookings:",len(mine))
cust=json.load(open(here+"/customers.json"))
amap={k.lower():k for k in cust}
open(here+"/404.html","w").write('<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Page not found</title>\n<script>(function(){var m='+json.dumps(amap)+';var p=location.pathname.replace(/^\\/+|\\/+$/g,"");var k=m[p.toLowerCase()];if(k&&k!==p)location.replace("/"+k+"/"+location.search)})();</script>\n<style>body{font:16px/1.5 system-ui,sans-serif;margin:0;padding:48px 16px;background:#f6f8fb;color:#14233a}main{max-width:480px;margin:0 auto}a{color:#1f4f9c}</style></head>\n<body><main><h1>Page not found</h1><p>Check the link you were given, or <a href="/">go to the booking page</a>.</p></main></body></html>\n')
print("built index.html and",len(json.load(open(here+"/customers.json"))),"customer page(s)")
