@echo off
rem WARNING: This batch file DELETES files. Run at your own risk.

cls
if exist test\*.nes del test\*.nes

echo === test.bat: default settings ===
python corruptor.py smb.nes test\corrupt1.nes
fc /b smb.nes test\corrupt1.nes
echo.

echo === test.bat: last byte ===
python corruptor.py --start 40975 smb.nes test\corrupt2.nes
fc /b smb.nes test\corrupt2.nes
echo.

echo === test.bat: invert all bits ===
python corruptor.py --method i smb.nes test\corrupt3.nes
fc /b smb.nes test\corrupt3.nes
echo.

echo === test.bat: add/subtract one ===
python corruptor.py --method a smb.nes test\corrupt4.nes
fc /b smb.nes test\corrupt4.nes
echo.

echo === test.bat: randomize 4 bytes between 0x2000-0x20ff ===
python corruptor.py --count 4 --method r --start 8192 --length 256 smb.nes test\corrupt5.nes
fc /b smb.nes test\corrupt5.nes
echo.

echo === test.bat: invalid args ===
python corruptor.py --start 40000 --length 1000 smb.nes test\dummy1.nes
python corruptor.py --start 40976 smb.nes test\dummy2.nes
python corruptor.py --start 40976 --length 1 smb.nes test\dummy3.nes
python corruptor.py --start 40975 --length 2 smb.nes test\dummy4.nes
echo.

echo === test.bat: help ===
python corruptor.py --help
