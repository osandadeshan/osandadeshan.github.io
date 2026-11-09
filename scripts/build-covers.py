#!/usr/bin/env python3
"""Build the project / publication cover images.

Usage:  python3 scripts/build-covers.py [slug ...]
Output: assets/img/covers/<slug>.jpg  (1280x800, 16:10)

Each cover is rendered from HTML (covers/<slug>.html, generated here) with headless
Chromium, in the site's own style: dark background, faint grid, violet/cyan glows,
Space Grotesk / Inter / JetBrains Mono, Bootstrap Icons. Left side: kind, name, value
line, tech chips. Right side: a stylised mock of what the project does.

To add a project: add an entry to PROJECTS (reuse a mock or write a new one), run this
script, then point the card, hero cover, pager thumbnails and og:image at the new file.
Text must be plain English with no em/en dashes (see CLAUDE.md).
"""
import glob, html, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "covers")
OUT = os.path.join(ROOT, "assets", "img", "covers")

E = html.escape

# ---------------------------------------------------------------- mocks
def win(title, body, cls=""):
    return (f'<div class="win {cls}"><div class="bar"><i></i><i></i><i></i>'
            f'<span>{E(title)}</span></div><div class="wb">{body}</div></div>')

def badge(t, kind="ok"):
    return f'<b class="badge {kind}">{E(t)}</b>'

def m_intelliapi():
    spec = ''.join(f'<div class="ln">{x}</div>' for x in [
        '<span class="h"># Login API</span>',
        '<span class="k">*</span> Send a POST request to <span class="s">"/api/login"</span>',
        '<span class="k">*</span> Verify the response status is <span class="s">"200"</span>',
        '<span class="k">*</span> Verify the field <span class="s">"token"</span> is not empty',
        '<span class="k">*</span> Verify the database has user <span class="s">"osanda"</span>',
    ])
    res = ''.join(f'<div class="row"><span>{E(n)}</span>{badge("PASS")}</div>' for n in
                  ["Send POST /api/login", "Response status 200", "Token is present", "Database record found"])
    return (win("login_api.spec", f'<div class="mono">{spec}</div>') +
            win("Execution report", res + '<div class="sum"><b class="g">4 passed</b> <span>0 failed</span> <span>Parallel run</span></div>', "shift"))

def m_healthchecker():
    svcs = [("Auth service", "ok ok ok"), ("Payments API", "ok down ok"), ("Orders API", "ok ok ok"),
            ("Search API", "ok ok warn"), ("Notifications", "ok ok ok"), ("User profile", "ok ok ok")]
    head = '<div class="hg"><span>Service</span><span>DEV</span><span>QA</span><span>PROD</span></div>'
    rows = ''.join('<div class="hg r"><span>%s</span>%s</div>' % (E(n), ''.join(f'<em class="dot {d}"></em>' for d in st.split())) for n, st in svcs)
    top = '<div class="live"><em class="dot ok pulse"></em> Live status <span>Auto refresh every 30 seconds</span></div>'
    return win("API Health Checker", top + head + rows, "wide")

def m_analyzer():
    bars = [("Element not found", 46), ("Timeout waiting for page", 28), ("Assertion failed", 16), ("Environment unavailable", 10)]
    b = ''.join(f'<div class="hb"><span>{E(n)}</span><div class="track"><div class="fill" style="width:{v*2}%"></div></div><b>{v}%</b></div>' for n, v in bars)
    donut = '<div class="donut" style="background:conic-gradient(#8B5CF6 0 46%,#22D3EE 46% 74%,#F59E0B 74% 90%,#64748B 90% 100%)"><div>4<small>root causes</small></div></div>'
    return win("Failure analysis.xlsx", f'<div class="split">{donut}<div class="bars">{b}</div></div>'
               '<div class="sum"><b class="r">Fix first:</b> <span>Element not found breaks the most tests</span></div>', "wide")

