fastboot %* getvar product 2>&1 | findstr /r /c:"^product: *piano" || echo Missmatching image and device
fastboot %* getvar product 2>&1 | findstr /r /c:"^product: *piano" || exit /B 1

::check anti_version
if exist "%~dp0images\anti_version.txt" (for /f "usebackq" %%a in ("%~dp0images\anti_version.txt") do (set CURRENT_ANTI_VER=%%a))
if [%CURRENT_ANTI_VER%] EQU [] set CURRENT_ANTI_VER=0
for /f "tokens=2 delims=: " %%i in ('fastboot %* getvar anti 2^>^&1 ^| findstr /r /c:"anti:"') do (set version=%%i)
if [%version%] EQU [] set version=0
set anticheck="antirollback check pass"
if %version% GTR %CURRENT_ANTI_VER% set anticheck="Current device antirollback version is greater than this pakcage"
echo %anticheck% | findstr /r /c:"pass" || @echo "Antirollback check error" && exit /B 1

fastboot %* getvar crc 2>&1 | findstr /r /c:"^crc: 1"
if %errorlevel% equ 0 (
fastboot %* flash crclist %~dp0images\crclist.txt || @echo "Flash crclist error" && exit /B 1
fastboot %* flash sparsecrclist %~dp0images\sparsecrclist.txt || @echo "Flash sparsecrclist error" && exit /B 1
)

