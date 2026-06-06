

adb logcat -d | findstr /i "FATAL AndroidRuntime moyu"
                                                                                                         
或者更完整（获取崩溃前后的日志）：                                                                       
                                                                                                         
adb logcat *:E -d | findstr /i "moyu"                                                                    

adb logcat -d | findstr /i "AndroidRuntime FATAL moyu"                                                   

adb logcat -d -s AndroidRuntime | findstr /i "moyu\|FATAL\|Exception\|at com"                            

adb logcat -d | findstr /n "." | findstr /i                                                              
"8822\|9031\|19914\|20219\|AndroidRuntime\|FATAL\|Exception\|at com.moyu"

adb logcat -d *:E > crash.txt                                                                            

adb pull /sdcard/Download/bubble0.png .
adb pull /storage/emulated/0/Download/frame_crop.png .