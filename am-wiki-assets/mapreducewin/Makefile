# Makefile
# setenv.bat  - you now have *.worker and *.taskfiles
# make i    - you now have MASTER-LOCK.BAT MASTER-LOGGER.BAT MASTER-TEMP.REMOTEEXEC.BAT WORKER-TEMP.LOCALEXEC.BAT
# make a  (will remove busy agents)
# make -j 1 all



# see help

# expected initial content of folder MASTER_WORKDIR on node HEADH:
# -
# bigfile*.csv
# make.exe
# Makefile
# PsExec.exe
# setenv.bat
# task.py
# -
# example of setenv.bat:
#set "MASTER_WORKDIR=folder\subfolder\subsubfolder"
#set "WORKER_WORKDIR=folder"

# see https://www.gnu.org/prep/standards/html_node/Standard-Targets.html#Standard-Targets
# A variable name may be any sequence of characters not containing `:', `#', `=', or leading or trailing whitespace

############  ENVIRONMENT SPECIFIC VALUES  - BEGIN

# HEADH = working workstation and head node

# remote workers labels: we assume one job per file per worker
#WORKERS=HOST001 HOST002 HOST003

# map tasks labels and files to process:
#TASKS=TASK001 TASK002 TASK003 TASK004 TASK005

# output file of the reduce step:
#FINALFILE=merged.out.csv
#
MASTER_NET_ABS_TEMPBAT_LOC=\\$(HEADH)\$(MASTER_WORKDIR)
PYCALL_AT_WORKER=c:\Python37-32\python.exe \\$(HEADH)\$(MASTER_WORKDIR)\task.py
WAIT5SEC=C:\Windows\System32\timeout.exe /T 5
WAIT5SEC=C:\Windows\System32\ping.exe 127.0.0.1 -n 5 >NUL
PSEXEC=PsExec.exe

############  ENVIRONMENT SPECIFIC VALUES  - END


help:
	@echo ''
	@echo HEADH is: $(HEADH)
	@echo HOST001 is: $(HOST001)
	@echo TASK001 is: $(TASK001)
	@echo MASTER_WORKDIR is: $(MASTER_WORKDIR)
	@echo WORKER_WORKDIR is: $(WORKER_WORKDIR)
	@echo ''
	@echo '1.   make install or make i'
	@echo '2.   make initialize or make a'
	@echo '3.   make clean or make c'
	@echo '4.   make -j 3 all'
	@echo '......... or whatever degree of parallelism as per needs'
	@echo '5.   make clean or make c'
	@echo '2r.  make clean_initialization or make ca'
	@echo '1r.  make uninstall or make ci'
	@echo ''
	@echo 'run: make util_test_rexec'
	@echo '... to run a remote execution test'
	@echo 'run: make util_rem_dir'
	@echo '... to see a list of the remote files'

#shortcuts

i:install
a:initialize
c:clean
ca:clean_initialization
ci:uninstall


all : map_reduce

map_reduce: $(FINALFILE)


phonytargets.workers.util_test_rexec = $(foreach WX, $(WORKERS), $(WX).phonytargets.workers.util_test_rexec)
util_test_rexec: $(phonytargets.workers.util_test_rexec)
$(phonytargets.workers.util_test_rexec):
	@echo doing HOST KEY $(patsubst %.phonytargets.workers.util_test_rexec,%,$@) VALUE $(call getWorkerValueOfWorkerKey,$(patsubst %.phonytargets.workers.util_test_rexec,%,$@))
	cmd /c '$(PSEXEC) \\$(call getWorkerValueOfWorkerKey,$(patsubst %.phonytargets.workers.util_test_rexec,%,$@)) -accepteula -s cmd /c cd'




initialize: step0_task_init worker_state_init
#rerunnable
	@echo initialize : main
	-cmd /c 'del /Q $(MASTER_LOG)'
	$(MASTER_LOGGER_BAT) END__ initialize



clean_initialization:
	@echo clean_initialization starts
	cmd /c 'del /Q *.agent'
	cmd /c 'del /Q *.mkcontrol'
	-cmd /c 'del /Q $(MASTER_LOG)'
	@echo clean_initialization is done.


