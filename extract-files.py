#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

from extract_utils.fixups_blob import (
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)

blob_fixups: blob_fixups_user_type = {
    'vendor/etc/msm_irqbalance.conf': blob_fixup()
        .regex_replace('IGNORED_IRQ=27,23,38$', 'IGNORED_IRQ=27,23,38,115,332'),
    'vendor/lib64/hw/camera.qcom.so': blob_fixup()
        .add_needed('libcamera_metadata_shim.so'),
    'vendor/lib64/vendor.qti.hardware.camera.postproc@1.0-service-impl.so': blob_fixup()
        .sig_replace('AF 0B 00 94', '1F 20 03 D5'),
    'vendor/lib/libgui1_vendor.so': blob_fixup()
        .replace_needed('libui.so', 'libui-v30.so'),
    'odm/lib64/libwvhidl.so': blob_fixup()
        .replace_needed('libprotobuf-cpp-lite-3.9.1.so', 'libprotobuf-cpp-full-3.9.1.so')
        .add_needed('libcrypto_shim.so'),
    'odm/lib64/mediadrm/libwvdrmengine.so': blob_fixup()
        .replace_needed('libprotobuf-cpp-lite-3.9.1.so', 'libprotobuf-cpp-full-3.9.1.so')
        .add_needed('libcrypto_shim.so'),
    (
        'odm/lib64/libdmtp.so',
        'odm/lib64/libdmtpclient.so',
        'odm/lib64/libdmtp-protos-lite.so',
        'odm/lib64/lib-virtual-modem-protos.so',
        'odm/lib64/liboplus_service.so',
        'vendor/lib64/libssc.so',
        'vendor/lib64/libsensorcal.so',
        'vendor/lib664/sensors.ssc.so',
        'vendor/lib64/libsnsdiaglog.so',
        'vendor/lib64/libsnsapi.so',
        'vendor/bin/sensors.qti',
    ): blob_fixup()
        .replace_needed('libprotobuf-cpp-lite-3.9.1.so', 'libprotobuf-cpp-full-3.9.1.so'),
    (
        'vendor/lib64/libwvhidl.so',
        'vendor/lib/mediadrm/libwvdrmengine.so',
        'vendor/lib64/mediadrm/libwvdrmengine.so',
    ): blob_fixup()
        .replace_needed('libcrypto.so', 'libcrypto-v33.so'),
}  # fmt: skip

module = ExtractUtilsModule(
    'sm8250-common',
    'realme',
    blob_fixups=blob_fixups,
)

if __name__ == '__main__':
    utils = ExtractUtils.device(module)
    utils.run()
