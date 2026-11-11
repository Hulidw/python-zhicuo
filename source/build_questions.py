import sys, io, json, contextlib
from pathlib import Path

# 固定题库：题目、代码、预期输出、概念说明。构建时逐题执行核验。
rows = [
('列表','索引','a = [10, 20, 30]\nprint(a[1])','20','索引从 0 开始，索引 1 对应第二个元素。','10','30'),
('列表','索引','a = [4, 7, 9]\nprint(a[-1])','9','负索引 -1 代表最后一个元素。','4','7'),
('列表','切片','a = [0, 1, 2, 3]\nprint(a[1:3])','[1, 2]','切片包含起点，不包含终点。','[1, 2, 3]','[0, 1, 2]'),
('列表','切片','a = [1, 2, 3, 4]\nprint(a[::2])','[1, 3]','步长为 2，从索引 0 开始每隔一个取值。','[2, 4]','[1, 2]'),
('列表','添加元素','a = [1]\na.append([2, 3])\nprint(a)','[1, [2, 3]]','append 将整个对象作为一个元素加入。','[1, 2, 3]','[2, 3]'),
('列表','添加元素','a = [1]\na.extend([2, 3])\nprint(a)','[1, 2, 3]','extend 逐个添加可迭代对象里的元素。','[1, [2, 3]]','[1]'),
('列表','赋值与复制','a = [1, 2]\nb = a\nb[0] = 9\nprint(a)','[9, 2]','赋值没有复制列表，a 和 b 指向同一个列表。','[1, 2]','[9, 9]'),
('列表','赋值与复制','a = [1, 2]\nb = a.copy()\nb[0] = 9\nprint(a)','[1, 2]','copy 创建新列表，修改这个新列表的元素不影响原列表。','[9, 2]','[9, 9]'),
('列表','修改列表','a = [1, 2, 3]\na.pop(1)\nprint(a)','[1, 3]','pop 的参数是索引，这里移除第二个元素。','[2, 3]','[1, 2]'),
('列表','修改列表','a = [1, 2]\nr = a.append(3)\nprint(r)','None','append 原地修改列表，返回值是 None。','[1, 2, 3]','3'),
('循环','range 边界','for i in range(3):\n    print(i)','0\n1\n2','range(3) 从 0 开始，到 3 之前结束。','1\n2\n3','0\n1\n2\n3'),
('循环','range 边界','for i in range(1, 5, 2):\n    print(i)','1\n3','起点 1，步长 2，不包含终点 5。','1\n3\n5','2\n4'),
('循环','缩进','for i in range(3):\n    x = i\nprint(x)','2','print 在循环外，只在循环结束后执行一次。','0\n1\n2','3'),
('循环','缩进','for i in range(2):\n    print(i)\nprint(9)','0\n1\n9','循环体打印两次，循环外的 print 只执行一次。','0\n9\n1\n9','1\n2\n9'),
('循环','累加初始化','s = 0\nfor i in range(1, 4):\n    s += i\nprint(s)','6','累加器在循环前初始化，逐次累加 1、2、3。','3','10'),
('循环','累加初始化','for i in range(1, 4):\n    s = 0\n    s += i\nprint(s)','3','每轮都将 s 重置为 0，所以只保留最后一轮的值。','6','0'),
('循环','break 与 continue','for i in range(4):\n    if i == 2:\n        break\n    print(i)','0\n1','break 立即结束整个循环。','0\n1\n3','0\n1\n2'),
('循环','break 与 continue','for i in range(4):\n    if i == 2:\n        continue\n    print(i)','0\n1\n3','continue 跳过当前轮剩余语句，继续下一轮。','0\n1','0\n1\n2\n3'),
('循环','循环条件','i = 0\nwhile i < 3:\n    i += 1\nprint(i)','3','先检查条件，再执行循环体。i 到 3 时退出。','2','4'),
('循环','循环条件','s = 0\nfor x in [2, 4]:\n    s += x\nprint(s)','6','遍历列表时 x 是元素的值，不是索引。','1','2'),
('函数','打印与返回','def add(a, b):\n    print(a + b)\n\nresult = add(2, 3)\nprint(result)','5\nNone','print 只向屏幕输出；函数没有显式 return 时返回 None。','5','None'),
('函数','打印与返回','def add(a, b):\n    return a + b\n\nresult = add(2, 3)\nprint(result)','5','return 把结果交给调用者，本身不打印。','5\n5','None'),
('函数','参数与返回值','def double(x):\n    return x * 2\nprint(double(3))','6','形参 x 接收实参 3，返回 3 乘 2。','3','None'),
('函数','参数与返回值','def sub(a, b):\n    return a - b\nprint(sub(2, 5))','-3','位置参数按顺序绑定，a 是 2，b 是 5。','3','7'),
('函数','局部变量','x = 10\ndef f():\n    x = 3\n    return x\nprint(f())\nprint(x)','3\n10','函数内赋值创建局部 x，不改变全局 x。','3\n3','10\n10'),
('函数','局部变量','x = 4\ndef f(x):\n    x += 1\n    return x\nprint(f(x))\nprint(x)','5\n4','形参是局部名称，对整数的重新赋值不会修改外部变量。','5\n5','4\n4'),
('函数','return 结束','def f():\n    return 1\n    print(2)\nprint(f())','1','执行 return 后函数立即结束，后面的 print 不执行。','2\n1','1\n2'),
('函数','return 结束','def f(x):\n    if x > 0:\n        return x\n    return 0\nprint(f(-2))','0','条件不满足，执行后面的 return 0。','-2','None'),
('函数','默认参数','def f(x=2):\n    return x + 1\nprint(f())','3','没有传入实参时，x 使用默认值 2。','2','None'),
('函数','默认参数','def f(x=2):\n    return x + 1\nprint(f(5))','6','传入的实参 5 覆盖默认值 2。','3','5'),
]
for n in range(3,9):
    rows.extend([
        ('列表','切片',f'a = list(range({n}))\nprint(a[-2:])',str([n-2,n-1]),'负数切片从列表尾部定位，省略终点表示取到末尾。',str([n-1]),str([n-2])),
        ('列表','添加元素',f'a = [{n}]\na.extend("ab")\nprint(a)',str([n,'a','b']),'字符串可以迭代，extend 会逐个添加字符。',str([n,'ab']),str([n,['a','b']])),
        ('列表','赋值与复制',f'a = [{n}, 0]\nb = a[:]\nb.append(1)\nprint(len(a))','2','全切片创建新列表，向新列表添加元素不会改变原列表长度。','3','1'),
        ('列表','修改列表',f'a = [{n}, 1, {n}]\na.remove({n})\nprint(a)',str([1,n]),'remove 按值删除第一个匹配元素，不会一次删除所有匹配项。','[1]',str([n,1])),
        ('列表','索引',f'a = [[{n}, 1], [2, 0]]\nprint(a[0][0])',str(n),'连续索引先选外层元素，再选择内部列表里的元素。','0','2'),
        ('循环','range 边界',f'print(list(range({n}, 0, -2)))',str(list(range(n,0,-2))),'负步长递减，终点仍不包含在序列内。',str(list(range(n,0,-2))+[0]),'[]'),
        ('循环','累加初始化',f's = 1\nfor i in range(1, {n}):\n    s *= 2\nprint(s)',str(2**(n-1)),'每轮将当前累积值乘以 2；循环次数由 range 边界决定。',str(2**n),str(n)),
        ('循环','break 与 continue',f's = 0\nfor i in range({n}):\n    if i == 1:\n        continue\n    s += i\nprint(s)',str(sum(range(n))-1),'continue 跳过本轮累加，只跳过值为 1 的那一轮。',str(sum(range(n))),'0'),
        ('循环','循环条件',f'i = {n}\nwhile i > 0:\n    i -= 2\nprint(i)',str(-(n % 2)),'每轮先判断条件再减 2，最终值可能低于边界。',str(0 if n%2 else -1),'2'),
        ('循环','缩进',f'count = 0\nfor i in range({n}):\n    for j in range(2):\n        count += 1\nprint(count)',str(n*2),'内层循环会为每一次外层循环完整执行。',str(n),str(n+2)),
        ('函数','参数与返回值',f'def f(a, b):\n    return a - b\nprint(f(b={n}, a=1))',str(1-n),'关键字参数按名称绑定，而不是按书写先后绑定。',str(n-1),str(n+1)),
        ('函数','打印与返回',f'def f(x):\n    print(x)\nr = f({n})\nprint(r)',str(n)+'\nNone','函数打印实参之后隐式返回 None，外部还会打印返回值。',str(n),'None'),
        ('函数','return 结束',f'def f():\n    for i in range({n}):\n        return i\nprint(f())','0','在循环第一轮就执行 return，整个函数随即结束。',str(n-1),str(n)),
        ('函数','局部变量',f'x = {n}\ndef f():\n    x = 1\n    return x\nf()\nprint(x)',str(n),'函数内部的局部赋值不会修改同名全局变量。','1','None'),
        ('函数','默认参数',f'def f(x={n}):\n    return x * 2\nprint(f(1))','2','显式传入实参时不会使用默认值。',str(n*2),str(n)),
    ])