#echo test - the agent of TASK001 will be: $(shell cmd /c type TASK001.agent)  -OK-
#echo test - the agent of TASK001 will be: $(file < TASK001.agent) -NOT OK-
#... file function is supported since v 4.2 and we are using GNU Make version 3.78.1 - Built for Windows32

phonytargets.workers.worker_state_init = $(foreach WX, $(WORKERS), $(WX).idle.agent)
worker_state_init: $(phonytargets.workers.worker_state_init)
$(phonytargets.workers.worker_state_init) :
	@echo initialize : worker_state_init
	cmd /c 'echo>$@'
	-cmd /c 'del /Q *.busy.agent'
#  cmd /c 'type $@'


# https://www.gnu.org/software/make/manual/html_node/Call-Function.html
# reverse = $(2) $(1)
# foo = $(call reverse,a,b)

getTaskKey = $(1)
# ... semantic
getWorkerKeyOfTaskKey    = $(strip $(shell cmd /c type $(1).agent))
getWorkerValueOfWorkerKey  = $(strip $(shell cmd /c type $(1).worker))
getWorkerValueOfTaskKey    = $(call getWorkerValueOfWorkerKey,$(call getWorkerKeyOfTaskKey,$(1)))
# do not add extra spaces between call and arg
getTaskValueOfTaskKey    = $(strip $(shell cmd /c type $(1).taskfiles))
getTaskValueOfTaskKeyOut  = $(strip $(shell cmd /c type $(1).taskfiles)).out.csv


testMacros:
	@echo 1 getTaskKey [$(call getTaskKey,TASK001)]
	@echo 2 getWorkerKeyOfTaskKey [$(call getWorkerKeyOfTaskKey,TASK001)]
	@echo 3 getWorkerValueOfWorkerKey [$(call getWorkerValueOfWorkerKey,HOST001)]
	@echo 4 getWorkerValueOfTaskKey [$(call getWorkerValueOfTaskKey,TASK001)]
	@echo 5 getTaskValueOfTaskKey [$(call getTaskValueOfTaskKey,TASK001)]


#ref. https://www.gnu.org/software/make/manual/html_node/Static-Usage.html

step0_targets = $(foreach TX, $(TASKS), $(TX).step0.inputFileReadyOnMaster.mkcontrol)
step1_targets = $(foreach TX, $(TASKS), $(TX).step1.workerAcquisitionLoopFinished.mkcontrol)
step2_targets = $(foreach TX, $(TASKS), $(TX).step2.inputFilePushedToWorker.mkcontrol)
step3_targets = $(foreach TX, $(TASKS), $(TX).step3.submittedToWorker.mkcontrol)
step4_targets = $(foreach TX, $(TASKS), $(TX).step4.workerCompletionCheckLoopFinished.mkcontrol)
step5_targets = $(foreach TX, $(TASKS), $(TX).step5.outputFilePulledToMaster.mkcontrol)

step0_task_init: $(step0_targets)
$(step0_targets) :
	@echo initialize : step0_task_init
	cmd /c 'echo>$@'




# enqueue map jobs:
# TASKnnn.step1.workerAcquisitionLoopFinished.mkcontrol is created when TASKnnn found and acquired an idle worker exclusively
$(step1_targets) : %.step1.workerAcquisitionLoopFinished.mkcontrol : %.step0.inputFileReadyOnMaster.mkcontrol
	@echo doing stem $* for step1.workerAcquisitionLoopFinished.mkcontrol
	cmd /c '$(MASTER_LOGGER_BAT) BEGIN $@'
	@cmd /c 'for /L %s in (0,5,36000) do \
	if not exist $@ \
	($(MASTER_LOCK_BAT) acquire $@ NA $(call getTaskKey,$*) && $(WAIT5SEC)) \
	else \
	(exit /b)'
	cmd /c '$(MASTER_LOGGER_BAT) END__ $@ $(call getWorkerKeyOfTaskKey,$*)'


