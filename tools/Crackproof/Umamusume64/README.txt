odd.sys (crackproof driver) for umamusume, you can edit the string of the driver with the one needed for whatever game you're trying to run.

to figure out the string, run the game via a debugger, at a certain point, it will crash and it will tell you which string it's looking for

Obfuscated HEX:
E8 85 FA FF FF 48 8D 4C 24 50

Deobfuscated HEX : 
48 74 73 79 73 6D 36 45 38 43

Raw Text : Htsysm6E8C 



8D 4C 24 50 would be the hex which would be edited with the string of the game you're trying to run. you have to obfuscate the string after finding it(dont know how to do it yet)
