# lab4 spoc discuss


## 掌握知识点
1. 内核线程的启动、运行、就绪、等待、退出
2. 内核线程的管理与简单调度
3. 内核线程的切换过程

请完成如下练习，完成代码填写，并形成spoc练习报告

## 1. 分析并描述创建分配进程的过程

> 注意 state、pid、cr3，context，trapframe的含义



## 练习2：分析并描述新创建的内核线程是如何分配资源的
###设计实现

> 注意 理解对kstack, trapframe, context等的初始化


当前进程中唯一，操作系统的整个生命周期不唯一，在get_pid中会循环使用pid，耗尽会等待

## 练习3：阅读代码，在现有基础上再增加一个内核线程，并通过增加cprintf函数到ucore代码中
能够把进程的生命周期和调度动态执行过程完整地展现出来

## 扩展练习4：增加可以睡眠的内核线程，睡眠的条件和唤醒的条件可自行设计，并给出测试用例，并在spoc练习报告中给出设计实现说明
