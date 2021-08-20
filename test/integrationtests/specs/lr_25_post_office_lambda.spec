# LR-25 Post Office Lambda

tags: preprod

## Ensure Lambda LR-25 can move a file from MESH inbound to LR-01 inbound

* send "A76543_GPR4LNA1.H2A" to mesh inbound folder
* invoke lambda LR-25
* connect to pass folder and check the destination file has loaded
