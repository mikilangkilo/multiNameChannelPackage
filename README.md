# 多渠道不同名称的打包方式

# 使用方式

## 步骤一：增加变体

在app的build.gradle中添加productFlavors变体

```
productFlavors {
        dev {}
        def lines = file("../channel_for_buildgradle.txt").readLines()
        lines.each {
            item ->
                "$item" {
                    manifestPlaceholders = [CHANNEL_VALUE: name]
                }
        }
        productFlavors.all { flavor ->
            flavor.manifestPlaceholders = [CHANNEL_VALUE: name]
            if (flavor.name == "dev") {
                resValue "string", "app_name", "测试版本名字"
                resValue "string", "app_short_name", "测试版本名字"
            } else if (flavor.name == "middlename") {
                // 小米和搜狗用
                resValue "string", "app_name", "app应用市场显示的中等长度名字"
                resValue "string", "app_short_name", "app原名"
            } else if (flavor.name == "shortname") {
                resValue "string", "app_name", "app应用市场显示的短名字"
                resValue "string", "app_short_name", "app原名"
            } else {
                resValue "string", "app_name", "app应用市场显示的中等长度名字"
                resValue "string", "app_short_name", "app原名"
            }
        }
    }
```

## 步骤二：拷贝

拷贝copy文件夹里面的所有文件到项目根目录

## 步骤三：打包

打包有两个入口，一个是全渠道打包，直接执行
```
python channel_release.py
```
执行结束之后会在项目根目录生成一个release_apks目录，里面就有所有的文件了。三个包对应三个名字

第二个打包入口是打单渠道包，这个可以补包，调用方式是

```
//打测试包
python release.py 

//打长名包
python release.py long

//打中名包
python release.py middle

//打短名包
python release.py short
```

## 注意点

由于zipalign对齐工具只能在mac/linux下调用，windows的话大家可以自己看看咋弄，我就没研究了。

另外里面有个自动增加versioncode的功能，用于鉴别相同version包的不同，如果不需要可以在release.py中注释掉。



## 原理

针对现在搜索引擎优化，所以apk名字在应用市场也要打一些广告，但是不同的应用市场对apk名字的限制又不同，所以分为了三类。

打不同名字的包使用的是谷歌提倡的变体，而相同名字打包使用的是美团的V1打包方案。