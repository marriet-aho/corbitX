/* ===================== READ THE WHOLE PAGE =====================
   Appended inside Kukua's script by tools/merge-readiness.py. Kukua reads every part of the page in order, from the hero
   to the footer, scrolling to each part as she goes. Every clip is a pre-recorded MP3 (see audioFor). */
function sp(t){   // text as it is spoken (also the key under which a clip is stored)
  const M={Jan:"January",Feb:"February",Mar:"March",Apr:"April",Jun:"June",Jul:"July",Aug:"August",Sep:"September",Sept:"September",Oct:"October",Nov:"November",Dec:"December",
           Mon:"Monday",Tue:"Tuesday",Wed:"Wednesday",Thu:"Thursday",Fri:"Friday",Sat:"Saturday",Sun:"Sunday"};
  return String(t).replace(/<[^>]+>/g,"").replace(/\bFAQs\b/g,"frequently asked questions").replace(/\bFAQ\b/g,"F A Q")
    .replace(/\bBOSs\b/g,"Branch Operations Supervisors").replace(/\bGL\b/g,"G L").replace(/\bEOD\b/g,"end of day").replace(/\bCIF\b/g,"C I F")
    .replace(/\b(Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept?|Oct|Nov|Dec|Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b/g,m=>M[m])
    .replace(/(\d)\s*%/g,"$1 percent").replace(/(\d)\+/g,"$1 plus").replace(/°/g," degree").replace(/&/g,"and").replace(/[→·]/g,",")
    .replace(/\s[–—]\s/g,", ").replace(/\.{2,}/g,".").replace(/\s+/g," ").trim();
}
function audioNameFor(text){
  const m=LISTS.KukuaMessages.find(x=>x.Text===text),i=STAGES.findIndex(x=>x.KukuaSays===text);
  return m?m.Key:i>=0?"stage"+(i+1):vh(sp(text));
}

const RCD=()=>window.CXJ_RC||{};
function segs(){
  const r=RCD(),C=r.CONFIG||{},P=r.POSTERS||[],out=[];
  const add=(cap,sel,texts,pre,alts)=>out.push({cap,sel,texts,pre,alts});
  const fm=(d,o)=>r.fmt?r.fmt(d,o):"";
  const N=n=>typeof n==="number"?n.toLocaleString("en"):n;
  const catName=id=>((r.CATS||[]).find(c=>c.id===id)||{}).name||"";

  /* ---- Readiness Centre: top */
  add("Welcome to the Readiness Centre","#home",["Welcome to the Corbit X Readiness Centre. Preparing our people, processes and branches for the future of banking. Use the menu at the top of the page to jump to the staff guides, Kukua's journey, the Knowledge Hub, and what's coming."]);
  add("Countdown to go-live",".countdown",["Corbit X is expected to go live on "+fm(r.GO,{weekday:"long",day:"numeric",month:"long",year:"numeric"})+". The countdown shows the days, hours, minutes and seconds remaining. Every day counts, so let's get ready together."]);
  const kp=(C.kpis||[]).map(k=>k.v==="days"?"The dashboard also shows the number of days left to go-live.":k.l+": "+k.v+(k.s==="%"?" percent":"")+".").join(" ");
  add("Readiness dashboard",".dash .ready",["Here is the readiness dashboard. "+(C.workstreams||[]).map(w=>w[0]+", "+w[1]+" percent.").join(" ")+" "+kp+(C.dataIsIllustrative?" These figures are illustrative until they come from the programme tracker.":"")]);
  if(C.announcement)add("Latest announcement",".annc",["Latest announcement. "+C.announcement.title+". "+C.announcement.body]);
  const potw=p=>"Poster of the week. "+p.title+". "+p.short+" "+catName(p.cat)+".";
  add("Poster of the week","#featCard",[document.getElementById("featTitle")?"Poster of the week. "+document.getElementById("featTitle").textContent+". "+document.getElementById("featText").textContent:""],null,P.map(p=>[potw(p)]));
  add("One Journey. One Platform. One Corbit X.",".band:not(.dark)",["One Journey. One Platform. One Corbit X."]);

  /* ---- Kukua: welcome, highlights, journey */
  add("Meet Kukua","#welcome",[msg("welcome").Text]);
  const hl=(LISTS.Highlights||[]).map(g=>g.Group+": "+g.Items.map(i=>N(i.Value)+(i.Suffix==="+"?" plus":i.Suffix==="%"?" percent":i.Suffix||"")+" "+i.Label).join("; ")+".").join(" ");
  add("Highlights so far","#highlights",[intro("highlights"),"Highlights so far. "+hl]);
  add("Kukua's journey","#kjourney",[msg("journeyIntro").Text]);
  add("Start of the journey","#kjourney",[msg("start").Text],()=>goTo(0));
  STAGES.forEach((s,i)=>add("Stop "+(i+1)+": "+s.Title,"#kjourney",["Stop "+(i+1)+". "+s.Title+".",s.KukuaSays],()=>goTo(i+1)));
  add("End of the journey","#kjourney",[msg("finish").Text],()=>goTo(cards.length-1));

  /* ---- Kukua: big changes, staff, tips, updates, training, next */
  const cust=(LISTS.CustomerChanges||[]).map(c=>c.Title+": "+c.Points.join(", ")+".").join(" ");
  add("Big changes for customers","#changes .ch-band",[intro("changes"),"For customers. "+cust]);
  const stf=(LISTS.StaffChanges||[]).map(s=>s.Title+": today, "+s.Today+"; with Corbit X, "+s.CX+". The gain: "+s.Gain+".").join(" ");
  add("What's in it for staff","#changes .staff",[intro("staff"),"What's in it for staff. "+stf]);
  add("Kukua's daily tip","#corner .tip",["A little something for today. "+(tips[ti]||"")],null,(LISTS.DailyTips||[]).map(t=>["A little something for today. "+t]));
  const gw=g=>"Guide of the week. "+g.Title+". Kukua's take: "+g.KukuaCommentary;
  add("Guide of the week","#feat",[gw(FEAT)],null,(LISTS.FeaturedGuides||[]).map(g=>[gw(g)]));
  add("Latest updates","#corner .news",["Latest updates. "+(LISTS.Announcements||[]).map(a=>a.Title+". "+a.Body).join(" ")]);
  const vids=(LISTS.TrainingMedia||[]).filter(m=>m.Type==="Video"),pics=(LISTS.TrainingMedia||[]).filter(m=>m.Type==="Picture");
  add("End-user training","#training",[intro("training"),"End-user training. Videos: "+vids.map(v=>v.Title).join("; ")+". Pictures: "+pics.map(v=>v.Title).join("; ")+"."+(vids.some(v=>!v.Url)?" Some videos are marked coming soon.":"")]);
  add("What's next","#next",[intro("next"),"What's next. "+(LISTS.WhatsNext||[]).map(n=>n.Label+": "+n.Title+". "+n.Text).join(" ")]);

  /* ---- Readiness Centre: guides, timeline, hub, coming */
  add("Staff guides","#guides .sec-head",["Corbit X Staff Guides. Clear, practical guidance for every customer moment around go-live. Tap any poster to open it full size and read the detailed guidance."]);
  (r.CATS||[]).forEach((c,k)=>add("Staff guides: "+c.name,()=>document.querySelectorAll("#groups > *")[k],[c.name+". "+c.desc+" "+P.filter(p=>p.cat===c.id).map(p=>p.title+". "+p.short).join(" ")]));
  add("Our key messages",".marquee-wrap",["Our key messages. "+(r.mq||[]).join(" ")]);
  add("Programme timeline","#journey .sec-head",["The road to go-live. Six phases take us from awareness to a stable new platform. Select a phase to see what it means for you and the materials that support it."]);
  (r.PHASES||[]).forEach((p,i)=>add("Phase "+(i+1)+": "+p.n,"#journey .tl",["Phase "+(i+1)+", "+p.n+". "+p.when+". "+p.d+" What to focus on: "+p.f.join("; ")+"."],()=>r.showPhase(i)));
  add("Preparing today for tomorrow",".band.dark",["Preparing today for tomorrow's banking experience."]);
  add("Knowledge Hub","#hub .sec-head",["Corbit X Knowledge Hub. Everything you need, in one place. Answers, training, quick references and key dates, so you can serve customers with confidence from day one. The hub has seven tabs: frequently asked questions, training videos, staff guides, quick reference cards, project updates, key dates and milestones, and support contacts."]);
  const hubSel="#hub .hub";
  (r.FAQS||[]).forEach((f,k)=>add("FAQ "+(k+1)+" of "+r.FAQS.length,hubSel,["Frequently asked question. "+f[0]+" "+f[1]],()=>{r.showHub("faq");document.querySelectorAll("#hubPanel details").forEach((d,j)=>{d.open=j===k})}));
  add("Training videos",hubSel,["Training videos. Short, focused videos to build your confidence in Corbit X. "+(r.VIDEOS||[]).map(v=>v[0]+". "+v[1]+".").join(" ")+" Links open in the learning platform once published."],()=>r.showHub("videos"));
  add("Staff guides tab",hubSel,["Staff guides. All six campaign guides. Open any guide for the full poster and detailed guidance. The guides are: "+P.map(p=>p.title).join("; ")+"."],()=>r.showHub("guides"));
  add("Quick reference cards",hubSel,["Quick reference cards. The essentials at a glance, for the counter and the back office. "+(r.QRC||[]).map(q=>q[0]+": "+q[1].map(x=>x[1]).join("; ")+".").join(" ")],()=>r.showHub("qrc"));
  add("Project updates",hubSel,["Project updates. The latest news from the Corbit X programme. "+(r.UPDATES||[]).map(u=>u[1]+". "+u[2]).join(" ")],()=>r.showHub("updates"));
  add("Key dates and milestones",hubSel,["Key dates and milestones. Calculated from the expected go-live date of "+fm(r.GO,{weekday:"long",day:"numeric",month:"long",year:"numeric"})+". "+(r.DATES||[]).map(d=>d[0]+": "+d[1]+". "+d[2]).join(" ")+" Dates will update automatically once the go-live date is confirmed."],()=>r.showHub("dates"));
  add("Support contacts",hubSel,["Support contacts. Not sure? Pause, check, and reach out. Help is close by. You can contact: "+(r.CONTACTS||[]).map(c=>c[1]+", for "+c[2].charAt(0).toLowerCase()+c[2].slice(1)).join("; ")+". Contact details are shown on the page."],()=>r.showHub("contacts"));
  add("What's coming","#coming .sec-head",["Coming to Corbit X. A platform built for what's next. Corbit X is more than a system change. Here's what it will make possible for our customers and for us."]);
  add("What Corbit X will bring","#capGrid",["What Corbit X will bring. "+(r.CAPS||[]).map(c=>c[1]+". "+c[2]).join(" ")]);

  /* ---- closing */
  add("Kukua's closing message","#closing",[msg("closing").Text,"One Team. One Journey. One Corbit X."]);
  add("Together we are ready","section.final",["Together we are ready for Corbit X. Read the guides, complete your training, and bring the same warm welcome to every customer through go-live and beyond. Here for your journey. Fidelity Bank. Believe with us."]);
  return out;
}
/* every clip that can be spoken (used at build time to record the voice) */
window.CXJ_CLIPS=function(){
  const seen={},list=[];
  segs().forEach(s=>[s.texts].concat(s.alts?s.alts:[]).forEach(arr=>arr.forEach(t=>{if(!t)return;const n=audioNameFor(t);if(!seen[n]){seen[n]=1;list.push({name:n,say:(LISTS.KukuaMessages.some(x=>x.Text===t)||STAGES.some(x=>x.KukuaSays===t))?t:sp(t)})}})));
  return list;
};

let tourToken=0,reading=null;
V.tour=false;V.tourDone=false;
function setReading(el){if(reading)reading.classList.remove("cx-reading");reading=el;if(el)el.classList.add("cx-reading")}
function cancelTour(){tourToken++;V.tour=false;setReading(null)}
function startTour(i){cancelTour();V.enabled=true;V.muted=false;const tok=++tourToken,list=segs().filter(s=>s.texts.some(t=>!!t));V.tour=true;V.tourDone=false;playSeg(list,i||0,0,tok)}
function playSeg(list,i,j,tok){
  if(tok!==tourToken)return;
  if(i>=list.length){endTour();return}
  const s=list[i],texts=s.texts.filter(t=>!!t);
  if(j>=texts.length){playSeg(list,i+1,0,tok);return}
  if(j===0){
    const el=typeof s.sel==="function"?s.sel():document.querySelector(s.sel);
    if(s.pre)try{s.pre()}catch(e){}
    if(el){setReading(el);el.scrollIntoView({behavior:reduced?"auto":"smooth",block:"start"})}
  }
  const t=texts[j];
  narrate("Reading: "+s.cap,audioFor(t),true);
  V.after=()=>playSeg(list,i,j+1,tok);
}
function endTour(){
  V.tour=false;V.tourDone=true;setReading(null);
  const m="That's the whole page. Tap play and I'll read it again from the top.";
  $("#bText").textContent=m;$("#dText").textContent=m;
}
