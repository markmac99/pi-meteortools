#!/bin/bash

echo "This script will install the UKMON ARCHIVE software"
echo "on your Pi. If you don't want to continue press Ctrl-C now"
echo " "
echo "You will need the location code, access key and secret provided by UKMON"
echo "If you are already a contributor from a PC the keys can be found in "
echo "%LOCALAPPDATA%\AUTH_ukmonlivewatcher.ini. The short string is the Key,"
echo "and the long string is the secret. Both are encrypted."
echo ""
echo "If you don't have these keys press crtl-c and come back after getting them".
echo "nb: its best to copy/paste the keys from email to avoid typos."
echo " " 

read -p "continue? " yn
if [ $yn == "n" ] ; then
  exit 0
fi

echo "Installing the AWS CLI...."
sudo apt-get install -y awscli

mkdir ~/ukmon
echo "Installing the package...."
ARCHIVE=`awk '/^__ARCHIVE_BELOW__/ {print NR + 1; exit 0; }' $0`
tail -n+$ARCHIVE $0 | tar xzv -C ~/ukmon

CREDFILE=~/ukmon/.archcreds

if [ -f $CREDFILE ] ; then
  read -p "Credentials already exist; overwrite? (yn) " yn
  if [[ "$yn" == "y" || "$yn" == "Y" ]] ; then 
    redocreds=1
  else
    redocreds=0
  fi
else
  redocreds=1
fi

if [ $redocreds -eq 1 ] ; then 
  while true; do
    read -p "Location: " loc
    read -p "Access Key: " key
    read -p "Secret: " sec 
    echo "you entered: "
    echo $loc
    echo $key
    echo $sec
    read -p " is this correct? (yn) " yn
    if [[ "$yn" == "y" || "$yn" == "Y" ]] ; then 
      break 
    fi
  done 
    
  echo "Creating credentials...."
  echo "export AWS_ACCESS_KEY_ID=`/home/pi/ukmon/.ukmondec $key k`" > $CREDFILE
  echo "export AWS_SECRET_ACCESS_KEY=`/home/pi/ukmon/.ukmondec $sec s`" >> $CREDFILE
  if [ "ARCHIVE" == "ARCHIVE" ] ; then 
    echo "export AWS_DEFAULT_REGION=eu-west-2" >> $CREDFILE
  else
    echo "export AWS_DEFAULT_REGION=eu-west-1" >> $CREDFILE
  fi
  echo "export loc=$loc" >> $CREDFILE
  chmod 0600 $CREDFILE
fi 
if [ "ARCHIVE" == "ARCHIVE" ] ; then 
  crontab -l | grep archToUkMon.sh
  if [ $? == 1 ] ; then
    crontab -l > /tmp/tmpct
    echo "Scheduling job..."
    echo "0 11 * * * /home/pi/ukmon/archToUkMon.sh >> /home/pi/ukmon/archiver.log 2>&1" >> /tmp/tmpct
    crontab /tmp/tmpct
    \rm -f /tmp/tmpct
  fi 
  echo "archToUkMon will run at 11am each day"
else
  crontab -l | grep liveMonitor.sh > /dev/null
  if [ $? == 1 ] ; then
    echo "Scheduling job..."
    crontab -l > /tmp/tmpct
    echo "@reboot sleep 3600 && /home/pi/ukmon/liveMonitor.sh >> /home/pi/ukmon/monitor.log 2>&1" >> /tmp/tmpct
    crontab /tmp/tmpct
    \rm -f /tmp/tmpct
  fi 
  echo "liveMonitor will start after next reboot"
fi
echo ""
echo "done"
exit 0

