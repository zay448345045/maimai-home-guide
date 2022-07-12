# Get the IV key from OPT.bin (this is the second 16 bytes of the file)
# decrypt the .opt using OPT.bin and get the first 16 bytes of the vhd. this is key1
# key1 xor EB769045584641542020200000000000 (exfat file header) this will give you key2
# key2 xor OPT IV key -> key3
# replace OPT.bin's IV with key3 and decrypt
import os
import glob

#function for taking bytes and xor'ing them
def byte_xor(ba1, ba2):
    return bytes([_a ^ _b for _a, _b in zip(ba1, ba2)])

print("You must decrypt the opt first using fstools and the OPT.bin\nPlace everything in the same directory\nONLY HAVE ONE VHD IN THE DIRECTORY AT A TIME")
cwd = os.getcwd()

#necessary because i couldn't figure out how else to do this, it's the exfat header duh
with open(str(cwd) + "/exfat.bin", "rb") as f:
	exfat_HEADER = f.read(-1)
	print("exFAT Header = " + str(exfat_HEADER.hex()))

#reads all bytees from OPT.bin then saves bytes (17, 32) and converts it to hexadecimal
with open(str(cwd) + "/OPT.bin", "rb") as f:
	opt_IV = f.read(-1)
	opt_IV = opt_IV[16:]
	print("OPT IV = " + str(opt_IV.hex()))

#puts all files with .vhd extension in a list, then pulls the first one in the list, will read first 16 bytes and convert to hexadecimal
placeholder = glob.glob("*.vhd")
vhd = str(placeholder[0])
with open(str(cwd) + "/" + vhd, "rb") as f:
	key1 = f.read(16)
	print("key1 =" + str(key1.hex()))

#calculates key 2 and key 3 then converts to hex
key2 = byte_xor(key1, exfat_HEADER)
print("key2 = " + str(key2.hex()))
key3 = byte_xor(key2, opt_IV)
print("key3 = " + str(key3.hex()))

