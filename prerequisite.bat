@echo off

set /p maya_version=Enter the main version of Maya you are running (e.g. 2022, do not enter 2022.2): 

cd "C:\program files\autodesk\maya%maya_version%\bin"
mayapy -m pip install numpy
pause