#push steps:
#... all rerunnable
$(step2_targets) : %.step2.inputFilePushedToWorker.mkcontrol : %.step1.workerAcquisitionLoopFinished.mkcontrol
# L : P : CP
# each item of the list L follows the pattern P and needs a dependent that has corresponding name CP
	@echo doing stem $* for step2.inputFilePushedToWorker.mkcontrol
	cmd /c '$(MASTER_LOGGER_BAT) BEGIN $@ $(call getWorkerKeyOfTaskKey,$*)'
	cmd /c 'copy $(call getTaskValueOfTaskKey,$*) \\$(call getWorkerValueOfTaskKey,$*)\$(WORKER_WORKDIR)\'
	echo> $@



# submit map jobs:
$(step3_targets) : %.step3.submittedToWorker.mkcontrol : %.step2.inputFilePushedToWorker.mkcontrol
	@echo doing stem $* for step3.submittedToWorker.mkcontrol
	cmd /c '$(MASTER_LOGGER_BAT) BEGIN $@ $(call getWorkerKeyOfTaskKey,$*)'
	cmd /c '$(MASTER_REXEC_BAT) $(call getWorkerValueOfTaskKey,$*) $(call getTaskValueOfTaskKey,$*) $(call getTaskKey,$*) && echo> $@'

# poll file steps:
$(step4_targets) : %.step4.workerCompletionCheckLoopFinished.mkcontrol : %.step3.submittedToWorker.mkcontrol
	@echo doing stem $* for step4.workerCompletionCheckLoopFinished.mkcontrol
	@cmd /c 'for /L %s in (0,5,36000) do \
	if not exist $*.step4.workerCompletionCheckLoopFinished.mkcontrol \
	($(WAIT5SEC)) \
	else \
	(echo> $@ && $(MASTER_LOCK_BAT) release NA $(call getWorkerKeyOfTaskKey,$*) && exit /b)'

#pull steps:
$(step5_targets) : %.step5.outputFilePulledToMaster.mkcontrol : %.step4.workerCompletionCheckLoopFinished.mkcontrol
	@echo doing stem $* for step5.outputFilePulledToMaster.mkcontrol
	cmd /c 'copy \\$(call getWorkerValueOfTaskKey,$*)\$(WORKER_WORKDIR)\$(call getTaskValueOfTaskKeyOut,$*)  .'
	cmd /c 'echo> $@'
	cmd /c '$(MASTER_LOGGER_BAT) END__ $< $(call getWorkerKeyOfTaskKey,$*)'


#reduce:
#ref. https://www.gnu.org/software/make/manual/html_node/Static-Usage.html
#objects = foo.o bar.o
#all: $(objects)
#$(objects): %.o: %.c
#  $(CC) -c $(CFLAGS) $< -o $@

#TASKS=TASK001 TASK002 TASK003 TASK004 TASK005
#$(FINALFILE) : $(TASK001).out.csv $(TASK002).out.csv $(TASK003).out.csv $(TASK004).out.csv $(TASK005).out.csv

output_files_from_map_tasks = $(foreach TX, $(TASKS), $(call getTaskValueOfTaskKeyOut,$(TX)))

$(FINALFILE) : $(step5_targets)
	$(MASTER_LOGGER_BAT) BEGIN reduce
	cmd /c 'type $(output_files_from_map_tasks) > $(FINALFILE)'
	$(MASTER_LOGGER_BAT) END__ reduce
	@echo output:
	cmd /c 'dir *.out.csv'
	@echo DONE!

###

MASTER_REXEC_BAT=MASTER-TEMP.REMOTEEXEC.BAT
WORKER_LEXEC_BAT=WORKER-TEMP.LOCALEXEC.BAT
MASTER_LOGGER_BAT=MASTER-LOGGER.BAT
MASTER_LOCK_BAT=MASTER-LOCK.BAT
MASTER_LOG=make-log.log



###

install: gen_loc_exec gen_rem_exec gen_logger gen_lock env_check
# NB will likely be done in parallel

env_check:
	@echo HEADH is: $(HEADH)
	@echo MASTER_WORKDIR is: $(MASTER_WORKDIR)
	@echo WORKER_WORKDIR is: $(WORKER_WORKDIR)

