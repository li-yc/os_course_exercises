# lec14: lab5 spoc 思考题

- 有"spoc"标记的题是要求拿清华学分的同学要在实体课上完成，并按时提交到学生对应的ucore_code和os_exercises的git repo上。


## 视频相关思考题

### 14.1 总体介绍

1. 第一个用户进程创建有什么特殊的？

用户态代码段/数据段的初始化

2. 系统调用的参数传递过程？

> 参见：用户态函数syscall()中的汇编代码；

用%ebx, %ecx, %edx, %esi四个寄存器分别存储四个参数。在%eax中存放系统调用的编号。

> Ref: https://www.ibm.com/developerworks/library/l-ia/index.html

3. getpid的返回值放在什么地方了？

> 参见：用户态函数syscall()中的汇编代码；

放在寄存器%eax中。

### 14.2 进程的内存布局

1. ucore的内存布局中，页表、用户栈、内核栈在逻辑地址空间中的位置？

> memlayout.h

> #define VPT 0xFAC00000

> #define KSTACKPAGE 2 // # of pages in kernel stack

> #define KSTACKSIZE (KSTACKPAGE * PGSIZE) // sizeof kernel stack

> #define USERTOP 0xB0000000

> #define USTACKTOP USERTOP

> #define USTACKPAGE 256 // # of pages in user stack

> #define USTACKSIZE (USTACKPAGE * PGSIZE) // sizeof user stack

页目录表启示地址在0xFAC00000，用户栈起始地址在0xB0000000，内核栈起始地址在0xF8000000。

1. (spoc)尝试在panic函数中获取并输出用户栈和内核栈的函数嵌套信息和函数调用参数信息，然后在你希望的地方人为触发panic函数，并输出上述信息。

在panic.c中的`__panic()`函数中加上以下代码：

```c++
    cprintf("stack frame:\n");
    print_stackframe();
```

我在init.c的`kern_init()`函数中调用panic得到

```text
kernel panic at kern/init/init.c:51:
    test panic
stack trackback:
ebp: 0xc011ffa8, eip: 0xc0100a93, args: 0x0000003f 0x00000023 0x00000023 0xc011ffdc 
    kern/debug/kdebug.c:296: print_stackframe+21
ebp: 0xc011ffc8, eip: 0xc0100466, args: 0xc01082cc 0x00000033 0xc01082c1 0xc01000ae 
    kern/debug/panic.c:27: __panic+107
ebp: 0xc011fff8, eip: 0xc01000c2, args: 0xc01084bc 0xc01084c4 0xc0100d15 0xc01084e3 
    kern/init/init.c:0: kern_init+139
```

1. (spoc)尝试在panic函数中获取和输出页表有效逻辑地址空间范围和在内存中的逻辑地址空间范围，然后在你希望的地方人为触发panic函数，并输出上述信息。

先在proc.c(和proc.h)中编写一个函数print_current_logic_address。

```c++
void print_current_logic_address() {
	if (current == NULL || current->mm == NULL) {
		cprintf("current proc doesn't has mm.\n");
		return;
	}

	cprintf("panic - page table logic address range:\n");
	struct mm_struct *mm = current->mm;
	ptstep();
	const int page_size = 4096;
	cprintf("\t%x ~ %x\n", mm->pgdir, mm->pgdir + page_size);

	cprintf("panic - logic address areas:\n");
	print_logic_area(mm);
}
```

其中`print_logic_area(mm);`的函数定义在vmm.c中：

```c++
void print_logic_area(struct mm_struct *mm) {
	list_entry_t *le = &(mm->mmap_list);
	if (le == NULL) {
		cprintf("area of this mm is empty\n");
		return ;
	}
	int i=0;
	do {
		struct vma_struct *vma = le2vma(le, list_link);
		cprintf("area[%d]: 0x%08x ~ 0x%08x\n", i++, vma->vm_start, vma->vm_end);
		le = le->next;
	} while (le != &(mm->mmap_list));
}
```

