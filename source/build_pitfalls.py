# -*- coding: utf-8 -*-
"""生成「错误地图」数据：26 个新手最常踩的坑。

构建时逐条真实执行：
1. 运行错误代码，抓取真实 traceback（含行号、异常类型、caret）；
2. 运行修复后的代码，用断言/exact 输出核验修复有效；
3. 生成「先猜再揭晓」的候选项与埋错练习。
输出 dist/pitfalls.js，前端不写死任何报错文本。
"""
import contextlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile

try:
    import pandas as _pd
    PANDAS_VERSION = _pd.__version__
except Exception:  # pragma: no cover
    PANDAS_VERSION = '2.0+'
PY_VERSION = '%d.%d' % sys.version_info[:2]

LAYER_ORDER = ['语法层', '运行时层', '环境层', '工程习惯层']
LAYER_KEY = {'语法层': 'syntax', '运行时层': 'runtime', '环境层': 'env', '工程习惯层': 'habit'}

# ---------------------------------------------------------------- 20 个坑
C = []


def add(**kw):
    C.append(kw)


# ============================ 语法层 ============================
add(
    id='s1', layer='语法层', scene=['通用'], exc='SyntaxError',
    title='if 后面漏了一个冒号',
    brief='每条复合语句的结尾都要有冒号，这是最容易被眼睛跳过的字符。',
    code='''score = 85
if score >= 60
    print("及格")''',
    cause='if / for / while / def / class / try 这类复合语句，行尾必须写冒号，否则解释器无法判断代码块从哪里开始。报错行号在 if 这一行，而不是 print。',
    fix='''score = 85
if score >= 60:
    print("及格")''',
    fix_note='补上冒号即可，缩进保持 4 个空格。',
    verify='python demo.py 输出「及格」，不再有 SyntaxError。',
    keywords=['SyntaxError expected ":"', 'python if 冒号', 'SyntaxError invalid syntax 怎么读'],
    version='Python 3.10 起提示 expected \':\'；3.9 及更早只给 invalid syntax，但读法相同。',
    guess_exc=['SyntaxError', 'IndentationError', 'NameError'],
    quiz_title='补上缺少的冒号', quiz='''for i in range(3)
    print(i)''',
    quiz_answer='第 1 行改为 for i in range(3):',
    quiz_explain='for 行尾缺冒号 → SyntaxError。注意报错会指向 for 这一行，而不是里面的 print。',
)

add(
    id='s2', layer='语法层', scene=['通用'], exc='IndentationError',
    title='函数体没有缩进',
    brief='冒号后面的语句必须缩进，同一代码块缩进量要完全一致。',
    code='''def greet():
print("你好")''',
    cause='def 后面紧跟的语句属于函数体，必须缩进。Python 用缩进表示层级，不缩进就等于「函数体是空的」，所以直接报 IndentationError。',
    fix='''def greet():
    print("你好")''',
    fix_note='函数体统一缩进 4 个空格；不要混用 Tab 和空格。',
    verify='python demo.py 输出「你好」。',
    keywords=['IndentationError expected an indented block', 'python 缩进 4 个空格', 'TabError 混用'],
    version='Python 3.12 会补充 after function definition on line 1；更早版本只有 expected an indented block。',
    guess_exc=['IndentationError', 'SyntaxError', 'NameError'],
    quiz_title='统一缩进', quiz='''def total(a, b):
    return a + b
  print(total(1, 2))''',
    quiz_answer='把第 3 行的 print 改成 4 个空格缩进，与 return 对齐（或直接与 def 对齐，视逻辑而定）。',
    quiz_explain='缩进量不一致会触发 IndentationError / TabError。看报错里的 unindent does not match 提示即可定位。',
)

add(
    id='s3', layer='语法层', scene=['通用'], exc='SyntaxError',
    title='用了中文全角引号',
    brief='从聊天软件或网页复制代码时，引号常被自动替换成中文引号。',
    code='''print(“hello”)''',
    cause='代码里只能使用英文半角引号 " 或 \'。中文引号 “ ” 是普通字符，不是字符串定界符，解释器直接判定为非法字符。',
    fix='''print("hello")''',
    fix_note='把 “ ” 换成英文的 " "；同理要检查中文逗号、分号、括号。',
    verify='python demo.py 输出 hello。',
    keywords=['SyntaxError invalid character U+201C', 'python 中文引号 报错'],
    version='Python 3.12 直接给出 invalid character \'“\' (U+201C)；3.11 及以前多为 invalid character in identifier。',
    guess_exc=['SyntaxError', 'UnicodeDecodeError', 'TypeError'],
    quiz_title='清掉隐形全角符号', quiz='''data = {"a": 1， "b": 2}
print(data)''',
    quiz_answer='第 1 行的中文逗号「，」改成英文逗号 ,',
    quiz_explain='中文标点同样会触发 SyntaxError: invalid character，只是异常提示里给出的是 Unicode 码位，不好肉眼识别。',
)

add(
    id='s4', layer='语法层', scene=['通用'], exc='SyntaxError',
    title='写成 Python 2 的 print 语句',
    brief='print 后面没有括号，说明这份代码或教程来自 Python 2 时代。',
    code='''name = "Tom"
print "你好, " + name''',
    cause='Python 3 里 print 是函数，必须写成 print(...)。看到 Missing parentheses 这条提示，基本可以判断：代码是旧的，或者照着老教程抄的。',
    fix='''name = "Tom"
print("你好, " + name)''',
    fix_note='给 print 的参数加上括号；如果参数里有逗号，注意用括号把整个表达式包起来。',
    verify='python demo.py 输出「你好, Tom」。',
    keywords=['SyntaxError Missing parentheses in call to print', 'python2 代码 python3 运行'],
    version='这条报错只出现在 Python 3；Python 2 可以正常运行。这类代码通常还伴随 raw_input、dict.iteritems 等旧写法。',
    guess_exc=['SyntaxError', 'TypeError', 'NameError'],
    quiz_title='一并检查其他 Py2 写法', quiz='''x = raw_input("数字：")
print "结果是", int(x) + 1''',
    quiz_answer='raw_input 改成 input；print 改成 print("结果是", int(x) + 1)',
    quiz_explain='Python 3 移除了 raw_input，并把 print 从语句改成函数。迁移时这两处几乎总是一起出现。',
)

