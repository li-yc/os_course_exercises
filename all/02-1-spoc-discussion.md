# lec 3 SPOC Discussion

## **提前准备**
（请在上课前完成）


 - 完成lec3的视频学习和提交对应的在线练习
 - git pull ucore_os_lab, v9_cpu, os_course_spoc_exercises  　in github repos。这样可以在本机上完成课堂练习。
 - 仔细观察自己使用的计算机的启动过程和linux/ucore操作系统运行后的情况。搜索“80386　开机　启动”
 - 了解控制流，异常控制流，函数调用,中断，异常(故障)，系统调用（陷阱）,切换，用户态（用户模式），内核态（内核模式）等基本概念。思考一下这些基本概念在linux, ucore, v9-cpu中的os*.c中是如何具体体现的。
 - 思考为什么操作系统需要处理中断，异常，系统调用。这些是必须要有的吗？有哪些好处？有哪些不好的地方？
 - 了解在PC机上有啥中断和异常。搜索“80386　中断　异常”
 - 安装好ucore实验环境，能够编译运行lab8的answer
 - 了解Linux和ucore有哪些系统调用。搜索“linux 系统调用", 搜索lab8中的syscall关键字相关内容。在linux下执行命令: ```man syscalls```
 - 会使用linux中的命令:objdump，nm，file, strace，man, 了解这些命令的用途。
 - 了解如何OS是如何实现中断，异常，或系统调用的。会使用v9-cpu的dis,xc, xem命令（包括启动参数），分析v9-cpu中的os0.c, os2.c，了解与异常，中断，系统调用相关的os设计实现。阅读v9-cpu中的cpu.md文档，了解汇编指令的类型和含义等，了解v9-cpu的细节。
 - 在piazza上就lec3学习中不理解问题进行提问。

## 第三讲 启动、中断、异常和系统调用-思考题

## 3.1 BIOS
-  x86中BIOS从磁盘读入的第一个扇区是是什么内容？为什么没有直接读入操作系统内核映像？

第一个内容是主引导记录。没有直接读入操作系统内核映像是因为这时候还未确定文件系统，但是又不可能把所有的文件系统的识别和读取方式都写进BIOS里。

- 比较UEFI和BIOS的区别。

UEFI是BIOS之后诞生的标准，旨在代替BIOS。UEFI中有认证功能，只有当认证了引导记录具有合法的签名才会读取扇区中的内容。UEFI还具有提供在所有平台上一致的启动接口的功能。

- 理解rcore中的Berkeley BootLoader (BBL)的功能。
	+ 从文件系统中读取启动配置信息。
	+ 根据读取的启动配置信息加载可选的操作系统内核。
	+ 根据配置加载指定内核并跳到内核执行。

## 3.2 系统启动流程

- x86中分区引导扇区的结束标志是什么？

0x55AA

- x86中在UEFI中的可信启动有什么作用？

为启动提供安全性的保障。例如，有些服务器上直接插入硬盘就能启动操作系统会带来安全性的隐患，所以需要对引导记录进行验证。

- RV中BBL的启动过程大致包括哪些内容？
	+ 从文件系统中读取启动配置信息。
	+ 根据读取的启动配置信息加载可选的操作系统内核。
	+ 根据配置加载指定内核并跳到内核执行。

## 3.3 中断、异常和系统调用比较
- 什么是中断、异常和系统调用？
	+ 这三者都会打断当前执行的应用程序，转而跳到对应的中断、异常和系统调用处理程序中。
	+ 中断是外设引起的，通常是外设和计算机之间的数据交换，比如键盘输入的数据。
	+ 异常是用户或者系统程序执行过程中出现了某些错误，比如除以0，页缺失等。
	+ 系统调用是操作系统为用户程序提供的一些服务接口，用户程序直接或间接通过系统调用使用这些服务，比如读写磁盘等。

- 中断、异常和系统调用的处理流程有什么异同？
	+ 三者都会进入内核态执行。三者都会打断当前执行的应用程序，首先进入中断向量表，然后转而跳到对应的中断、异常和系统调用处理流程中。
	+ 中断会从中断向量表进入对应设备的驱动中。结束后会返回原来的应用程序。
	+ 异常会从中断向量表进入异常服务历程中。然后可能会直接杀死造成异常的程序，也可能回到程序中。
	+ 系统调用会从中断向量表进入系统调用表查询具体是哪个系统调用，然后跳到相应的系统调用的实现中。系统调用和应用程序可能是同步或者异步的。

- 以ucore/rcore lab8的answer为例，ucore的系统调用有哪些？大致的功能分类有哪些？

有exit、fork、wait、exec、open等。大致有线程控制、IO、文件读写、内存管理几类。

## 3.4 linux系统调用分析
- 通过分析[lab1_ex0](https://github.com/chyyuu/ucore_lab/blob/master/related_info/lab1/lab1-ex0.md)了解Linux应用的系统调用编写和含义。(仅实践，不用回答)
- 通过调试[lab1_ex1](https://github.com/chyyuu/ucore_lab/blob/master/related_info/lab1/lab1-ex1.md)了解Linux应用的系统调用执行过程。(仅实践，不用回答)


## 3.5 ucore/rcore系统调用分析 （扩展练习，可选）
-  基于实验八的代码分析ucore的系统调用实现，说明指定系统调用的参数和返回值的传递方式和存放位置信息，以及内核中的系统调用功能实现函数。
- 以ucore/rcore lab8的answer为例，分析ucore 应用的系统调用编写和含义。
- 以ucore/rcore lab8的answer为例，尝试修改并运行ucore OS kernel代码，使其具有类似Linux应用工具`strace`的功能，即能够显示出应用程序发出的系统调用，从而可以分析ucore应用的系统调用执行过程。

 
## 3.6 请分析函数调用和系统调用的区别
- 系统调用与函数调用的区别是什么？
	+ 系统调用会进入操作系统内核态运行。
	+ 系统调用和函数调用的功能不同，只有系统调用可以使用一些操作系统提供的服务。
	+ 系统调用过程中会发生堆栈的切换，函数调用不会。

- 通过分析x86中函数调用规范以及`int`、`iret`、`call`和`ret`的指令准确功能和调用代码，比较x86中函数调用与系统调用的堆栈操作有什么不同？

在系统调用中需要进行用户态和内核态的转换，执行int的时候需要将SS:ESP，CS:EIP，EFLAGS压栈，执行iret的时候需要将这些寄存器从栈中弹出恢复它们系统调用之前的值。

- 通过分析RV中函数调用规范以及`ecall`、`eret`、`jal`和`jalr`的指令准确功能和调用代码，比较x86中函数调用与系统调用的堆栈操作有什么不同？

在系统调用中需要进行用户态和内核态的转换。

## 课堂实践 （在课堂上根据老师安排完成，课后不用做）
### 练习一
通过静态代码分析，举例描述ucore/rcore键盘输入中断的响应过程。

### 练习二
通过静态代码分析，举例描述ucore/rcore系统调用过程，及调用参数和返回值的传递方法。
