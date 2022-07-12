╔═════════════════════╗
 SEGA Decryption Guide
╚═════════════════════╝

╭─────────╮
 app files
╰─────────╯

1. create a new file titled <PCB CODE>.bin

2. fill in the first 16 bytes of <PCB CODE>.bin with
the AES key. (e.g. 9D 0B BA 20 D1 E8 4F 24 59 39 9F 53 83 BE EE 72)

3. the next 16 bytes will be the NTFS header (EB 52 90 4E 54 46 53 20 20 20 20 00 10 01 00 00)
the NTFS header is always the same

4. save this file, then decrypt the app files with the following command:
fsdecrypt <PCB CODE>.bin 0x200000 <path/to/app> <out.vhd>

5. once it finishes decrypting, run the calculate_iv.py script
save the output of key 1. script is found here: https://discord.com/channels/162861213309599744/243895668790394882/995170669329391706

6. open <PCB CODE>.bin inside the hex editor once more, replace the NTFS header with
the key 1

7. run "fsdecrypt <PCB CODE>.bin 0x200000 <path/to/app> <out.vhd>" once more

8. your app is now decrypted, you can extract the internal_0 with poweriso or any other tool

╭─────────╮
 opt files
╰─────────╯

1. decrypt the opt file using fstools with the following command:
fstool dec OPT.bin in.opt out.vhd

2. run the calculate_iv.py script and save key 3
script is found here: https://discord.com/channels/162861213309599744/243895668790394882/995170669329391706

3. replace the IV key of the OPT.bin with key 3, the IV key of OPT.bin are the second 16 bytes

4. decrypt the opt file once more with the new key
