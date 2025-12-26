from flask import Flask, request, render_template_string, jsonify
import requests, os, textwrap
from bs4 import BeautifulSoup
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-2.5-flash-lite")

STRUCTURA_LOGO_BASE64 = """

""".strip()

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Structura</title>

<link rel="icon" type="image/png" href="/static/structura_logo.png?v=3">

<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap" rel="stylesheet">

<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{
height:100%;
font-family:Inter;
background:
radial-gradient(1200px at 10% 10%, rgba(99,102,241,.18), transparent),
radial-gradient(900px at 90% 20%, rgba(236,72,153,.18), transparent),
#05060a;
color:#e5e7eb;
overflow:hidden;
}
.container{display:flex;height:100vh;width:100vw}
.left{
width:68%;
padding:60px;
display:flex;
flex-direction:column;
overflow-y:auto;
}
.right{
width:32%;
display:flex;
flex-direction:column;
background:rgba(255,255,255,0.06);
backdrop-filter:blur(28px);
border-left:1px solid rgba(255,255,255,0.08);
overflow-y:auto;
}
h1{
font-size:52px;
font-weight:800;
display:flex;
align-items:center;
gap:14px;
background:linear-gradient(135deg,#c7d2fe,#fbcfe8);
-webkit-background-clip:text;
color:transparent;
}
.subtitle{margin-top:16px;font-size:18px;color:#9ca3af;max-width:520px}
.input-wrap{margin-top:48px;display:flex;gap:16px}
input{
flex:1;
padding:18px 22px;
border-radius:18px;
border:1px solid rgba(255,255,255,0.12);
background:rgba(255,255,255,0.04);
color:#fff;
font-size:16px;
outline:none;
}
button{
padding:18px 30px;
border-radius:18px;
border:none;
cursor:pointer;
font-weight:700;
font-size:15px;
color:#05060a;
background:linear-gradient(135deg,#e9d5ff,#fbcfe8);
box-shadow:0 20px 60px rgba(236,72,153,.35);
transition:.3s;
}
button:hover{transform:translateY(-2px)}
.card{
margin-top:50px;
padding:36px;
border-radius:28px;
background:linear-gradient(180deg,rgba(255,255,255,.08),rgba(255,255,255,.02));
border:1px solid rgba(255,255,255,.12);
}
.score{
font-size:64px;
font-weight:800;
background:linear-gradient(135deg,#a5b4fc,#f9a8d4);
-webkit-background-clip:text;
color:transparent;
}
.meta{margin-top:10px;font-size:15px;color:#9ca3af}
.signal{
margin-top:14px;
padding:14px 18px;
border-radius:14px;
background:rgba(255,255,255,0.05);
border:1px solid rgba(255,255,255,0.08);
}
.chat-head{padding:28px;border-bottom:1px solid rgba(255,255,255,0.08)}
.chat{flex:1;padding:26px;overflow-y:auto}
.bubble{
max-width:88%;
padding:16px 20px;
border-radius:18px;
margin-bottom:18px;
line-height:1.6;
}
.user{
margin-left:auto;
background:linear-gradient(135deg,#6366f1,#ec4899);
color:white;
}
.marin{
background:rgba(255,255,255,0.07);
border:1px solid rgba(255,255,255,0.1);
}
.chatbox{
display:flex;
gap:12px;
padding:22px;
border-top:1px solid rgba(255,255,255,0.08);
}
.chatbox input{
flex:1;
padding:16px 20px;
border-radius:16px;
border:1px solid rgba(255,255,255,0.12);
background:rgba(255,255,255,0.05);
color:white;
}
</style>
</head>

<body>
<div class="container">

<div class="left">
<h1>
<img src="/static/structura_logo.png" style="width:56px">
<span>STRUCTURA</span>
</h1>

<div class="subtitle">
Structural intelligence for detecting product complexity and bloat.
</div>

<div class="input-wrap">
<input id="url" placeholder="https://example.com">
<button onclick="analyze()">Analyze</button>
</div>

<div id="output"></div>
</div>

<div class="right">
<div class="chat-head">
<h3>MARIN</h3>
<div style="font-size:13px;color:#9ca3af">Product reasoning layer</div>
</div>

<div class="chat" id="chat">
<div class="bubble marin">
Analyze a product, then ask what the signals imply.
</div>
</div>

<div class="chatbox">
<input id="msg" placeholder="Ask Marin…">
<button onclick="send()">Send</button>
</div>
</div>

</div>

<script>
let analysis=null

function analyze(){
let url=document.getElementById("url").value
fetch("/analyze",{method:"POST",headers:{"Content-Type":"application/json"},
body:JSON.stringify({url:url})})
.then(r=>r.json()).then(d=>{
analysis=d
document.getElementById("output").innerHTML=`
<div class="card">
<div class="score">${d.score}</div>
<div class="meta">Structural Load • ${d.status}</div>
${d.signals.map(s=>`<div class="signal">${s}</div>`).join("")}
</div>`
})
}

function send(){
let msg=document.getElementById("msg").value
if(!analysis)return
document.getElementById("chat").innerHTML+=
`<div class="bubble user">${msg}</div>`

fetch("/chat",{method:"POST",headers:{"Content-Type":"application/json"},
body:JSON.stringify({msg:msg,analysis:analysis})})
.then(r=>r.json()).then(d=>{
document.getElementById("chat").innerHTML+=
`<div class="bubble marin">${d.reply}</div>`
})
document.getElementById("msg").value=""
}
</script>
</body>
</html>
"""

def analyze_site(url):
    try:
        if not url.startswith("http"):
            url = "https://" + url

        r = requests.get(
            url,
            timeout=8,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        soup = BeautifulSoup(r.text, "html.parser")

        links = len(soup.find_all("a"))
        forms = len(soup.find_all("form"))
        inputs = len(soup.find_all("input"))
        buttons = len(soup.find_all("button"))

        density = links + forms + inputs + buttons
        score = min(100, int(density * 0.6))

        signals = []
        if links > 80: signals.append("Navigation surface is dense")
        if forms > 4: signals.append("Multiple workflows coexist")
        if inputs > 25: signals.append("Configuration complexity is high")
        if not signals: signals.append("Structure is lean")

        status = "Lean"
        if score > 45: status = "Overextended"
        if score > 70: status = "Obese"

        return score, status, signals

    except Exception as e:
        return 0, "Unreachable", [
            "Target could not be analyzed",
            "The site may block automated inspection",
            "Network or protocol failure detected"
        ]


@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/analyze",methods=["POST"])
def analyze():
    url=request.json["url"]
    score,status,signals=analyze_site(url)
    return jsonify({"score":score,"status":status,"signals":signals})

@app.route("/chat", methods=["POST"])
def chat():
    data=request.json
    msg=data.get("msg","")
    analysis=data.get("analysis",{})

    prompt=f"""
You are Marin, a calm, sharp product consultant.
Explain implications, not metrics.
you don't give very long replies, you just give the required amount of answer

Score: {analysis.get('score')}
Status: {analysis.get('status')}
Signals: {', '.join(analysis.get('signals', []))}

User question:
{msg}
"""

    try:
        response=model.generate_content(textwrap.dedent(prompt))
        reply=response.text.strip()
    except:
        reply="The concern is not the score itself, but how these signals interfere with the core user journey."

    return jsonify({"reply":reply})

if __name__=="__main__":
    app.run(debug=True)
