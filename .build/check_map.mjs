import { chromium } from 'playwright';
import fs from 'node:fs/promises';
const b=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
const page=await b.newPage({viewport:{width:1440,height:950}});
const errors=[];const bad=[];
page.on('pageerror',e=>errors.push(String(e)));
page.on('response',r=>{if(r.url().startsWith('http://127.0.0.1:8000')&&r.status()>=400)bad.push([r.status(),r.url()]);});
await page.goto('http://127.0.0.1:8000/',{waitUntil:'networkidle'});
for(const layer of ['NDVI','NDBI','MNDWI','RGB']){
 await page.selectOption('#layer',layer);
 await page.waitForFunction(()=>document.querySelector('#state').textContent.includes('gotowa'));
 const count=await page.locator('img.leaflet-tile-loaded').count();
 if(count===0)throw Error('No tiles '+layer);
}
await page.selectOption('#layer','NDVI');
await page.locator('#opacity').fill('0.65');
await page.locator('#opacity').dispatchEvent('input');
await page.locator('#reset').click();
await page.screenshot({path:'LABOLATORIUM/.build/map-desktop.png',fullPage:true});
await page.setViewportSize({width:390,height:844});
await page.screenshot({path:'LABOLATORIUM/.build/map-mobile.png',fullPage:true});
await fs.writeFile('LABOLATORIUM/.build/map-check.json',JSON.stringify({errors,bad,checkedLayers:4},null,2));
await b.close();
if(errors.length||bad.length)throw Error(JSON.stringify({errors,bad}));
console.log('All four layers and local requests passed');