在panic.c的__panic()函数中添加以下代码调用编写的函数：

```c++
void
__panic(const char *file, int line, const char *fmt, ...) {
    if (is_panic) {
        goto panic_dead;
    }
    is_panic = 1;

    // print the 'message'
    va_list ap;
    va_start(ap, fmt);
    cprintf("kernel panic at %s:%d:\n    ", file, line);
    vcprintf(fmt, ap);
    cprintf("\n");
    
    cprintf("stack trackback:\n");
    print_stackframe();
    
    print_current_logic_address();  // 更改在此

    va_end(ap);

panic_dead:
    intr_disable();
    while (1) {
        kmonitor(NULL);
    }
}
```


在proc.c中的load_icode()函数中调用panic()，得到的输出是：

```text
stack trackback:
ebp:0xc03aedc4 eip:0xc0101edd args:0xc03aefac 0x00000000 0x0000004c 0xc03aedf8 
    kern/debug/kdebug.c:350: print_stackframe+21
ebp:0xc03aede4 eip:0xc01017d4 args:0xc010ec20 0x00000286 0xc010ee1b 0xc010abb8 
    kern/debug/panic.c:32: __panic+107
ebp:0xc03aee54 eip:0xc010b12e args:0xc0154548 0x00007870 0x00000004 0x00000000 
    kern/process/proc.c:646: load_icode+1450
ebp:0xc03aee94 eip:0xc010b243 args:0xc010ee55 0x00000004 0xc0154548 0x00007870 
    kern/process/proc.c:685: do_execve+209
ebp:0xc03aeec4 eip:0xc010bb51 args:0xc03aeee0 0xc0102a31 0xc0102f3e 0x0000000a 
    kern/syscall/syscall.c:35: sys_exec+63
ebp:0xc03aef04 eip:0xc010bc38 args:0xc03aef2c 0xc010024e 0x0000000a 0x00000000 
    kern/syscall/syscall.c:93: syscall+116
ebp:0xc03aef24 eip:0xc0103b58 args:0xc03aef60 0xc010c303 0x0000000a 0xc03aef90 
    kern/trap/trap.c:216: trap_dispatch+271
ebp:0xc03aef54 eip:0xc0103cc8 args:0xc03aef60 0x00000000 0x00000000 0x00000000 
    kern/trap/trap.c:287: trap+80
ebp:0xc03aefcc eip:0xc0104792 args:0xc010ee55 0xc0154548 0x00007870 0x00000010 
    kern/trap/trapentry.S:24: <unknown>+0
ebp:0xc03aefec eip:0xc010b519 args:0x00000000 0x00000000 0x00000010 0x003b1007 
    kern/process/proc.c:821: user_main+59
panic - page table logic address range:
step1
	c03af000 ~ c03b3000
panic - logic address areas:
area[0]: 0x0000003c ~ 0x00000005
area[1]: 0x00200000 ~ 0x00204000
area[2]: 0x00800000 ~ 0x00802000
area[3]: 0x00802000 ~ 0x00803000
area[4]: 0xaff00000 ~ 0xb0000000
```

1. 尝试在进程运行过程中获取内核空间中各进程相同的页表项（代码段）和不同的页表项（内核堆栈）？

### 14.3 执行ELF格式的二进制代码-do_execve的实现

1. 在do_execve中的的当前进程如何清空地址空间内容的？在什么时候开始使用新加载进程的地址空间？

> 清空进程地址空间是在initproc所在进程地址空间

> CR3设置成新建好的页表地址后，开始使用新的地址空间

2. 新加载进程的第一级页表的建立代码在哪？
3. do_execve在处理中是如何正确区分出用户进程和线程的？并为此采取了哪些不同的处理？

### 14.4 执行ELF格式的二进制代码-load_icode的实现

1. 第一个内核线程和第一个用户进程的创建有什么不同？

> 相应线程的内核栈创建时，多了SS和ESP的设置；

> 用户进程需要创建用户地址空间，并把用户代码复制到用户地址空间；

2. 尝试跟踪分析新创建的用户进程的开始执行过程？

