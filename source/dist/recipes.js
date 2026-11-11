const RECIPES = [
 {
  "id": "r01",
  "scene": "列表处理",
  "title": "统计偶数个数",
  "task": "给定一个整数列表，统计其中偶数的个数并打印。",
  "input": "nums = [1, 2, 3, 4, 5, 6]",
  "output": "3",
  "need": [
   "for 遍历",
   "% 取余判断",
   "计数器累加"
  ],
  "steps": [
   "for 遍历：逐个取出列表元素",
   "% 取余判断：n % 2 == 0 即为偶数",
   "计数器累加：满足条件就 count += 1"
  ],
  "pool": [
   "for 遍历",
   "% 取余判断",
   "计数器累加",
   "sort 排序",
   "split 拆分",
   "列表推导筛选",
   "len 计数",
   "replace 替换"
  ],
  "code": "nums = [1, 2, 3, 4, 5, 6]\ncount = 0\nfor n in nums:\n    if n % 2 == 0:\n        count += 1\nprint(count)",
  "alt": {
   "need": [
    "列表推导筛选",
    "len 计数"
   ],
   "steps": [
    "列表推导筛选：[n for n in nums if n % 2 == 0] 直接得到偶数列表",
    "len 计数： len(列表) 就是偶数个数"
   ],
   "code": "nums = [1, 2, 3, 4, 5, 6]\nevens = [n for n in nums if n % 2 == 0]\nprint(len(evens))"
  },
  "tip": "「遍历 + 判断 + 计数」是统计类问题的通用三板斧；列表推导 + len 是更简洁的等价组合。"
 },
 {
  "id": "r02",
  "scene": "列表处理",
  "title": "求所有正数的和",
  "task": "列表里有正有负，把正数挑出来求和并打印。",
  "input": "nums = [3, -1, 7, 0, -5, 8]",
  "output": "18",
  "need": [
   "for 遍历",
   "if 条件筛选",
   "累加求和"
  ],
  "steps": [
   "for 遍历：逐个取出元素",
   "if 条件筛选：只要 n > 0 的元素",
   "累加求和：total += n"
  ],
  "pool": [
   "for 遍历",
   "if 条件筛选",
   "累加求和",
   "生成式筛选",
   "sum 求和",
   "sort 排序",
   "count 统计次数",
   "join 拼接"
  ],
  "code": "nums = [3, -1, 7, 0, -5, 8]\ntotal = 0\nfor n in nums:\n    if n > 0:\n        total += n\nprint(total)",
  "alt": {
   "need": [
    "生成式筛选",
    "sum 求和"
   ],
   "steps": [
    "生成式筛选：n for n in nums if n > 0 逐个给出正数",
    "sum 求和：sum(...) 直接累加，无需手写循环"
   ],
   "code": "nums = [3, -1, 7, 0, -5, 8]\nprint(sum(n for n in nums if n > 0))"
  },
  "tip": "筛选 + 聚合是最常见的组合之一；sum 可以直接吃生成式，省掉中间列表。"
 },
 {
  "id": "r03",
  "scene": "字典与最值",
  "title": "找出最高分的人",
  "task": "字典存了姓名和成绩，找出成绩最高的人，打印姓名和分数。",
  "input": "scores = {'小明': 80, '小红': 95, '小刚': 88}",
  "output": "小红 95",
  "need": [
   "items 遍历字典",
   "if 比较更新",
   "变量记录最值"
  ],
  "steps": [
   "items 遍历字典：同时拿到姓名和分数",
   "if 比较更新：分数更高就更新记录",
   "变量记录最值：用 high 和 best 保存当前最高"
  ],
  "pool": [
   "items 遍历字典",
   "if 比较更新",
   "变量记录最值",
   "max+key 最值",
   "get 取值",
   "split 拆分",
   "append 收集",
   "% 取余判断"
  ],
  "code": "scores = {'小明': 80, '小红': 95, '小刚': 88}\nbest = ''\nhigh = -1\nfor name, s in scores.items():\n    if s > high:\n        high = s\n        best = name\nprint(best, high)",
  "alt": {
   "need": [
    "max+key 最值",
    "get 取值"
   ],
   "steps": [
    "max+key 最值：max(scores, key=scores.get) 按分数找姓名",
    "get 取值：scores[best] 取回最高分"
   ],
   "code": "scores = {'小明': 80, '小红': 95, '小刚': 88}\nbest = max(scores, key=scores.get)\nprint(best, scores[best])"
  },
  "tip": "手写「打擂台」循环要掌握；max/min 配 key 参数是等价的内置组合。"
 },
 {
  "id": "r04",
  "scene": "字符串处理",
  "title": "名字规范化后拼接",
  "task": "一组小写英文名字，把每个名字首字母大写，再用空格连成一个字符串打印。",
  "input": "names = ['tom', 'alice', 'bob']",
  "output": "Tom Alice Bob",
  "need": [
   "for 遍历",
   "capitalize 处理",
   "append 收集",
   "join 拼接"
  ],
  "steps": [
   "for 遍历：逐个取出名字",
   "capitalize 处理：首字母大写",
   "append 收集：处理结果放进新列表",
   "join 拼接：' '.join(列表) 用空格连接"
  ],
  "pool": [
   "for 遍历",
   "capitalize 处理",
   "append 收集",
   "join 拼接",
   "生成式处理",
   "upper 全大写",
   "split 拆分",
   "sort 排序"
  ],
  "code": "names = ['tom', 'alice', 'bob']\nresult = []\nfor n in names:\n    result.append(n.capitalize())\nprint(' '.join(result))",
  "alt": {
   "need": [
    "生成式处理",
    "join 拼接"
   ],
   "steps": [
    "生成式处理：n.capitalize() for n in names 边遍历边处理",
    "join 拼接：直接交给 join，无需中间列表"
   ],
   "code": "names = ['tom', 'alice', 'bob']\nprint(' '.join(n.capitalize() for n in names))"
  },
  "tip": "「逐个处理 + 收集 + join」是字符串批量加工的固定套路。"
 },
 {
  "id": "r05",
  "scene": "字符串处理",
  "title": "统计单词个数",
  "task": "给定一句英文，统计里面有多少个单词（单词之间用空格隔开）。",
  "input": "text = 'python is easy to learn'",
  "output": "5",
  "need": [
   "split 分词",
   "len 计数"
  ],
  "steps": [
   "split 分词：text.split() 按空白切成单词列表",
   "len 计数：len(列表) 得到单词数"
  ],
  "pool": [
   "split 分词",
   "len 计数",
   "strip 去空白",
   "replace 替换",
   "for 遍历",
   "join 拼接"
  ],
  "code": "text = 'python is easy to learn'\nwords = text.split()\nprint(len(words))",
  "alt": null,
  "tip": "split() 不传参数会自动处理连续空格，比 split(' ') 更稳。"
 },
 {
  "id": "r06",
  "scene": "字符串处理",
  "title": "清洗并重新拼接数据",
  "task": "一串逗号分隔的水果名，带多余空格和大小写混乱。要求转成全小写、去掉多余空格，用 | 连接后打印。",
  "input": "text = ' apple, BANANA ,Cherry '",
  "output": "apple|banana|cherry",
  "need": [
   "split 拆分",
   "strip 去空格",
   "lower 转小写",
   "append 收集",
   "join 拼接"
  ],
  "steps": [
   "split 拆分：按逗号切开",
   "strip 去空格：去掉每段两头空白",
   "lower 转小写：统一大小写",
   "append 收集：清洗结果放进列表",
   "join 拼接：'|'.join(列表)"
  ],
  "pool": [
   "split 拆分",
   "strip 去空格",
   "lower 转小写",
   "append 收集",
   "join 拼接",
   "sort 排序",
   "replace 替换",
   "for 遍历"
  ],
  "code": "text = ' apple, BANANA ,Cherry '\nparts = text.split(',')\nclean = []\nfor p in parts:\n    clean.append(p.strip().lower())\nprint('|'.join(clean))",
  "alt": null,
  "tip": "真实数据清洗就是「拆 → 逐个清洗 → 收集 → 拼」四步组合，顺序不能乱。"
 },
 {
  "id": "r07",
  "scene": "字符串处理",
  "title": "找出包含 py 的单词",
  "task": "给定一串以空格分隔的单词，把包含字母组合 py 的单词挑出来，组成列表打印。",
  "input": "words = 'python happy copy java'",
  "output": "['python', 'happy', 'copy']",
  "need": [
   "split 分词",
   "for 遍历",
   "in 包含判断",
   "append 收集"
  ],
  "steps": [
   "split 分词：先切成单词列表",
   "for 遍历：逐个检查单词",
   "in 包含判断：'py' in w 判断子串",
   "append 收集：命中就放进结果列表"
  ],
  "pool": [
   "split 分词",
   "for 遍历",
   "in 包含判断",
   "append 收集",
   "count 统计次数",
   "replace 替换",
   "sort 排序"
  ],
  "code": "words = 'python happy copy java'.split()\nhits = []\nfor w in words:\n    if 'py' in w:\n        hits.append(w)\nprint(hits)",
  "alt": null,
  "tip": "in 用于字符串是「包含子串」，用于列表是「是其中一员」，别混淆。"
 },
 {
  "id": "r08",
  "scene": "字典与最值",
  "title": "统计字母出现次数",
  "task": "统计字符串里每个字母出现了几次，用字典打印。",
  "input": "text = 'banana'",
  "output": "{'b': 1, 'a': 3, 'n': 2}",
  "need": [
   "for 遍历",
   "get 默认值",
   "字典计数"
  ],
  "steps": [
   "for 遍历：逐个取出字符",
   "get 默认值：counts.get(ch, 0) 取旧次数，没有就是 0",
   "字典计数：旧次数 +1 写回字典"
  ],
  "pool": [
   "for 遍历",
   "get 默认值",
   "字典计数",
   "Counter 计数器",
   "append 收集",
   "sort 排序",
   "split 拆分"
  ],
  "code": "text = 'banana'\ncounts = {}\nfor ch in text:\n    counts[ch] = counts.get(ch, 0) + 1\nprint(counts)",
  "alt": {
   "need": [
    "Counter 计数器"
   ],
   "steps": [
    "Counter 计数器：collections.Counter(text) 一步完成计数，dict(...) 转成普通字典打印"
   ],
   "code": "from collections import Counter\ntext = 'banana'\nprint(dict(Counter(text)))"
  },
  "tip": "get(ch, 0) 避免了「键不存在」报错；Counter 是标准库里的现成组合。"
 },
 {
  "id": "r09",
  "scene": "字典与最值",
  "title": "按成绩从高到低排序",
  "task": "字典存了姓名和成绩，按分数从高到低，逐行打印「姓名 分数」。",
  "input": "scores = {'小明': 80, '小红': 95, '小刚': 88}",
  "output": "小红 95\n小刚 88\n小明 80",
  "need": [
   "items 取键值对",
   "sorted+key 排序",
   "reverse 倒序",
   "for 遍历输出"
  ],
  "steps": [
   "items 取键值对：得到 (姓名, 分数) 元组",
   "sorted+key 排序：key=lambda x: x[1] 指定按分数排",
   "reverse 倒序：reverse=True 从高到低",
   "for 遍历输出：逐行打印"
  ],
  "pool": [
   "items 取键值对",
   "sorted+key 排序",
   "reverse 倒序",
   "for 遍历输出",
   "sort 排序",
   "get 默认值",
   "append 收集"
  ],
  "code": "scores = {'小明': 80, '小红': 95, '小刚': 88}\nitems = sorted(scores.items(), key=lambda x: x[1], reverse=True)\nfor name, s in items:\n    print(name, s)",
  "alt": null,
  "tip": "排序的关键是想清楚「按什么排」：key 函数就是告诉 sorted 取哪一项来比较。"
 },
 {
  "id": "r10",
  "scene": "综合任务",
  "title": "去重但保持原顺序",
  "task": "列表里有重复元素，去掉重复的、只保留第一次出现的，顺序不变，打印结果列表。",
  "input": "nums = [3, 1, 3, 2, 1, 4]",
  "output": "[3, 1, 2, 4]",
  "need": [
   "for 遍历",
   "not in 判断",
   "append 收集"
  ],
  "steps": [
   "for 遍历：按原顺序逐个取出",
   "not in 判断：结果列表里还没有才处理",
   "append 收集：第一次出现的元素放进结果"
  ],
  "pool": [
   "for 遍历",
   "not in 判断",
   "append 收集",
   "set 转集合",
   "fromkeys 去重",
   "list 转换",
   "sort 排序"
  ],
  "code": "nums = [3, 1, 3, 2, 1, 4]\nseen = []\nfor n in nums:\n    if n not in seen:\n        seen.append(n)\nprint(seen)",
  "alt": {
   "need": [
    "fromkeys 去重",
    "list 转换"
   ],
   "steps": [
    "fromkeys 去重：dict.fromkeys(nums) 利用字典键不重复且保序",
    "list 转换：list(...) 转回列表"
   ],
   "code": "nums = [3, 1, 3, 2, 1, 4]\nprint(list(dict.fromkeys(nums)))"
  },
  "tip": "set 能去重但不保证顺序，这题是干扰项；保序去重要用「遍历 + 成员判断」或 dict.fromkeys。"
 },
 {
  "id": "r11",
  "scene": "综合任务",
  "title": "奇偶分组",
  "task": "把 0 到 9 的整数分成两组：奇数一组、偶数一组，分别打印两个列表。",
  "input": "使用 range(10) 生成 0 到 9",
  "output": "[1, 3, 5, 7, 9]\n[0, 2, 4, 6, 8]",
  "need": [
   "range 生成序列",
   "for 遍历",
   "% 取余判断",
   "append 分组收集"
  ],
  "steps": [
   "range 生成序列：range(10) 产出 0 到 9",
   "for 遍历：逐个取出整数",
   "% 取余判断：n % 2 == 0 分奇偶",
   "append 分组收集：分别放进 odds 和 evens"
  ],
  "pool": [
   "range 生成序列",
   "for 遍历",
   "% 取余判断",
   "append 分组收集",
   "len 计数",
   "join 拼接",
   "sort 排序"
  ],
  "code": "odds = []\nevens = []\nfor n in range(10):\n    if n % 2 == 0:\n        evens.append(n)\n    else:\n        odds.append(n)\nprint(odds)\nprint(evens)",
  "alt": null,
  "tip": "分组问题 = 遍历 + 判断 + 多个收集列表，是「统计三板斧」的升级版。"
 },
 {
  "id": "r12",
  "scene": "综合任务",
  "title": "把二维列表拉平",
  "task": "一个列表里装着若干小列表，把所有元素按顺序拉平成一个一维列表打印。",
  "input": "matrix = [[1, 2], [3, 4], [5]]",
  "output": "[1, 2, 3, 4, 5]",
  "need": [
   "嵌套 for 遍历",
   "append 收集"
  ],
  "steps": [
   "嵌套 for 遍历：外层取每个小列表，内层取小列表里的元素",
   "append 收集：逐个放进结果列表"
  ],
  "pool": [
   "嵌套 for 遍历",
   "append 收集",
   "双层列表推导",
   "sum 求和",
   "sort 排序",
   "split 拆分"
  ],
  "code": "matrix = [[1, 2], [3, 4], [5]]\nflat = []\nfor row in matrix:\n    for x in row:\n        flat.append(x)\nprint(flat)",
  "alt": {
   "need": [
    "双层列表推导"
   ],
   "steps": [
    "双层列表推导：[x for row in matrix for x in row] 与嵌套循环等价，顺序从左到右读"
   ],
   "code": "matrix = [[1, 2], [3, 4], [5]]\nflat = [x for row in matrix for x in row]\nprint(flat)"
  },
  "tip": "嵌套结构就配嵌套循环；列表推导的双层写法和嵌套 for 的顺序一致。"
 }
];