__ARCHIVE_BELOW__
� ���^ �Yl���;;�;��Q��*K8~���/q���q�������v�;r��v�&Zh�*)�@[h����B����D���
Q5��PD�v���#(�U��{;��{�%�ZZ�ڗ�g޼o޼y3;�fNT�����[򹈚"�ŀ�W��<޽2f͑���.�Z�ݕHtuƻ	�$:c���?��SQ�D��I!}f�;��G���\tTTS>5_T�2��hqk6��FDXIE�T��[3�Q�p\S@�e`H�DM�� �M�6�3��o��������N�h3�K��5#r2��CRɢƇ%^��c ���	;G|�JM��d<� I��dՈ���ք2�d4GC�
$�%-��
Қ�[�|8s�����"Iu�9(��l�/����s��~�/=��x#B�|x\���'?���Rr����@��.^��%�����R��Ք���P�pX�Hf���/�l9p��E
�q[��j>g�J�{���ެ`W�Mh��l!��'gTƦ;>��R��8��y)%q�7������C�"�������Ǚ��xw窄��'��]�N��c+�	g��O����8���.r	A�YG�]
u��A� ;�t��p>�>NOm���a�RBO��t����܍2�'�BOR�2�\��詉�a-�s�i5T\��~Q!?&��恟gv6r�8=�~�E�ъ&5��@�fңьΤsŉ��dSc5�"�}�Y~���Oi[�Ƀ�(zb$�UF{z~��7o}���O6>�fx��ɵ��9�,��ڂ}���m=u_G���E�����G>s�m�����g#�y͛v�϶�ю�xk��6�f�����������߰��?���`<�T�|���IV�����@_&����ьLa�8�sM�p�6a��eDU�U��4�EYM��-�$$��ı�$������,Ly"�U��H���D�+�3r�d�*k�2S�b:G����"+������	���[������V����M��k��ۙ)�N/B=����E�E<�����%�r� �a�-��BVc����`={{�/G	��wǡ9O9\��U�*�.{�T9� ,����3�f�u�b��,���r�R~�R�c)�c)ﰔ'�<U�%�Ҭ'��E|i�Ã=$\	<���y:\i!�*-�}�?V���t�.i!G4ȃP��Uܱ�eߟ�2��j��C�z�d3G�,� LA�H����K�#��-�F���/�-.�ס��J�\`���Z�~�;�?	LM#��n��. >m�y��:&��P���`|��W��C,�����^��94W����V}]����~��l����L���L��+��t�f�1��@��x�o�W܁�� ��X��,���*)M�����篂m(�bwΠl�2�	���.����ɖ�j�5ݨ��q�?�>�+w 6V�v�~��kg�=���`~�y���Cl��x�fg ��Pf�q�P9������A��|��A.�pA�2��O������4��4x��6��q�AY���|f��c��O�����?���x�����������,�Wږ�+;��vƵ�4�X(�^m������#T���V��rӷ;ϻv�6��;���*J ���4��㗗1���XFͶq�����^!���8eڼ�gy�z�yi�l��%`�`N\���Q���Q�r`��� �����ی6���@i��3���"�΁�V�c6��pO�W�@���O��]���CP�����!��'�.�1�9Cb�Up�[�^��U�[���z��o�����q�����S�[<�v��Πm����f#�b���V��h�N6V_��}�I�4�?���?���<���4���<"���iמ�t
�n��O�y��\?CzJ�\�]3�ؓ����-�y����O�U�.��8����4�x.aDxa�����|��cjj�]X>���v<KGNU�Þ�=U�<��&��m�ؙj&<[1����Kr�G�W�C�	���Y|��v���q&Ư\��c� ��y}������~#��"|�\H'ܜ^��� 8�����V�SP_������mF��B�9��|�d%�g��/�"��Ѵ����#��x�C�<���y)�x;ju$�_J�[=�"�EPlZE����B��Z�Y��s�s�m�Rn�����-�HD��j�(�B�Q��LV
$��kr�w���&�3n<W���ɧ%�s)QM��4�}4�*�&+j:��c�)rq�P�h�!D�M���c��(�?$һe �h-��	�S"fe�RE��-���IE7F̦�`@S���J"�|6+�4�S�4%=Z� �mL	v�s�[�`��s^��4�[�=z~�����g��ۗ���d��O�x������z~���w����k��-z�l�_����Q�,=?V��g��ӈ�d�o�����[��S~��w�����5�~����������5�M�k�Rb%��kX�vb��<��5Ĝ/��,� ��k,��C�m�c5��:o؇7�A[���d����w1}!��=���:���Y���7��e�U���?�G�
K�x�Xa�o�f�M��3yOS���-���{-�(g�F��z��7=;�����$Ü��D����V������k��[B��L�^����Q˂2�Ӝe=`�o������������6y�W���� ���l����}��u�����5{�s&��#�kwX/������{����r�3�o��׹z7����5�����,<�G,|���ϣ[���0�]�n��e~�<��!�9��O��>S'o#������4i����~��|�[��K���6��l�1��������f<j��7ݏp����γ��n�>$�^�\��~|ns��ہ����A���p�������@��c��~�gퟲ����͞�>�_mx/�lZ?g��<��/����b<�EU�Ǔɨ�d�$�$,�Ƣ]E#�� �h�H��$�=�Ҡ.)f2�-��U��{��P���Zql,�$�pM���а �OвB��TҠJ��0�ɏ�A��*��	�R!#k��<K4	f�%@h�L=B�b6;	M,�`mj��I
DΌ��A�[z��7��gH}HF�N�D�u���;���^�?��������m�0�~X�]ۿ^0^�jQ7���<��!ͧQd�,�z�ɔY�����|�n��6��Cz���Ch��|���A������慔���n|c��n��R:'UYbO�zB��Qy��\h�a�+m�}6��n�^�K*�ǈ^a�2}H�7]tuF'��:���3{-�7&�X����{�l1Di�S���]�[q�����&C�S�ĺ ������}� c��[px�(�9� ������x���Ѻ&���g���qpeB�����=b���.z����S��;2�W�F�~],m%�N�e��L�������4����7�nz���;n-���nz�G\���ي�����!��S￻-8z'd���^��g�2��v}Zp7�vk��}�����c���=j�a8��W�I���l��}���̊�%!�m����1�9BC��^s܋�_�a�ȟ7K��G{4w4p��W,�0~���K��0�f�a����|���"���Po���O���:���p��
 �
F���M��������p�po�sf�Q��ðA|�7��]h����Q�@��K�C9�C9�C9�C9�C9�C9�C9�C9�C9�C9�����X�d P  