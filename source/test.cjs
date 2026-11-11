const fs=require('fs'),vm=require('vm'),assert=require('assert');
const elements={};const storage={};const ctx=vm.createContext({console,Date,Set,JSON,Math,alert:()=>{},location:{hash:''},window:{},localStorage:{getItem:k=>storage[k],setItem:(k,v)=>storage[k]=v},document:{querySelector:s=>elements[s]||(elements[s]={innerHTML:''})}});
vm.runInContext(fs.readFileSync('dist/questions.js','utf8')+'\n'+fs.readFileSync('dist/pitfalls.js','utf8')+'\n'+fs.readFileSync('dist/app.js','utf8'),ctx);
function run(s){return vm.runInContext(s,ctx)}
assert.equal(run('QUESTIONS.length'),120);
run("start('函数');selection='5';submitAnswer()");assert.equal(run('db.records[0].ok'),false);assert.equal(run('db.mistakes[20].reason'),'待确认');
run("setReason('漏看代码或缩进')");assert.equal(run('db.mistakes[20].reason'),'漏看代码或缩进');
run("start(null,[1]);selection='-1';submitAnswer()");assert.equal(run('db.records[1].ok'),true);
run("start(null,[20]);hint(1);selection='5\\nNone';submitAnswer()");assert.equal(run('db.records[2].hint'),1);
run("start('列表');for(let i=0;i<5;i++){selection=getq(db.session.ids[db.session.index]).answer;submitAnswer();next()}");assert.equal(run('db.session.index'),5);
run("start(null,[20]);traceStep(1)");assert.equal(run('db.session.hint'),2);
run("go('mistakes');go('stats');go('home')");assert.ok(storage['py-helper-v1']);
run("start(null,[1]);selection='2';submitAnswer()");assert.equal(run('db.records[8].ok'),true);assert.equal(run('db.records[8].alt'),true);
run("start(null,[11]);selection='02';submitAnswer()");assert.equal(run('db.records[9].ok'),true);
run("start(null,[1]);selection='3';submitAnswer()");assert.equal(run('db.records[10].ok'),false);
console.log('PASS: 120 questions, incorrect answer, editable reason, fill-in, hint tracking, five-question session, trace usage and persistence.');
console.log('PASS: equivalent answers accepted (a[2] for a[-1], 04 for 4) and wrong answers still rejected.');
