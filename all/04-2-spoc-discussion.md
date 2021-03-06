#lec9: 虚存置换算法spoc练习

## 视频相关思考题

### 9.1 页面置换算法的概念

1. 设计置换算法时需要考虑哪些影响因素？如何评判的好坏？

考虑的因素有程序的页面访问规律。

通过测试应用某种算法后的缺页率来评判算法的好坏。

2. 全局和局部置换算法的不同？

全局置换算法要是在所有进程的页中选择要换出的页，局部置换算法是在当前进程的页中选择。

### 9.2 最优算法、先进先出算法和最近最久未使用算法

1. 最优算法、先进先出算法和LRU算法的思路？

最优算法：每次选择距离下一次访问时间最长的页换出。先进先出算法：每次选择最先换入的页面换出。LRU算法：每次选择最长时间未访问的页换出。

### 9.3 时钟置换算法和最不常用算法

1. 时钟置换算法的思路？

- 将所有在内存中的页表的编号组织成一个双向链表，并且用1位（叫访问位）记录近期是否访问过。
- 每次置换的时候，按照链表顺序逐个查找，如果访问位为1，就置0；如果访问位为0，就将该页面换出。
- 每次访问一个页面，将该页面的访问位置1。

2. 改进的时钟置换算法与时钟置换算法有什么不同？

改进的时钟置换算法增加了1位记录是否修改过。每次置换的时候，先将访问位置0；如果访问位为0，且修改位为1，再将修改位置0；如果两位均为0就将该页换出。这个算法的优点是可以加快页面修改的速度。

3. LFU算法的思路？

给每个页面记录一个近期访问次数，每次置换时选择近期访问次数最少的页面。

### 9.4 Belady现象和局部置换算法比较

1. 什么是Belady现象？如何判断一种置换算法是否存在Belady现象？

Belady现象是指分配给一个进程的物理页面更多之后，该进程运行过程中的缺页次数反而增加的现象。通过构造例子证明存在Belady现象，而证明不存在Belady现象比较复杂。

2. 请证明LRU算法不存在Belady现象。

最近使用的n个页面一定是最近使用的n+1个页面的子集，所以在LRU算法中，如果某次访问在分配的页面更多之前不会产生缺页，在分配的页面更多之后也不会产生缺页。所以LRU算法不存在Belady现象。

### 9.5 工作集置换算法

1. CPU利用率与并发进程数的关系是什么？

CPU利用率随着并发进程数的增加先增加后下降。

2. 什么是工作集？

当前某个程序正在访问的逻辑页面的集合。

3. 什么是常驻集？

当前时刻在内存中的页面的集合。

4. 工作集算法的思路？

维护链表记录内存中的页面。每次访存时，将时间t内未访问的页面换出。每次缺页时，将页面换入。

### 9.6 缺页率置换算法

1. 缺页率算法的思路？

设置一个时间窗口大小t。每次缺页的时候，如果距离上次缺页间隔不大于t，就将页面加入内存；如果大于t，就先将t时间内未访问的页面移出内存，再将该页面加入内存。

### 9.7 抖动和负载控制

1. 什么是虚拟内存管理的抖动现象？

抖动现象是指分配给进程的物理页面太少，导致频繁缺页，系统花费大量时间处理缺页。

2. 操作系统负载控制的最佳状态是什么状态？

最佳状态是：每个进程的工作集大小的总和是物理内存大小，而且缺页时间间隔略大于处理缺页所需的时间。

3. 局部置换算法（如FIFO, LRU等）是否能作为全局置换算法来使用？为什么？

不能。因为如果采用局部置换算法，进程切换会导致该进程的页面大量被置换出去，局部置换算法不能满足系统进程数的负载均衡的需求。

## 扩展思考题

1. 改进时钟置换算法的极端情况: 如果所有的页面都被修改过了，这时需要分配新的页面时，算法的performance会如何？能否改进在保证正确的前提下提高缺页中断的处理时间？

2. 如何设计改进时钟算法的写回策略?

3. （spoc）根据你的`学号 mod 4`的结果值，确定选择四种页面置换算法（0：LRU置换算法，1:改进的clock 页置换算法，2：工作集页置换算法，3：缺页率置换算法）中的一种来设计一个应用程序（可基于python, ruby, C, C++，LISP等）模拟实现，并给出测试用例和测试结果。请参考如python代码或独自实现。
 - [页置换算法实现的参考实例](https://github.com/chyyuu/ucore_lab/blob/master/related_info/lab3/page-replacement-policy.py)

```c++
#include <iostream>
#include <list>
#include <memory.h>
#include <random>

using namespace std;

struct Page {
    bool valid = 0;
    int vpn;  // virtual page number
    int ppn;  // physical page number
    int last_access_time;
    
    bool operator==(Page& page1) {
        return this->vpn == page1.vpn;
    }
};

int last_access_time;
const int virtual_page_count = 200;
const int physical_page_count = 100;
int time_window = 50;

Page page_table[virtual_page_count];
bool physical_page[physical_page_count];  // 1 means in use, 0 means idle.
list<int> valid_pages;

void page_fault(int vpn, int time) {
    if (time - last_access_time > time_window) {
        int time_bound = time - time_window;
        valid_pages.remove_if([time_bound](int vpn){
            if (page_table[vpn].last_access_time < time_bound) {
                page_table[vpn].valid = false;
                physical_page[page_table[vpn].ppn] = 0;
                return true;
            }
            return false;
        });
    }
    
    int ppn=0;
    while (physical_page[ppn] && ppn < physical_page_count) {
        ppn++;
    }
    if (ppn >= physical_page_count) {
        fprintf(stderr, "error: all physical pages in use\n");
        exit(1);
    }
    physical_page[ppn] = 1;
    valid_pages.emplace_back(vpn);
    page_table[vpn].ppn = ppn;
    page_table[vpn].valid = 1;
}

/**
 * return the physical page number of the page
 */
int access_page(int vpn, int time) {
    if (vpn >= virtual_page_count) {
        fprintf(stderr, "Segmentation fault (access page larger than virtual memory size)\n");
        exit(1);
    }
    int ppn;
    if (page_table[vpn].valid) {
        page_table[vpn].last_access_time = time;
        ppn = page_table[vpn].ppn;
    } else {
        page_fault(vpn, time);
        page_table[vpn].last_access_time = time;
        ppn = page_table[vpn].ppn;
    }
    last_access_time = time;
    return ppn;
}

void init_page_table() {
    valid_pages.clear();
    memset(physical_page, 0, sizeof(bool) * physical_page_count);
    last_access_time = 0;
}
```

4. 请判断OPT、LRU、FIFO、Clock和LFU等各页面置换算法是否存在Belady现象？如果存在，给出实例；如果不存在，给出证明。

5. 了解LIRS页置换算法的设计思路，尝试用高级语言实现其基本思路。此算法是江松博士（导师：张晓东博士）设计完成的，非常不错！
	- 参考信息：
 	- [LIRS conf paper](http://www.ece.eng.wayne.edu/~sjiang/pubs/papers/jiang02_LIRS.pdf)
	 - [LIRS journal paper](http://www.ece.eng.wayne.edu/~sjiang/pubs/papers/jiang05_LIRS.pdf)
	 - [LIRS-replacement ppt1](http://dragonstar.ict.ac.cn/course_09/XD_Zhang/(6)-LIRS-replacement.pdf)
	 - [LIRS-replacement ppt2](http://www.ece.eng.wayne.edu/~sjiang/Projects/LIRS/sig02.ppt)