questions=[]
for idx,(cat,topic,code,expected,explain,w1,w2) in enumerate(rows):
    output=io.StringIO(); steps=[]
    def trace(frame,event,arg):
        if frame.f_code.co_filename == '<question>' and event in ('line','return'):
            values={k:repr(v) for k,v in frame.f_locals.items() if not k.startswith('__') and not callable(v)}
            steps.append(dict(line=frame.f_lineno,event=event,scope=frame.f_code.co_name,variables=values,output=output.getvalue().rstrip(),returned=repr(arg) if event=='return' else ''))
        return trace
    with contextlib.redirect_stdout(output):
        sys.settrace(trace)
        try: exec(compile(code,'<question>','exec'),{})
        finally: sys.settrace(None)
    assert output.getvalue().strip()==expected,(idx,output.getvalue(),expected)
    options=[expected,w1,w2]; options=options[idx%3:]+options[:idx%3]
    kind='输出选择题'; prompt='这段代码会输出什么？'; answer=expected; display=code
    if idx in (1,11,22):
        kind='填空题'; token={1:'-1',11:'2',22:'2'}[idx]; display=code.replace(token,'___',1);answer=token;prompt='填入一个整数，使代码输出：'+expected
    if idx in (5,15,26):
        kind='找错题';prompt='哪一项正确解释了这段代码的行为？';answer=explain;options=[explain,'每一行代码都会按书写顺序执行且只执行一次。','函数和方法总会自动返回最后计算的数值。'];options=options[1:]+options[:1]
    assert len(set(options)) == 3, (idx, options)
    questions.append(dict(id=idx,category=cat,topic=topic,code=code,display=display,kind=kind,prompt=prompt,answer=answer,options=options,explain=explain,steps=steps,expected=expected,level='基础' if idx<30 else '变式巩固'))
Path(__file__).with_name('dist').joinpath('questions.js').write_text('const QUESTIONS = '+json.dumps(questions,ensure_ascii=False)+';',encoding='utf-8')
print(f'Verified {len(questions)} answers and generated execution traces.')
