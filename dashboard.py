from flask import Flask, render_template_string, jsonify
import json

app = Flask(__name__)

HTML = r"""
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Surveillance Bétail — INPT</title>
<meta http-equiv="refresh" content="30">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:wght@600&display=swap" rel="stylesheet">
<style>
:root{
  --g50:#EAF3DE;--g100:#C0DD97;--g400:#639922;--g600:#3B6D11;--g800:#27500A;
  --r50:#FCEBEB;--r400:#E24B4A;--r600:#A32D2D;--r800:#791F1F;
  --a50:#FAEEDA;--a400:#EF9F27;--a600:#854F0B;--a800:#633806;
  --bg:#0f1a0c;--surf:#162012;--card:#1c2a17;
  --brd:rgba(99,153,34,0.18);--brd2:rgba(99,153,34,0.32);
  --tx:#d6eabc;--tx2:#8aad62;--tx3:#5a7a3a;
}
*{margin:0;padding:0;box-sizing:border-box}
html,body{height:100%;overflow:hidden}
body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--tx);display:flex;flex-direction:column}

.hdr{background:var(--surf);border-bottom:0.5px solid var(--brd2);padding:11px 22px;display:flex;align-items:center;justify-content:space-between;flex-shrink:0}
.hdr-l{display:flex;align-items:center;gap:12px}
.logo{width:36px;height:36px;border-radius:50%;background:var(--g600);display:flex;align-items:center;justify-content:center;font-size:18px}
.hdr h1{font-family:'Playfair Display',serif;font-size:17px;color:var(--g100)}
.hdr-sub{font-size:10px;color:var(--tx3);margin-top:2px;letter-spacing:.04em}
.hdr-r{display:flex;align-items:center;gap:14px}
.sp{background:var(--card);border:0.5px solid var(--brd2);border-radius:20px;padding:5px 13px;text-align:center}
.sp .n{font-size:17px;font-weight:600}.sp .l{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.05em}
.sp.tot .n{color:var(--g100)}.sp.ok .n{color:var(--g400)}.sp.fv .n{color:var(--r400)}.sp.ch .n{color:var(--a400)}
.live{display:flex;align-items:center;gap:6px;font-size:11px;color:var(--tx3)}
.ldot{width:7px;height:7px;border-radius:50%;background:var(--g400);animation:blink 2s infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.25}}

.body{display:flex;flex:1;overflow:hidden}
.sb{width:265px;flex-shrink:0;background:var(--surf);border-right:0.5px solid var(--brd2);display:flex;flex-direction:column;overflow:hidden}
.sb-sec{padding:9px 14px 5px;font-size:10px;font-weight:600;color:var(--tx3);text-transform:uppercase;letter-spacing:.07em;border-bottom:0.5px solid var(--brd)}

.nlist{padding:0 12px;border-bottom:0.5px solid var(--brd2)}
.ni{display:flex;gap:8px;padding:7px 0;border-bottom:0.5px solid var(--brd);align-items:flex-start}
.ni:last-child{border-bottom:none}
.ndot{width:7px;height:7px;border-radius:50%;margin-top:4px;flex-shrink:0}
.ndot.r{background:var(--r400)}.ndot.a{background:var(--a400)}.ndot.g{background:var(--g400)}
.ntxt{font-size:11px;color:var(--tx);line-height:1.4}.ntm{font-size:10px;color:var(--tx3);margin-top:1px}

.clist{flex:1;overflow-y:auto;padding:4px 6px 8px}
.clist::-webkit-scrollbar{width:3px}.clist::-webkit-scrollbar-thumb{background:var(--g600);border-radius:2px}
.cbtn{width:100%;display:flex;align-items:center;gap:9px;padding:8px 9px;border-radius:8px;border:0.5px solid transparent;background:transparent;cursor:pointer;text-align:left;transition:all .15s;margin-bottom:2px}
.cbtn:hover{background:var(--card);border-color:var(--brd)}
.cbtn.active{background:var(--card);border-color:var(--brd2)}
.av{width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:600;flex-shrink:0}
.av.ok{background:var(--g50);color:var(--g800)}.av.fv{background:var(--r50);color:var(--r800)}.av.ht{background:var(--a50);color:var(--a800)}
.ci{flex:1;min-width:0}.cn{font-size:12px;font-weight:500;color:var(--tx)}.cs{font-size:10px;color:var(--tx3);margin-top:1px}
.ct{font-size:12px;font-weight:600}.ct.ok{color:var(--g400)}.ct.fv{color:var(--r400)}.ct.ht{color:var(--a400)}

.main{flex:1;display:flex;flex-direction:column;overflow:hidden}
.dhdr{padding:11px 20px;border-bottom:0.5px solid var(--brd);display:flex;align-items:center;justify-content:space-between;flex-shrink:0;background:var(--surf)}
.dtit{font-size:15px;font-weight:600;color:var(--tx);display:flex;align-items:center;gap:10px}
.badge{padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600}
.badge.ok{background:var(--g50);color:var(--g800)}.badge.fv{background:var(--r50);color:var(--r800)}.badge.ht{background:var(--a50);color:var(--a800)}

.mrow{display:grid;grid-template-columns:repeat(4,1fr);gap:9px;padding:11px 20px;border-bottom:0.5px solid var(--brd);flex-shrink:0}
.mc{background:var(--card);border:0.5px solid var(--brd);border-radius:8px;padding:9px 13px}
.ml{font-size:10px;color:var(--tx3);margin-bottom:3px}
.mv{font-size:21px;font-weight:600;color:var(--tx)}.mu{font-size:11px;color:var(--tx3);font-weight:400;margin-left:2px}

.tabs{display:flex;background:var(--surf);border-bottom:0.5px solid var(--brd2);flex-shrink:0;padding:0 20px}
.tab{padding:9px 16px;font-size:12px;font-weight:500;color:var(--tx3);cursor:pointer;border:none;background:transparent;border-bottom:2px solid transparent;transition:all .15s}
.tab:hover{color:var(--tx2)}.tab.active{color:var(--g100);border-bottom-color:var(--g400)}

.tc{display:none;flex:1;overflow:hidden;flex-direction:column}.tc.vis{display:flex}

.gp{flex:1;overflow-y:auto;padding:13px 20px 16px;display:grid;grid-template-columns:1fr 1fr;gap:12px}
.gp::-webkit-scrollbar{width:3px}.gp::-webkit-scrollbar-thumb{background:var(--g600);border-radius:2px}
.gc{background:var(--card);border:0.5px solid var(--brd);border-radius:10px;padding:11px 14px}
.gc h3{font-size:11px;font-weight:500;color:var(--tx2);margin-bottom:8px}
.cw{position:relative;width:100%;height:130px}

.mp{flex:1;overflow:hidden}
#map{width:100%;height:100%}
.leaflet-tile{filter:brightness(.6) saturate(.45) hue-rotate(55deg)}
.leaflet-popup-content-wrapper{background:var(--card);color:var(--tx);border:0.5px solid var(--brd2);border-radius:8px;font-family:'Inter',sans-serif;font-size:12px}
.leaflet-popup-tip{background:var(--card)}
</style>
</head>
<body>

<div class="hdr">
  <div class="hdr-l">
    <div class="logo">&#x1F404;</div>
    <div>
      <h1>Surveillance Bétail — LoRaWAN</h1>
      <div class="hdr-sub">INPT · Cloud & IoT 2025/2026 · Données réelles MmCows (NeurIPS 2024)</div>
    </div>
  </div>
  <div class="hdr-r">
    <div class="sp tot"><div class="n" id="st-tot">0</div><div class="l">Total</div></div>
    <div class="sp ok"> <div class="n" id="st-ok">0</div> <div class="l">Saines</div></div>
    <div class="sp fv"> <div class="n" id="st-fv">0</div>  <div class="l">Fièvre</div></div>
    <div class="sp ch"> <div class="n" id="st-ch">0</div>  <div class="l">Chaleurs</div></div>
    <div class="live"><span class="ldot"></span> En ligne · 5 s</div>
  </div>
</div>

<div class="body">

  <div class="sb">
    <div class="sb-sec">&#x1F514; Notifications</div>
    <div class="nlist" id="notifList"></div>
    <div class="sb-sec" style="margin-top:4px">&#x1F404; Troupeau</div>
    <div class="clist" id="cowList"></div>
  </div>

  <div class="main">

    <div class="dhdr">
      <div class="dtit">
        <span id="cowTitle">—</span>
        <span class="badge ok" id="cowBadge">Saine</span>
      </div>
      <div style="font-size:11px;color:var(--tx3)" id="cowScenario"></div>
    </div>

    <div class="mrow">
      <div class="mc"><div class="ml">🌡 Température</div><div class="mv" id="mT">—<span class="mu">°C</span></div></div>
      <div class="mc"><div class="ml">↔ Accél. X</div>    <div class="mv" id="mX">—<span class="mu">g</span></div></div>
      <div class="mc"><div class="ml">↕ Accél. Y</div>    <div class="mv" id="mY">—<span class="mu">g</span></div></div>
      <div class="mc"><div class="ml">⇅ Accél. Z</div>    <div class="mv" id="mZ">—<span class="mu">g</span></div></div>
    </div>

    <div class="tabs">
      <button class="tab active" onclick="showTab('graphs',this)">📈 Graphes</button>
      <button class="tab"        onclick="showTab('map',this)">🗺 Carte GPS</button>
    </div>

    <div class="tc vis" id="tc-graphs">
      <div class="gp">
        <div class="gc"><h3>🌡 Température corporelle (30 mesures)</h3><div class="cw"><canvas id="cTemp"></canvas></div></div>
        <div class="gc"><h3>📊 Accéléromètre X · Y · Z</h3>          <div class="cw"><canvas id="cAccel"></canvas></div></div>
        <div class="gc"><h3>📐 Intensité mouvement |a|</h3>           <div class="cw"><canvas id="cMag"></canvas></div></div>
        <div class="gc"><h3>📍 Distribution température 24 h</h3>     <div class="cw"><canvas id="cHist"></canvas></div></div>
      </div>
    </div>

    <div class="tc" id="tc-map">
      <div class="mp"><div id="map"></div></div>
    </div>

  </div>
</div>

<script>
/* ─── DATA FROM API (REAL DATASETS) ─── */
let COWS_DATA = [];
let selected = null;
let charts = {};
let mapObj = null, mapMarkers = {};
let historyBuffer = {}; // stores last 30 values per cow

const stateLabel = {ok:'Saine', fv:'Fièvre', ht:'Chaleurs'};

function getState(temp, scenario){
  if(temp > 39.5) return 'fv';
  if(scenario === 'heating') return 'ht';
  return 'ok';
}

function genHist(cow){
  const bins=['38.0','38.2','38.4','38.6','38.8','39.0','39.2','39.4','39.6','39.8','40.0','40.2'];
  return bins.map(b=>{
    const d=Math.abs(parseFloat(b)-cow.temp);
    return Math.max(0,Math.round(40*Math.exp(-d*d/0.07)));
  });
}

/* ─── NOTIFICATIONS ─── */
function buildNotifs(cows){
  const n = [];
  cows.forEach(c=>{
    if(c.state==='fv') n.push({dot:'r',text:`${c.id} — fièvre détectée ${c.temp}°C`,time:'maintenant'});
    if(c.state==='ht') n.push({dot:'a',text:`${c.id} — chaleurs en cours`,time:'maintenant'});
  });
  return n.slice(0,8);
}

/* ─── RENDER ─── */
function renderAll(cows){
  if(!cows.length) return;
  if(!selected) selected = cows[0];
  
  /* Stats */
  document.getElementById('st-tot').textContent = cows.length;
  document.getElementById('st-ok').textContent  = cows.filter(c=>c.state==='ok').length;
  document.getElementById('st-fv').textContent  = cows.filter(c=>c.state==='fv').length;
  document.getElementById('st-ch').textContent  = cows.filter(c=>c.state==='ht').length;
  
  /* Notifs */
  const notifs = buildNotifs(cows);
  document.getElementById('notifList').innerHTML = notifs.map(n=>`
    <div class="ni">
      <span class="ndot ${n.dot}"></span>
      <div><div class="ntxt">${n.text}</div><div class="ntm">${n.time}</div></div>
    </div>`).join('');
  
  /* Cow list */
  document.getElementById('cowList').innerHTML = cows.map(c=>`
    <button class="cbtn ${c.id===selected.id?'active':''}" onclick="selectCow('${c.id}')">
      <div class="av ${c.state}">${c.id.substring(0,2)}</div>
      <div class="ci">
        <div class="cn">${c.id}</div>
        <div class="cs">${c.scenario}</div>
      </div>
      <div class="ct ${c.state}">${c.temp}°</div>
    </button>`).join('');
  
  renderDetail(selected);
  buildCharts(selected);
  initMap(cows);
}

function renderDetail(cow){
  document.getElementById('cowTitle').textContent    = cow.id;
  document.getElementById('cowScenario').textContent = 'Scénario : '+cow.scenario;
  const b = document.getElementById('cowBadge');
  b.textContent = stateLabel[cow.state];
  b.className   = 'badge '+cow.state;
  document.getElementById('mT').innerHTML = cow.temp+'<span class="mu">°C</span>';
  document.getElementById('mX').innerHTML = cow.ax+'<span class="mu">g</span>';
  document.getElementById('mY').innerHTML = cow.ay+'<span class="mu">g</span>';
  document.getElementById('mZ').innerHTML = cow.az+'<span class="mu">g</span>';
}

/* ─── HISTORY BUFFER ─── */
function addToHistory(cow){
  if(!historyBuffer[cow.id]) historyBuffer[cow.id] = {t:[],x:[],y:[],z:[],m:[]};
  const h = historyBuffer[cow.id];
  h.t.push(cow.temp); h.x.push(cow.ax); h.y.push(cow.ay); h.z.push(cow.az);
  h.m.push(Math.sqrt(cow.ax*cow.ax + cow.ay*cow.ay + cow.az*cow.az));
  if(h.t.length > 30){ h.t.shift(); h.x.shift(); h.y.shift(); h.z.shift(); h.m.shift(); }
  cow.history = h;
  cow.hist = genHist(cow);
}

/* ─── CHARTS ─── */
const LABELS30 = Array.from({length:30},(_,i)=>i===29?'now':`-${29-i}s`);
const CHARTBASE = {
  responsive:true, maintainAspectRatio:false,
  plugins:{legend:{display:false}},
  elements:{point:{radius:0}},
  animation:{duration:300},
  scales:{
    x:{ticks:{font:{size:9},color:'#5a7a3a',maxTicksLimit:7},grid:{color:'rgba(99,153,34,0.08)'},border:{color:'rgba(99,153,34,0.12)'}},
    y:{ticks:{font:{size:9},color:'#5a7a3a'},              grid:{color:'rgba(99,153,34,0.08)'},border:{color:'rgba(99,153,34,0.12)'}}
  }
};

function stateColor(state){ return state==='fv'?'#E24B4A': state==='ht'?'#EF9F27':'#639922'; }

function buildCharts(cow){
  const histBins=['38.0','38.2','38.4','38.6','38.8','39.0','39.2','39.4','39.6','39.8','40.0','40.2'];
  
  if(charts.t)  charts.t.destroy();
  if(charts.a)  charts.a.destroy();
  if(charts.m)  charts.m.destroy();
  if(charts.h)  charts.h.destroy();

  const h = cow.history;
  const col = stateColor(cow.state);
  const labels = h.t.length === 30 ? LABELS30 : Array.from({length:h.t.length},(_,i)=>i===h.t.length-1?'now':`-${h.t.length-1-i}s`);

  charts.t = new Chart(document.getElementById('cTemp'),{
    type:'line', data:{labels:labels, datasets:[{
      data:h.t, borderColor:col, borderWidth:2, backgroundColor:col+'1a', fill:true, tension:0.4
    }]},
    options:{...CHARTBASE, scales:{...CHARTBASE.scales, y:{...CHARTBASE.scales.y,
      ticks:{...CHARTBASE.scales.y.ticks, callback:v=>v.toFixed(1)+'°'},
      min:Math.min(...h.t)-0.2, max:Math.max(...h.t)+0.2}}}
  });

  charts.a = new Chart(document.getElementById('cAccel'),{
    type:'line', data:{labels:labels, datasets:[
      {data:h.x, borderColor:'#378ADD', borderWidth:1.5, tension:0.3, fill:false, label:'X'},
      {data:h.y, borderColor:'#EF9F27', borderWidth:1.5, tension:0.3, fill:false, label:'Y'},
      {data:h.z, borderColor:'#639922', borderWidth:1.5, tension:0.3, fill:false, label:'Z'},
    ]},
    options:{...CHARTBASE, plugins:{legend:{display:true, position:'top',
      labels:{color:'#8aad62', font:{size:10}, boxWidth:20, padding:10,
        generateLabels:chart=>chart.data.datasets.map((ds,i)=>({text:ds.label, fillStyle:ds.borderColor,
        strokeStyle:ds.borderColor, lineWidth:2, datasetIndex:i}))}}}}
  });

  charts.m = new Chart(document.getElementById('cMag'),{
    type:'line', data:{labels:labels, datasets:[{
      data:h.m, borderColor:'#5DCAA5', borderWidth:2, backgroundColor:'#5DCAA51a', fill:true, tension:0.4
    }]},
    options:{...CHARTBASE}
  });

  charts.h = new Chart(document.getElementById('cHist'),{
    type:'bar', data:{labels:histBins, datasets:[{
      data:cow.hist, backgroundColor:histBins.map(b=>parseFloat(b)>39.5?'#E24B4a99':parseFloat(b)>39.0?'#EF9F2799':'#63992299'),
      borderColor:'transparent', borderRadius:3
    }]},
    options:{...CHARTBASE, scales:{...CHARTBASE.scales,
      x:{...CHARTBASE.scales.x, ticks:{...CHARTBASE.scales.x.ticks, maxRotation:45}},
      y:{...CHARTBASE.scales.y, ticks:{...CHARTBASE.scales.y.ticks, callback:v=>v}}}}
  });
}

/* ─── MAP ─── */
function initMap(cows){
  if(!mapObj){
    mapObj = L.map('map').setView([33.5731,-7.5898],15);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'© OSM | INPT'}).addTo(mapObj);
  }
  const colors = {ok:'#639922', fv:'#E24B4A', ht:'#EF9F27'};
  cows.forEach(cow=>{
    const c = colors[cow.state]||'#639922';
    if(mapMarkers[cow.id]){
      mapMarkers[cow.id].setLatLng([cow.lat,cow.lon]);
      mapMarkers[cow.id].setStyle({fillColor:c, color: cow.id===selected.id?'#fff':'#1c2a17', weight: cow.id===selected.id?3:1.5});
    } else {
      mapMarkers[cow.id] = L.circleMarker([cow.lat,cow.lon],{
        radius:9, fillColor:c, color:cow.id===selected.id?'#fff':'#1c2a17',
        weight:cow.id===selected.id?3:1.5, fillOpacity:.9
      }).addTo(mapObj);
      mapMarkers[cow.id].bindPopup(`<b style="color:${c}">${cow.id}</b><br>🌡 ${cow.temp} °C<br>${stateLabel[cow.state]}`);
    }
    if(cow.id===selected.id) mapMarkers[selected.id].openPopup();
  });
}

/* ─── SELECT ─── */
function selectCow(id){
  selected = COWS_DATA.find(c=>c.id===id);
  if(!selected) return;
  renderAll(COWS_DATA);
}

/* ─── TABS ─── */
function showTab(name, btn){
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.tc').forEach(t=>t.classList.remove('vis'));
  btn.classList.add('active');
  document.getElementById('tc-'+name).classList.add('vis');
  if(name==='map') setTimeout(()=>mapObj&&mapObj.invalidateSize(),50);
}

/* ─── FETCH REAL DATA ─── */
function fetchRealData(){
  fetch('/api/cows')
    .then(r=>r.json())
    .then(data=>{
      if(!data || !data.length) return;
      COWS_DATA = data.map(d=>({
        ...d,
        state: getState(d.temp, d.scenario),
        temp: d.temp,
        history: {t:[],x:[],y:[],z:[],m:[]},
        hist: []
      }));
      COWS_DATA.forEach(c=>addToHistory(c));
      if(!selected && COWS_DATA.length) selected = COWS_DATA[0];
      renderAll(COWS_DATA);
    });
}

/* ─── INIT ─── */
fetchRealData();
setInterval(fetchRealData, 5000);
</script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(HTML)

@app.route('/api/cows')
def api_cows():
    try:
        with open('data.json', 'r') as f:
            return jsonify(json.load(f))
    except:
        return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)