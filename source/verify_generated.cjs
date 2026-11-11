const vm=require('vm'),fs=require('fs'),cp=require('child_process'),assert=require('assert');
const elements={};const ctx=vm.createContext({console,Date,Set,JSON,Math,setTimeout,clearTimeout,alert:()=>{},location:{hash:''},window:{APP_CONFIG:{}},localStorage:{getItem:()=>null,setItem:()=>{}},document:{querySelector:s=>elements[s]||(elements[s]={innerHTML:'',insertAdjacentHTML:()=>{}})}});
for(const f of ['questions.js','pitfalls.js','recipes.js','app.js','account.js','adaptive.js'])vm.runInContext(fs.readFileSync('dist/'+f,'utf8'),ctx);
let cases=[];for(let c=0;c<3;c++)for(let k=0;k<3;k++)for(let l=1;l<=3;l++)for(let seed=1;seed<=30;seed++){let id=1000000000+c*100000000+k*10000000+l*1000000+seed;cases.push(vm.runInContext(`generatedQuestion(${id})`,ctx))}
const py="import json,sys,io,contextlib\nqs=json.load(sys.stdin)\nfor q in qs:\n o=io.StringIO()\n with contextlib.redirect_stdout(o): exec(q['code'],{})\n assert o.getvalue().strip()==q['answer'], (q['id'],o.getvalue(),q['answer'])\n assert q['steps'][-1]['output']==q['answer']\nprint('PASS: 810 generated Python programs match expected answers and final output snapshots.')";
let r=cp.spawnSync('python',['-c',py],{input:JSON.stringify(cases),encoding:'utf8',maxBuffer:10000000});if(r.status!==0)throw Error(r.stderr);console.log(r.stdout);
vm.runInContext('adaptiveStart()',ctx);assert.equal(vm.runInContext('db.session.ids.length',ctx),5);assert.equal(vm.runInContext('new Set(db.session.ids).size',ctx),5);
vm.runInContext("selection=getq(db.session.ids[0]).answer;submitAnswer();go('stats');go('mistakes');go('plan')",ctx);
assert.equal(vm.runInContext('db.records[0].ok',ctx),true);console.log('PASS: adaptive selection, generated question grading, dashboard and plan rendering.');
