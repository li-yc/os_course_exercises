#include <stdio.h>
#include <ulib.h>

int magic = -0x10384;
int magic2 = -0x10972;

int
main(void) {
    int pid, code;
    cprintf("I am the parent. Forking the child...\n");
    if ((pid = fork()) == 0) {
        cprintf("I am the child.\n");
//        int pid2, code2;
//        if ((pid2 = fork()) == 0) {
//        	cprintf("I am process A.\n");
//        	yield();
//        	yield();
//        	exit(magic2);
//        } else {
//        	cprintf("I am a parent. My child is process A. My child's pid is %d\n", pid2);
//
//        	assert(waitpid(pid2, &code2) == 0 && code2 == magic2);
//			assert(waitpid(pid2, &code2) != 0 && wait() != 0);
//		    cprintf("waitpid %d ok.\n", pid2);
//        }
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

