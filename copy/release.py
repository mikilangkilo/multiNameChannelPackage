# coding=utf-8
import zipfile
import shutil
import sys
import subprocess
import os
import re

findline = u"(versionCode\s+:.+)"
findversion = u"([0-9]+)"
findversionname = u"(?<= versionName      : \").+?(?=\")"
depgradlefilepath = "dependencies.gradle"
BRANCH = "dev"


def release(channelName):
    channelName = channelName
    print 'start build ' + channelName

    apk = './app/build/outputs/apk/dev/release/app-dev-release.apk'
    hasApk = os.path.exists(apk)
    path = './release_apks/dev/'
    clean_code = subprocess.check_call("./gradlew clean", shell=True)
    if clean_code != 0:
        print "clean failed"
        sys.exit()
    if channelName == 'long':
        apk = './app/build/outputs/apk/longname/release/app-longname-release.apk'
        path = './release_apks/long/'
        if os.path.exists("release_apks/long"):
            shutil.rmtree("release_apks/long")
        print "delete exist release_apks/long success"
        os.mkdir("release_apks/long")
        assemble_release_code = subprocess.check_call("./gradlew assembleLongnameRelease",
                                                      shell=True)
    elif channelName == 'short':
        apk = './app/build/outputs/apk/shortname/release/app-shortname-release.apk'
        path = './release_apks/short/'
        if os.path.exists("release_apks/short"):
            shutil.rmtree("release_apks/short")
        print "delete exist release_apks/short success"
        os.mkdir("release_apks/short")
        assemble_release_code = subprocess.check_call("./gradlew assembleShortnameRelease",
                                                      shell=True)
    elif channelName == 'middle':
        apk = './app/build/outputs/apk/middlename/release/app-middlename-release.apk'
        path = './release_apks/middle/'
        if os.path.exists("release_apks/middle"):
            shutil.rmtree("release_apks/middle")
        print "delete exist release_apks/middle success"
        os.mkdir("release_apks/middle")
        assemble_release_code = subprocess.check_call("./gradlew assembleMiddlenameRelease",
                                                      shell=True)
    else:
        if os.path.exists("release_apks/dev"):
            shutil.rmtree("release_apks/dev")
        print "delete exist release_apks/dev success"
        os.mkdir("release_apks/dev")
        assemble_release_code = subprocess.check_call("./gradlew assembleDevRelease", shell=True)

    if assemble_release_code != 0:
        print "assembleRelease failed"
        sys.exit()

    emptyFile = 'xxx.txt'
    f = open(emptyFile, 'w')
    f.close()

    if channelName == 'long':
        with open('channelNameLong.txt', 'r') as f:
            contens = f.read()
        lines = contens.split('\n')
    elif channelName == 'short':
        with open('channelNameShort.txt', 'r') as f:
            contens = f.read()
        lines = contens.split('\n')
    elif channelName == 'middle':
        with open('channelNameMiddle.txt', 'r') as f:
            contens = f.read()
        lines = contens.split('\n')
    else:
        with open('devChannel.txt', 'r') as f:
            contens = f.read()
        lines = contens.split('\n')

    if not os.path.exists(path):
        os.mkdir(path)
    else:
        for f in os.listdir(path):
            if not f.endswith('.gitignore'):
                os.remove(path + f)

    for line in lines:
        print line
        channel = 'channel_' + line
        destfile = path + '%s.apk' % channel
        shutil.copyfile(apk, destfile)
        zipped = zipfile.ZipFile(destfile, 'a', zipfile.ZIP_DEFLATED)
        channelFile = "META-INF/{channelname}".format(channelname=channel)
        zipped.write(emptyFile, channelFile)
        zipped.close()
    os.remove('./xxx.txt')

    for f in os.listdir(path):
        if f.endswith('.apk'):
            os.system('zipalign -f -v 4 ' + path + f + ' ' + path + 'temp-' + f)
            os.remove(path + f)

    for f in os.listdir(path):
        if f.startswith('temp-'):
            os.system('zipalign -f -v 4 ' + path + f + ' ' + path + f.replace('temp-', ''))
            os.remove(path + f)


def versionCodePlusPlus(msg):
    gitstash = subprocess.check_call("git stash", shell=True)
    if gitstash != 0:
        print "git stash fail"
        sys.exit()
    print "git stash success"
    gitcheckout = subprocess.check_call("git checkout " + BRANCH, shell=True)
    if gitcheckout != 0:
        print "git checkout dev fail"
        sys.exit()
    print "git checkout dev success"
    gitfetchall = subprocess.check_call("git fetch --all", shell=True)
    if gitfetchall != 0:
        print "git fetch all fail"
        sys.exit()
    gitresetall = subprocess.check_call("git reset --hard origin/" + BRANCH, shell=True)
    if gitresetall != 0:
        print "git reset hard origin dev fail"
        sys.exit()
    gitpull = subprocess.check_call("git pull", shell=True)
    if gitpull != 0:
        print "git pull fail"
        sys.exit()
    print "git pull success"

    originContent = open(depgradlefilepath).read()
    originVersionCodeLine = re.search(findline, originContent).group(0)
    originVersionCodeString = re.search(findversion, originVersionCodeLine).group(0)
    versionname = re.search(findversionname, originContent).group(0)
    originVersionCode = int(originVersionCodeString)
    finalVersionCode = originVersionCode + 1
    finalVersionCodeLine = "versionCode      : " + str(finalVersionCode) + ","
    finalContent = originContent.replace(originVersionCodeLine, finalVersionCodeLine, 1)
    open(depgradlefilepath, 'w').write(finalContent)
    gitadd = subprocess.check_call("git add .", shell=True)
    if gitadd != 0:
        print "git add failed"
        sys.exit()
    gitCommit = subprocess.check_call(
        u"git commit -m \"build/auto increase versionCode = " + str(
            finalVersionCode) + "," + msg + "\"",
        shell=True)
    if gitCommit != 0:
        print "gitCommit failed"
        sys.exit()
    gitPush = subprocess.check_call(
        "git push origin " + BRANCH, shell=True
    )
    if gitPush != 0:
        print "gitpush failed"
        sys.exit()

    gitpull = subprocess.check_call("git pull", shell=True)
    if gitpull != 0:
        print "git pull fail"
        sys.exit()
    print "git pull success"
    return finalVersionCode, versionname


if __name__ == '__main__':
    if os.path.exists("release_apks"):
        shutil.rmtree("release_apks")
        print "delete exist release_apks success"
    os.mkdir("release_apks")

    if os.path.exists("app/build"):
        shutil.rmtree("app/build")
    print "delete exist release_apks success"
    channel = 'dev'
    if len(sys.argv) >= 2:
        channel = sys.argv[1]
    versionCodePlusPlus(channel)
    release(channel)