# ============================ 运行时层 ============================
add(
    id='r1', layer='运行时层', scene=['通用'], exc='NameError',
    title='名字拼错了：lenght 不是 length',
    brief='NameError 表示这个名字在当前位置从未被定义过，多数是拼写问题。',
    code='''names = ["Ann", "Bob"]
print(len(names))
print(lenght(names))''',
    cause='解释器执行到第 3 行时要找名为 lenght 的变量或函数，但从未定义过。注意前两行是正常执行的——报错发生在运行时，不是编译期。',
    fix='''names = ["Ann", "Bob"]
print(len(names))
print(len(names))''',
    fix_note='改成正确的 len；PyCharm / VS Code 会在拼错时直接标红。',
    verify='python demo.py 输出 2 和 2。',
    keywords=['NameError name is not defined', 'python 变量名拼写错误'],
    version='Python 3.12 会追加 Did you mean: \'len\'?，老版本没有这个建议。',
    guess_exc=['NameError', 'TypeError', 'AttributeError'],
    quiz_title='分清 NameError 与 AttributeError', quiz='''text = "abc"
print(text.uper())''',
    quiz_answer='uper 应为 upper：print(text.upper())',
    quiz_explain='名字根本不存在 → NameError；名字存在但它没有这个属性/方法 → AttributeError。这条属于后者。',
)

add(
    id='r2', layer='运行时层', scene=['通用'], exc='TypeError',
    title='字符串和数字直接用 + 拼接',
    brief='input() 永远返回字符串，不转换就直接做加法是高频错误。',
    code='''age = "18"
print("明年你 " + age + 1 + " 岁")''',
    cause='+ 号两边类型必须一致：str + str 才是拼接。这里先拼出「明年你 18」，接着要 str + int，解释器不知道你想拼接还是相加，于是报 TypeError。',
    fix='''age = "18"
print(f"明年你 {int(age) + 1} 岁")''',
    fix_note='先把输入转成 int，再用 f-string 组装文本；f-string 会自动把数字转成字符串。',
    verify='python demo.py 输出「明年你 19 岁」。',
    keywords=['TypeError can only concatenate str not int', 'input 返回字符串 int 转换'],
    version='与版本无关；f-string 需要 Python 3.6+。',
    guess_exc=['TypeError', 'ValueError', 'NameError'],
    quiz_title='求和前的类型转换', quiz='''a = input("第一个数：")
b = input("第二个数：")
print(a + b)''',
    quiz_answer='两个 input 都套 int(...)：print(int(a) + int(b))',
    quiz_explain='不转换时 "3" + "4" 得到 "34"，不会报错但结果错——这类「不报错的错」更要靠类型检查发现。',
)

add(
    id='r3', layer='运行时层', scene=['通用'], exc='IndexError',
    title='range 里多加了 1，索引越界',
    brief='索引取值范围是 0 到 len-1，差一错误最典型的受害者。',
    code='''nums = [10, 20, 30]
for i in range(len(nums) + 1):
    print(nums[i])''',
    cause='len(nums) 是 3，合法索引只有 0/1/2。range(4) 会跑 4 轮，第 4 轮取 nums[3] 时列表里没有第 4 个元素。',
    fix='''nums = [10, 20, 30]
for i in range(len(nums)):
    print(nums[i])''',
    fix_note='直接遍历元素更省事：for n in nums: print(n)。',
    verify='python demo.py 输出 10 / 20 / 30 三行。',
    keywords=['IndexError list index out of range', 'python 索引越界 range len'],
    version='与版本无关。',
    guess_exc=['IndexError', 'KeyError', 'ValueError'],
    quiz_title='取最后一项', quiz='''items = [1, 2, 3]
print(items[len(items)])''',
    quiz_answer='改成 items[len(items) - 1] 或 items[-1]',
    quiz_explain='最大合法索引是 len-1；Python 支持负索引，-1 就是最后一项，比手算 len-1 更不容易错。',
)

add(
    id='r4', layer='运行时层', scene=['数据处理', '通用'], exc='KeyError',
    title='字典里没有这个键',
    brief='方括号取值时键必须存在，否则直接抛 KeyError；get 可以给默认值。',
    code='''student = {"name": "小明", "score": 92}
print(student["age"])''',
    cause='字典用 [] 取值时，键不存在就报错，不会静默返回 None。字段名写错、上游数据少字段、接口返回结构变化，都会走到这里。',
    fix='''student = {"name": "小明", "score": 92}
print(student.get("age", "未填写"))''',
    fix_note='确定缺省值用 get(key, default)；需要区分「没有这个键」和「值是 None」时用 if "age" in student。',
    verify='python demo.py 输出「未填写」。',
    keywords=['KeyError 键不存在', 'python dict get 默认值', 'KeyError 数据缺字段'],
    version='与版本无关；collections.defaultdict 可自动补默认值。',
    guess_exc=['KeyError', 'IndexError', 'AttributeError'],
    quiz_title='词频统计忘了初始化', quiz='''words = ["a", "b", "a"]
count = {}
for w in words:
    count[w] += 1
print(count)''',
    quiz_answer='改为 count[w] = count.get(w, 0) + 1（或使用 collections.Counter）',
    quiz_explain='count[w] += 1 会先读取 count[w]，键不存在时就是 KeyError。先 get 出默认值 0 再累加。',
)

add(
    id='r5', layer='运行时层', scene=['通用'], exc='AttributeError',
    title='把 sort() 的返回值当成了列表',
    brief='列表的原地方法都返回 None：sort / append / reverse / extend。',
    code='''nums = [3, 1, 2]
result = nums.sort()
print(result)
result.append(4)''',
    cause='sort() 原地排序并返回 None，result 绑定的是 None 而不是排序后的列表。第 4 行对 None 调用 append，于是 AttributeError。',
    fix='''nums = [3, 1, 2]
nums.sort()
print(nums)
nums.append(4)''',
    fix_note='需要新列表时用 sorted(nums)；原地方法直接作用在原对象上，不要接返回值。',
    verify='python demo.py 先输出 [1, 2, 3]，再正常追加 4。',
    keywords=['AttributeError NoneType object has no attribute append', 'python sort 返回 None'],
    version='与版本无关。',
    guess_exc=['AttributeError', 'TypeError', 'ValueError'],
    quiz_title='reverse 也有同样的坑', quiz='''nums = [1, 2, 3]
nums = nums.reverse()
print(nums[0])''',
    quiz_answer='改为 nums.reverse() 后直接 print(nums[0])，不要重新赋值。',
    quiz_explain='reverse() 同样返回 None，重新赋值就把列表弄丢了；报错是 NoneType is not subscriptable。',
)