def m_extent():
    donut = '<div class="donut" style="background:conic-gradient(#22C55E 0 88%,#EF4444 88% 96%,#F59E0B 96% 100%)"><div>88%<small>passed</small></div></div>'
    tests = [("Login with valid user", "PASS"), ("Search product", "PASS"), ("Checkout with card", "FAIL"), ("Update profile", "PASS")]
    t = ''.join(f'<div class="row"><span>{E(n)}</span>{badge(s, "ok" if s == "PASS" else "bad")}</div>' for n, s in tests)
    shot = '<div class="shot"><i class="bi bi-image"></i><span>Failure screenshot attached</span></div>'
    return win("Extent Report", f'<div class="split">{donut}<div class="list">{t}</div></div>{shot}', "wide")

def m_webdriver():
    code = ('<div class="mono big"><span class="c">// one line, any browser, any OS</span><br>'
            'driver = <span class="k">DriverFactory</span>.<span class="f">getDriver</span>(<br>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">BrowserType</span>.<span class="s">CHROME</span>);</div>')
    br = ''.join(f'<div class="ico"><i class="bi bi-{i}"></i><span>{n}</span></div>' for i, n in
                 [("browser-chrome", "Chrome"), ("browser-firefox", "Firefox"), ("browser-edge", "Edge"), ("browser-safari", "Safari")])
    os_ = ''.join(f'<div class="ico sm"><i class="bi bi-{i}"></i><span>{n}</span></div>' for i, n in
                  [("windows", "Windows"), ("apple", "macOS"), ("ubuntu", "Linux")])
    checks = '<div class="checks"><span><i class="bi bi-check2-circle"></i> No driver downloads</span><span><i class="bi bi-check2-circle"></i> Zero configuration</span></div>'
    return win("BrowserTest.java", code) + f'<div class="icons">{br}</div><div class="icons">{os_}</div>{checks}'

def m_greporter():
    hdr = ('<div class="mail"><div><b>From</b> GReporter</div><div><b>To</b> Stakeholders (QA environment)</div>'
           '<div><b>Subject</b> Test execution summary: Regression suite</div></div>')
    donut = '<div class="donut" style="background:conic-gradient(#22C55E 0 82%,#EF4444 82% 94%,#F59E0B 94% 100%)"><div>82%<small>passed</small></div></div>'
    stats = ''.join(f'<div class="stat {c}"><b>{v}</b><span>{n}</span></div>' for v, n, c in [("82%", "Passed", "g"), ("12%", "Failed", "r"), ("6%", "Skipped", "y")])
    return win("Inbox", hdr + f'<div class="split">{donut}<div class="stats">{stats}</div></div>', "wide")

def m_tam():
    arts = [("browser-chrome", "Web automation with Selenium"), ("phone", "Mobile automation with Appium"),
            ("plug", "API testing with Rest Assured"), ("gear-wide-connected", "CI/CD pipelines for test suites")]
    a = ''.join(f'<div class="art"><i class="bi bi-{i}"></i><div><b>{E(t)}</b><span>Step-by-step tutorial</span></div></div>' for i, t in arts)
    return f'<div class="pub"><div class="pubh"><i class="bi bi-medium"></i> Test Automation Master</div>{a}</div>'

def phone(inner):
    return f'<div class="phone"><div class="notch"></div><div class="scr">{inner}</div></div>'

def m_mysight():
    lines = ''.join(f'<div class="tl" style="width:{w}%"></div>' for w in [92, 80, 88, 70, 85, 60])
    scr = f'<div class="paper">{lines}<div class="scan"></div></div><div class="cam"><i class="bi bi-camera-fill"></i> Capturing text</div>'
    waves = '<div class="voice"><i class="bi bi-volume-up-fill"></i><div class="waves">' + ''.join(f'<i style="height:{h}px"></i>' for h in [18, 34, 52, 30, 60, 40, 22, 48, 28, 16]) + '</div><span>Reading aloud</span></div>'
    return f'<div class="duo">{phone(scr)}{waves}</div>'

