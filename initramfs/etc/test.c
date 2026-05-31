#define SYS_PRINT 1

static inline unsigned long long syscall(
    unsigned long long num,
    unsigned long long arg1,
    unsigned long long arg2)
{
    register unsigned long long rdi asm("rdi") = num;
    register unsigned long long rsi asm("rsi") = arg1;
    register unsigned long long rdx asm("rdx") = arg2;
    register unsigned long long rax asm("rax");

    __asm__ volatile("syscall"
        : "=a"(rax)
        : "r"(rdi), "r"(rsi), "r"(rdx)
        : "rcx", "r11", "memory"
    );
    return rax;
}

void _start(void) {
    syscall(SYS_PRINT, (unsigned long long)"Hello from user mode!\n", 0xFFFFFF);
    while(1) __asm__ volatile("hlt");
}