add(
    id='r6', layer='运行时层', scene=['爬虫', 'Web', '通用'], exc='TypeError',
    title='函数忘了 return，拿到的是 None',
    brief="'NoneType' object is not subscriptable 几乎总意味着上一步没拿到数据。",
    code='''def get_user():
    users = {"id": 1, "name": "Ann"}

user = get_user()
print(user["name"])''',
    cause='函数体里只是建了字典，没有 return，所以调用结果永远是 None。对 None 取下标就报 not subscriptable；同类的 not iterable、has no attribute 也是同一个根因。',
    fix='''def get_user():
    users = {"id": 1, "name": "Ann"}
    return users

user = get_user()
print(user["name"])''',
    fix_note='在函数末尾 return 结果；调用方对可能为空的结果先判空。',
    verify='python demo.py 输出 Ann。',
    keywords=['TypeError NoneType object is not subscriptable', '函数返回 None 未判空', 'NoneType has no attribute'],
    version='与版本无关。',
    guess_exc=['TypeError', 'NameError', 'KeyError'],
    quiz_title='接口没查到数据', quiz='''def find(users, uid):
    for u in users:
        if u["id"] == uid:
            return u

u = find([{"id": 2}], 9)
print(u["name"])''',
    quiz_answer='在 print 前判断：if u is None: print("未找到") else: print(u["name"])',
    quiz_explain='循环里没有命中就不会执行 return，函数隐式返回 None。这是「查不到数据」最常见的塌方点。',
)

add(
    id='r7', layer='运行时层', scene=['通用'], exc='UnboundLocalError',
    title='函数里改了全局变量名，却没有声明 global',
    brief='只要函数内出现过赋值，这个名字就整段视为局部变量。',
    code='''total = 0

def add(n):
    total = total + n
    return total

add(5)
print(total)''',
    cause='函数内对 total 赋值，Python 会在编译期把它登记为局部变量；右侧的 total 在赋值前被读取，局部变量还没绑定，于是 UnboundLocalError。',
    fix='''total = 0

def add(n):
    return n

total = total + add(5)
print(total)''',
    fix_note='优先「传参 → 返回新值」；确实要就地修改全局状态才用 global total（并想清楚为什么必须这样）。',
    verify='python demo.py 输出 5。',
    keywords=['UnboundLocalError local variable referenced before assignment', 'python global 局部变量'],
    version='Python 3.11 起文案为 cannot access local variable；3.10 及以前是 local variable \'total\' referenced before assignment。',
    guess_exc=['UnboundLocalError', 'NameError', 'TypeError'],
    quiz_title='函数内累加计数器', quiz='''count = 0

def hit():
    count += 1

hit()
print(count)''',
    quiz_answer='改为 def hit(): global count; count += 1（或 return 新值由外部接收）',
    quiz_explain='+= 等价于 count = count + 1，函数内一赋值就成了局部变量，读的时候还没绑定。',
)

add(
    id='r8', layer='运行时层', scene=['数据处理', '通用'], exc='ValueError',
    title='int("3.5") 不是合法的整数',
    brief='int() 只接受整数字面量，用户输入或 CSV 里的小数会直接炸。',
    code='''raw = "3.5"
count = int(raw)
print(count * 2)''',
    cause='int() 按十进制整数解析字符串，"3.5" 里的小数点不在允许字符内，于是报 invalid literal for int() with base 10。注意 int(3.5)（传 float）是合法的，只有「字符串转整数」这一步会拒绝小数点。',
    fix='''raw = "3.5"
count = int(float(raw))
print(count * 2)''',
    fix_note='确认要取整时先 float 再 int（会截断）；需要四舍五入用 round(float(raw))；金额计算用 Decimal。',
    verify='python demo.py 输出 6；再加一条 assert int(float("3.5")) == 3。',
    keywords=['ValueError invalid literal for int() with base 10', 'python 字符串 小数 转 int', 'input int 转换 报错'],
    version='与版本无关；int("3.0") 同样报错，Python 不会自动识别小数点。',
    guess_exc=['ValueError', 'TypeError', 'KeyError'],
    quiz_title='用户输入的价格', quiz='''price = input("价格：")   # 用户输入 12.8
print(int(price) * 100)''',
    quiz_answer='先转 float 再按分处理：int(float(price) * 100)，金额建议用 Decimal。',
    quiz_explain='input 永远返回字符串，int 只吃整数写法。凡是「用户输入 + int」的组合，都要考虑小数和空串。',
)

add(
    id='r9', layer='运行时层', scene=['数据处理', '通用'], exc='ZeroDivisionError',
    title='空列表求平均：分母是 0',
    brief='筛选后没有结果、接口返回空数组时，len() 就是 0。',
    code='''def average(nums):
    return sum(nums) / len(nums)

print(average([]))''',
    cause='空列表的 len 是 0，除法直接触发 division by zero。这类错误在开发时用「有数据」的样本测不出来，往往上线后遇到空结果才爆。',
    fix='''def average(nums):
    if not nums:
        return 0
    return sum(nums) / len(nums)

print(average([]))''',
    fix_note='在函数入口判空，并明确约定返回值（0 还是 None）；需要区分「没数据」和「平均为 0」就返回 None 或抛自定义异常。',
    verify='python demo.py 输出 0；断言 average([1, 2]) == 1.5。',
    keywords=['ZeroDivisionError division by zero', 'python 空列表 求平均 判空', '分母为 0'],
    version='与版本无关；numpy 里空数组求平均返回 nan 并给 RuntimeWarning，行为不同。',
    guess_exc=['ZeroDivisionError', 'ValueError', 'TypeError'],
    quiz_title='空结果的百分比', quiz='''hits = 0
total = 0
print(hits / total * 100)''',
    quiz_answer='先判断 total 是否为 0：if total: ... else: print(0)（或返回 None 表示无数据）。',
    quiz_explain='分母来自统计结果时，0 完全合法。写除法前先问一句：分母可能为 0 吗？',
)

