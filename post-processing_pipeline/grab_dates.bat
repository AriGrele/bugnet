if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit )
cd "../data/input"

for /r %%f in (*.*) do (
    setlocal EnableDelayedExpansion
    set "info=%%~ff,1,"
    for /f "usebackq tokens=*" %%i in (`magick identify -format "%%[EXIF:DateTime]" "%%~ff"`) do set "info=!info!%%i"
    echo !info! >> ../../post-processing_pipeline/data/exif_dates.txt
    endlocal
)