def m_webbot():
    spec = ''.join(f'<div class="ln">{x}</div>' for x in [
        '<span class="h"># Login to the portal</span>',
        '<span class="k">*</span> Open <span class="s">"Login page"</span>',
        '<span class="k">*</span> Type <span class="s">"osanda"</span> into <span class="s">"Username"</span>',
        '<span class="k">*</span> Click <span class="s">"Sign in"</span>',
        '<span class="k">*</span> Verify the title is <span class="s">"Dashboard"</span>',
    ])
    minis = ''.join(f'<div class="mini"><div class="bar"><i></i><i></i><i></i><span>{n}</span></div><div class="prog"><div style="width:{w}%"></div></div>{badge("PASS")}</div>'
                    for n, w in [("Chrome", 100), ("Firefox", 100), ("Edge", 100)])
    return win("login.spec", f'<div class="mono">{spec}</div>') + f'<div class="minis">{minis}</div>'

def m_soapui():
    steps = ''.join(f'<div class="row"><span><i class="bi bi-arrow-right-short"></i>{E(n)}</span></div>' for n in ["Create order request", "Get order by id", "Validate response schema", "Delete order"])
    rep = ''.join(f'<div class="row"><span>{E(n)}</span>{badge("PASS")}</div>' for n in ["Create order request", "Get order by id", "Validate response schema", "Delete order"])
    return (f'<div class="flow">{win("SoapUI suite", steps, "half")}'
            f'<div class="arrow"><i class="bi bi-arrow-right"></i><span>Run from Gauge</span></div>'
            f'{win("Gauge HTML report", rep + "<div class=sum><b class=g>4 steps passed</b></div>", "half")}</div>')

def m_textextractor():
    img = '<div class="photo"><i class="bi bi-image"></i>' + ''.join(f'<div class="tl" style="width:{w}%"></div>' for w in [85, 70, 90, 60]) + '</div><div class="cam"><i class="bi bi-camera-fill"></i> Scan image</div>'
    out = ('<div class="txt"><div class="txth"><i class="bi bi-fonts"></i> Recognised text</div>'
           '<p>Meeting notes: review the release checklist and share the test report with the team.</p>'
           '<div class="btns"><span><i class="bi bi-clipboard"></i> Copy</span><span><i class="bi bi-share"></i> Share</span></div></div>')
    return f'<div class="duo">{phone(img)}<div class="arrow v"><i class="bi bi-arrow-right"></i></div>{out}</div>'

def m_mock():
    term = ('<div class="mono term"><div><span class="p">$</span> firebase deploy --only functions</div>'
            '<div class="dim">Deploying functions to Firebase</div>'
            '<div class="g">Deploy complete</div>'
            '<div><span class="p">$</span> curl /api/users/1</div></div>')
    js = ('<div class="mono json">{<br>&nbsp;&nbsp;<span class="s">"id"</span>: 1,<br>&nbsp;&nbsp;<span class="s">"name"</span>: <span class="s">"Osanda"</span>,<br>'
          '&nbsp;&nbsp;<span class="s">"role"</span>: <span class="s">"QA Lead"</span>,<br>&nbsp;&nbsp;<span class="s">"active"</span>: <span class="k">true</span><br>}</div>')
    return win("Terminal", term) + win("GET /api/users/1   200 OK", js, "shift")

def m_quiz():
    rows = [("1", "Amaya Perera", 100), ("2", "Priya Raman", 80), ("3", "Daniel Silva", 80), ("4", "Kevin Fernando", 60)]
    r = ''.join(f'<div class="lb"><em>{k}</em><span>{E(n)}</span><div class="track"><div class="fill" style="width:{v}%"></div></div><b>{v}%</b></div>' for k, n, v in rows)
    top = '<div class="live"><i class="bi bi-trophy"></i> Results <span>Ranked by score, then time</span></div>'
    q = ('<div class="qz"><div class="qh"><b>Question 5 of 10</b><span class="timer"><i class="bi bi-clock"></i> 20:00</span></div>'
         '<div class="opt on"><i class="bi bi-check-square-fill"></i> Continuous integration testing</div>'
         '<div class="opt"><i class="bi bi-square"></i> Testing only after coding is complete</div></div>')
    return win("Quiz 1: Basic QA Concepts", top + r, "wide") + win("Private quiz link", q, "shift")

