# Deployment
I deploy all code to my Pis and other servers with Ansible

## Deployment Secrets
Various ansible deployment scripts include passwords and other sensitive data. These are read from an encrypted file on my PC and are not on Github. 

### Encrypted File
The file contains a list of ansible variable definitions in `keyword: value` form. It is then encrypted with `ansible-vault`. You'll have to provide a password - see below for how to store this. 

Basic ansible-vault commands are:  
```
ansible-vault encrypt secretsfile  # encrypts the file
ansible-vault edit secretsfile     # allows editing of the file contents
ansible-vault decrypt secretsfile  # decrypts the file - no real reason to do this!
```
### Using the Encrypted Values
To use the file in a playbook, add this to the `- hosts` section in the playbook
```
  vars_files: 
    - secretsfile
```
Then use the variables exactly as normal eg `userid: {{ keyword }}`

Ansible will decrypt the file and do the usual variable-substitution.

### The Vault file password
The vault file password can either be provided on the commandline
```
ansible-playbook mydeployment.yml --ask-vault-pass
```
or stored in a separate file. I tend to keep the vault password file in my `~/.ssh` folder along with my ssh keys, as this area is reasonably well protected. The file can then be referenced through an environment variable
```
export ANSIBLE_VAULT_PASSWORD_FILE=somefile
ansible-playbook mydeployment.yml 
```
or passed in on the commandline:
```
ansible-playbook mydeployment.yml --vault-password-file=somefile
```