gen_lock:
	echo ''                   > $(MASTER_LOCK_BAT)
	echo 'set task=%4'               >> $(MASTER_LOCK_BAT)
	echo 'if [%1]==[release] goto RELEASE'     >> $(MASTER_LOCK_BAT)
	echo 'del /q %task%.tentative.mkcontrol'   >> $(MASTER_LOCK_BAT)
	echo 'FOR %%F in (*.idle.agent) do (echo %%F>%task%.tentative.mkcontrol)'  >> $(MASTER_LOCK_BAT)
	echo 'if not exist %task%.tentative.mkcontrol goto END'  >> $(MASTER_LOCK_BAT)
	echo 'set /p worker=<%task%.tentative.mkcontrol'     >> $(MASTER_LOCK_BAT)
	echo 'SET worker=%worker:~0,-11%'            >> $(MASTER_LOCK_BAT)
	echo 'rem 11 = strlen(.idle.agent)'            >> $(MASTER_LOCK_BAT)
	echo 'ren %worker%.idle.agent %worker%.busy.agent'    >> $(MASTER_LOCK_BAT)
	echo 'if [%errorlevel%]==[0] goto MUTEX'   >> $(MASTER_LOCK_BAT)
	echo 'exit /b 0'               >> $(MASTER_LOCK_BAT)
	echo ':MUTEX'                 >> $(MASTER_LOCK_BAT)
	echo 'echo %worker%>%task%.agent'      >> $(MASTER_LOCK_BAT)
	echo 'echo>%2'                 >> $(MASTER_LOCK_BAT)
	echo 'rem the above will make the loop end'  >> $(MASTER_LOCK_BAT)
	echo 'exit /b 0'               >> $(MASTER_LOCK_BAT)
	echo ':RELEASE'               >> $(MASTER_LOCK_BAT)
	echo 'ren %3.busy.agent %3.idle.agent'     >> $(MASTER_LOCK_BAT)
	echo ':END'                 >> $(MASTER_LOCK_BAT)
	echo 'exit /b 0'               >> $(MASTER_LOCK_BAT)




uninstall:
	@echo uninstall starts
	cmd /c 'del /Q $(MASTER_REXEC_BAT) $(MASTER_LOGGER_BAT) $(MASTER_LOCK_BAT) $(WORKER_LEXEC_BAT)'
	@echo uninstall done


###

gen_logger:
	echo '' > $(MASTER_LOGGER_BAT)
	echo 'echo %TIME% %1 %2 %3 >> $(MASTER_LOG)' >> $(MASTER_LOGGER_BAT)



gen_loc_exec:
	echo '' > $(WORKER_LEXEC_BAT)
	echo 'rem I am expected to be a worker' >> $(WORKER_LEXEC_BAT)
	echo 'SET MYHOSTNAME=%1' >> $(WORKER_LEXEC_BAT)
	echo 'SET FILENM=%2' >> $(WORKER_LEXEC_BAT)
	echo 'SET FILECTR=%3' >> $(WORKER_LEXEC_BAT)
	echo '$(PYCALL_AT_WORKER) \\%MYHOSTNAME%\$(WORKER_WORKDIR)\%FILENM%  \\%MYHOSTNAME%\$(WORKER_WORKDIR)\%FILENM%.out.csv' >> $(WORKER_LEXEC_BAT)
	echo 'echo> \\$(HEADH)\$(MASTER_WORKDIR)\%FILECTR%.step4.workerCompletionCheckLoopFinished.mkcontrol' >> $(WORKER_LEXEC_BAT)

gen_rem_exec:
	echo '' > $(MASTER_REXEC_BAT)
	echo 'rem I am expected to be the head node' >> $(MASTER_REXEC_BAT)
	echo 'set REMOTEHOST=%1' >> $(MASTER_REXEC_BAT)
	echo '$(PSEXEC)  \\%REMOTEHOST%  -accepteula -s -d $(MASTER_NET_ABS_TEMPBAT_LOC)\$(WORKER_LEXEC_BAT) %1 %2 %3' >> $(MASTER_REXEC_BAT)
	echo cd >> $(MASTER_REXEC_BAT)
