#include <Constants.au3>
#include <Date.au3>

;
; AutoIt Version: 3.0
; Language:       English
; Platform:       Win10
; Author:         Mark McIntyre
;
; Script Function:
;   Opens Colorgramme, selects the speclab file
;

$now=_NowCalcDate()
$yr=stringleft($now,4)
$mth=stringmid($now,6,2)
$filename = "RMOB-" & $yr & $mth & ".DAT"
consolewrite($filename)

; Run app
Run("C:\Program Files (x86)\Colorgramme Lab\colorlab.exe", "C:\Program Files (x86)\Colorgramme Lab\")
; bring the window to the front
Winactivate("Colorgramme")
; Wait for app to be active
WinWaitActive("Colorgramme")

Send("!L")
Sleep(5000)
send("S")
Sleep(10000)
ControlSend("Open","File &name","[CLASSNN:Edit1]",$filename)
sleep(1000)
ControlClick("Open","&Open","[CLASSNN:Button2]")

; Finished!
