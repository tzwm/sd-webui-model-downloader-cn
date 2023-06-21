## sd-webui-model-downloader-cn

- 国内免梯子高速下载 civitai 模型
- 一键下载，自动识别模型类型、自动选择下载路径
- 支持 Checkpoint、LoRA、LyCORIS、VAE、TextualInversion(embedding)、Hypernetwork

![](https://raw.githubusercontent.com/tzwm/sd-webui-model-downloader-cn/main/docs/preview.png)


## 安装方式

### 直接通过 webui 安装（推荐）

![](https://raw.githubusercontent.com/tzwm/sd-webui-model-downloader-cn/main/docs/extension_install.png)


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

![](https://raw.githubusercontent.com/tzwm/sd-webui-model-downloader-cn/main/docs/banner_url_tips.png)

## TODO

- [ ] 下载进度显示
- [ ] 预览更多模型信息，包括图片等
- [ ] 模型推荐

## 交流互助

- Email：sd-model-downloader-cn@tzwm.me
- sd webui 微信交流讨论群：

![](https://oss.talesofai.cn/public/qrcode_20230413-183818.png?cc0429)

## ChangeLog

- v1.0.1 20230621
  - 尝试修复某些平台 util.py 文件加载不出来的问题
- v1.0.0 20230621
  - 基本的免梯子全自动下载功能实现
