'use strict';
const translations = {
 de: {
  navDashboard:'Dashboard',navIndustry:'Energieanalysen',navApproach:'Methodik',photoCaption:'WIND · SOLAR · STROMNETZE',platform:'ENERGY MARKET INTELLIGENCE',howitworks:'Methodik ↗',heroEyebrow:'ENERGIEDATEN AUS DEUTSCHLAND · ÖFFENTLICHE QUELLEN',heroTitle:'Energie verstehen.<br><span>Märkte intelligent analysieren.</span>',heroDescription:'Strommarktanalyse und transparente Preisprognosen – mit realen Daten der Bundesnetzagentur und nachvollziehbaren Modellen.',explore:'Dashboard ansehen',source:'Offizielle Datenquelle',overview:'MARKTÜBERSICHT',dashboard:'Deutschland im Überblick',loading:'Lade Daten …',ready:'Daten geladen',stale:'Daten möglicherweise veraltet',unavailable:'Keine Daten',latest:'Letzter Strompreis',average:'Ø Preis · 24 Stunden',low:'Minimum · 24 Stunden',high:'Maximum · 24 Stunden',history:'HISTORISCHE DATEN',aiForecast:'KI & PROGNOSE',outlook:'Nächste 24 Stunden',waiting:'Warte auf echte Marktdaten.',method:'Gewählte Methode',mae:'Validierungsfehler · MAE',baseline:'24-h-Baseline · MAE',caution:'Prognosen sind Modellschätzungen, keine garantierten Preise oder Handlungsempfehlungen.',lastUpdated:'Letzte Aktualisierung',dataPoints:'Historische Preisdaten',updateRate:'Aktualisierung geplant',hours6:'alle 6 Stunden',thePlatform:'DIE PLATTFORM',howTitle:'Eine Plattform. Vier Fähigkeiten.',oneTitle:'Datenpipeline',oneText:'Automatischer Abruf öffentlicher SMARD-Zeitreihen mit Qualitätskontrollen und SQL-Verarbeitung.',twoTitle:'Marktanalyse',twoText:'Historische Preis-, Wind-, Solar- und Verbrauchsdaten übersichtlich vergleichen.',threeTitle:'Prognosemodelle',threeText:'Machine Learning mit zeitlicher Validierung und transparentem Vergleich mit einfachen Baselines.',fourTitle:'Öffentliche Website',fourText:'Zweisprachiges Dashboard, automatisch aktualisiert und ohne eigenen Server veröffentlicht.',footerTag:'By Hope Intelligence',disclaimer:'Demonstrations- und Forschungsprojekt. Kein Echtzeit-Handelssystem.',adapted:'Daten aggregiert und analysiert.',notYet:'Das Dashboard ist vorbereitet. Nach dem ersten erfolgreichen GitHub-Actions-Lauf werden echte SMARD-Daten und Modellresultate angezeigt.',fetchFailed:'Live-Daten sind derzeit nicht verfügbar. Bitte prüfen Sie GitHub Actions und die SMARD-Datenquelle.',forecastUnavailable:'Eine belastbare Prognose ist noch nicht verfügbar; fehlende Daten werden nicht erfunden.',staleWarning:'Die jüngsten SMARD-Preisdaten liegen mehr als 72 Stunden zurück. Die angezeigten Werte sind historisch.',model:'Machine Learning',yesterday:'24-h-Baseline',last_week:'7-Tage-Baseline',seriesPrice:'Strompreis',seriesSolar:'Photovoltaik',seriesWind:'Wind Onshore',seriesLoad:'Stromverbrauch',observed:'Letzter Datenpunkt',dateLabel:'Zeitpunkt',currency:'EUR/MWh',energyUnit:'MWh (je Stunde)',industryTag:'MARKTSIGNALE',industryTitle:'Analysen für Energieunternehmen',negativeLabel:'Stunden mit negativen Preisen · 7 Tage',negativeHelp:'Historische Stunden mit negativem Großhandelspreis, keine Prognose.',volatilityLabel:'Preisvolatilität · 7 Tage',volatilityHelp:'Standardabweichung der stündlichen Großhandelspreise.',spreadLabel:'Preisspanne P10–P90 · 7 Tage',spreadHelp:'Differenz zwischen niedrigem und hohem Preisperzentil.',scenarioTag:'BEISPIELSZENARIO',scenarioTitle:'Lastverschiebung und Preisexposition',scenarioHelp:'Theoretischer Großhandelspreisunterschied, falls Stromverbrauch aus einem teuren (P90) in ein günstiges Zeitfenster (P10) verschoben werden könnte.',volumeLabel:'Verschiebbare Strommenge (MWh)',scenarioResult:'Theoretischer Preisunterschied',scenarioDisclaimer:'Keine garantierte Ersparnis und kein Tarifangebot: ohne Netzentgelte, Steuern, Zeitplanung, Restriktionen und Ausführungsrisiken.',sourceCode:'Quellcode ↗' },
 en: {
  navDashboard:'Dashboard',navIndustry:'Energy analytics',navApproach:'Methodology',photoCaption:'WIND · SOLAR · GRID',platform:'ENERGY MARKET INTELLIGENCE',howitworks:'Methodology ↗',heroEyebrow:'GERMAN DATA · PUBLIC SOURCE',heroTitle:'Energy markets.<br><span>Smarter decisions.</span>',heroDescription:'Explore Germany’s electricity market with official data, transparent forecasts and reproducible energy analytics.',explore:'Explore dashboard',source:'Official data source',overview:'MARKET OVERVIEW',dashboard:'Germany at a glance',loading:'Loading data …',ready:'Data available',stale:'Data may be stale',unavailable:'No data',latest:'Latest wholesale price',average:'Average · 24 hours',low:'Minimum · 24 hours',high:'Maximum · 24 hours',history:'HISTORICAL DATA',aiForecast:'AI & FORECAST',outlook:'Next 24 hours',waiting:'Waiting for real market data.',method:'Selected method',mae:'Validation error · MAE',baseline:'24h baseline · MAE',caution:'Forecasts are model estimates, not guaranteed market prices or trading advice.',lastUpdated:'Last data refresh',dataPoints:'Historical price points',updateRate:'Planned refresh',hours6:'every 6 hours',thePlatform:'THE PLATFORM',howTitle:'One platform. Four capabilities.',oneTitle:'Data pipeline',oneText:'Automated ingestion of public SMARD time series with validation and SQL processing.',twoTitle:'Market analytics',twoText:'Explore historical wholesale prices, wind, solar generation and electricity consumption.',threeTitle:'Forecasting models',threeText:'Machine learning with chronological validation and transparent comparison against seasonal baselines.',fourTitle:'Public website',fourText:'Bilingual dashboard, automatically refreshed and published without a dedicated server.',footerTag:'By Hope Intelligence',disclaimer:'Research and demonstration project. Not a real-time trading system.',adapted:'Data aggregated and analysed.',notYet:'The dashboard is ready for deployment. Genuine SMARD data and forecast results appear after the first successful GitHub Actions run.',fetchFailed:'Market data is currently unavailable. Check the GitHub Actions run and SMARD source.',forecastUnavailable:'Forecast not yet available; missing data are never replaced with fabricated predictions.',staleWarning:'Latest SMARD observations are more than 72 hours old. The displayed values are historical.',model:'Machine Learning',yesterday:'24h baseline',last_week:'7-day baseline',seriesPrice:'Wholesale price',seriesSolar:'Solar PV',seriesWind:'Onshore wind',seriesLoad:'Electricity load',observed:'Latest observation',dateLabel:'Date',currency:'EUR/MWh',energyUnit:'MWh (per hour)',industryTag:'MARKET SIGNALS',industryTitle:'Insights for energy companies',negativeLabel:'Negative-price hours · 7 days',negativeHelp:'Historical hours with wholesale prices below zero, not a forecast.',volatilityLabel:'Price volatility · 7 days',volatilityHelp:'Standard deviation of hourly wholesale prices.',spreadLabel:'P10–P90 price spread · 7 days',spreadHelp:'Difference between low and high price percentiles.',scenarioTag:'ILLUSTRATIVE SCENARIO',scenarioTitle:'Load-shifting price exposure',scenarioHelp:'Theoretical wholesale price difference if a chosen volume could move from an expensive interval (P90) to a cheaper interval (P10).',volumeLabel:'Shiftable consumption (MWh)',scenarioResult:'Theoretical price difference',scenarioDisclaimer:'Not guaranteed savings or a tariff quote: excludes network fees, taxes, scheduling, constraints and execution risk.',sourceCode:'Source code ↗'}
};
let language = 'de';
let dataset = null;
const $ = id => document.getElementById(id);
// Pages project links are constructed from the current hostname and first path segment.
function discoverRepoUrl(){
 const host=window.location.hostname;
 if(!host.endsWith('.github.io')) return null;
 const owner=host.slice(0,-'.github.io'.length);
 const name=window.location.pathname.split('/').filter(Boolean)[0];
 if(!owner || !name) return null;
 return 'https://github.com/'+encodeURIComponent(owner)+'/'+encodeURIComponent(name);
}
const repo=discoverRepoUrl();
if(repo){$('source-code-link').href=repo;}else{$('source-code-link').style.display='none';}
const tr = key => translations[language][key] || key;
function htmlText(id,text){const e=$(id);if(e)e.textContent=text;}
function dateTime(utc){if(!utc) return '—';try{return new Intl.DateTimeFormat(language==='de'?'de-DE':'en-GB',{timeZone:'Europe/Berlin',day:'2-digit',month:'short',year:'numeric',hour:'2-digit',minute:'2-digit'}).format(new Date(utc));}catch(_){return String(utc);}}
function number(n,decimal=2){return typeof n==='number' && Number.isFinite(n) ? new Intl.NumberFormat(language==='de'?'de-DE':'en-GB',{maximumFractionDigits:decimal,minimumFractionDigits:decimal}).format(n) : '—';}
function setStatus(text,kind){const node=$('status');node.textContent='● '+text;node.className='status '+(kind||'');}
function notice(text){const node=$('notice');node.textContent=text;node.classList.toggle('visible',Boolean(text));}
function chart(svgContainer,points,forecast=false){
 const target=$(svgContainer);target.innerHTML='';
 if(!Array.isArray(points)||points.length<2){target.innerHTML='<p class="placeholder">'+tr('waiting')+'</p>';return;}
 const data=points.filter(p => Number.isFinite(p.value)&&Number.isFinite(new Date(p.ts).getTime()));
 if(data.length<2){target.innerHTML='<p class="placeholder">'+tr('waiting')+'</p>';return;}
 const W=620,H=270,left=56,right=14,top=20,bottom=34;
 const times=data.map(d=>new Date(d.ts).getTime());const v=data.map(d=>d.value);
 let lo=Math.min(...v),hi=Math.max(...v);const pad=Math.max(3,(hi-lo)*.15);lo-=pad;hi+=pad;if(hi===lo)hi+=1;
 let tlo=Math.min(...times),thi=Math.max(...times);if(thi===tlo)thi+=1;
 const x=t=>left+((t-tlo)/(thi-tlo))*(W-left-right),y=n=>top+((hi-n)/(hi-lo))*(H-top-bottom);
 const NS='http://www.w3.org/2000/svg';const svg=document.createElementNS(NS,'svg');svg.setAttribute('viewBox',`0 0 ${W} ${H}`);svg.setAttribute('role','img');svg.setAttribute('aria-label',forecast?tr('outlook'):tr('history'));
 const path=(name,attrs={})=>{const el=document.createElementNS(NS,name);for(const [k,val] of Object.entries(attrs))el.setAttribute(k,val);svg.appendChild(el);return el;};
 for(let i=0;i<=4;i++){const val=lo+(hi-lo)*i/4;const yi=y(val);path('line',{x1:left,y1:yi,x2:W-right,y2:yi,class:'svggrid'});const t=path('text',{x:0,y:yi+4,class:'svglabel'});t.textContent=number(val,0);}
 for(let i=0;i<=4;i++){let time=tlo+(thi-tlo)*i/4;let tick=path('text',{x:x(time),y:H-8,'text-anchor':'middle',class:'svglabel'});tick.textContent=new Intl.DateTimeFormat(language==='de'?'de-DE':'en-GB',{timeZone:'Europe/Berlin',month:'numeric',day:'numeric',hour:'2-digit'}).format(new Date(time));}
 const coordinates=data.map((p,i)=>`${x(times[i]).toFixed(1)},${y(p.value).toFixed(1)}`);
 if(!forecast){const defs=document.createElementNS(NS,'defs');defs.innerHTML='<linearGradient id="areaFill" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stop-color="#45c8ea" stop-opacity=".32"/><stop offset="100%" stop-color="#45c8ea" stop-opacity="0"/></linearGradient>';svg.appendChild(defs);path('polygon',{points:`${x(times[0])},${H-bottom} ${coordinates.join(' ')} ${x(times.at(-1))},${H-bottom}`,class:'svgarea'});}
 path('polyline',{points:coordinates.join(' '),class:forecast?'svgforecast':'svgline'});
 const circle=path('circle',{cx:x(times.at(-1)),cy:y(data.at(-1).value),r:4,fill:forecast?'#97aaff':'#52d8f3'});
 circle.setAttribute('aria-label',`${number(data.at(-1).value)}`);
 target.append(svg);
}
function render(){
 document.documentElement.lang=language;
 document.querySelectorAll('[data-i18n]').forEach(element=>{let content=tr(element.dataset.i18n);if(element.dataset.i18n==='heroTitle')element.innerHTML=content;else element.textContent=content;});
 $('language').textContent=language==='de'?'EN':'DE';
 $('lang-current').textContent=language.toUpperCase();
 const metricSelect=$('metric'); const labels={price:tr('seriesPrice'),solar:tr('seriesSolar'),wind:tr('seriesWind'),load:tr('seriesLoad')};
 for(const op of metricSelect.options)op.textContent=labels[op.value];
 const status=dataset?.metadata?.status;
 if(status!=='live'){
  setStatus(tr('unavailable'),'bad');notice(tr('notYet'));
  ['latest-price','average-price','min-price','max-price','method-name','model-mae','baseline-mae','data-updated','data-points','negative-hours','volatility','price-spread','potential-difference'].forEach(id=>htmlText(id,'—'));
  htmlText('chart-title',labels[metricSelect.value]);htmlText('chart-unit',metricSelect.value==='price'?tr('currency'):tr('energyUnit'));
  chart('historical-chart',[]);chart('forecast-chart',[]);return;
 }
 const meta=dataset.metadata;const sourceTime=Date.parse(meta.latest_price_timestamp);const lag=(Date.now()-sourceTime)/3600000;const stale=!Number.isFinite(lag)||lag>72;
 setStatus(tr(stale?'stale':'ready'),stale?'bad':'ok');notice(stale?tr('staleWarning'):'');
 const sum=dataset.summary||{};
 const a=dataset.analytics||{};
 htmlText('negative-hours',typeof a.negative_price_hours==='number'?number(a.negative_price_hours,0)+' h':'—');
 htmlText('volatility',typeof a.price_volatility_std_eur_mwh==='number'?number(a.price_volatility_std_eur_mwh)+' €/MWh':'—');
 htmlText('price-spread',typeof a.p10_p90_spread_eur_mwh==='number'?number(a.p10_p90_spread_eur_mwh)+' €/MWh':'—');
 const rawVolume=Number($('volume-mwh').value);
 const validVolume=$('volume-mwh').value.trim()!=='' && Number.isFinite(rawVolume) && rawVolume>=0 && rawVolume<=1000000;
 const validSpread=typeof a.p10_p90_spread_eur_mwh==='number' && a.p10_p90_spread_eur_mwh>=0;
 htmlText('potential-difference',validVolume && validSpread ? number(rawVolume*a.p10_p90_spread_eur_mwh)+' €':'—');
 htmlText('latest-price',number(sum.current_price));htmlText('average-price',number(sum.avg_price_24h));htmlText('min-price',number(sum.min_price_24h));htmlText('max-price',number(sum.max_price_24h));
 htmlText('data-updated',dateTime(meta.generated_at));htmlText('data-points',Number(meta.historical_observations||0).toLocaleString(language==='de'?'de-DE':'en-GB'));
 const metric=metricSelect.value,period=Number($('period').value);
 htmlText('chart-title',labels[metric]);htmlText('chart-unit',metric==='price'?tr('currency'):tr('energyUnit'));
 const series=dataset.history?.[metric]||[];
 chart('historical-chart',series.slice(-period));
 htmlText('last-observation',`${tr('observed')}: ${dateTime(series.at(-1)?.ts)}`);
 const forecast=dataset.forecast||{};if(forecast.status==='ok'&&Array.isArray(forecast.points)){
  chart('forecast-chart',forecast.points);const method=forecast.selected_method;
  htmlText('method-name',{machine_learning:tr('model'),yesterday:tr('yesterday'),last_week:tr('last_week')}[method]||method);
  htmlText('model-mae',number(forecast.validation?.mae_eur_mwh?.[method])+' €/MWh');
  htmlText('baseline-mae',number(forecast.validation?.mae_eur_mwh?.yesterday)+' €/MWh');
 }else{
  chart('forecast-chart',[]);htmlText('method-name',tr('forecastUnavailable'));htmlText('model-mae','—');htmlText('baseline-mae','—');
 }
}
$('language').addEventListener('click',()=>{language=language==='de'?'en':'de';render();});
$('metric').addEventListener('change',render);$('period').addEventListener('change',render);$('volume-mwh').addEventListener('input',render);
fetch('./data/dashboard.json',{cache:'no-store'})
 .then(response=>{if(!response.ok)throw Error(String(response.status));return response.json();})
 .then(data=>{dataset=data;render();})
 .catch(err=>{dataset={metadata:{status:'awaiting_first_real_data'}};render();notice(tr('fetchFailed')+' ('+String(err.message)+')');});
