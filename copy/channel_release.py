# coding=utf-8
from release import release, versionCodePlusPlus
import os
import shutil


FLAVOR_FILE = 'all_channels.txt'
if __name__ == '__main__':
    if os.path.exists("release_apks"):
        shutil.rmtree("release_apks")
        print "delete exist release_apks success"
    if os.path.exists("app/build"):
        shutil.rmtree("app/build")
    print "delete exist release_apks success"
    os.mkdir("release_apks")


    versionCodePlusPlus('middle')
    release('middle')
    versionCodePlusPlus('long')
    release('long')
    versionCodePlusPlus('short')
    release('short')