#  the below cd is required to override the (false) error code returned by PsEcex when used with the -d switch
#TBC use -

###

clean: mkcontrolFilesCleanup remoteInOutFilesCleanup localOutputFilesCleanup localReduceOutputFilesCleanup

mkcontrolFilesCleanup:
#  rerunnable
	@echo === cleaning the .mkcontrol files
	cmd /c 'del /Q *.mkcontrol'
	@echo === done

localReduceOutputFilesCleanup:
	@echo doing ReduceOutputFilesCleanup
	cmd /c 'del /Q $(FINALFILE)'





phonytargets.tasks.remoteInOutFilesCleanup = $(foreach TX, $(TASKS), $(TX).phonytargets.tasks.remoteInOutFilesCleanup)
remoteInOutFilesCleanup: $(phonytargets.tasks.remoteInOutFilesCleanup)
$(phonytargets.tasks.remoteInOutFilesCleanup):
	@echo for remoteInOutFilesCleanup : doing TASK KEY $(patsubst %.phonytargets.tasks.remoteInOutFilesCleanup,%,$@) VALUE $(call getTaskValueOfTaskKey,$(patsubst %.phonytargets.tasks.remoteInOutFilesCleanup,%,$@)) ON WORKER $(call getWorkerValueOfTaskKey,$(patsubst %.phonytargets.tasks.remoteInOutFilesCleanup,%,$@))
	-cmd /c 'del /Q \\$(call getWorkerValueOfTaskKey,$(patsubst %.phonytargets.tasks.remoteInOutFilesCleanup,%,$@))\$(WORKER_WORKDIR)\$(call getTaskValueOfTaskKey,$(patsubst %.phonytargets.tasks.remoteInOutFilesCleanup,%,$@))'
	-cmd /c 'del /Q \\$(call getWorkerValueOfTaskKey,$(patsubst %.phonytargets.tasks.remoteInOutFilesCleanup,%,$@))\$(WORKER_WORKDIR)\$(call getTaskValueOfTaskKeyOut,$(patsubst %.phonytargets.tasks.remoteInOutFilesCleanup,%,$@))'


phonytargets.tasks.localOutputFilesCleanup = $(foreach TX, $(TASKS), $(TX).phonytargets.tasks.localOutputFilesCleanup)
localOutputFilesCleanup: $(phonytargets.tasks.localOutputFilesCleanup)
$(phonytargets.tasks.localOutputFilesCleanup):
	@echo for localOutputFilesCleanup : doing TASK KEY $(patsubst %.phonytargets.tasks.localOutputFilesCleanup,%,$@) VALUE $(call getTaskValueOfTaskKey,$(patsubst %.phonytargets.tasks.localOutputFilesCleanup,%,$@))
	-cmd /c 'del /Q $(call getTaskValueOfTaskKeyOut,$(patsubst %.phonytargets.tasks.localOutputFilesCleanup,%,$@))'



phonytargets.workers.util_rem_dir = $(foreach WX, $(WORKERS), $(WX).phonytargets.workers.util_rem_dir)
util_rem_dir: $(phonytargets.workers.util_rem_dir)
$(phonytargets.workers.util_rem_dir):
	@echo doing HOST KEY $(patsubst %.phonytargets.workers.util_rem_dir,%,$@) VALUE $(call getWorkerValueOfWorkerKey,$(patsubst %.phonytargets.workers.util_rem_dir,%,$@))
	-cmd /c 'dir /OD \\$(call getWorkerValueOfWorkerKey,$(patsubst %.phonytargets.workers.util_rem_dir,%,$@))\$(WORKER_WORKDIR)\'
	@echo 'that was  \\$(call getWorkerValueOfWorkerKey,$(patsubst %.phonytargets.workers.util_rem_dir,%,$@))\$(WORKER_WORKDIR)\'
	@echo '--------'



###

# https://www.gnu.org/software/make/manual/make.html#Wildcard-Function
# https://www.gnu.org/software/make/manual/make.html#Automatic-Variables
# https://www.gnu.org/software/make/manual/html_node/Functions.html
# https://www.gnu.org/software/make/manual/html_node/Pattern-Rules.html    for stems