import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const ROOT=path.resolve(process.argv[2]??'LABOLATORIUM');
const BUILD=path.join(ROOT,'.build');
const SKILL=process.env.PRESENTATION_SKILL_DIR;
if(!SKILL)throw Error('Ustaw PRESENTATION_SKILL_DIR na katalog umiejętności prezentacji Codex.');
const PYTHON=process.env.RUNTIME_PYTHON;
if(!PYTHON)throw Error('Ustaw RUNTIME_PYTHON na interpreter dostarczonego środowiska Codex.');
const {finalizePresentation,applyPresentationChartFont}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
const slides=JSON.parse(await fs.readFile(path.join(ROOT,'tools/wyklad_tresc.json'),'utf8'));
slides[19].kind='image'; slides[19].image='map_web.png';
slides[20].body='python -m http.server 8000 \\\n  --bind 127.0.0.1 \\\n  --directory outputs/site\n\nhttp://127.0.0.1:8000/';
const summary=JSON.parse(await fs.readFile(path.join(ROOT,'outputs/summary.json'),'utf8'));
const p=Presentation.create({slideSize:{width:1280,height:720}});
const font='Arial';
function txt(slide,text,x,y,w,h,size=30,color='#183f4b',bold=false){
 const shape=slide.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 shape.text=text;
 shape.text.style={typeface:font,fontSize:size,color,bold,autoFit:'none'};
 return shape;
}
let elapsed=0;
for(const [i,s] of slides.entries()){
 const slide=p.slides.add();
 const dark=s.kind==='cover'||[6,10,17].includes(i);
 slide.background.fill=dark?'#123e4a':'#ffffff';
 const ink=dark?'#ffffff':'#183f4b',muted=dark?'#badbdd':'#506b73';
 if(s.kind==='cover'){
  txt(slide,s.title,80,120,1120,210,64,ink,true);
  txt(slide,s.body,84,410,1050,150,30,'#bedee0');
 } else {
  txt(slide,s.title,64,42,1152,88,44,ink,true);
  if(s.kind==='image'){
   txt(slide,s.body.replaceAll('\n','\n\n'),64,182,420,410,28,ink);
   const img=await fs.readFile(path.join(ROOT,'outputs/figures',s.image));
   slide.images.add({blob:new Uint8Array(img),contentType:'image/png',alt:s.title,fit:'contain',position:{left:506,top:143,width:728,height:520}});
  } else if(s.kind==='chart'){
   txt(slide,'NDVI: 0.6179\n\nNDBI: −0.1905\n\nMNDWI: −0.4896\n\nWspólna maska: 1 729 266 pikseli',64,180,420,420,27,ink);
   const c=slide.charts.add('bar',{position:{left:530,top:160,width:690,height:440},categories:['NDVI','NDBI','MNDWI'],series:[{name:'Średnia',values:Object.values(summary.indices).map(v=>Number(v.mean.toFixed(4))),fill:'#147f82'}],barOptions:{direction:'column',grouping:'clustered'},hasLegend:false,yAxis:{min:-1,max:1,majorUnit:0.5,numberFormatCode:'0.0',textStyle:{fontSize:22}},xAxis:{tickLabelPosition:'low',textStyle:{fontSize:22}},dataLabels:{showValue:false},chartFill:'#ffffff',plotAreaFill:'#ffffff'});
   applyPresentationChartFont(c,{fontFamily:font});
  } else if(s.kind==='bands'){
   const lines=s.body.split('\n');
   for(let j=0;j<lines.length;j++)txt(slide,lines[j],90,160+j*83,1030,65,34,ink,j===3);
  } else {
   txt(slide,s.kind==='command'?s.body:s.body.replaceAll('\n','\n\n'),82,194,1090,390,s.kind==='command'?35:36,ink);
  }
 }
 txt(slide,`${String(i+1).padStart(2,'0')}  /  25`,1110,677,115,27,16,muted);
 txt(slide,`${elapsed}–${elapsed+s.minutes} min`,65,677,200,27,16,muted);
 slide.speakerNotes.textFrame.setText(`Czas: ${s.minutes} min (${elapsed}–${elapsed+s.minutes} min wykładu).\n\n${s.notes}\n\nŹródła: ${s.source}`);
 elapsed+=s.minutes;
}
await fs.mkdir(path.join(BUILD,'slides'),{recursive:true});
const candidate=path.join(BUILD,'wyklad_candidate.pptx');
await (await PresentationFile.exportPptx(p)).save(candidate);
console.log('Draft PPTX exported');
const finalPath=path.join(ROOT,'materials/wyklad_landsat_90min_rebuild.pptx');
await finalizePresentation({workspaceDir:ROOT,candidatePath:candidate,finalPath,
 pythonExecutable:PYTHON,
 integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],
 explicitTotalSlideCount:25,requiredNativeChartOwnerSlides:[15],requiredNativeTableOwnerSlides:[],
 materializeLiteralChartWorkbooks:true,
 fontPolicy:{basis:'design',families:[font]},verifyArtifactToolImport:true,
 receiptPath:path.join(BUILD,'presentation-validation-rebuild.json')});
console.log('Final PPTX validated');
for(let i=0;i<p.slides.items.length;i++){
 const blob=await p.export({slide:p.slides.items[i],format:'png',scale:1});
 await fs.writeFile(path.join(BUILD,'slides',`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await blob.arrayBuffer()));
}
console.log('Rendered all slides');
