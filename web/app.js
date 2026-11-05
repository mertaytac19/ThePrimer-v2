/* The Primer v2 — oyun, davranış ölçümü, gerçek ONNX inference ve gönüllü veri kaydı. */
'use strict';
const $ = id => document.getElementById(id);
const FEATURES = ['karar_suresi_sn', 'onceki_hata_sayisi', 'karar_degistirme_sayisi', 'sahne_zorlugu', 'tereddut_suresi_sn'];
const CSV_FIELDS = ['session_id', ...FEATURES, 'yardim_etkisi', 'kaynak'];
const MODEL_BASE = new URL(document.querySelector('meta[name="primer-model-base"]').content, document.baseURI);
const CONFIG_URL = new URL('config.json', MODEL_BASE).href;
const MODEL_URL = new URL('model.onnx', MODEL_BASE).href;
const ORT_CDN = 'https://cdn.jsdelivr.net/npm/onnxruntime-web@1.22.0/dist/ort.min.js';

const scenes = [
  {id:1,title:'İlk Gün — Sisteme Giriş',difficulty:1,story:'Üretim ortamına ilk kez giriyorsun. Erişim denetimleri doğru yapılandırılmadıysa her şey tehlikede.',hint:'En az yetki ilkesi ve çok faktörlü kimlik doğrulamayı düşün.',options:[['Yetkilerimi ve kimlik doğrulamayı kontrol ederim',true],['Tüm ekibe yönetici yetkisi veririm',false],['Güvenlik uyarılarını kapatırım',false]]},
  {id:2,title:'İlk Hata — Bug Tespiti',difficulty:2,story:'Giriş servisinde NullPointerException oluştu. Kullanıcılar oturum açamıyor.',hint:'Stack trace, hatanın oluştuğu satırı ve null referansı gösterir.',options:[['Logları ve stack trace’i inceleyip hatayı yeniden üretirim',true],['Hata mesajını gizlerim',false],['Sunucuyu sebepsiz yere sürekli yeniden başlatırım',false]]},
  {id:3,title:'Algoritma Krizi',difficulty:3,story:'Arama işlevi veri büyüdükçe çok yavaşlıyor. Önce algoritmik darboğazı belirlemelisin.',hint:'Profil çıkar; O(n²) yerine uygun veri yapısı veya daha iyi karmaşıklık ara.',options:[['Profil çıkarıp algoritma ve veri yapısını iyileştiririm',true],['Kodu ölçmeden daha büyük sunucu kiralarım',false],['Yalnızca kod yorumlarını silerim',false]]},
  {id:4,title:'Veritabanı Problemi',difficulty:3,story:'Yük altında veritabanı bağlantıları zaman aşımına uğruyor. Sorguların bazıları kilitleniyor.',hint:'Yavaş sorgu günlüğü, indeksler ve bağlantı havuzu kullanımını kontrol et.',options:[['Yavaş sorguları, kilitleri ve bağlantı havuzunu ölçerim',true],['Tüm tabloları silerim',false],['Hatalı sorguları hiçbir ölçüm yapmadan tekrarlatırım',false]]},
  {id:5,title:'Güvenlik Açığı',difficulty:4,story:'Kullanıcı yorumlarında kalıcı XSS riski tespit edildi. Bir saldırgan tarayıcıda betik çalıştırabiliyor.',hint:'Çıktıyı bağlama uygun kodla; DOM’a HTML olarak güvenilmez veri yerleştirme.',options:[['Güvensiz HTML eklemeyi kaldırır, çıktı kodlaması uygularım',true],['HTTPS’i kapatırım',false],['Kullanıcıların dikkatli olmasını söyleyip kodu değiştirmem',false]]},
  {id:6,title:'Test Laboratuvarı',difficulty:3,story:'Yeni sürümün güvenli dağıtılabilmesi için otomatik testlere ve doğrulanabilir kabul kriterlerine ihtiyacın var.',hint:'Birim, entegrasyon ve uçtan uca test farklı seviyeleri sınar.',options:[['Tekrarlanabilir testleri CI sürecine eklerim',true],['Testleri atlayıp doğrudan yayınlarım',false],['Sadece mutlu yol senaryosunu gözle kontrol ederim',false]]},
  {id:7,title:'Kritik Sistem Kararı',difficulty:5,story:'Milyonlarca kullanıcı bağlıyken yeni bir sürümü güvenle devreye alman gerekiyor.',hint:'Canary dağıtımı ve hızlı rollback, olası arızanın etkisini sınırlayabilir.',options:[['Önce küçük kullanıcı grubunda canary dağıtımı yaparım',true],['Tüm kullanıcılara test etmeden aynı anda açarım',false],['Geri dönüş planı hazırlamam',false]]},
  {id:8,title:'Son Vardiya — Üretim Alarmı',difficulty:5,story:'Yayın sonrası hata oranı kritik eşiği aştı. Kullanıcı verilerini koruyarak hızlı karar vermelisin.',hint:'İzleme verilerine bak ve doğrulanmış güvenli sürüme geri dönmeyi değerlendir.',options:[['Ölçümlere göre rollback yapar, kök nedeni incelerim',true],['Bütün izleme uyarılarını sustururum',false],['Kanıtsız şekilde veritabanını sıfırlarım',false]]}
];

