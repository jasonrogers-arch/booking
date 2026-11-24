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
    open(here+"/availability.js","w").write("window.AVAIL="+json.dumps({"busy":busy,"built":today},separators=(",",":"))+";\n")
    print({r:len(v) for r,v in busy.items()})
tpl=open(here+"/template.html").read()
rooms=json.dumps([{"id":r,"name":n} for r,n in ROOMS],separators=(",",":"))
tpl=tpl.replace("/*__DATA__*/null","Object.assign({rooms:"+rooms+'},window.AVAIL||{busy:{},built:""})')
i=tpl.index('<div class="wrap">');head,body=tpl[:i],tpl[i:]
def page(prefix,customer):
    pre='<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n<style>:root{color-scheme:light}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n'
    h=head.replace("<title>Book a Room</title>","<title>Book a Room</title>\n"+'<link rel="icon" type="image/png" href="'+prefix+'favicon.png">\n<link rel="apple-touch-icon" href="'+prefix+'apple-touch-icon.png">'+("\n<meta name=\"robots\" content=\"noindex\">" if customer else ""))
    b=body.replace("<script>",'<script src="'+prefix+'availability.js"></script>\n'+("<script>window.CUSTOMER="+json.dumps(customer,separators=(",",":"))+";</script>\n" if customer else "")+"<script>",1)
    return pre+h+"</head>\n<body>\n"+b+"\n</body>\n</html>\n"
open(here+"/index.html","w").write(page("",None))
for slug,c in json.load(open(here+"/customers.json")).items():
    os.makedirs(here+"/"+slug,exist_ok=True)
    open(here+"/"+slug+"/index.html","w").write(page("../",dict(c,slug=slug)))
print("built index.html and",len(json.load(open(here+"/customers.json"))),"customer page(s)")