### 14.5 进程复制

1. 为什么新进程的内核堆栈可以先于进程地址空间复制进行创建？

> 内核栈在进程的内核地址空间，而各进程的内核地址空间是共享的；

2. 进程复制的代码在哪？复制了哪些内容？



3. 进程复制过程中有哪些修改？为什么要修改？

> 内核栈

> 页表

> trapframe

> context

> PCB字段修改

1. 分析第一个用户进程的创建流程，说明进程切换后执行的第一条是什么。

### 14.6 内存管理的copy-on-write机制

1. 什么是写时复制？

在fork()复制进程的时候不复制页，当子进程或者父进程修改页面中的某一项的内容的时候，复制该页并修改。

2. 写时复制的页表在什么时候进行复制？共享地址空间和写时复制有什么不同？

当子进程或者父进程修改页面中的某一项的内容的时候进行复制。共享地址空间是线程共用同一块地址空间，不一定共用其中的内容；而写时复制是在写页面之前，所有该页面中的内容均共用，一旦共享该页面的某个进程修改页中的内容，就要复制该页面，之后不再共享。

3. 存在有多个（n>2）进程具有父子关系，且采用了COW机制的情况。这个情况与只有父子两个进程的情况相比，在设计COW时，需要注意的新问题是什么？有何解决方案？

需要注意的问题是，修改时复制出来的页面应该由修改内容的那一个进程使用，而不是剩下未修改页面内容的进程使用。

## 小组练习与思考题

### (1)(spoc) 在真实机器的u盘上启动并运行ucore lab,

请准备一个空闲u盘，然后请参考如下网址完成练习

https://github.com/chyyuu/ucore_lab/blob/master/related_info/lab1/lab1-boot-with-grub2-in-udisk.md

> 注意，grub_kernel的源码在ucore_lab的lab1_X的git branch上，位于 `ucore_lab/labcodes_answer/lab1_result`

(报告可课后完成)请理解grub multiboot spec的含义，并分析ucore_lab是如何实现符合grub multiboot spec的，并形成spoc练习报告。

#### 实验操作

首先准备一个硬盘。然后在硬盘创建一个新的分区。用`df`得到/dev/sda2。

然后格式化U盘。

```
fdisk /dev/sdb2

命令(输入 m 获取帮助)：d
命令(输入 m 获取帮助)：n
  Partition type
   p   primary (0 primary, 0 extended, 4 free)
   e   extended (container for logical partitions)

	p 
 分区号 (1-4, default 1): 
	1 
 First sector (2048-16222013, default 2048):
	<enter>
 Last sector, +sectors or +size{K,M,G,T,P} (2048-16222013, default 16222013): 
	<enter>
   
命令(输入 m 获取帮助)：a
命令(输入 m 获取帮助)：w

umount /dev/sdb2
mkfs.vfat -F 32 -n MULTIBOOT /dev/sdb2
```

然后安装grub

```
mkdir /media/MULTIBOOT/              
mount /dev/sdb1 /media/MULTIBOOT/    
grub-install --force --no-floppy --root-directory=/media/MULTIBOOT/ /dev/sdb2    
```

之后配置cfg文件，最后将grub_kernel拷贝到/media/MULTIBOOT/boot目录下。

重新启动电脑之后进入BIOS，运行之后得到输出

```text
entry  0x00100000 (phys)
etext  0x0010354e (phys)
edata  0x0010ea16 (phys)
end  0x0010fd80 (phys)
ebp:0x00007b38 eip:0x00100a4c args:0x00010094 0x00010094 0x00007b68 0x00100084 
    kern/debug/kdebug.c:305: print_stackframe+21
......
```

由于不能复制手写比较麻烦所以省略其余输出。

### (2)(spoc) 理解用户进程的生命周期。

> 需写练习报告和简单编码，完成后放到网络学堂 OR git server 对应的git repo中

### 练习用的[lab5 spoc exercise project source code](https://github.com/chyyuu/ucore_lab/tree/master/related_info/lab5/lab5-spoc-discuss)

