SPK_NAME = twitter_video_downloader
SPK_VERS = 1.0
SPK_REV = 1
SPK_ICON = src/twitter_video_downloader.png

DEPENDS =

REQUIRED_MIN_DSM = 7.0
UNSUPPORTED_ARCHS =

MAINTAINER = guoli
DESCRIPTION = "A Flask service to download Twitter videos."
DISPLAY_NAME = Twitter Video Downloader
STARTABLE = yes
RELOAD_UI = no
BETA = 1

HOMEPAGE = http://your-homepage
LICENSE  = Apache License 2.0

WIZARDS_DIR = src/wizard/

SERVICE_USER = auto
SERVICE_SETUP = src/service-setup.sh
SERVICE_PORT = 8000
SERVICE_PORT_TITLE = Twitter Video Downloader Web UI

# Admin link for in DSM UI
ADMIN_PORT = $(SERVICE_PORT)

POST_STRIP_TARGET = twitter_video_downloader_extra_install

include ../../mk/spksrc.spk.mk

.PHONY: twitter_video_downloader_extra_install
twitter_video_downloader_extra_install:
	@echo "执行额外安装步骤: 创建目标目录并复制配置文件" | tee -a $(STAGING_DIR)/install.log
	install -m 755 -d $(STAGING_DIR)/var | tee -a $(STAGING_DIR)/install.log
	# 如果有其他配置文件需要安装，请在这里添加
	# install -m 644 src/your_config_file $(STAGING_DIR)/var/your_config_file | tee -a $(STAGING_DIR)/install.log

.PHONY: service-setup
service-setup:
	@echo "开始服务设置步骤" | tee -a $(STAGING_DIR)/install.log
	./src/service-setup.sh | tee -a $(STAGING_DIR)/install.log
	@echo "服务设置完成" | tee -a $(STAGING_DIR)/install.log

# 使服务设置步骤在安装后执行
POST_STRIP_TARGET += service-setup
