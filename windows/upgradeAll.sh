#!/bin/bash

# update OS on all the Linux OSes

ssh imac "echo -e '\033[0;31m' && hostname && echo -e '\033[0;00m' && sudo apt-get update && sudo apt-get upgrade -y && sudo shutdown -h now"
ssh testpi3 "echo -e '\033[0;31m' && hostname && echo -e '\033[0;00m' && sudo apt-get update && sudo apt-get upgrade -y && sudo shutdown -h now" 
ssh testpi5 "echo -e '\033[0;31m' && hostname && echo -e '\033[0;00m' && sudo apt-get update && sudo apt-get upgrade -y && sudo shutdown -h now"
ssh testpi4 "echo -e '\033[0;31m' && hostname && echo -e '\033[0;00m' && sudo apt-get update && sudo apt-get upgrade -y && sudo reboot"
ssh allsky "echo -e '\033[0;31m' && hostname && echo -e '\033[0;00m' && sudo apt-get update && sudo apt-get upgrade -y && sudo reboot"
ssh wxsatpi "echo -e '\033[0;31m' && hostname && echo -e '\033[0;00m' && sudo apt-get update && sudo apt-get upgrade -y && sudo reboot"
ssh ohserver "echo -e '\033[0;31m' && hostname && echo -e '\033[0;00m' && sudo apt-get update && sudo apt-get upgrade -y && sudo reboot"
ssh uk0006 "echo -e '\033[0;31m' && hostname && echo -e '\033[0;00m' && sudo apt-get update && sudo apt-get upgrade -y && sudo reboot"
ssh uk000f "echo -e '\033[0;31m' && hostname && echo -e '\033[0;00m' && sudo apt-get update && sudo apt-get upgrade -y && sudo reboot"
ssh uk001l "echo -e '\033[0;31m' && hostname && echo -e '\033[0;00m' && sudo apt-get update && sudo apt-get upgrade -y && sudo reboot"
ssh uk002f "echo -e '\033[0;31m' && hostname && echo -e '\033[0;00m' && sudo apt-get update && sudo apt-get upgrade -y && sudo reboot"
ssh weatherpi3 "echo -e '\033[0;31m' && hostname && echo -e '\033[0;00m' && sudo apt-get update && sudo apt-get upgrade -y && sudo reboot"
ssh auroracam "echo -e '\033[0;31m' && hostname && echo -e '\033[0;00m' && sudo apt-get update && sudo apt-get upgrade -y && sudo reboot"
ssh thelinux "echo -e '\033[0;31m' && hostname && echo -e '\033[0;00m' && sudo apt-get update && sudo apt-get upgrade -y"