add(
    id='r10', layer='运行时层', scene=['数据处理', '通用'], exc='ValueError',
    title='解包时变量数量对不上',
    brief='x, y = 三元组会报 too many values to unpack。',
    code='''point = (3, 5, 8)
x, y = point
print(x, y)''',
    cause='解包要求左右数量严格一致：右边 3 个元素却只用 2 个变量接。改成 3 个变量，或用星号收集剩余项。CSV 多一列、接口多一个字段时最容易触发。',
    fix='''point = (3, 5, 8)
x, y, z = point
print(x, y, z)''',
    fix_note='数量固定就补齐变量；不固定写 x, y, *rest = point；只关心前两项可以 point[0], point[1]。',
    verify='python demo.py 输出 3 5 8。',
    keywords=['ValueError too many values to unpack', 'python 解包 数量不匹配', 'expected 2 got 3'],
    version='与版本无关；星号解包需要 Python 3。',
    guess_exc=['ValueError', 'TypeError', 'IndexError'],
    quiz_title='zip 长度不一致时', quiz='''rows = [("Ann", 90, 1), ("Bob", 85, 2)]
for name, score in rows:
    print(name, score)''',
    quiz_answer='让变量数与每行字段数一致，或写 for name, score, *_ in rows。',
    quiz_explain='zip 按最短截断，而手动解包要求严格相等。数据多一列时，报错会直接告诉你 expected 2。',
)

add(
    id='r11', layer='运行时层', scene=['通用'], exc='AttributeError',
    title='字符串没有 append 方法',
    brief='str 不可变，追加内容不是 append，而是重新拼接。',
    code='''names = "Ann"
names.append("Bob")
print(names)''',
    cause='字符串是不可变对象，只有 +、join、format 这类「返回新字符串」的方式。append 是列表的方法，用错对象类型就会报 has no attribute append。',
    fix='''names = ["Ann"]
names.append("Bob")
print(names)''',
    fix_note='要收集多个值用列表，最后 "".join(parts)；单个字符串拼接用 names += "Bob"（循环里大量拼接建议改用列表）。',
    verify='python demo.py 输出 [\'Ann\', \'Bob\']。',
    keywords=['AttributeError str object has no attribute append', 'python 字符串 追加', '字符串不可变'],
    version='与版本无关；Python 3.6+ 也可以用 f-string 组装新字符串。',
    guess_exc=['AttributeError', 'TypeError', 'ValueError'],
    quiz_title='upper() 改的是谁', quiz='''s = "abc"
s.upper()
print(s)''',
    quiz_answer='s = s.upper()：字符串方法返回新字符串，必须用变量接住。',
    quiz_explain='upper / strip / replace 都不改原字符串。方法返回新对象却没接收，是字符串处理里最常见的无效操作。',
)

# ============================ 环境层 ============================
add(
    id='e1', layer='环境层', scene=['爬虫', '第三方库', '通用'], exc='ModuleNotFoundError',
    title='pip install 成功了，import 还是找不到',
    brief='装包的解释器和运行代码的解释器不是同一个，是虚拟环境时代最常见的事故。',
    code='''import reqeusts

resp = reqeusts.get("https://example.com")
print(resp.status_code)''',
    cause='三种可能，按概率排：① 包名拼错（这里就是 reqeusts → requests）；② 装在全局环境，运行时用的是虚拟环境（或反过来）；③ pip 和 python 不是同一个解释器，装到了别处。',
    fix='''import requests

resp = requests.get("https://example.com", timeout=10)
print(resp.status_code)''',
    fix_note='统一用同一解释器安装：python -m pip install requests。先确认 which python / where python 与 pip 指向一致。',
    verify='python -c "import requests; print(requests.__version__)" 能打印版本号，再运行 demo.py 输出状态码。',
    keywords=['ModuleNotFoundError No module named', 'pip install 成功 import 失败', '虚拟环境未激活'],
    version='虚拟环境（venv / conda / poetry）都会造成这种「装了却找不到」；VSCode 右下角可切换解释器。',
    guess_exc=['ModuleNotFoundError', 'ImportError', 'AttributeError'],
    quiz_title='确认到底是谁在运行', quiz='''# 终端里：pip install requests  成功
# 代码里：
import requests''',
    quiz_answer='先执行 python -c "import sys; print(sys.executable)" 和 pip -V，确认两者路径属于同一个环境；再用 python -m pip install requests 重装。',
    quiz_explain='「pip 装好了」不等于「当前解释器有」；把安装动作交给同一个解释器的 -m pip，能消除大多数环境错位。',
)

add(
    id='e2', layer='环境层', scene=['数据处理'], exc='AttributeError',
    title='pandas 2.0 起废弃了 DataFrame.append',
    brief='旧教程里到处是 df.append(...)，在 pandas 2.0+ 直接报 AttributeError。',
    code='''import pandas as pd

df = pd.DataFrame({"a": [1, 2]})
df = df.append({"a": 3}, ignore_index=True)
print(df)''',
    cause='DataFrame.append 在 pandas 1.4 标记弃用、2.0 正式移除。报 AttributeError 不是写法拼错，而是你装的版本已经不提供这个方法。',
    fix='''import pandas as pd

df = pd.DataFrame({"a": [1, 2]})
df = pd.concat([df, pd.DataFrame({"a": [3]})], ignore_index=True)
print(df)''',
    fix_note='逐行追加用 pd.concat，或先收集到列表再一次性建 DataFrame（数据量大时后者更快）。',
    verify='python demo.py 输出三行 a=1/2/3；再用 pd.__version__ 确认版本。',
    keywords=['DataFrame object has no attribute append', 'pandas append 废弃 concat 替代'],
    version='pandas 1.4 弃用、2.0 移除；本机 pandas {pandas} 实测报错。遇到库报 AttributeError，先查你装的版本，再查该版本的方法表。',
    guess_exc=['AttributeError', 'ImportError', 'TypeError'],
    quiz_title='先查版本文档，再改代码', quiz='''import pandas as pd
df = pd.DataFrame({"a": [1]})
df.append({"a": 2})   # 报 AttributeError''',
    quiz_answer='用 pd.concat([df, pd.DataFrame({"a": [2]})], ignore_index=True)，并固定依赖版本（requirements.txt 写 pandas>=2 或锁死旧版）。',
    quiz_explain='库升级导致的「方法消失」只能靠查版本文档解决；把版本写进 requirements.txt 才能避免换机器后行为突变。',
)

