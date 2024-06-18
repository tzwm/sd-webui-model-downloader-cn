> 这个插件暂时没法用了。因为 civitai 修改了逻辑，现在需要登录验证才能拿到下载信息。

## sd-webui-model-downloader-cn

> 视频演示: https://www.bilibili.com/video/BV11u411a7wB/

- 国内免梯子高速下载 civitai 模型
- 一键下载，自动识别模型类型、自动选择下载路径
- 支持 Checkpoint、LoRA、LyCORIS、VAE、TextualInversion(embedding)、Hypernetwork
- 支持模型图片预览，并且自动下载模型图片到模型同目录下

![](https://files.tzwm.me/images/sd-webui-model-downloader-cn/preview.png)


## 安装方式

### 直接通过 webui 安装（推荐）

![](https://files.tzwm.me/images/sd-webui-model-downloader-cn/extension_install.png)


### 下载安装

1. 下载这个仓库所有文件
2. 解压后把整个文件夹扔进 webui 目录下的 extensions 目录下
3. 重启 webui

### 命令行安装

1. 通过命令行进入 webui 的文件夹
2. 执行

```
cd extensions && git clone --depth 1 https://github.com/tzwm/sd-webui-model-downloader-cn.git
```

3. 重启 webui

## 使用

### 下载不同版本的模型

![](https://files.tzwm.me/images/sd-webui-model-downloader-cn/banner_url_tips.png)

## TODO

- [ ] 下载进度显示
- [x] 预览更多模型信息，包括图片等
- [ ] 模型推荐
- [ ] 下载 LoRA 后自动生成一个 wildcard 文件包含触发词，方便后续一键触发不用到处找触发词

## 交流互助

- Email：sd-model-downloader-cn@tzwm.me
- sd webui 微信交流讨论群：

![](https://oss.talesofai.cn/public/qrcode_20230413-183818.png?cc0429)

## ChangeLog

- v1.1.3 20230629
  - 修复了一下输入错误的地址的报错问题
- v1.1.0 20230624
  - 增加了模型图片预览，并且自动下载模型图片到模型同目录下
- v1.0.1 20230621
  - 尝试修复某些平台 util.py 文件加载不出来的问题
- v1.0.0 20230621
  - 基本的免梯子全自动下载功能实现
