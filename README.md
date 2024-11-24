# 简谱转调工具

## 功能

通俗来说，这是一个转调工具。但这个工具的作用**不是**音乐意义上的转调，
它的功能是将一个调号下的记谱符号转为另一个调号下的记谱符号，
符号代表的音高并不改变。

比如，一个C#调的旋律`1 2 3`，转为C调后为`#1 #2 #3`。
这方便在C调为基准的乐器，比如C调口琴下进行演奏。

## 命令参数

- **--help**: 显示帮助。
- **--comment-key-signature**: 在注释中显示原来的调号标记。
- **--prefer**: 可选择**sharp**或者**flat**。
  - 选择**sharp**表示尽可能使用升调号`#`，这会将所有`4`与`1`，替换为`#3`与`#7`。
  - 选择**flat**表示尽可能使用降调号`b`，这会将所有`3`与`7`，替换为`b4`与`b1`。
- **--orig-key**: 如果缺少调号，将使用此参数指定的**tone**作为基调。
- **--target-key**: 必须指定，将转调到此参数指定的**tone**。
- **input_file**: 输入的乐谱。
- **output_file**: 将结果输出到指定文件，若未指定则输出到屏幕。

## 乐谱格式

输入的简谱应该有类似的格式：

```
标题
1=C
1 2 3 4
```

第一行是简谱标题，通常是歌曲名称，这一行不会被修改。

第二行是调号，以`1=`作为前缀，后面接着一个*key*，这一行在输出文件中会被
修改为转调后的调号。你可以在`keymap`找到*key*的定义。**调号是可选的**

之后的是乐谱记谱符号，有效的符号为`1-7`、`#`、`b`、`()`、`[]`以及空格。
所有其他字符均会被忽略，但会保留在输出文件中。

`1`表示以调号标注的音为基准音，在以`1=C`为调号时表示'C'这个音。

`#1`表示一个半音，它比`1`高一个半音，`b1`表示一个半音，它比`1`低一个半音。

`1#`和`1b`均是非法的，因为可能造成混淆。

`(1)`表示一个低音，它比`1`低一个八度，`[1]`表示一个高音，它比`1`高一个八度。

`()`和`[]`可以重复使用，比如`((1))`比`1`低两个八度。

`//`起始的行是一个注释行，这一行的内容不会被修改，并且会保存在输出的结果中。

## 一个例子

```
Foo

// 可以使用`//`表示一个注释行
// 1 2 3 4
// 注释行不会被修改，并且会保留
// 但目前不支持行内注释

1=C
(#7) #3 #7
1 #3 [1]
// 上面两行表示的音是一样的

1=C#
1 2 3 4
// 转C调后，结果应该是#1 #2 4 #4

1=C
1 2 3 4
// 这一行不变

1=(B)
1 2 3 4
1=B
1 2 3 4
// 1=(B)与1=B转调后的结果差一个八度
```

使用命令

```
python3 notation.py --comment-key-signature --target-key C foo.txt
```

转C调后的结果为：

```
Foo
1=C

// 可以使用`//`表示一个注释行
// 1 2 3 4
// 注释行不会被修改，并且会保留
// 但目前不支持行内注释

// origin key signature 1=C
1 4 [1]
1 4 [1]
// 上面两行表示的音是一样的

// origin key signature 1=C#
#1 #2 4 #4
// 转C调后，结果应该是#1 #2 4 #4

// origin key signature 1=C
1 2 3 4
// 这一行不变

// origin key signature 1=(B)
(7) #1 #2 3
// origin key signature 1=B
7 [#1 #2 3]
// 1=(B)与1=B转调后的结果差一个八度
```

## 一些定义

1. 调 (key)
   **key**定义为`C, C#, D, D#, E, F, F#, G, G#, A, A#, B`其中之一。
2. 修饰符 (decoration)
   **decoration**定义为`()`与`[]`，用于区分低音与高音。修饰符是可以叠加的，比如，
   `C`表示**中音C**，则`(C)`表示**低音C**，`((C))`表示**倍低音C**。
3. 音调 (tone)
   **tone**定义与调**key**类似，与**key**不同的是，它可以使用**修饰符**调整音高。
4. 音符 (note)
   **note**定义为`1, #1, 2, #2, 3, 4, #4, 5, #5, 6, #6, 7`其中之一。音符可以使用修饰符。
5. 调号 (key signature)
   **调号**定义为`1=X`，其中`1=`是一个**固定前缀**，`X`表示一个**tone**。