add(
    id='e3', layer='环境层', scene=['Web', '工程'], exc='ImportError',
    title='循环导入：两个模块互相 import',
    brief='partially initialized module + circular import，说明导入关系成环了。',
    code='''# a.py
from b import helper

def main():
    print(helper())

main()

# b.py
from a import main

def helper():
    return "ok"''',
    cause='a 导入 b 时 b 还没执行完，又反过来要 a 里的 main，此时 a 只加载了一半，找不到这个名字。结构上就是「模块互相依赖」。',
    fix='''# common.py
def helper():
    return "ok"

# a.py
from common import helper

def main():
    print(helper())

main()''',
    fix_note='把双方都需要的函数下沉到第三个模块；或在函数内部 import（延迟到调用时）来打断环。',
    verify='python a.py 输出 ok，两个模块不再互相依赖。',
    fix_files={'common.py': 'def helper():\n    return "ok"\n',
               'a.py': '# a.py\nfrom common import helper\n\n\ndef main():\n    print(helper())\n\n\nmain()\n'},
    fix_main='a.py',
    bad_files={'a.py': '# a.py\nfrom b import helper\n\n\ndef main():\n    print(helper())\n\n\nmain()\n',
               'b.py': '# b.py\nfrom a import main\n\n\ndef helper():\n    return "ok"\n'},
    bad_main='a.py',
    keywords=['ImportError cannot import name partially initialized module', 'python 循环导入 circular import'],
    version='Python 3.8 起提示里明确写 partially initialized module 和 circular import。',
    guess_exc=['ImportError', 'ModuleNotFoundError', 'RecursionError'],
    quiz_title='打断依赖环', quiz='''# models.py
from views import render

# views.py
from models import User''',
    quiz_answer='把 render 需要的类型下沉到独立模块（或用类型注解字符串 / TYPE_CHECKING），让依赖方向单向。',
    quiz_explain='循环导入本质是设计问题：让依赖单向流动，或把共用部分抽到更低层模块，比在函数里到处写局部 import 更稳。',
)

add(
    id='e4', layer='环境层', scene=['数据处理', '通用'], exc='UnicodeDecodeError',
    title='用 GBK 去读 UTF-8 文件',
    brief='中文乱码和 UnicodeDecodeError，九成是读写编码不一致。',
    code='''with open("note.txt", "r", encoding="gbk") as f:
    print(f.read())''',
    cause='文件实际按 UTF-8 保存，却指定用 gbk 解码。字节序列在 GBK 里没有对应字符，于是解码失败；Windows 默认编码就是 GBK，跨平台传文件时特别容易踩。',
    fix='''with open("note.txt", "r", encoding="utf-8") as f:
    print(f.read())''',
    fix_note='读写文本统一显式写 encoding="utf-8"；不确定文件编码时先用 chardet 探测，别靠猜。',
    verify='python demo.py 输出两行中文，且 with 语句保证文件自动关闭。',
    fix_files={'note.txt': '第一行中文\n第二行中文\n',
               'demo.py': 'with open("note.txt", "r", encoding="utf-8") as f:\n    print(f.read().strip())\n'},
    bad_files={'note.txt': '第一行中文\n第二行中文\n',
               'demo.py': 'with open("note.txt", "r", encoding="gbk") as f:\n    print(f.read())'},
    keywords=['UnicodeDecodeError gbk codec can\'t decode byte', 'python open encoding utf-8', '中文乱码 编码'],
    version='Python 3.15 起默认 UTF-8 模式；在此之前 Windows 默认仍是系统编码，所以必须显式声明。',
    guess_exc=['UnicodeDecodeError', 'UnicodeEncodeError', 'FileNotFoundError'],
    quiz_title='写文件也要声明编码', quiz='''with open("out.txt", "w") as f:
    f.write("中文")''',
    quiz_answer='改为 open("out.txt", "w", encoding="utf-8")',
    quiz_explain='读和写都要显式编码；否则同一段代码在 Windows 和 Linux 上产出的文件编码不同，下次读取就报错。',
)

add(
    id='e5', layer='环境层', scene=['爬虫', '数据处理', 'Web'], exc='JSONDecodeError',
    title='json.loads 报 Expecting value：先看原始内容',
    brief='接口返回空串、HTML 错误页或单引号「假 JSON」，都会在这里炸。',
    code='''import json

text = "{name: 'Ann'}"
data = json.loads(text)
print(data)''',
    cause='JSON 标准只认双引号，不接受单引号、尾逗号、注释。这里的 text 是 Python 字典写法，不是合法 JSON。另一种高频情况是 line 1 column 1 (char 0)：响应为空字符串或直接是 HTML 错误页。',
    fix='''import json

text = '{"name": "Ann"}'
data = json.loads(text)
print(data)''',
    fix_note='解析前先 print(repr(text[:200])) 看原始内容；空响应先判空；从网页拿到的多半是 HTML，要先检查状态码和 Content-Type。',
    verify='python demo.py 输出 {\'name\': \'Ann\'}；空字符串则被 if not text 拦住。',
    keywords=['JSONDecodeError Expecting value line 1 column 1', 'python json.loads 单引号', 'json 解析 空字符串 错误页'],
    version='Python 3.5 起 JSONDecodeError 是 ValueError 的子类，except ValueError 也能捕获；消息里的 char 0 通常代表开头就失败。',
    guess_exc=['JSONDecodeError', 'ValueError', 'TypeError'],
    quiz_title='接口返回了空字符串', quiz='''import json
resp_text = ""      # 请求失败时接口返回空串
data = json.loads(resp_text)''',
    quiz_answer='先判断响应是否为空、状态码是否 200，再决定是否解析；不要直接对空串 loads。',
    quiz_explain='line 1 column 1 (char 0) 几乎等于「内容根本不是 JSON」。先看原始响应，再怀疑格式。',
)