def m_ratecast():
    act = "40,70 80,68 120,84 160,90 200,76 240,78 280,104 320,104 360,86"
    fc = "360,86 400,74 440,75 480,75 520,76 560,76 600,75"
    band = "360,92 400,66 440,58 480,52 520,50 560,46 600,44 600,108 560,106 520,104 480,100 440,96 400,90 360,96"
    svg = (f'<svg viewBox="0 0 640 140" class="chart"><polygon points="{band}" fill="rgba(139,92,246,.22)"/>'
           f'<polyline points="{act}" fill="none" stroke="#22D3EE" stroke-width="3.5"/>'
           f'<polyline points="{fc}" fill="none" stroke="#A78BFA" stroke-width="3.5" stroke-dasharray="8 7"/>'
           '<line x1="360" y1="10" x2="360" y2="130" stroke="rgba(255,255,255,.3)" stroke-dasharray="3 5"/></svg>')
    cards = ''.join(f'<div class="stat"><span>{E(n)}</span><b>{v}</b></div>' for n, v in
                    [("Today, 1 SGD", "259.795"), ("Tomorrow", "259.561"), ("Month end", "259.516")])
    leg = '<div class="sum"><b class="g">Actual (Wise)</b> <span>Forecast with 80% range</span></div>'
    return win("RateCast · SGD to LKR", f'<div class="rc">{cards}</div>{svg}{leg}', "wide")

PROJECTS = [
    # slug, kind, name, value line, chips, mock, icon
    ("maxsoft-intelliapi", "Publication", "MaxSoft IntelliAPI", "Codeless API and database testing in plain business language. Adopted by the Pearson Mobile team.", ["Java", "Gauge", "Rest Assured"], m_intelliapi, "plug"),
    ("maxsoft-api-healthchecker", "Publication", "MaxSoft API Health Checker", "Spot a failing backend service before it blocks your team.", ["Node.js", "Express", "JavaScript"], m_healthchecker, "heart-pulse"),
    ("maxsoft-testng-test-results-analyzer", "Publication", "TestNG Test Results Analyzer", "Fix the issue that breaks the most tests first.", ["Java", "TestNG", "Apache POI"], m_analyzer, "bar-chart-line"),
    ("maxsoft-extent-reporter", "Publication", "MaxSoft Extent Reporter", "Rich HTML test reports for any TestNG framework, with zero reporting code.", ["Java", "TestNG", "Extent Reports"], m_extent, "file-earmark-bar-graph"),
    ("maxsoft-webdriver-manager", "Publication", "MaxSoft WebDriver Manager", "Start any browser on any OS in one line of code.", ["Java", "Selenium", "Maven"], m_webdriver, "window-stack"),
    ("maxsoft-greporter", "Publication", "MaxSoft GReporter", "Visual test summaries emailed to stakeholders after every Gauge run.", ["Java", "Gauge", "JavaMail"], m_greporter, "envelope-paper"),
    ("test-automation-master", "Publication", "Test Automation Master", "Hands-on tutorials on web, mobile and API automation and DevOps.", ["Medium", "275+ followers"], m_tam, "journal-richtext"),
    ("mysight", "Publication", "MySight", "A new vision for the blind: point a phone at printed text and hear it read aloud.", ["Android", "OpenCV", "OCR", "Text-to-Speech"], m_mysight, "eye"),
    ("quiz-portal", "Project", "Quiz Portal", "Timed quizzes with a private link per person and a ranked leaderboard.", ["Node.js", "Express", "PostgreSQL"], m_quiz, "ui-checks"),
    ("ratecast", "Project", "RateCast", "SGD to LKR and USD rate forecasts that learn from their own misses.", ["Next.js", "TypeScript", "Postgres"], m_ratecast, "graph-up-arrow"),
    ("maxsoft-webbot", "Project", "MaxSoft WebBot", "Codeless web UI automation in plain language, with parallel runs.", ["Java", "Gauge", "Selenium"], m_webbot, "robot"),
    ("soapui-to-gauge", "Project", "SoapUI to Gauge Plugin", "Run SoapUI suites from Gauge with detailed HTML reports.", ["Java", "SoapUI", "Gauge"], m_soapui, "arrow-left-right"),
    ("text-extractor", "Project", "Text Extractor", "Turn any image into editable text in seconds.", ["Android", "Java", "OCR"], m_textextractor, "fonts"),
    ("mockserver", "Project", "Mock API Server", "Mock APIs on Firebase before the real API exists.", ["Node.js", "Express", "Firebase"], m_mock, "hdd-network"),
]

