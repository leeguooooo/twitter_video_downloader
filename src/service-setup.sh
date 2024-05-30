#!/bin/sh

echo "$(date): 开始服务设置"

# 创建必要的目录
INSTALL_DIR="/var/packages/${SYNOPKG_PKGNAME}/target"
mkdir -p ${INSTALL_DIR}


# 复制文件到目标目录（如果有需要）
# cp -r /path/to/your/app/* ${INSTALL_DIR} >> ${LOG_FILE} 2>&1

# 服务命令
SERVICE_COMMAND="${INSTALL_DIR}/bin/twitter_video_downloader.sh"

# 启动服务
service_postinst ()
{
    echo "$(date): Starting post-installation steps" >> ${LOG_FILE}
    ln -s ${SYNOPKG_PKGDEST} ${INSTALL_DIR} >> ${LOG_FILE} 2>&1
    ${SERVICE_COMMAND} start >> ${LOG_FILE} 2>&1
    echo "$(date): Service started" >> ${LOG_FILE}
}

# 停止服务
service_postuninst ()
{
    echo "$(date): Starting post-uninstallation steps" >> ${LOG_FILE}
    ${SERVICE_COMMAND} stop >> ${LOG_FILE} 2>&1
    rm -f ${INSTALL_DIR} >> ${LOG_FILE} 2>&1
    echo "$(date): Service stopped and directory removed" >> ${LOG_FILE}
}

# 执行安装后的步骤
service_postinst