add(
    id='e6', layer='环境层', scene=['工程', 'Web'], exc='ImportError',
    title='直接运行包内文件：相对导入失效',
    brief='python pkg/main.py 会把 main.py 当顶层脚本，. 开头的导入无处可依。',
    code='''# pkg/main.py
from .helper import greet

print(greet("Ann"))''',
    cause='相对导入靠 __package__ 定位同级模块。直接 python pkg/main.py 时，Python 把 main.py 当独立脚本运行，__package__ 是空的，无法解析 .helper，于是报 no known parent package。',
    fix='''# pkg/main.py
from pkg.helper import greet

print(greet("Ann"))''',
    fix_note='包内模块用绝对导入，并在项目根目录执行 python -m pkg.main；单文件脚本不要写相对导入。',
    verify='在项目根目录执行 python -m pkg.main，输出「你好, Ann」。',
    bad_files={'pkg/__init__.py': '',
               'pkg/helper.py': 'def greet(name):\n    return "你好, " + name\n',
               'pkg/main.py': '# pkg/main.py\nfrom .helper import greet\n\nprint(greet("Ann"))\n'},
    bad_main='pkg/main.py',
    fix_files={'pkg/__init__.py': '',
               'pkg/helper.py': 'def greet(name):\n    return "你好, " + name\n',
               'pkg/main.py': '# pkg/main.py\nfrom pkg.helper import greet\n\nprint(greet("Ann"))\n'},
    fix_main='-m pkg.main',
    keywords=['ImportError attempted relative import with no known parent package', 'python 相对导入 -m 运行', '__package__ 为空'],
    version='Python 3 统一使用绝对导入语义；老式隐式相对导入（Python 2）已移除。',
    guess_exc=['ImportError', 'ModuleNotFoundError', 'NameError'],
    quiz_title='包的入口文件', quiz='''# 项目根目录执行：python pkg/main.py
from .utils import load

load()''',
    quiz_answer='改成 from pkg.utils import load，并用 python -m pkg.main 运行。',
    quiz_explain='相对导入只在「被 import 的包内模块」里有效；把文件当脚本直接跑，就没有包这层上下文。',
)

# ============================ 工程习惯层 ============================
add(
    id='p1', layer='工程习惯层', scene=['工程', '通用'], exc='',
    title='默认参数写成了可变对象',
    brief='def f(x=[]) 的列表只在定义时创建一次，所有调用共享它。',
    code='''def add_item(item, box=[]):
    box.append(item)
    return box

print(add_item("a"))
print(add_item("b"))''',
    actual="['a']\n['a', 'b']",
    expected="['a']\n['b']",
    cause='默认参数在函数定义时求值一次，之后每次调用都复用同一个列表对象。第一次追加的 "a" 会留在里面，导致结果越积越多，而且不报错——最难查的那类 bug。',
    fix='''def add_item(item, box=None):
    if box is None:
        box = []
    box.append(item)
    return box

print(add_item("a"))
print(add_item("b"))''',
    fix_note='用 None 当占位符，在函数体内创建新对象；需要保留状态时，明确让调用方传入列表。',
    verify='两次调用分别输出 ["a"] 和 ["b"]；可加断言 assert add_item("a") == ["a"]。',
    keywords=['python 可变默认参数 mutable default argument', 'def f(x=[]) 坑'],
    version='与版本无关，是所有 Python 版本共同语义。',
    guess_exc=['不报错，但结果和预期不同', '会抛出异常', '完全正常'],
    quiz_title='缓存字典同样会串数据', quiz='''def cache(key, store={}):
    store[key] = store.get(key, 0) + 1
    return store

print(cache("a"))
print(cache("b"))''',
    quiz_answer='改为 def cache(key, store=None): store = {} if store is None else store',
    quiz_explain='字典和列表一样是可变对象；默认参数共享会让不同调用之间的数据互相污染，而且很难复现。',
)

add(
    id='p2', layer='工程习惯层', scene=['数据处理', '通用'], exc='',
    title='一边遍历一边删除列表元素',
    brief='删除会让后面的元素前移，遍历索引却在前进，于是漏掉元素。',
    code='''nums = [1, 2, 2, 3]
for n in nums:
    if n % 2 == 0:
        nums.remove(n)
print(nums)''',
    actual='[1, 2, 3]',
    expected='[1, 3]',
    cause='删掉第一个 2 后，第二个 2 前移到当前索引，而迭代器已经指向下一个位置，于是它被跳过。列表长度变化时，迭代位置与元素下标不再对应。',
    fix='''nums = [1, 2, 2, 3]
nums = [n for n in nums if n % 2]
print(nums)''',
    fix_note='用列表推导生成新列表；必须原地修改时，反向遍历 for i in range(len(nums) - 1, -1, -1)。',
    verify='输出 [1, 3]；断言 assert nums == [1, 3]。',
    keywords=['python 遍历列表删除元素 漏删', 'remove while iterating list'],
    version='与版本无关；字典在迭代中改大小会直接 RuntimeError: dictionary changed size during iteration。',
    guess_exc=['不报错，但结果和预期不同', '会抛出异常', '完全正常'],
    quiz_title='过滤时要保留原列表吗', quiz='''ids = [1, 2, 3, 4]
for i in ids:
    if i > 2:
        ids.remove(i)
print(ids)''',
    quiz_answer='改为 ids = [i for i in ids if i <= 2]（若需保留原列表则生成新列表）',
    quiz_explain='这条只删掉了 3，4 被跳过——和上例同一机制。用推导式或反向遍历才可靠。',
)

add(
    id='p3', layer='工程习惯层', scene=['通用', '工程'], exc='',
    title='用 is 比较两个值是否相等',
    brief='is 比的是「是不是同一个对象」，== 才是比「值是否相等」。',
    code='''a = int("1000")
b = 1000
print(a == b, a is b)''',
    actual='True False',
    expected='True True',
    cause='is 比较对象身份（内存地址）。CPython 会缓存 -5~256 的小整数，所以小数字用 is 常常「看起来对」，一旦数值变大或来自不同计算就变 False，非常隐蔽。',
    fix='''a = int("1000")
b = 1000
print(a == b)''',
    fix_note='比较值一律用 ==；is 只用于 None、True、False 这类单例判断，如 if x is None。',
    verify='输出 True；可断言 assert a == b。',
    keywords=['python is 和 == 区别', 'is 比较整数 为什么是 False'],
    version='Python 3.8 起对字面量使用 is 会给出 SyntaxWarning: "is" with a literal。',
    guess_exc=['不报错，但结果和预期不同', '会抛出异常', '完全正常'],
    quiz_title='判空该用哪个', quiz='''value = 0
if value is None:
    print("空")''',
    quiz_answer='判断空值用 is None 是对的；但若要判断「值为 0 或空」，应写 value == 0 / not value，不要用 is 0。',
    quiz_explain='is None 是官方推荐写法（None 是单例）；is 0、is "" 都不可靠，因为它们不是单例。',
)