CSS = r"""
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1280px;height:800px;overflow:hidden}
body{background:#07080F;color:#E7E9F5;font-family:Inter,Arial,sans-serif;position:relative}
.bg{position:absolute;inset:0;
 background:
  radial-gradient(620px 420px at 88% 18%,rgba(139,92,246,.38),transparent 70%),
  radial-gradient(560px 420px at 70% 100%,rgba(34,211,238,.26),transparent 70%),
  radial-gradient(500px 380px at 0% 0%,rgba(139,92,246,.18),transparent 70%),
  linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px) 0 0/40px 40px,
  linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px) 0 0/40px 40px,#07080F}
.wrap{position:relative;display:grid;grid-template-columns:470px 1fr;gap:44px;height:100%;padding:70px 64px;align-items:center}
.kind{font:600 17px 'JetBrains Mono',monospace;letter-spacing:.14em;text-transform:uppercase;color:#22D3EE;display:flex;align-items:center;gap:12px;margin-bottom:26px}
.kind .ic{width:52px;height:52px;border-radius:14px;display:grid;place-items:center;font-size:26px;color:#fff;background:linear-gradient(135deg,#8B5CF6,#22D3EE);box-shadow:0 10px 30px rgba(139,92,246,.45)}
h1{font:700 58px/1.04 'Space Grotesk',sans-serif;letter-spacing:-.02em;color:#fff;margin-bottom:22px}
h1 .g{background:linear-gradient(90deg,#A78BFA,#22D3EE);-webkit-background-clip:text;background-clip:text;color:transparent}
.val{font-size:23px;line-height:1.45;color:#B4B9D3;margin-bottom:30px}
.chips{display:flex;flex-wrap:wrap;gap:10px}
.chips span{font:500 16px 'JetBrains Mono',monospace;padding:8px 14px;border-radius:999px;border:1px solid rgba(255,255,255,.14);background:rgba(255,255,255,.05);color:#D7DAEE}
.right{display:flex;flex-direction:column;gap:18px;justify-content:center;position:relative}
.win{background:rgba(16,18,32,.88);border:1px solid rgba(255,255,255,.12);border-radius:18px;box-shadow:0 30px 70px rgba(0,0,0,.55);overflow:hidden}
.win.shift{margin-left:70px;margin-top:-6px}
.bar{display:flex;align-items:center;gap:7px;padding:12px 16px;background:rgba(255,255,255,.04);border-bottom:1px solid rgba(255,255,255,.08)}
.bar i{width:11px;height:11px;border-radius:50%;background:#EF4444;display:inline-block}
.bar i:nth-child(2){background:#F59E0B}.bar i:nth-child(3){background:#22C55E}
.bar span{margin-left:10px;font:500 14px 'JetBrains Mono',monospace;color:#9CA3C7}
.wb{padding:18px 20px}
.mono{font:15.5px/1.75 'JetBrains Mono',monospace;color:#D7DAEE}
.mono.big{font-size:19px;line-height:1.9}
.mono .h{color:#A78BFA;font-weight:600}.mono .k{color:#22D3EE}.mono .s{color:#FCD34D}.mono .c{color:#6B7194}.mono .f{color:#4ADE80}
.row{display:flex;justify-content:space-between;align-items:center;padding:9px 0;border-bottom:1px dashed rgba(255,255,255,.08);font-size:16px;color:#D7DAEE}
.row:last-of-type{border-bottom:0}
.badge{font:700 12.5px 'JetBrains Mono',monospace;padding:4px 10px;border-radius:7px;letter-spacing:.05em}
.badge.ok{background:rgba(34,197,94,.16);color:#4ADE80}.badge.bad{background:rgba(239,68,68,.16);color:#F87171}
.sum{margin-top:12px;display:flex;gap:16px;font:14px 'JetBrains Mono',monospace;color:#9CA3C7;align-items:center}
.sum .g{color:#4ADE80}.sum .r{color:#F87171}
.live{display:flex;align-items:center;gap:10px;font:600 16px Inter;color:#fff;margin-bottom:14px}
.live span{margin-left:auto;font:400 13px 'JetBrains Mono',monospace;color:#9CA3C7}
.hg{display:grid;grid-template-columns:1fr 70px 70px 70px;align-items:center;padding:8px 0;font:600 13px 'JetBrains Mono',monospace;color:#8B90B3;letter-spacing:.06em}
.hg.r{font:500 16px Inter;color:#D7DAEE;letter-spacing:0;border-top:1px solid rgba(255,255,255,.07)}
.hg span:not(:first-child){text-align:center}
.dot{width:14px;height:14px;border-radius:50%;display:block;margin:auto}
.dot.ok{background:#22C55E;box-shadow:0 0 12px rgba(34,197,94,.7)}.dot.down{background:#EF4444;box-shadow:0 0 12px rgba(239,68,68,.8)}.dot.warn{background:#F59E0B;box-shadow:0 0 12px rgba(245,158,11,.7)}
.live .dot{margin:0}
.split{display:flex;gap:26px;align-items:center}
.donut{flex:0 0 170px;height:170px;border-radius:50%;display:grid;place-items:center}
.donut>div{width:112px;height:112px;border-radius:50%;background:#101220;display:grid;place-items:center;align-content:center;font:700 30px 'Space Grotesk';color:#fff;text-align:center}
.donut small{display:block;font:500 12px 'JetBrains Mono',monospace;color:#9CA3C7;margin-top:2px}
.bars{flex:1;display:flex;flex-direction:column;gap:13px}
.hb{display:grid;grid-template-columns:1fr 46px;gap:4px 10px;font-size:15px;color:#D7DAEE}
.hb .track{grid-column:1;height:10px;border-radius:6px;background:rgba(255,255,255,.07);overflow:hidden}
.hb .fill{height:100%;border-radius:6px;background:linear-gradient(90deg,#8B5CF6,#22D3EE)}
.hb b{grid-row:1/3;grid-column:2;align-self:center;font:700 16px 'JetBrains Mono';color:#fff;text-align:right}
.list{flex:1}
.shot{margin-top:14px;display:flex;gap:10px;align-items:center;padding:12px 14px;border-radius:12px;background:rgba(239,68,68,.08);border:1px dashed rgba(239,68,68,.4);color:#FCA5A5;font-size:15px}
.icons{display:flex;gap:14px}
.ico{flex:1;display:flex;flex-direction:column;align-items:center;gap:8px;padding:18px 8px;border-radius:16px;background:rgba(16,18,32,.85);border:1px solid rgba(255,255,255,.1);font-size:15px;color:#D7DAEE}
.ico i{font-size:38px;background:linear-gradient(135deg,#A78BFA,#22D3EE);-webkit-background-clip:text;background-clip:text;color:transparent}
.ico.sm{padding:12px 8px}.ico.sm i{font-size:26px}
.checks{display:flex;gap:22px;font-size:17px;color:#4ADE80}
.mail{display:flex;flex-direction:column;gap:8px;font-size:15.5px;color:#D7DAEE;padding-bottom:16px;margin-bottom:18px;border-bottom:1px solid rgba(255,255,255,.08)}
.mail b{display:inline-block;width:76px;color:#8B90B3;font:600 13px 'JetBrains Mono',monospace;letter-spacing:.06em;text-transform:uppercase}
.stats{flex:1;display:grid;gap:12px}
.stat{display:flex;justify-content:space-between;align-items:center;padding:12px 16px;border-radius:12px;background:rgba(255,255,255,.05)}
.stat b{font:700 24px 'Space Grotesk'}.stat span{color:#9CA3C7;font-size:15px}
.stat.g b{color:#4ADE80}.stat.r b{color:#F87171}.stat.y b{color:#FCD34D}
.pub{display:flex;flex-direction:column;gap:14px}
.pubh{font:700 22px 'Space Grotesk';color:#fff;display:flex;gap:12px;align-items:center;margin-bottom:4px}
.pubh i{font-size:28px;color:#fff}
.art{display:flex;gap:16px;align-items:center;padding:18px 20px;border-radius:16px;background:rgba(16,18,32,.88);border:1px solid rgba(255,255,255,.1);box-shadow:0 16px 40px rgba(0,0,0,.4)}
.art:nth-child(odd){margin-left:40px}
.art>i{flex:0 0 52px;height:52px;border-radius:14px;display:grid;place-items:center;font-size:24px;color:#fff;background:linear-gradient(135deg,#8B5CF6,#22D3EE)}
.art b{display:block;font:600 18px Inter;color:#fff}.art span{font-size:14px;color:#9CA3C7}
.duo{display:flex;align-items:center;gap:30px;justify-content:center}
.phone{flex:0 0 250px;height:500px;border-radius:40px;padding:14px;background:#151827;border:2px solid rgba(255,255,255,.14);box-shadow:0 30px 70px rgba(0,0,0,.6);position:relative}
.notch{position:absolute;top:14px;left:50%;transform:translateX(-50%);width:90px;height:20px;border-radius:0 0 14px 14px;background:#151827;z-index:2}
.scr{height:100%;border-radius:28px;background:linear-gradient(180deg,#1B1F35,#0E1020);padding:44px 16px 16px;display:flex;flex-direction:column;gap:14px;overflow:hidden}
.paper{position:relative;background:#F4F1E8;border-radius:10px;padding:20px 16px;display:flex;flex-direction:column;gap:12px;height:290px}
.paper .tl{height:9px;border-radius:4px;background:#3B3B4F;opacity:.75}
.scan{position:absolute;inset:-6px;border:3px solid #22D3EE;border-radius:12px;box-shadow:0 0 24px rgba(34,211,238,.6)}
.cam{margin-top:auto;text-align:center;font:600 14px 'JetBrains Mono';color:#22D3EE}
.voice{display:flex;flex-direction:column;align-items:center;gap:16px;color:#fff}
.voice>i{font-size:56px;color:#22D3EE}
.waves{display:flex;gap:7px;align-items:center;height:70px}
.waves i{width:9px;border-radius:5px;background:linear-gradient(180deg,#A78BFA,#22D3EE)}
.voice span{font:600 17px 'JetBrains Mono';color:#B4B9D3}
.minis{display:flex;gap:14px}
.mini{flex:1;background:rgba(16,18,32,.88);border:1px solid rgba(255,255,255,.12);border-radius:14px;overflow:hidden;display:flex;flex-direction:column;align-items:flex-start;gap:12px;padding-bottom:14px}
.mini .bar{width:100%}.mini .bar span{margin-left:6px;font-size:13px}
.prog{margin:0 14px;width:calc(100% - 28px);height:8px;border-radius:5px;background:rgba(255,255,255,.08)}
.prog div{height:100%;border-radius:5px;background:linear-gradient(90deg,#8B5CF6,#22D3EE)}
.mini .badge{margin-left:14px}
.flow{display:flex;align-items:center;gap:14px}
.win.half{flex:1}
.win.half .row{font-size:14.5px}
.arrow{display:flex;flex-direction:column;align-items:center;gap:6px;color:#22D3EE;font:600 12px 'JetBrains Mono';text-align:center;width:74px}
.arrow i{font-size:34px}
.arrow.v{width:auto}
.photo{background:#2A2F4A;border-radius:12px;padding:22px 16px;display:flex;flex-direction:column;gap:12px;height:280px;position:relative}
.photo>i{font-size:30px;color:#8B90B3;margin-bottom:8px}
.photo .tl{height:9px;border-radius:4px;background:#8B90B3;opacity:.6}
.txt{flex:0 0 270px;background:rgba(16,18,32,.9);border:1px solid rgba(255,255,255,.12);border-radius:18px;padding:22px;box-shadow:0 30px 70px rgba(0,0,0,.5)}
.txth{font:600 14px 'JetBrains Mono';color:#22D3EE;margin-bottom:12px}
.txt p{font-size:18px;line-height:1.55;color:#fff;margin-bottom:18px}
.btns{display:flex;gap:10px}.btns span{padding:8px 14px;border-radius:10px;background:rgba(139,92,246,.2);color:#C4B5FD;font-size:14px}
.term div{white-space:nowrap}.term .p{color:#22D3EE}.term .dim{color:#6B7194}.term .g{color:#4ADE80}
.json{font-size:17px}
.lb{display:grid;grid-template-columns:34px 170px 1fr 56px;gap:12px;align-items:center;padding:9px 0;border-top:1px solid rgba(255,255,255,.07);font-size:16px;color:#D7DAEE}
.lb em{font:700 14px 'JetBrains Mono';font-style:normal;width:28px;height:28px;border-radius:50%;display:grid;place-items:center;background:rgba(139,92,246,.22);color:#C4B5FD}
.lb .track{height:10px;border-radius:6px;background:rgba(255,255,255,.07);overflow:hidden}.lb .fill{height:100%;border-radius:6px;background:linear-gradient(90deg,#8B5CF6,#22D3EE)}
.lb b{font:700 15px 'JetBrains Mono';color:#fff;text-align:right}
.live>i{color:#FCD34D}
.qh{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;font-size:15px;color:#9CA3C7}
.timer{font:700 15px 'JetBrains Mono';color:#fff;padding:5px 12px;border-radius:999px;background:rgba(255,255,255,.08)}
.opt{display:flex;gap:10px;align-items:center;padding:10px 14px;border-radius:10px;border:1px solid rgba(255,255,255,.1);font-size:15.5px;color:#D7DAEE;margin-top:8px}
.opt.on{border-color:#8B5CF6;background:rgba(139,92,246,.16)}.opt.on i{color:#A78BFA}
.rc{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:14px}
.rc .stat{flex-direction:column;align-items:flex-start;gap:4px}.rc .stat b{font-size:28px;color:#fff}.rc .stat span{font:500 12.5px 'JetBrains Mono';text-transform:uppercase;letter-spacing:.06em}
.chart{width:100%;height:auto;display:block}
"""

