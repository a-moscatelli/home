cd /D %WORKDIR%

cd %APPDIR%
call %MAVEN% clean package

cd /D %WORKDIR%

