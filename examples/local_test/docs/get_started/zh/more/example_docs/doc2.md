
---
标题: LoRa 重要知识
关键词： LoRa 知识 概念 参数
简介：LoRa: Long Range的缩写，是一种基于线性调制扩频技术（CSS: chirp spread spectrum)的一种扩频调制技术，应用于低功耗远距离低速率通信

---

与同类技术相比，提供更长的通信距离,更低的功耗，速率比较低。
调制是基于扩频技术，线性调制扩频（CSS）的一个变种，并具有前向纠错（FEC）特性。
LoRa显著地提高了接受灵敏度(低至-148dBm)，与其他扩频技术一样，使用了整个信道带宽广播一个信号，从而使信道噪声和由于使用低成本晶振而引起频率偏移的不敏感性更健壮。
LoRa可以调制信号19.5dB低于底噪声，而大多数频移键控（FSK）在底噪声上需要一个8-10dB的信号功率才可以正确调制。

先直观地看一下LoRa传输时的波形,下面几张图是我实际抓到的LoRa传输时的波形

![图一：cubicSDR LoRa470MHz SF12 4/5 8preamble瀑布流图](https://neucrack.com/image/1/12/3500903-fc78285d2f434924.png)

![图二：cubicSDR 捕获到的LoRa 470MHz SF12 4/5 时域波形图](https://neucrack.com/image/1/12/3500903-33e72130ee303b5d.PNG)

![图三：LoRa瀑布图2(来源网络)](https://neucrack.com/image/1/12/3500903-485276d0e85783fc.jpg)


## 基础知识

### （一）EIRP  ERP （e.r.p/e.i.r.p）
 EIRP即射频发射功率(dBm)+天线增益（单位dBi)-线路衰减(dB)
 ERP即射频发射功率(dBm)+天线增益（单位dBd)-线路衰减(dB)
 其中 EIRP(dBm) = ERP(dBm)+2.15

![ERP EIRP](https://neucrack.com/image/1/12/3500903-a715a0ea486b36a4.png)

![ERP EIRP](https://neucrack.com/image/1/12/3500903-747e6641f7790ab2.png)

![ERP EIRP](https://neucrack.com/image/1/12/3500903-b0c5862e98c04a7f.png)


这里引出一个问题，国内在470~510MHz频段要求功率不能超过50mW [17dBm (e.r.p)]，那为什么厂商出厂都标明了芯片或者模块是20dBm呢，这不是超出了限制范围？
芯片或模块的信号还要经过传输线和天线，总所周知，芯片到天线会有插入损耗以及线损等，然后经过天线再增益后才得到最后的空中功率值


### （二）dBm dB dBi dBd mW 含义及关系和区别

请自行看书或搜索学习

如果需要看视频教程，推荐：
视频(中文字幕):[hackrf bilibili](https://www.bilibili.com/video/av7079120/?p=3) , 视频(英文):[hackrf greatscottgadgets](http://greatscottgadgets.com/sdr/3/)
其它视频：[LoRa youtube](https://www.youtube.com/watch?v=ePtFD3z8WwU&list=PLmL13yqb6OxdeOi97EvI8QeO8o-PqeQ0g&index=5)


### （三）链路预算

首先要了解接收灵敏度和发射功率

接收灵敏度值越低越好，比如-120dBm和-145dBm，-145dBm值更小，我们说接收灵敏度更好。
而经常也会有人说最大灵敏度，这里的大不能理解为值大而知最好灵敏度，这里需要注意，表达时容易混淆。

可以简单理解成 最好接收灵敏度值绝对值+最大发射功率， 更详细解释请自行学习
![link budget margin](https://neucrack.com/image/1/12/3500903-16ae3a51a2fc387a.png)

比如按照[semtech的sx1276手册说明](https://www.semtech.com/products/wireless-rf/lora-transceivers/SX1276)，芯片最大功率位20dBm，最大接收灵敏度位-148dBm,所以最大链路预算为168dBm。



## LoRa相关基础术语和名词解释

### （一）up-chirp/down-chirp 

首先大家都明白调频(`FM`)和调幅(`AM`)，如下图：
![AM FM](https://neucrack.com/image/1/12/3500903-4486aeed492a2927.gif)
使用不同幅度或者频率来表示不同的数据（数值）。

`up-chirp/down-chirp` ：这里chirp是鸟叫声的意思，也正如鸟叫声一样，`up-chirp`指频率逐渐增加的过程，`down-chirp`则相反是频率逐渐降低的过程。
比如下图就是`up-chirp`，反之如果时间从右往左就是`down-chirp`:
![up-chirp， 横轴时间，纵轴幅度](https://neucrack.com/image/1/12/3500903-5eae062bb04611c5.jpg)

通过这种变化过程来表示一个或者多个数据（数值），
比如最简单的`up-chirp`代表1，`down-chirp`代表0,；
再复杂一点，从最低频率变化到最高这个过程表示1，从中间频率到最大频率然后跳变到最低频率再变化到中间频率这个过程表示2，从最高变成最低标识3等等。具体表示什么就看具体的应用和标准了。
而LoRa就采用这种调制方式：
![LoRa调制](https://neucrack.com/image/1/12/3500903-7b21bde3326948c5.png)

### （二）带宽（BandWidth）

带宽 BW (BandWidth): 
表示频率最大值减去最小值的差值。
而带宽和信号的传输速率又有着极大的关系，信道带宽与数据传输速率的关系可以奈奎斯特(Nyquist)准则与香农(Shanon)定律描述。如果忘记了可以看[这里](https://blog.csdn.net/reborn_lee/article/details/80745218)。
所以带宽越大，速率越快,单位是Hz

### （三）码片（chips）

[码片](https://baike.baidu.com/item/%E7%A0%81%E7%89%87/5934932?fr=aladdin)：通过扩频技术，将一个数据位用很多码片来表示。

### （四）符号（symbol）

一个完整的扫频信号（sweep signal)可以被称为一个符号，如下图中需黄色虚线部分的黑色实线称为为一个符号:
![symbol](https://neucrack.com/image/1/12/3500903-5483a5940069225d.png)

就像前面说的， 这样一个chirp信号可以用来表示一个或者多个数据（数值），在LoRa调制中，一个符号代表的数据内容长度由扩频因子决定，扩频因子含义见后面阐述。

### （五）扩频因子（Spreading Factor）

前面说了使用扩频技术用多个码片来代表1个数字信号中的数据位（即我们真实想传输的数据），我们将一个符号分成2^SF个单元，这个单元即为前面说的码片（chips），来表示SF个数据位（注意不是1个数据位或者1个字节），SF即扩频因子。
> 比如一个符号可以表示`1011111`(95)，7位数据，值位95，这里一个符号代表的数据的位数就是扩频因子的值，比如上面这个95的值对应的扩频因子的值位7

这里即我们用了`2^SF/SF`个码片来表示一个实际的位。如果SF越大，因为用来表示这个位数据的码片多了，抗干扰能力自然就会好很多；而由于代表每个符号的码片增加了，单位时间传输码片数量是定了的，因此需要的时间自然就增加了。
综上，扩频因子值越小速率越高，抗干扰性越低，传输距离越近。
在semtech的LoRa芯片中，SF取值6~12,6为特殊值

![符号 扩频因子 码片](https://neucrack.com/image/1/12/3500903-23ea40e7f9d37935.png)

### （六）编码率 CR (Code Rate)

LoRa使用了向前纠错技术，传输的数据有一部分需要拿来纠错，在实际发送的长度为SF指定的长度中，实际传输的数据只有一部分即CR（CR的取值是一个小于1的分数，而semtech的lora的数据手册上为了简化寄存器，有几个CR值分别用1~4来表示4/5～4/8，不要弄混淆了），其它的用来纠错的数据。
比如SF8发送了8个字节，但是由于有向前纠错技术，这8个字节中的一部分需要拿来做这个事情，比如这里CR设置4/5，其中有1/5的数据为纠错数据，实际发送的有效数据内容只有8*4/5字节，如下图：
![code rate](https://neucrack.com/image/1/12/3500903-4d6610239238cfac.png)
 
所以CR值越大（4/5>4/8)，则实际一个符号中的有效数据更少，所以速率也就更低，但是鲁棒性会更好

## 速率

![带宽 码片速率](https://neucrack.com/image/1/12/3500903-15b8cad4652e7676.png)

* 码片速度Rc:
前面也说到，带宽和信号的传输速率有极大的关系，这里码片的传输速率和带宽（单位Hz）的值相等，即：
`Rc= BW = |BW|chips/s`

* 符号速度Rs:
每个符号有2^SF个码片，而码片的传输速率为Rc，所以，符号传输速率Rs为：
`Rs = Rc/2^SF = BW/2^SF`

* 数据传输速率DR(或者说bit Rate)：
`DR = Rb(bits/sec) = SF * Rs * CR = SF * (BW/2^SF) * CR`

## 传输时间

* 1个码片传输时间`Tc = 1/Rc = 1/BW`
* 1个符号传输时间`Ts = 1/Rs = 2^SF/BW`
![Ts](https://neucrack.com/image/1/12/3500903-70da7b969a84fca2.png)
由此看出，SF每增加一个值，Ts就要是之前的两倍,如下图：
![Ts](https://neucrack.com/image/1/12/3500903-88d436e41b8c89f9.png)

* 传输时间：
LoRa在传输过程中需要传前导码、头、以及payload
`Tpreamble = (Npreamble+2+2+1/4) * Ts`
其中`Npreamble`可以设置，比如本文的捕捉到的波形图中值为8.
`Tpayload = Ts * N(payloadSymbNb)`
![payload 符号数量](https://neucrack.com/image/1/12/3500903-915d0fecb43b0722)
max()取最大值函数
ceil()取整数函数

然后传输时间相加`Tpreamble + Tpayload`即为传输时间

这里放[一张网友手算的图](https://blog.csdn.net/qq_26602023/article/details/76026684)：
![手算LoRa传输时间](https://neucrack.com/image/1/12/3500903-f8faa1685468bfd7)

当然，有现成的计算工具，semtech官方也提供了工具

* [semtech LoRa 计算器(sx1276页面)](https://www.semtech.com/uploads/documents/SX1272LoRaCalculatorSetup1_1.zip)

* [在线传输时间计算工具](https://www.loratools.nl)

## 实际波形分析（解码)

了解了以上的知识，再回头来看看实际捕捉到的波形图（瀑布图）

![图一：cubicSDR LoRa470MHz SF12 4/5 8preamble瀑布流图](https://neucrack.com/image/1/12/3500903-fc78285d2f434924.png)

如上面瀑布图所示，纵轴是时间轴，横轴是频率。
可以看到传输数据时在一周期T内频率会从某个起点均匀变化（增大或减小）直到设置的带宽的临界值，然后跳变为最小或者最大值继续变化直到频率变为起始时的频率，即前面说的`up-chirp` 或者 `down-chirp`，而实际也可以看到，除了有(2+1/4)个符号使用了`down-chirp`，其它的都是使用的`up-chirp`。

在这张瀑布流图中可以清晰地看到preamble和sync word，前12+1/4个符号可以看到有清晰的规则，其中前8个up-chirp是preamble，中间两个up-chirp是sync word,外加后面（2+1/4）个down-chirp的符号， 然后后面跟的数据就是header和payload了，由于数据不像preamble那样规则这里就不分析了。

## 为什么网关要用sx1301，可以用sx1276代替么

1301可以同时监听8个上行通道，每个通道可以同时监听6个正交扩频因子SF7~SF12，这也就是文档中说的多大49个虚拟通道的来源，但是需要注意的是，虽然每个通道可以同时监听6个SF，但同一时刻也只能处理一个信号，比如同时来自SF7和SF12的消息也只能处理其中一个。 
也就是说1301的上行也就能同时处理8个通道（频率范围），那可能就会想到如果我用8个SX1276是不是就可以替代1301了，事实上也是不行的，因为1301每个通道都能检测6个SF通道，虽然同一时刻只能处理其中一个，但是1276/1278是不能做到这点的，SX1276/8同一时刻只能检测一个SF信道。sx1301这个特性的好处就是因为检测到多个SF信道，因此可以很容易做速率自适应（ADR），而如果采用SX1276/78因为同时只能监听一个确定的SF的通道（即SF值和频率均确定为一个），要做到相对来说就更困难。




## 参考资料

* [mobilefish.com教学视频](https://www.youtube.com/channel/UCG5_CT_KjexxjbgNE4lVGkg/videos)(推荐)(文章中的部分截图来自这里，见截图水印）
* [DecodingLora](https://revspace.nl/DecodingLora)(推荐)
* https://lora-alliance.org/sites/default/files/2018-04/lorawantm_specification_-v1.1.pdf
* http://blog.sina.com.cn/s/blog_7880d3350102wkzf.html
* http://www.eefocus.com/communication/403484/r0
* https://blog.csdn.net/jiangjunjie_2005/article/details/75123968
* http://bbs.eeworld.com.cn/thread-1060636-1-1.html
* https://wenku.baidu.com/view/390050fa6037ee06eff9aef8941ea76e58fa4a1a.html
* https://blog.csdn.net/qq_26602023/article/details/76026684
