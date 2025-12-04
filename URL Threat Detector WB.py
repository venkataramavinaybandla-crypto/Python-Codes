from flask import Flask, request, render_template_string, send_file, url_for
import re, math, tldextract, uuid, os
from urllib.parse import urlparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime

IP_RE = re.compile(r'^\d{1,3}(\.\d{1,3}){3}$')
ENCODING_RE = re.compile(r'%[0-9a-fA-F]{2}')
DOUBLE_ENCODE_RE = re.compile(r'%25[0-9a-fA-F]{2}')
JS_RE = re.compile(r'(javascript:|<script|onerror=|alert\()')
SHORTENERS = {"bit.ly","tinyurl.com","goo.gl","is.gd","t.co","shorte.st","adf.ly","cutt.ly","rb.gy"}
TEST_DOMAINS = ["amtso","eicar","testmalware","malware-test","phishing-test"]
RARE_TLDS = {"zip","kim","country","gq","tk","ml","cricket","review"}
BAD_EXT = {".exe",".scr",".zip",".rar",".msi",".apk"}
SUSPICIOUS_PORTS = {8080,8888,2087,2096,21,22}
HOMOGLYPHS = {"а":"a","о":"o","е":"e","с":"c","р":"p","х":"x","і":"i","ԁ":"d","ԃ":"d","ԍ":"g"}

def entropy(s):
    if not s: return 0
    f={c:s.count(c) for c in set(s)}
    return -sum((f[c]/len(s))*math.log2(f[c]/len(s)) for c in f)

def mixed_script(h): return any(ord(c)>127 for c in h)
def homoglyph_attack(h): return any(c in HOMOGLYPHS for c in h)
def suspicious_params(q): return any(k in q.lower() for k in ["id=","token=","redirect","auth","session=","email="])
def bad_path(p): return any(k in p.lower() for k in ["malware","virus","payload","download"])
def format_quality(u): return "Poor" if any(b in u.lower() for b in ["//","..","\\","??","///"]) else "Normal"
def is_shortener(h): return h in SHORTENERS

def heuristic_score(url):
    try:
        p=urlparse(url); h=p.hostname or ""; path=p.path or ""; q=p.query or ""; port=p.port
    except: return 95
    s=0
    if url.startswith("http://"): s+=15
    if IP_RE.match(h): s+=25
    if any(t in h for t in TEST_DOMAINS): s+=40
    ext=tldextract.extract(h)
    if ext.suffix in RARE_TLDS: s+=14
    if len(h.split("."))>=5: s+=12
    if "@" in url: s+=20
    if "xn--" in h: s+=20
    if port in SUSPICIOUS_PORTS: s+=15
    if len(h)>60: s+=12
    if is_shortener(h): s+=20
    e=entropy(h)
    if e>4.3: s+=20
    elif e>3.7: s+=12
    if mixed_script(h): s+=20
    if homoglyph_attack(h): s+=22
    if suspicious_params(q): s+=18
    if bad_path(path): s+=25
    if ENCODING_RE.search(url): s+=10
    if DOUBLE_ENCODE_RE.search(url): s+=18
    if JS_RE.search(url): s+=16
    for b in BAD_EXT:
        if url.lower().endswith(b): s+=30
    if format_quality(url)=="Poor": s+=15
    if len(url)>180: s+=12
    elif len(url)>120: s+=7
    return min(100,s)

def phishing_probability(s): return min(100,int(s*0.93))
def verdict(s):
    if s<=20: return "Safe"
    if s<=40: return "Low Risk"
    if s<=60: return "Suspicious"
    if s<=80: return "Risky"
    return "High Danger"

app = Flask(__name__)

BASE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<title>{{ title }}</title>
<link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}">
<meta name="viewport" content="width=device-width, initial-scale=1">

<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Segoe UI,Arial;color:#e6eef8;background:#070512;overflow-x:hidden}

