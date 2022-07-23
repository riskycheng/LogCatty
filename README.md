# 字符串创建
字符串支持动态修改，拼接:
```
/// String 初始化
var strVal = String()
if strVal.isEmpty
{
    print("this is empty")
}
strVal += "Hello World!"
```
对于String和Character，支持String遍历:
```
// 使用for-in遍历所有字符
for c in strVal
{
    print(c)
}
// 获取字符串长度
print("the characters count:\(strVal.count)")
```

# 访问字符串
字符串中各位字符支持下标访问，常用的有：
- stringData[indexer]
- stringData.startIndex
- stringData.endIndex
- stringData.index(before:)
- stringData.index(after:)
- stringData.index(indexer, offsetBy:)
示例：
```
// 字符串索引
var strData : String = "Test_string_data"
var a = strData[strData.index(after: strData.startIndex)]       // e
var b = strData[strData.index(before: strData.endIndex)]        // a
var c = strData[strData.index(strData.startIndex, offsetBy: 5)] // s
```

# 修改字符串
## 插入
调用`insert(_:at:)`可以在一个字符串的指定索引位置插入一个字符，而调用`insert(contentOf:at:)`可以在一个字符串的指定索引位置插入一段字符串。
```
var welcomeStr = "Helloworld"
// 插入字符
welcomeStr.insert(",", at: welcomeStr.index(welcomeStr.startIndex, offsetBy: 5))
print(welcomeStr)
//插入字符串
welcomeStr.insert(contentsOf: "Jian", at: welcomeStr.endIndex)
print(welcomeStr)
```

## 删除
调用`remove(at:)`可以在一个字符串的指定索引位置删除一个字符，而调用`removeSubrange(_:)`可以在一个字符互传的指定位置删除一个子字符串。
```
var welcomeStr = "Hello,world"
// 删除字符
welcomeStr.remove(at: welcomeStr.index(welcomeStr.startIndex, offsetBy:5))
print(welcomeStr)
// 删除字符串
welcomeStr.removeSubrange(welcomeStr.index(welcomeStr.startIndex, offsetBy: 5)..<welcomeStr.endIndex)
print(welcomeStr)
```

## 字符串及引用
使用下标或者`prefix(_:)`之类的方法可以得到一个`Substring`实例，并非一个`String`，在临时变量中可以使用`Substring`，如果需要持久持有则需要转化为`String`。
换句话说，`String`在内存中有一块独立的空间，`Substring`则仅仅是一个指向该内存的引用，本身并不会真实创建并持有一块专有的内存空间。  
![stringSubstring_2x.png](http://tva1.sinaimg.cn/large/6b260656gy1h46trw7yeaj20l80ggdhg.jpg)

## 字符串比较
swift支持三种方式比较文本：
- 字符串相等，使用`==` 或者 `!=`
- 字符串前缀，使用 `hasPrefix(_:)`
- 字符串后缀，使用 `hasSuffix(_:)`
```
var welcomeStr = "Hello,world"
var welcomeStr2 = "Hello,world2"
print(welcomeStr == welcomeStr2)
print(welcomeStr.hasPrefix("Hello2"))
print(welcomeStr.hasSuffix("world"))
```