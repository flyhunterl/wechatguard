from PyInstaller.utils.win32.versioninfo import *

version_info = VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=(0, 1, 5, 0),
        prodvers=(0, 1, 5, 0),
        mask=0x3f,
        flags=0x0,
        OS=0x40004,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0)
    ),
    kids=[
        StringFileInfo(
            [
                StringTable(
                    u'040904B0',
                    [
                        StringStruct(u'CompanyName', u'个人开发'),
                        StringStruct(u'FileDescription', u'WeChat Guardian - 微信守护程序'),
                        StringStruct(u'FileVersion', u'0.1.5.0'),
                        StringStruct(u'InternalName', u'WeChatGuard'),
                        StringStruct(u'LegalCopyright', u'(C) 2024 个人开发'),
                        StringStruct(u'OriginalFilename', u'WeChatGuard.exe'),
                        StringStruct(u'ProductName', u'WeChat Guardian'),
                        StringStruct(u'ProductVersion', u'0.1.5.0')
                    ]
                )
            ]
        ),
        VarFileInfo([VarStruct(u'Translation', [2052, 1200])])
    ]
)

# 使用 UTF-8 编码写入文件
with open('version_info.txt', 'w', encoding='utf-8') as f:
    f.write(str(version_info)) 