.bg-animation{position:fixed;top:0;left:0;width:100%;height:100%;z-index:-1;
background:linear-gradient(120deg,#050c1b,#2b0b1a,#071f33);
animation:mov 14s infinite alternate ease-in-out}
@keyframes mov{0%{filter:hue-rotate(0deg)}50%{filter:hue-rotate(70deg)}100%{filter:hue-rotate(140deg)}}

.particle{position:absolute;width:4px;height:4px;background:rgba(200,120,255,0.8);
border-radius:50%;animation:float 10s infinite linear}
@keyframes float{0%{transform:translateY(100vh);opacity:.15}
50%{opacity:.9}
100%{transform:translateY(-10vh);opacity:0}}

header{text-align:center;padding-top:26px}
.logo{max-height:88px;display:block;margin:0 auto 8px;
filter:drop-shadow(0 0 10px rgba(139,77,255,0.6))}

h1{font-size:28px;color:#cfe9ff;margin-bottom:10px;letter-spacing:1px}

nav{text-align:center;margin-bottom:6px}
nav a{color:#bfe3ff;text-decoration:none;margin:0 12px;font-weight:600;
padding:6px 10px;border-radius:6px;transition:.18s}
nav a:hover{background:rgba(0,150,255,0.12)}

.top-section{display:flex;justify-content:center;align-items:center;height:32vh;margin-top:10px}
.container{width:75%;background:rgba(5,12,23,0.72);padding:22px;border-radius:12px;
box-shadow:0 8px 30px rgba(0,0,0,0.5);backdrop-filter:blur(6px)}

.content-section{display:flex;justify-content:center;padding:26px 0}
.content-wrapper{width:85%;background:rgba(5,12,23,0.68);padding:20px;
border-radius:12px;box-shadow:0 10px 30px rgba(0,0,0,0.45);backdrop-filter:blur(6px)}

input{width:64%;padding:12px;border-radius:8px;border:1px solid rgba(19,77,115,0.6);
background:#071a28;color:#e6eef8}
button{padding:10px 18px;background:#0ea5ff;color:#042531;border:none;border-radius:8px;font-weight:700}
button:hover{background:#38b5ff}

.scan-wrap{margin-top:12px;height:14px;background:rgba(255,255,255,0.05);
border-radius:10px;overflow:hidden;display:none}
.scan-bar{height:100%;width:0;background:linear-gradient(90deg,#7b61ff,#00d6ff)}
.scan-text{font-size:13px;margin-top:8px;color:#bcdff8}

.result{margin-top:14px;padding:14px;border-radius:8px;background:rgba(6,12,20,0.45)}
.safe{background:#0f3d1e;padding:10px;border-radius:8px;color:#76ff7a}
.suspicious{background:#3a1b4d;padding:10px;border-radius:8px;color:#d07cff}
.danger{background:#5a0e14;padding:10px;border-radius:8px;color:#ff7a82}

.footer{text-align:center;margin-top:24px;color:#9fbadf;font-size:13px}

.rules-card{max-width:980px;margin:auto;padding:22px;border-radius:12px;background:rgba(255,255,255,0.02);
box-shadow:0 10px 30px rgba(0,0,0,0.45);line-height:1.65;font-size:16px}
.rules-card ol{margin-left:20px;padding-left:18px}
.rules-card li{margin:10px 0}
</style>
</head>

<body>
<div class="bg-animation">
{% for i in range(26) %}
<div class="particle" style="left:{{ (i*3.6)%100 }}%;animation-delay:{{ i*0.32 }}s"></div>
{% endfor %}
</div>

<header>
{% if logo_exists %}
<img src="{{ logo_url }}" class="logo">
{% endif %}
<h1>URL THREAT DETECTOR</h1>
</header>

<nav>
<a href="/">Home</a>
<a href="/about">About</a>
<a href="/features">Features</a>
<a href="/rules">Rules</a>
<a href="/contact">Contact</a>
</nav>

{% if show_top %}
<div class="top-section"><div class="container">
<form id="scanForm" method="POST">
<input type="text" name="url" placeholder="Enter URL to analyze" required>
<button type="submit">Scan</button>
</form>
<div class="scan-wrap" id="scanWrap">
<div class="scan-bar" id="scanBar"></div>
</div>
<div class="scan-text" id="scanText" style="display:none">Scanning — analyzing heuristics...</div>
{{ body|safe }}
</div></div>
{% else %}
<div class="content-section"><div class="content-wrapper">
{{ body|safe }}
</div></div>
{% endif %}

<div class="footer">Official Internal Use — Local Demo</div>

<script>
document.addEventListener("DOMContentLoaded",()=>{
let f=document.getElementById("scanForm");
let w=document.getElementById("scanWrap");
let b=document.getElementById("scanBar");
let t=document.getElementById("scanText");
if(f){
f.addEventListener("submit",e=>{
w.style.display="block";
t.style.display="block";
b.style.width="0%";
b.style.transition="width 1s linear";
setTimeout(()=>b.style.width="40%",50);
setTimeout(()=>b.style.width="70%",700);
setTimeout(()=>b.style.width="95%",1400);
setTimeout(()=>{b.style.transition="width .3s linear";b.style.width="100%"},2000);
setTimeout(()=>f.submit(),2100);
e.preventDefault();
});
}
});
</script>

</body>
</html>
"""

@app.route("/",methods=["GET","POST"])
def home():
    logo_exists=os.path.exists(os.path.join("static","logo.png"))
    logo_url=url_for('static',filename='logo.png') if logo_exists else ""
    result_html=""

    if request.method=="POST":
        url=request.form.get("url","").strip()
        if url:
            s=heuristic_score(url)
            p=phishing_probability(s)
            v=verdict(s)
            cc="safe" if v in ["Safe","Low Risk"] else "suspicious" if v=="Suspicious" else "danger"
            cid=uuid.uuid4().hex[:12].upper()
            ts=datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            result_html=f"""
            <div class='result'>
            <div><b>URL:</b> {url}</div>
            <div><b>Score:</b> {s}</div>
            <div><b>Phishing Probability:</b> {p}%</div>
            <div class='{cc}' style='margin-top:8px;'><b>{v}</b></div>
            <div style='margin-top:12px;'>
            <a href="/download_report?u={url}&s={s}&p={p}&v={v}&cid={cid}&ts={ts}">
            <button>Download Forensic PDF</button></a></div>
            <div style='margin-top:12px;'><small>Case ID: {cid} · Generated: {ts}</small></div>
            </div>
            """

    body=f"<div>{result_html}</div>"
    return render_template_string(BASE_TEMPLATE,title="URL Threat Detector",body=body,
                                  logo_exists=logo_exists,logo_url=logo_url,show_top=True)

@app.route("/download_report")
def download_report():
    url=request.args.get("u","")
    s=request.args.get("s","")
    p=request.args.get("p","")
    v=request.args.get("v","")
    cid=request.args.get("cid",uuid.uuid4().hex[:12].upper())
    ts=request.args.get("ts",datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    fn=f"report_{cid}.pdf"
    c=canvas.Canvas(fn,pagesize=A4)
    w,h=A4
    if os.path.exists(os.path.join("static","logo.png")):
        try: c.drawImage(os.path.join("static","logo.png"),(w-140)/2,h-100,width=140,height=70)
        except: pass
    c.setFont("Helvetica-Bold",16)
    c.drawCentredString(w/2,h-130,"FORENSIC URL THREAT ANALYSIS REPORT")
    c.line(50,h-140,w-50,h-140)
    c.setFont("Helvetica",11)
    c.drawString(60,h-170,f"Case ID: {cid}")
    c.drawString(300,h-170,f"Generated: {ts}")
    c.drawString(60,h-200,f"URL: {url}")
    c.drawString(60,h-220,f"Score: {s}")
    c.drawString(60,h-240,f"Probability: {p}%")
    c.drawString(60,h-260,f"Verdict: {v}")
    c.save()
    return send_file(fn,as_attachment=True)

@app.route("/about")
def about():
    body="<p>The Forensic URL Threat Detector performs multi-layered heuristic analysis to identify malicious URLs.</p>"
    return render_template_string(BASE_TEMPLATE,title="About",body=body,
                                  logo_exists=os.path.exists("static/logo.png"),
                                  logo_url=url_for('static',filename='logo.png'),
                                  show_top=False)

@app.route("/features")
def features():
    body="<ul><li>Heuristic scoring</li><li>Homoglyph checks</li><li>Encoding detection</li><li>Forensic PDF reports</li></ul>"
    return render_template_string(BASE_TEMPLATE,title="Features",body=body,
                                  logo_exists=os.path.exists("static/logo.png"),
                                  logo_url=url_for('static',filename='logo.png'),
                                  show_top=False)

@app.route("/rules")
def rules():
    body="""<div class='rules-card'>
    <ol>
    <li>Checks insecure HTTP usage.</li>
    <li>Detects raw IP hosts.</li>
    <li>Identifies shortened URLs.</li>
    <li>Flags rare TLDs.</li>
    <li>Searches for suspicious keywords.</li>
    <li>Detects malware domain tokens.</li>
    <li>Counts subdomain layers.</li>
    <li>Checks '@' in URLs.</li>
    <li>Detects punycode.</li>
    <li>Identifies suspicious ports.</li>
    <li>Flags long hostnames.</li>
    <li>Detects encoding tricks.</li>
    <li>Finds JS code in URLs.</li>
    <li>Checks bad extensions.</li>
    <li>Detects mixed scripts.</li>
    <li>Detects homoglyphs.</li>
    <li>Checks parameter abuse.</li>
    <li>Inspects malicious paths.</li>
    <li>Computes entropy.</li>
    <li>Evaluates formatting.</li>
    </ol></div>"""
    return render_template_string(BASE_TEMPLATE,title="Rules",body=body,
                                  logo_exists=os.path.exists("static/logo.png"),
                                  logo_url=url_for('static',filename='logo.png'),
                                  show_top=False)

@app.route("/contact")
def contact():
    body="""
    <h2 style='margin-bottom:10px;'>Project Team</h2>
    <ul style='margin-top:12px;line-height:1.7;font-size:16px;'>
    <li>Bandla Vinay</li>
    <li>Teja Hasini</li>
    <li>Chakrika</li>
    <li>Manikanth</li>
    <li>Gnaneshwar</li>
    <li>Hima Sekhar</li>
    <li>Lavanya</li>
    <li>Hansika</li>
    </ul>
    """
    return render_template_string(BASE_TEMPLATE,title="Contact",body=body,
                                  logo_exists=os.path.exists("static/logo.png"),
                                  logo_url=url_for('static',filename='logo.png'),
                                  show_top=False)

if __name__=="__main__":
    app.run(debug=True)