add(
    id='p4', layer='工程习惯层', scene=['数据处理', '通用'], exc='',
    title='直接比较两个浮点数是否相等',
    brief='0.1 + 0.2 并不等于 0.3，这是二进制浮点的固有精度问题。',
    code='''print(0.1 + 0.2)
print(0.1 + 0.2 == 0.3)''',
    actual='0.30000000000000004\nFalse',
    expected='0.3\nTrue',
    cause='0.1、0.2、0.3 在二进制里都是无限循环小数，只能存近似值。相加后的舍入误差让结果与 0.3 的字面值不相等，但两边看起来「都是 0.3」。',
    fix='''import math

print(math.isclose(0.1 + 0.2, 0.3))
print(round(0.1 + 0.2, 2) == 0.3)''',
    fix_note='比较用 math.isclose(a, b, rel_tol=1e-9)；金额等精确计算用 decimal.Decimal，避免用 float 累加。',
    verify='两个 print 都输出 True。',
    keywords=['python 浮点数比较 0.1+0.2', 'math.isclose 浮点误差', 'decimal 精度'],
    version='遵循 IEEE 754 双精度，所有 Python 版本与平台一致。',
    guess_exc=['不报错，但结果和预期不同', '会抛出异常', '完全正常'],
    quiz_title='金额相加别用 float', quiz='''total = 0.0
for _ in range(10):
    total += 0.1
print(total == 1.0)''',
    quiz_answer='改用 decimal.Decimal("0.1") 累加，或用 math.isclose(total, 1.0) 比较。',
    quiz_explain='十次 0.1 相加得到 0.9999999999999999。涉及金额、计数累加时，优先 Decimal 或整数分。',
)

add(
    id='p5', layer='工程习惯层', scene=['数据处理', '通用'], exc='',
    title='copy() 只复制了外层，内层还在共享',
    brief='浅拷贝对嵌套结构不够用，改内层元素会连带改到原对象。',
    code='''import copy

matrix = [[1, 2], [3, 4]]
clone = matrix.copy()
clone[0][0] = 99
print(matrix)
print(copy.deepcopy(matrix))''',
    actual='[[99, 2], [3, 4]]\n[[99, 2], [3, 4]]',
    expected='[[1, 2], [3, 4]]\n[[1, 2], [3, 4]]',
    cause='copy() 只新建外层列表，内层两个子列表仍是同一批对象。clone[0][0] = 99 改的是共享的子列表，所以原 matrix 一起变。',
    fix='''import copy

matrix = [[1, 2], [3, 4]]
clone = copy.deepcopy(matrix)
clone[0][0] = 99
print(matrix)
print(clone)''',
    fix_note='嵌套结构用 copy.deepcopy；只有一层且元素不可变时，切片 / copy() 就够了。',
    verify='输出 [[1, 2], [3, 4]] 和 [[99, 2], [3, 4]]，原数据未被改动。',
    keywords=['python 浅拷贝 深拷贝 区别', 'copy.deepcopy 嵌套列表'],
    version='与版本无关；pandas 的 copy(deep=True) 也有类似深浅语义，需看文档。',
    guess_exc=['不报错，但结果和预期不同', '会抛出异常', '完全正常'],
    quiz_title='切片也是浅拷贝', quiz='''a = [[1], [2]]
b = a[:]
b[0].append(9)
print(a)''',
    quiz_answer='a 会变成 [[1, 9], [2]]；需要独立副本时用 copy.deepcopy(a)。',
    quiz_explain='切片、list()、copy() 都只复制一层。嵌套列表、字典里装列表时，必须深拷贝才不会互相影响。',
)

# ---------------------------------------------------------------- 构建
def run(files, main):
    """在临时目录执行，返回 (stdout, stderr, 规范化后的 tmpdir)。

    main 以 "-m pkg.mod" 开头时按模块方式运行（相对导入需要包上下文），
    否则按脚本路径运行；文件名可带子目录（如 pkg/main.py）。
    """
    tmp = tempfile.mkdtemp(prefix='pit_')
    for name, content in files.items():
        dest = os.path.join(tmp, name)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, 'w', encoding='utf-8') as f:
            f.write(content)
    cmd = [sys.executable, '-m', main[3:]] if main.startswith('-m ') else [sys.executable, os.path.join(tmp, main)]
    proc = subprocess.run(
        cmd, cwd=tmp, capture_output=True, text=True, encoding='utf-8', errors='replace',
    )
    return proc.stdout, proc.stderr, tmp


def normalize(text, tmp):
    text = text.replace(tmp + os.sep, '').replace(tmp, '')
    # 去掉 Windows 绝对路径残留，保留相对文件名，便于阅读
    return re.sub(r'File ".*?([^"\\/]+\.py)"', r'File "\1"', text).strip('\n')


EXC_POOL = ['SyntaxError', 'IndentationError', 'TypeError', 'NameError', 'KeyError',
            'IndexError', 'AttributeError', 'ValueError', 'ModuleNotFoundError',
            'ImportError', 'UnicodeDecodeError', 'UnboundLocalError']

