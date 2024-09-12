#!/bin/bash

# update OS on all the Linux OSes

ssh imac "echo -e '\033[0;31m' && hostname && echo -e '\033[0;00m' && sudo apt-get update && sudo apt-get upgrade -y && sudo shutdown -h now"
ssh testpi3 "echo -e '\033[0;31m' && hostname && echo -e '\033[0;00m' && sudo apt-get update && sudo apt-get upgrade -y && sudo shutdown -h now" 
ssh testpi5 "echo -e '\033[0;31m' && hostname && echo -e '\033[0;00m' && sudo apt-get update && sudo apt-get upgrade -y && sudo shutdown -h now"
ssh testpi4 "echo -e '\033[0;31m' && hostname && echo -e '\033[0;00m' && sudo apt-get update && sudo apt-get upgrade -y"
ssh allsky2 "echo -e '\033[0;31m' && hostname && echo -e '\033[0;00m' && sudo apt-get update && sudo apt-get upgrade -y"
ssh wxsatpi "echo -e '\033[0;31m' && hostname && echo -e '\033[0;00m' && sudo apt-get update && sudo apt-get upgrade -y"
ssh ohserver "echo -e '\033[0;31m' && hostname && echo -e '\033[0;00m' && sudo apt-get update && sudo apt-get upgrade -y"
ssh uk0006 "echo -e '\033[0;31m' && hostname && echo -e '\033[0;00m' && sudo apt-get update && sudo apt-get upgrade -y"
ssh uk000f "echo -e '\033[0;31m' && hostname && echo -e '\033[0;00m' && sudo apt-get update && sudo apt-get upgrade -y"
ssh uk001l "echo -e '\033[0;31m' && hostname && echo -e '\033[0;00m' && sudo apt-get update && sudo apt-get upgrade -y"
ssh uk002f "echo -e '\033[0;31m' && hostname && echo -e '\033[0;00m' && sudo apt-get update && sudo apt-get upgrade -y"
ssh weatherpi3 "echo -e '\033[0;31m' && hostname && echo -e '\033[0;00m' && sudo apt-get update && sudo apt-get upgrade -y"
ssh auroracam "echo -e '\033[0;31m' && hostname && echo -e '\033[0;00m' && sudo apt-get update && sudo apt-get upgrade -y"
ssh thelinux "echo -e '\033[0;31m' && hostname && echo -e '\033[0;00m' && sudo apt-get update && sudo apt-get upgrade -y"