let session = null;
let model = null, config = null, modelError = '', ortReady = false;
let inFlight = false, autoTimer = null, loadingPromise = null;
let generation = 0;
const ms = () => performance.now();
const secs = x => Math.max(0, Math.round(x / 10) / 100);
const freshSession = mode => ({
  mode, id:(globalThis.crypto && crypto.randomUUID ? crypto.randomUUID() : 'session-'+Date.now()+'-'+Math.floor(Math.random()*1e8)),
  sceneIndex:0, sceneStarted:0, firstSelectedAt:null, selected:-1, changes:0,
  errors:0, finished:0, hintUsed:false, preProbability:null,
  records:[], history:[], exported:false, final:false, locked:false
});

function setStatus(text,level='') {
  const el=$('model-status'); el.textContent=text; el.className='status '+level;
}
function loadOrtScript() {
  if(window.ort) return Promise.resolve();
  return new Promise((resolve,reject)=>{
    const script=document.createElement('script'); script.src=ORT_CDN; script.async=true;
    let done=false; const timer=setTimeout(()=>finish(new Error('ONNX Runtime yüklenmesi zaman aşımına uğradı')),12000);
    function finish(err){if(done)return;done=true;clearTimeout(timer);err?reject(err):resolve();}
    script.onload=()=> window.ort?finish():finish(new Error('ONNX Runtime tanımlanmadı'));
    script.onerror=()=>finish(new Error('ONNX Runtime CDN erişim hatası'));
    document.head.appendChild(script);
  });
}
async function loadModel() {
  if(loadingPromise)return loadingPromise;
  loadingPromise=(async()=>{
    try {
      setStatus('Model yükleniyor…');
      await loadOrtScript();
      const response=await fetch(CONFIG_URL,{cache:'no-store'});
      if(!response.ok)throw new Error('config.json HTTP '+response.status);
      const loadedConfig=await response.json();
      const names=loadedConfig.features.map(f=>f.name);
      if(names.length!==FEATURES.length||FEATURES.some((x,i)=>x!==names[i]))throw new Error('Model özellik sözleşmesi farklı');
      const loadedModel=await ort.InferenceSession.create(MODEL_URL,{executionProviders:['wasm']});
      model=loadedModel; config=loadedConfig; ortReady=true; modelError='';
      const status=config.evaluation_status==='production_verified'?'doğrulanmış':'deneysel / doğrulanmamış';
      setStatus('Model yüklendi · '+status,'ok');
    }catch(err){ortReady=false;model=null;modelError=String(err&&err.message||err);setStatus('Model yüklenemedi; oyun modelsiz çalışabilir: '+modelError,'bad');}
    updateDebug();
  })();
  return loadingPromise;
}
function threshold(){return typeof config?.decision_threshold==='number'?config.decision_threshold:0.6;}
async function runInference(features){
  if(!ortReady||!model||!config)return null;
  try{
    const values=config.features.map(f=>Number(features[f.name]));
    if(values.some(v=>!Number.isFinite(v)||v<0))throw new Error('Geçersiz model girdisi');
    const names=model.inputNames||['input'];
    const t=new ort.Tensor('float32',Float32Array.from(values),[1,values.length]);
    const out=await model.run({[names[0]]:t});
    const posIndex=(config.classes||['0','1']).map(String).indexOf('1');
    if(posIndex<0)throw new Error('Pozitif sınıf tanımlı değil');
    const probs=out.probabilities||Object.values(out).find(v=>v?.data?.length>=2);
    if(!probs)throw new Error('Olasılık çıktısı bulunamadı');
    let p;
    if(probs.data?.length>=2)p=Number(probs.data[posIndex]);
    else if(Array.isArray(probs)&&probs[0] instanceof Map)p=Number(probs[0].get(1));
    else throw new Error('Tanımlanmayan olasılık biçimi');
    if(!Number.isFinite(p)||p<0||p>1)throw new Error('Geçersiz olasılık');
    return p;
  }catch(err){modelError='Çıkarım hatası: '+(err?.message||err);setStatus(modelError,'bad');return null;}
}
const currentScene=()=>scenes[session.sceneIndex];
function getFeatureSnapshot(){
  const now=ms();
  return {
    karar_suresi_sn:secs(now-session.sceneStarted),
    onceki_hata_sayisi:session.errors, // mevcut kararın sonucu henüz bilinmiyor
    karar_degistirme_sayisi:session.changes,
    sahne_zorlugu:currentScene().difficulty,
    tereddut_suresi_sn:session.firstSelectedAt===null?0:secs(now-session.firstSelectedAt)
  };
}
function updateDebug(snapshot=null, prob=null){
  const s=session;
  const lines=[
    'ONNX: '+(ortReady?'YÜKLENDİ':'YÜKLENMEDİ / YÜKLENİYOR'),
    'Model: '+(config?.title||'—'),
    'Model durumu: '+(config?.evaluation_status||'—'),
    'Model bilgisi: '+(modelError||'hata yok'),
    'Özellik sırası: '+FEATURES.join(', '),
    'Eşik: '+threshold(),
    'Aktif mod: '+(s?.mode||'seçilmedi')
  ];
  if(s){
    lines.push('Oturum: '+s.id);
    lines.push('Sahne: '+(s.sceneIndex+1)+'/8 · tamamlanan karar: '+s.finished);
    const last=s.history[s.history.length-1];
    const input=snapshot||last?.features;
    if(input)for(const key of FEATURES)lines.push(key+': '+input[key]);
    const p=prob??last?.probability??s.preProbability;
    lines.push('AI olasılığı: '+(p===null||p===undefined?'Henüz yok':p.toFixed(8)));
    lines.push('AI kararı: '+(p==null?'—':p>=threshold()?'İpucu öner':'İpucu önermez'));
    lines.push('Kaydedilmiş veri satırı: '+s.records.length);
  }
  $('debug-output').textContent=lines.join('\n');
}
function start(mode){
  session=freshSession(mode); generation++;
  $('mode-picker').hidden=true; $('game').hidden=false;
  $('mode-label').textContent=mode==='collection'?'Veri Toplama Modu · İpuçları kapalı':'Oyun modu · Adaptif ipuçları';
  $('export-section').hidden=true; $('summary').hidden=true;
  renderScene();
}
function renderScene(){
  clearTimeout(autoTimer);inFlight=false;
  const s=session, scene=currentScene();
  if(!scene){showEnding();return;}
  const gen=++generation;
  s.sceneStarted=ms();s.firstSelectedAt=null;s.selected=-1;s.changes=0;s.hintUsed=false;s.preProbability=null;s.locked=false;
  $('scene-title').textContent=scene.title;$('story').textContent=scene.story;
  $('difficulty').textContent='Zorluk '+scene.difficulty+'/5';
  $('scene-count').textContent='Sahne '+(s.sceneIndex+1)+' / 8';
  $('progress').style.width=(s.finished/scenes.length*100)+'%';
  document.querySelector('.progress-track').setAttribute('aria-valuenow',String(s.finished/scenes.length*100));
  $('feedback').textContent='';$('self-report').hidden=true;$('summary').hidden=true;
  $('confirm').disabled=true;$('confirm').hidden=false;$('scene').hidden=false;
  $('hint-area').hidden=s.mode==='collection';
  $('hint-text').hidden=true;$('hint-text').textContent='';$('hint-btn').disabled=false;
  $('options').replaceChildren();
  scene.options.forEach(([label],idx)=>{
    const btn=document.createElement('button');btn.type='button';btn.textContent=label;btn.dataset.cy='option-'+idx;
    btn.addEventListener('click',()=>{
      if(s.locked)return;
      if(s.firstSelectedAt===null)s.firstSelectedAt=ms();
      else if(s.selected!==-1 && s.selected!==idx)s.changes++;
      s.selected=idx;
      $('options').querySelectorAll('button').forEach((b,i)=>{b.classList.toggle('selected',i===idx);b.setAttribute('aria-pressed',String(i===idx));});
      $('confirm').disabled=false;
      updateDebug(getFeatureSnapshot());
      if(s.mode==='normal')evaluateAdaptive(gen);
    });
    btn.setAttribute('aria-pressed','false');$('options').appendChild(btn);
  });
  if(s.mode==='normal')autoTimer=setTimeout(()=>evaluateAdaptive(gen),6000);
  updateDebug();
}
async function evaluateAdaptive(gen){
  const s=session;
  if(!s||s.mode!=='normal'||s.locked||s.hintUsed||!ortReady||gen!==generation||inFlight)return;
  inFlight=true;
  const inputs=getFeatureSnapshot();
  const p=await runInference(inputs);
  inFlight=false;
  if(gen!==generation||s.locked||p===null)return;
  s.preProbability=p;
  updateDebug(inputs,p);
  if(p>=threshold())showHint('Model, bu sahnede destek öneriyor.',p,'adaptive');
}
function showHint(prefix,prob=null,source='manual'){
  const scene=currentScene();
  session.hintUsed=true;
  const el=$('hint-text');el.hidden=false;
  el.textContent=prefix+' '+scene.hint+(prob===null?'':' (AI: '+(prob*100).toFixed(1)+'%)');
  $('hint-btn').disabled=true;
  el.dataset.hintSource=source;
}
$('hint-btn').addEventListener('click',async()=>{
  if(!session||session.mode==='collection'||session.locked)return;
  // Kullanıcının kendi isteği AI kararı değildir; iki mekanizma ayrı raporlanır.
  if(!ortReady){showHint('Manuel ipucu (model şu anda yok):');return;}
  const gen=generation;
  const input=getFeatureSnapshot();
  const prob=await runInference(input);
  if(gen!==generation||session.locked)return;
  session.preProbability=prob;
  showHint('İstediğin manuel ipucu:',prob,'manual');updateDebug(input,prob);
});
function saveDecision(row,selectedCorrect,prob){
  session.history.push({features:row,correct:selectedCorrect,probability:prob,hintUsed:session.hintUsed,sceneId:currentScene().id});
  session.finished++;
  if(!selectedCorrect)session.errors++;
  updateDebug(row,prob);
}
function advanceScene(){
  session.sceneIndex++;
  setTimeout(()=>renderScene(),450);
}
$('confirm').addEventListener('click',async()=>{
  const s=session;
  if(!s||s.locked||s.selected===-1)return;
  s.locked=true;clearTimeout(autoTimer);$('confirm').disabled=true;
  const row=getFeatureSnapshot();
  const correct=currentScene().options[s.selected][1];
  if(s.mode==='collection'){
    s.pending={row,correct};
    $('self-report').hidden=false;
    $('feedback').textContent='Kararın alındı. Lütfen yardım ihtiyacını değerlendir.';
    return;
  }
  const gen=generation;
  const prob=await runInference(row);
  if(gen!==generation)return;
  saveDecision(row,correct,prob);
  $('feedback').textContent=(correct?'Doğru yaklaşım. ':'Bu karar riskli. ')+
    'Karar süresi: '+row.karar_suresi_sn+' sn · Tereddüt: '+row.tereddut_suresi_sn+
    ' sn · Karar değiştirme: '+row.karar_degistirme_sayisi+
    (prob===null?' · Model tahmini alınamadı.':' · AI yardım olasılığı: '+(100*prob).toFixed(2)+'%');
  advanceScene();
});
function submitSelfReport(value){
  if(!session||session.mode!=='collection'||!session.pending)return;
  const {row,correct}=session.pending;session.pending=null;
  session.records.push({session_id:session.id,...row,yardim_etkisi:value,kaynak:'gercek'});
  session.exported=false;
  saveDecision(row,correct,null);
  $('self-report').hidden=true;
  $('export-section').hidden=false;
  $('export-count').textContent='Kaydedilen karar: '+session.records.length;
  $('feedback').textContent='Öz değerlendirmen kaydedildi. '+(correct?'Karar doğru.':'Bu karar hatalıydı.')+' Sonraki sahneye geçiliyor.';
  advanceScene();
}
$('need-help').addEventListener('click',()=>submitSelfReport(1));
$('no-help').addEventListener('click',()=>submitSelfReport(0));
function showEnding(){
  session.final=true;$('scene').hidden=true;$('self-report').hidden=true;
  $('progress').style.width='100%';$('scene-count').textContent='Tamamlandı';
  const rescued=session.errors<=3 && session.history[session.history.length-1]?.correct;
  const title=rescued?'Sistem kurtarıldı!':'Sistem krizi büyüdü';
  const box=$('summary');box.hidden=false;
  box.replaceChildren();
  const h=document.createElement('h2');h.textContent=title;box.appendChild(h);
  const p=document.createElement('p');p.textContent='Karar: '+session.finished+' · Hatalı karar: '+session.errors+
    ' · Ortalama karar süresi: '+(session.history.reduce((sum,x)=>sum+x.features.karar_suresi_sn,0)/session.finished).toFixed(2)+' sn';box.appendChild(p);
  if(session.mode==='collection'){
    const note=document.createElement('p');note.textContent='Bu oturumdan '+session.records.length+' satır toplandı. Teslim için CSV indir ve sonraki gerçek oturumlarla birleştir.';box.appendChild(note);
  }
  updateDebug();
}
function csvEncode(value){const s=String(value??'');return /[",\r\n]/.test(s)?'"'+s.replace(/"/g,'""')+'"':s;}
function exportCSV(){
  if(!session||session.mode!=='collection'||!session.records.length)return;
  const text=[CSV_FIELDS.join(','),...session.records.map(r=>CSV_FIELDS.map(k=>csvEncode(r[k])).join(','))].join('\r\n')+'\r\n';
  const blob=new Blob(['\uFEFF'+text],{type:'text/csv;charset=utf-8'});
  const url=URL.createObjectURL(blob);
  const a=document.createElement('a');a.href=url;a.download='oturum-'+session.id+'.csv';document.body.appendChild(a);a.click();a.remove();
  setTimeout(()=>URL.revokeObjectURL(url),2000);
  session.exported=true;
  $('export-count').textContent='CSV indirildi · '+session.records.length+' karar';
}
$('export-csv').addEventListener('click',exportCSV);
function resetGame(){
  if(session?.mode==='collection'&&session.records.length&&!session.exported&&
    !confirm('İndirilmemiş veri var. Yeni oturumda kaybolacak. Devam edilsin mi?'))return;
  generation++;clearTimeout(autoTimer);session=null;
  $('game').hidden=true;$('mode-picker').hidden=false;
}
$('reset').addEventListener('click',resetGame);
$('normal-mode').addEventListener('click',()=>start('normal'));
$('collection-mode').addEventListener('click',()=>{
  if(confirm('Bu mod kişisel veri toplamaz. Karar davranışların ve kendi yardım ihtiyacı yanıtların CSV olarak yalnızca bu tarayıcıda hazırlanacak. Devam etmek istiyor musun?'))start('collection');
});
window.primerRunInference=runInference; // Cypress gerçek model sonucunu buradan okur
window.primerModelLoaded=()=>ortReady;
window.primerTestState=()=> session?{
  scene:session.sceneIndex+1,changes:session.changes,errors:session.errors,records:session.records.length,
  mode:session.mode,finished:session.finished,last:session.history.at(-1)||null
}:null;
loadModel(); // arayüz model indirilmeden de açılabilir
updateDebug();