fastboot %* erase boot_ab || @echo "Erase boot error" && exit /B 1
fastboot %* flash abl_ab %~dp0images/abl.elf || @echo "Flash abl error" && exit 1
fastboot %* flash xbl_ab %~dp0images/xbl_s.melf || @echo "Flash xbl error" && exit 1
fastboot %* flash xbl_config_ab %~dp0images/xbl_config.elf || @echo "Flash xbl_config error" && exit 1
fastboot %* flash cpucp_dtb_ab %~dp0images/cpucp_dtbs.elf || @echo "Flash cpucp_dtb error" && exit 1
fastboot %* flash shrm_ab %~dp0images/shrm.elf || @echo "Flash shrm error" && exit 1
fastboot %* flash aop_ab %~dp0images/aop.mbn || @echo "Flash aop error" && exit 1
fastboot %* flash aop_config_ab %~dp0images/aop_devcfg.mbn || @echo "Flash aop_config error" && exit 1
fastboot %* flash tz_ab %~dp0images/tz.mbn || @echo "Flash tz error" && exit 1
fastboot %* flash devcfg_ab %~dp0images/devcfg.mbn || @echo "Flash devcfg error" && exit 1
fastboot %* flash featenabler_ab %~dp0images/featenabler.mbn || @echo "Flash featenabler error" && exit 1
fastboot %* flash hyp_ab %~dp0images/hypvmperformance.mbn || @echo "Flash hyp error" && exit 1
fastboot %* flash uefi_ab %~dp0images/uefi.elf || @echo "Flash uefi error" && exit 1
fastboot %* flash uefisecapp_ab %~dp0images/uefi_sec.mbn || @echo "Flash uefisecapp error" && exit 1
fastboot %* flash spuservice_ab %~dp0images/spu_service.mbn || @echo "Flash spu_service error" && exit 1
fastboot %* flash modem_ab %~dp0images/NON-HLOS.bin || @echo "Flash modem error" && exit 1
::fastboot %* flash modemfirmware_ab %~dp0images/MODEM-FW.bin || @echo "Flash modem firmware error" && exit 1
fastboot %* flash bluetooth_ab %~dp0images/BTFM.bin || @echo "Flash bluetooth error" && exit 1
fastboot %* flash dsp_ab %~dp0images/dspso.bin || @echo "Flash dsp error" && exit 1
fastboot %* flash keymaster_ab %~dp0images/keymint.mbn || @echo "Flash keymaster error" && exit 1
fastboot %* flash idmanager_ab %~dp0images/idmanager.mbn || @echo "Flash idmanager error" && exit 1
fastboot %* flash qupfw_ab %~dp0images/qupv3fw.elf || @echo "Flash qupfw error" && exit 1
fastboot %* flash multiimgoem_ab %~dp0images/multi_image.mbn || @echo "Flash multiimgoem error" && exit 1
fastboot %* flash multiimgqti_ab %~dp0images/multi_image_qti.mbn || @echo "Flash multiimgqti error" && exit 1
fastboot %* flash cpucp_ab %~dp0images/cpucp.elf || @echo "Flash cpucp error" && exit 1
fastboot %* flash pdp_cdb_ab %~dp0images/pdp_cdb.elf || @echo "Flash pdp_cdb error" && exit 1
fastboot %* flash soccp_debug_ab %~dp0images/sdi.mbn || @echo "Flash soccp_debug error" && exit 1
fastboot %* flash soccp_dcd_ab %~dp0images/dcd.mbn || @echo "Flash soccp_dcd error" && exit 1
fastboot %* flash pdp_ab %~dp0images/pdp.elf || @echo "Flash pdp error" && exit 1
fastboot %* flash xbl_sc_test_mode %~dp0images/xbl_sc_test_mode.bin || @echo "Flash xbl_sc_test_mode error" && exit 1
fastboot %* flash logfs %~dp0images/logfs_ufs_8mb.bin || @echo "Flash logfs error" && exit 1
fastboot %* flash storsec %~dp0images/storsec.mbn || @echo "Flash storsec error" && exit 1
fastboot %* flash toolsfv %~dp0images/tools.fv || @echo "Flash toolsfv error" && exit 1
fastboot %* flash xbl_ramdump_ab %~dp0images/XblRamdump.elf || @echo "Flash xbl_ramdump error" && exit 1
fastboot %* erase imagefv_ab || @echo "Erase imagefv error" && exit /B 1
fastboot %* flash imagefv_ab %~dp0images/imagefv.elf || @echo "Flash imagefv error" && exit 1
fastboot %* flash pvmfw_ab %~dp0images/pvmfw.img || @echo "Flash pvmfw error" && exit 1
fastboot %* flash countrycode %~dp0images/countrycode.img || @echo "Flash countrycode error" && exit 1
fastboot %* flash init_boot_ab %~dp0images/init_boot.img || @echo "Flash init_boot error" && exit 1
fastboot %* flash super %~dp0images/super.img || @echo "Flash super error" && exit 1
fastboot %* flash vendor_boot_ab %~dp0images/vendor_boot.img || @echo "Flash vendor_boot error" && exit 1
fastboot %* flash dtbo_ab %~dp0images/dtbo.img || @echo "Flash dtbo error" && exit 1
fastboot %* flash vm-bootsys_ab %~dp0images/vm-bootsys.img || @echo "Flash vm-bootsys error" && exit 1
fastboot %* flash vbmeta_ab %~dp0images/vbmeta.img || @echo "Flash vbmeta error" && exit 1
fastboot %* flash vbmeta_system_ab %~dp0images/vbmeta_system.img || @echo "Flash vbmeta_system error" && exit 1
fastboot %* erase metadata || @echo "Erase metadata error" && exit 1
fastboot %* flash metadata %~dp0images/metadata.img || @echo "Flash metadata error" && exit 1
fastboot %* flash userdata %~dp0images/userdata.img || @echo "Flash userdata error" && exit 1
fastboot %* flash rescue %~dp0images/rescue.img || @echo "Flash rescue error" && exit 1
fastboot %* flash misc %~dp0images\misc.img || @echo "Flash misc error" && exit /B 1
fastboot %* flash recovery_ab %~dp0images/recovery.img || @echo "Flash recovery error" && exit 1
fastboot %* flash boot_ab %~dp0images/boot.img || @echo "Flash boot error" && exit 1
fastboot %* set_active a || @echo "Set active a error" && exit 1
fastboot %* oem lock || @echo "Reboot error" && exit 1