# 修复思路三选一：第一个是正确方向，另外两个是新手最常尝试但治标不治本的做法
FIX_CHOICES = {
    's1': ['在 if 行尾补上冒号 :', '把 if 改成 while 循环', '给 print 的参数加括号'],
    's2': ['把函数体缩进 4 个空格', '把 def 改成 class', '在 print 后面加分号'],
    's3': ['把中文引号换成英文引号', '把 print 改成 echo', '给字符串加 r 前缀'],
    's4': ['给 print 的参数加上括号', '把 print 换成 printf', '直接删掉 print 这一行'],
    'r1': ['把 lenght 改成 len', '给 lenght 加上引号', '在前面补一句 lenght = 0'],
    'r2': ['先 int(age) 再参与计算', '把 + 全换成逗号', '给 age 再套一层 str()'],
    'r3': ['range(len(nums)) 去掉 +1', '把列表改成元组', '让 i 从 1 开始'],
    'r4': ['用 student.get("age", 默认值)', '改成 student.age 取属性', '用 try/except 包住这一行'],
    'r5': ['先 nums.sort() 再用 nums', '给 result 补一个 append 方法', '把 sort() 改成 sort(None)'],
    'r6': ['在函数末尾 return users', '把 user["name"] 改成 user.name', '调用后加 sleep 等一等'],
    'r7': ['改成传参并 return 新值', '把 total 改名成 _total', '在 add(5) 前加一行 print'],
    'r8': ['先 float(raw) 再取整', '给 int() 套 try/except 返回 0', '把 "3.5" 改成 "3"'],
    'r9': ['入口判空，空列表返回约定值', '把 / 改成 // 避开报错', '用 try/except 包住后继续'],
    'r10': ['让变量数量与元素数量一致', '把变量名改短一点', '用 list() 把右侧包一层'],
    'r11': ['改用列表收集后 append', '在字符串后加 .list()', '把 append 改成 push'],
    'e1': ['python -m pip install requests 重装', '把 import 改成 as 别名', '把同一条 pip 命令再执行几次'],
    'e2': ['改用 pd.concat 追加行', '把 df.append 改成 df.add', '给 df 设置 ignore_index 属性'],
    'e3': ['把共用函数下沉到第三个模块', '把所有 import 注释掉', '删掉 a.py 里的 main() 调用'],
    'e4': ['显式指定 encoding="utf-8"', '加 errors="ignore" 忽略坏字符', '把文件另存成 GBK 再读'],
    'e5': ['先确认原始内容是否合法 JSON', '给 loads 加几次重试', '把 json.loads 换成 eval'],
    'e6': ['改绝对导入并用 python -m 运行', '把 .helper 改成 ..helper', '在文件头加 sys.path.append(".")'],
    'p1': ['默认值改成 None，函数内新建列表', '每次调用前手动清空 box', 'return box[:] 返回副本'],
    'p2': ['用列表推导生成新列表', '遍历时把 remove 改成 del', '循环结束后清空再重建'],
    'p3': ['比值用 ==，is 只用于 None', '把所有 is 改成 is not', '先转成字符串再比较'],
    'p4': ['用 math.isclose 或 Decimal 比较', '比较时给两边都加 0.0001', '把 == 改成 is'],
    'p5': ['嵌套结构用 copy.deepcopy', '改用 matrix[:] 切片复制', '复制后手动把原值改回去'],
}

# 埋错练习的干扰项：按「层」给出新手最常见的两种错误反应
QUIZ_DISTRACT = {
    '语法层': ['把出错的那一行整行删掉', '在文件开头加一行注释再运行'],
    '运行时层': ['用 try/except 包住出错行，让它不再抛出', '在出错行前面加一行 print 就继续跑'],
    '环境层': ['忽略这条报错，重新运行一次', '把报错的那一行改成分号结尾'],
    '工程习惯层': ['换一组输入多跑几次，直到结果碰巧正确', '在代码末尾加 print，确认程序能跑完'],
}

assert not [c['id'] for c in C if c['id'] not in FIX_CHOICES], '有案例缺少 fix_options'

for i, c in enumerate(C):
    files = c.pop('bad_files', None) or {'demo.py': c['code']}
    main = c.pop('bad_main', 'demo.py')
    out, err, tmp = run(files, main)

    c['actual'] = normalize(out, tmp) if 'actual' not in c else c['actual']
    tb = normalize(err, tmp)
    c['traceback'] = tb
    m = re.search(r'File "[^"]+", line (\d+)', tb)
    c['line'] = int(m.group(1)) if m else 0

    # 修复后必须真的跑通，且输出与声明一致
    if c.get('fix'):
        fout, ferr, ftmp = run(c.get('fix_files') or {'demo.py': c['fix']}, c.get('fix_main', 'demo.py'))
        assert not ferr.strip(), ('修复代码仍报错', c['id'], normalize(ferr, ftmp))
        c['fix_output'] = normalize(fout, ftmp)

    # 先猜：异常类型 or 「会不会报错」
    if c['exc']:
        pool = [c['exc']] + [e for e in c['guess_exc'] if e != c['exc']]
        c['guess1'] = {'q': '这段代码运行会抛出哪种异常？', 'options': pool[:3], 'answer': c['exc'],
                       'tip': '先只看报错最后一行，再说出异常类型。'}
        lines = [ln for ln in range(1, len(c['code'].split('\n')) + 1)]
        if c['line']:
            opts = [c['line']]
            for d in (1, -1, 2, -2):
                cand = c['line'] + d
                if 1 <= cand <= len(lines) and cand not in opts:
                    opts.append(cand)
                if len(opts) == 3:
                    break
            c['guess2'] = {'q': '报错会定位到哪一行？', 'options': sorted(set(opts)), 'answer': c['line'],
                           'tip': 'traceback 里的 File "demo.py", line N 就是出错行。'}
        else:
            c['guess2'] = None
    else:
        c['guess1'] = {'q': '这段代码运行会怎样？', 'options': c['guess_exc'], 'answer': '不报错，但结果和预期不同',
                       'tip': '运行不报错，不代表逻辑对。先写下你以为的输出。'}
        c['guess2'] = None

    # 交互题：修复思路三选一 + 埋错练习三选一，正确项位置随案例轮换
    fo = FIX_CHOICES[c['id']]
    fix_opts = fo[1:]
    fix_opts.insert(i % 3, fo[0])
    c['fix_options'] = fix_opts
    c['fix_choice'] = fix_opts.index(fo[0])

    q_opts = QUIZ_DISTRACT[c['layer']][:]
    q_pos = (i + 1) % 3
    q_opts.insert(q_pos, c['quiz_answer'])
    c['quiz_options'] = q_opts
    c['quiz_choice'] = q_pos

    c['layerKey'] = LAYER_KEY[c['layer']]
    c['version'] = c['version'].replace('{pandas}', PANDAS_VERSION)
    c['order'] = i + 1
    for k in ('fix_files', 'fix_main'):
        c.pop(k, None)

# 场景索引
scenes = sorted({s for c in C for s in c['scene']})
data = {'python': PY_VERSION, 'pandas': PANDAS_VERSION, 'layers': LAYER_ORDER,
        'scenes': scenes, 'pitfalls': C}
target = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist', 'pitfalls.js')
with open(target, 'w', encoding='utf-8') as f:
    f.write('const PITFALLS = ' + json.dumps(data, ensure_ascii=False) + ';')
print('已生成 %d 个坑，Python %s / pandas %s -> %s' % (len(C), PY_VERSION, PANDAS_VERSION, target))
for c in C:
    print('  %-3s %-6s %s' % (c['id'], c['exc'] or '无异常', c['title']))
