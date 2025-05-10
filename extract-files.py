#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

from extract_utils.file import File
from extract_utils.fixups_blob import (
    BlobFixupCtx,
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixup_remove,
    lib_fixups,
    lib_fixups_user_type,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)
from extract_utils.tools import (
    llvm_objdump_path,
)
from extract_utils.utils import (
    run_cmd,
)

namespace_imports = [
    'device/realme/sm8250-common',
    'hardware/oplus',
    'hardware/qcom-caf/sm8250',
    'hardware/qcom-caf/wlan',
    'vendor/qcom/opensource/commonsys-intf/display',
    'vendor/qcom/opensource/commonsys/display',
    'vendor/qcom/opensource/dataservices',
    'vendor/qcom/opensource/display',
]

def lib_fixup_vendor_suffix(lib: str, partition: str, *args, **kwargs):
    return f'{lib}_vendor' if partition in ['odm', 'vendor'] else None


lib_fixups: lib_fixups_user_type = {
    **lib_fixups,
    (
        'com.qti.stats.pdlib',
        'com.qualcomm.qti.dpm.api@1.0',
        'libmmosal',
        'vendor.qti.hardware.wifidisplaysession@1.0',
        'vendor.qti.imsrtpservice@3.0',
    ): lib_fixup_vendor_suffix,
}

def blob_fixup_nop_call(
    ctx: BlobFixupCtx,
    file: File,
    file_path: str,
    call_instruction: str,
    disassemble_symbol: str,
    symbol: str,
    *args,
    **kwargs,
):
    for line in run_cmd(
        [
            llvm_objdump_path,
            f'--disassemble-symbols={disassemble_symbol}',
            file_path,
        ]
    ).splitlines():
        line = line.split(maxsplit=3)

        if len(line) != 4:
            continue

        offset, _, instruction, args = line

        if instruction != call_instruction:
            continue

        if not args.endswith(f' <{symbol}>'):
            continue

        with open(file_path, 'rb+') as f:
            f.seek(int(offset[:-1], 16))
            f.write(b'\x1f\x20\x03\xd5')  # AArch64 NOP

        break


blob_fixups: blob_fixups_user_type = {
    'vendor/etc/msm_irqbalance.conf': blob_fixup()
        .regex_replace(r'(IGNORED_IRQ=27,23,38)$', r'\\1,115,332'),
    'vendor/lib64/hw/camera.qcom.so': blob_fixup()
        .add_needed('libcamera_metadata_shim.so'),
    'vendor/lib64/vendor.qti.hardware.camera.postproc@1.0-service-impl.so': blob_fixup()
        .sig_replace('AF 0B 00 94', '1F 20 03 D5'),
    ('vendor/lib/libgui1_vendor.so'): blob_fixup()
        .replace_needed('libui.so', 'libui-v30.so'),
    ('odm/lib64/mediadrm/libwvdrmengine.so', 'odm/lib64/libwvhidl.so'): blob_fixup()
        .add_needed('libcrypto_shim.so'),
    ('odm/lib64/libwvhidl.so', 'odm/lib64/mediadrm/libwvdrmengine.so', 'odm/lib64/libdmtp.so', 'odm/lib64/libdmtpclient.so', 'odm/lib64/libdmtp-protos-lite.so', 'odm/lib64/lib-virtual-modem-protos.so', 'odm/lib64/liboplus_service.so', 'vendor/lib64/libssc.so', 'vendor/lib64/libsensorcal.so', 'vendor/lib64/sensors.ssc.so', 'vendor/lib64/libsnsdiaglog.so', 'vendor/lib64/libsnsapi.so', 'vendor/bin/sensors.qti'): blob_fixup()
        .replace_needed('libprotobuf-cpp-lite-3.9.1.so', 'libprotobuf-cpp-full-3.9.1.so'),
    ('odm/lib64/mediadrm/libwvdrmengine.so', 'odm/lib64/libwvhidl.so'): blob_fixup()
        .add_needed('libcrypto_shim.so'),
    ('vendor/lib64/libwvhidl.so', 'vendor/lib/mediadrm/libwvdrmengine.so', 'vendor/lib64/mediadrm/libwvdrmengine.so'): blob_fixup()
        .replace_needed('libcrypto.so', 'libcrypto-v33.so'),
}  # fmt: skip


module = ExtractUtilsModule(
    'sm8250-common',
    'realme',
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
    namespace_imports=namespace_imports,
)

if __name__ == '__main__':
    utils = ExtractUtils.device(module)
    utils.run()