TPL = """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{name} cover</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@600;700&display=block" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
<style>{css}</style></head><body><div class="bg"></div>
<div class="wrap"><div class="left">
<div class="kind"><span class="ic"><i class="bi bi-{icon}"></i></span>{kind}</div>
<h1>{title}</h1><p class="val">{val}</p><div class="chips">{chips}</div></div>
<div class="right">{mock}</div></div></body></html>"""


def title_html(name):
    # Gradient on the last word for the site's signature look.
    parts = name.rsplit(" ", 1)
    return E(parts[0]) + (f' <span class="g">{E(parts[1])}</span>' if len(parts) == 2 else "")


def find_browser():
    env = os.environ.get("CHROME")
    if env:
        return env
    cands = sorted(glob.glob(os.path.expanduser("~/Library/Caches/ms-playwright/chromium_headless_shell-*/*/chrome-headless-shell")), reverse=True)
    cands += ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Chromium.app/Contents/MacOS/Chromium"]
    for c in cands:
        if os.access(c, os.X_OK):
            return c
    sys.exit("No Chromium found; set CHROME=/path/to/chrome")


def main():
    only = set(sys.argv[1:])
    os.makedirs(SRC, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    browser = find_browser()
    for slug, kind, name, val, chips, mock, icon in PROJECTS:
        if only and slug not in only:
            continue
        page = TPL.format(name=E(name), css=CSS, icon=icon, kind=E(kind), title=title_html(name), val=E(val),
                          chips="".join(f"<span>{E(c)}</span>" for c in chips), mock=mock())
        src = os.path.join(SRC, slug + ".html")
        with open(src, "w") as f:
            f.write(page)
        png = os.path.join(tempfile.gettempdir(), slug + ".png")
        with tempfile.TemporaryDirectory() as prof:
            subprocess.run([browser, "--headless", "--hide-scrollbars", "--disable-gpu", f"--user-data-dir={prof}",
                            "--window-size=1280,800", "--virtual-time-budget=10000", f"--screenshot={png}", "file://" + src],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        jpg = os.path.join(OUT, slug + ".jpg")
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "86", png, "--out", jpg],
                       check=True, stdout=subprocess.DEVNULL)
        print(f"{slug}: {os.path.getsize(jpg) // 1024} KB")


if __name__ == "__main__":
    main()
