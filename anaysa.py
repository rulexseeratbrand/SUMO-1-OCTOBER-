# app.py
from flask import Flask, render_template_string, request, jsonify
import requests
import re
from bs4 import BeautifulSoup

app = Flask(__name__)

HTML = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>POST & PROFILE UID</title>
<style>
  /* Simple styling inspired by your screenshot */
  body {
    background: linear-gradient(180deg,#0f1116 0%, #1b1418 100%);
    font-family: "Segoe UI", Roboto, Arial, sans-serif;
    color: #b6f5b6;
    display:flex;
    align-items:center;
    justify-content:center;
    min-height:100vh;
    margin:0;
  }
  .card{
    width:360px;
    background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
    border-radius:18px;
    padding:22px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.6);
    border: 1px solid rgba(255,255,255,0.04);
  }
  h1 { color:#ff9a00; text-align:center; margin:0 0 14px; font-size:22px; letter-spacing:2px;}
  label { color:#4fe0ff; font-size:13px; display:block; margin-bottom:8px;}
  input[type="text"]{
    width:100%;
    padding:14px;
    border-radius:12px;
    border:1px solid rgba(255,255,255,0.06);
    background: rgba(0,0,0,0.25);
    color:#ddd;
    outline:none;
    box-sizing:border-box;
    font-size:14px;
  }
  .btn {
    display:block;
    margin-top:14px;
    width:100%;
    padding:14px;
    background: linear-gradient(90deg,#ff8a00,#ff5f3b);
    color:#fff;
    font-weight:600;
    border:none;
    border-radius:12px;
    cursor:pointer;
    font-size:16px;
  }
  .result {
    margin-top:18px;
    padding:14px;
    border-radius:10px;
    background: rgba(0,0,0,0.35);
    border:1px solid rgba(79,224,255,0.08);
    color:#47ff7a;
    word-wrap:break-word;
    text-align:center;
  }
  .error { color:#ff6b6b; }
  .copy-btn{
    margin-top:10px;
    display:inline-block;
    padding:8px 12px;
    border-radius:8px;
    background: #00d4ff;
    color:#023047;
    font-weight:700;
    cursor:pointer;
    border:none;
  }
  .small { font-size:12px; color:#9aa4b2; margin-top:12px; text-align:center;}
</style>
</head>
<body>
  <div class="card">
    <h1>POST & PROFILE UID</h1>
    <label for="fburl">PASTE FB POST OR PROFILE LINK</label>
    <input id="fburl" type="text" placeholder="e.g: https://www.facebook.com/username_or_post_link">
    <button id="getuid" class="btn">🔍 GET UID</button>

    <div id="output" class="result" style="display:none;"></div>
    <div class="small">© TRICKS BY SEERAT BRAND SYSTEM .</div>
  </div>

<script>
document.getElementById('getuid').addEventListener('click', async () => {
  const url = document.getElementById('fburl').value.trim();
  const output = document.getElementById('output');
  output.style.display = 'block';
  output.innerHTML = 'Processing...';
  try {
    const res = await fetch('/extract_uid', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ url })
    });
    const data = await res.json();
    if(data.success){
      output.innerHTML = '<div style="font-size:18px; font-weight:700;">' + data.uid + '</div>' +
        '<button class="copy-btn" onclick="navigator.clipboard.writeText(\\'' + data.uid + '\\')">COPY UID</button>';
    } else {
      output.innerHTML = '<span class="error">' + (data.error || 'UID not found') + '</span>';
    }
  } catch(err){
    output.innerHTML = '<span class="error">Server error. Try again.</span>';
  }
});
</script>
</body>
</html>
"""

# Patterns to look for in HTML/text to extract numeric id:
UID_PATTERNS = [
    re.compile(r'profile\.php\?id=(\d{5,})'),
    re.compile(r'ft_ent_identifier[":\']+?(\d{5,})'),
    re.compile(r'entity_id[":\']+?(\d{5,})'),
    re.compile(r'owner[":\']\s*{[^}]*id[":\']\s*"?(\d{5,})'),
    re.compile(r'"pageID":\s*"?(\\?(\d{5,}))'),
    # Generic long digit sequences (15+ digits common in FB ids)
    re.compile(r'(\d{9,25})'),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
}

def extract_uid_from_text(text):
    # Try specific patterns first
    for pat in UID_PATTERNS:
        for m in pat.finditer(text):
            # pick reasonable ids (avoid timestamps like 2024...)
            uid = m.group(1)
            if uid and len(re.sub(r'^0+','',uid)) >= 5:
                # prefer numeric sequences that are not obviously dates
                return uid
    return None

def fetch_page_text(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=12, allow_redirects=True)
        if resp.status_code == 200:
            return resp.text
        else:
            return None
    except requests.RequestException:
        return None

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML)

@app.route('/extract_uid', methods=['POST'])
def extract_uid():
    data = request.get_json() or {}
    url = (data.get('url') or '').strip()
    if not url:
        return jsonify(success=False, error="Koi URL nahi diya gaya.")
    # Pre-check: if URL already contains profile.php?id=
    m = re.search(r'profile\.php\?id=(\d{5,})', url)
    if m:
        return jsonify(success=True, uid=m.group(1))

    # Try to extract trailing numeric id in path (some share links contain long digits)
    m2 = re.search(r'/(\d{9,25})(?:[/?]|$)', url)
    if m2:
        return jsonify(success=True, uid=m2.group(1))

    # Fetch page and parse
    page = fetch_page_text(url)
    if not page:
        return jsonify(success=False, error="Facebook page fetch nahi hua (shayed private ya blocked).")

    # Quick search in raw HTML
    uid = extract_uid_from_text(page)
    if uid:
        return jsonify(success=True, uid=uid)

    # Try to parse Open Graph meta tags and scripts using BeautifulSoup
    try:
        soup = BeautifulSoup(page, "html.parser")
        # OG tags sometimes contain canonical URL with numeric id
        for tag in soup.find_all('meta'):
            if tag.get('property') in ('al:android:url','al:ios:url','og:url','og:image'):
                content = tag.get('content','')
                m = re.search(r'profile\.php\?id=(\d{5,})', content)
                if m:
                    return jsonify(success=True, uid=m.group(1))
                m2 = re.search(r'/(\d{9,25})(?:[/?]|$)', content)
                if m2:
                    return jsonify(success=True, uid=m2.group(1))
        # search scripts for ft_ent_identifier
        scripts = soup.find_all('script')
        for s in scripts:
            text = s.string or s.get_text() or ""
            uid = extract_uid_from_text(text)
            if uid:
                return jsonify(success=True, uid=uid)
    except Exception:
        pass

    # Final fallback: look for long digits anywhere (but filter out short years)
    mfinal = re.search(r'(\d{9,25})', page)
    if mfinal:
        candidate = mfinal.group(1)
        return jsonify(success=True, uid=candidate)

    return jsonify(success=False, error="UID nahi mila. Ho sakta hai page private ho ya Facebook ne content block kiya ho.")

if __name__ == '__main__':
    # Run on 0.0.0.0:5000 for Replit/Termux compatibility
    app.run(host='0.0.0.0', port=5000, debug=True)
