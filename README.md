## autojump
# 微信跳一跳自动跳动脚本
- 本脚本仅仅作为演示使用，供学习使用，由此产生的任何问题，概不负责
- 使用了opencv3.2完成图像处理，使用python3进行编程
- 使用ADB完成和测试机交互

##算法主要思路
- 使用模板匹配算法检测小人，准确度 100%
- 使用canny + 轮廓提取 + 轮廓分析得到棋盘位置
- HSV空间进行处理，绕过目前微信程序设置的颜色空间的陷阱

##测试情况
- 目前尝试可以达到上万分，算法稍加调整基本可实现无失误
- 目前只支持python3及Android
- 试验机 华为P10,其他大小屏幕需要调整参数及更新下小人目标模板

- 效果截图：
![输入图片说明](https://gitee.com/uploads/images/2018/0114/225449_09f2b87d_385234.png "732.png")