#### 掌握知识点
1. 用户进程的启动、运行、就绪、等待、退出
2. 用户进程的管理与简单调度
3. 用户进程的上下文切换过程
4. 用户进程的特权级切换过程
5. 用户进程的创建过程并完成资源占用
6. 用户进程的退出过程并完成资源回收

> 注意，请关注：内核如何创建用户进程的？用户进程是如何在用户态开始执行的？用户态的堆栈是保存在哪里的？

阅读代码，在现有基础上再增加一个用户进程A，并通过增加cprintf函数到ucore代码中，
能够把个人思考题和上述知识点中的内容展示出来：即在ucore运行过程中通过`cprintf`函数来完整地展现出来进程A相关的动态执行和内部数据/状态变化的细节。(约全面细致约好)

请完成如下练习，完成代码填写，并形成spoc练习报告

#### 实现

代码见[lab5-spoc-discuss](./lab5-spoc-discuss)

因为related_info/lab5/lab5-spoc-discuss中的代码不能运行，所以我使用了ucore_os_lab/labcodes_answer/lab5_result中的代码为基础实现本练习。

我首先编写了一个用户态程序，能够用fork()创建一个子进程并用wait()和exit()回收子进程。

```c++
int magic = -0x10384;

int
main(void) {
    int pid, code;
    cprintf("I am the parent. Forking the child...\n");
    if ((pid = fork()) == 0) {
        cprintf("I am the child.\n");
        yield();
        yield();
        yield();
        yield();
        yield();
        yield();
        yield();
        exit(magic);
    }
    else {
        cprintf("I am parent, fork a child pid %d\n",pid);
    }
    assert(pid > 0);
    cprintf("I am the parent, waiting now..\n");

    assert(waitpid(pid, &code) == 0 && code == magic);
    assert(waitpid(pid, &code) != 0 && wait() != 0);
    cprintf("waitpid %d ok.\n", pid);

    cprintf("exit pass.\n");
    return 0;
}
```

我在do_fork(), do_exit(), copy_mm(), copy_thread(), proc_init()等函数中添加了相应的输出信息，然后运行代码。

#### 运行结果

运行输出如下，其中有前缀`spoc5 -`的是我添加的输出信息：

```text
	spoc5 - from proc0 switch to proc1
	spoc5 - forking process1...
	spoc5 - setup kstack at address 0xc03ad000
	spoc5 - copying thread from proc1 to new proc
	spoc5 - trapframe addrss: 0xc03aefb4	esp: 0x08x
	spoc5 - new process get pid 2...
	spoc5 - wake up proc2
	spoc5 - from proc1 switch to proc2
kernel_execve: pid = 2, name = "exit".
I am the parent. Forking the child...
	spoc5 - forking process2...
	spoc5 - setup kstack at address 0xc03be000
	spoc5 - copy mm from proc2 to new proc, area is:
		page table directory:
			c03c0000 ~ c03c4000
		area[0]: 0xc03a52e0 ~ 0x00000005
		area[1]: 0x00200000 ~ 0x00204000
		area[2]: 0x00800000 ~ 0x00802000
		area[3]: 0x00802000 ~ 0x00803000
		area[4]: 0xaff00000 ~ 0xb0000000
	spoc5 - copying thread from proc2 to new proc
	spoc5 - trapframe addrss: 0xc03bffb4	esp: 0x08x
	spoc5 - new process get pid 3...
	spoc5 - wake up proc3
I am parent, fork a child pid 3
I am the parent, waiting now..
	spoc5 - from proc2 switch to proc3
I am the child.
	spoc5 - exit proc3...
	spoc5 - waking up proc2 because child exits.
	spoc5 - wake up proc2
	spoc5 - from proc3 switch to proc2
waitpid 3 ok.
exit pass.
	spoc5 - exit proc2...
	spoc5 - waking up proc1 because child exits.
	spoc5 - wake up proc1
	spoc5 - from proc2 switch to proc1

```


