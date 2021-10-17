# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['C:/Users/janle/Documents/Programming/Python/SecureMessages/client/client.py'],
             pathex=['C:\\Users\\janle\\Documents\\Programming\\Python\\SecureMessages\\output'],
             binaries=[],
             datas=[('C:/Users/janle/Documents/Programming/Python/SecureMessages/client/Crypto', 'Crypto/'), ('C:/Users/janle/Documents/Programming/Python/SecureMessages/client/json', 'json/'), ('C:/Users/janle/Documents/Programming/Python/SecureMessages/client/requests', 'requests/'), ('C:/Users/janle/Documents/Programming/Python/SecureMessages/client/hashlib.py', '.'), ('C:/Users/janle/Documents/Programming/Python/SecureMessages/client/urllib', 'urllib/'), ('C:/Users/janle/Documents/Programming/Python/SecureMessages/client/urllib3', 'urllib3/'), ('C:/Users/janle/Documents/Programming/Python/SecureMessages/client/urllib3-1.26.4.dist-info', 'urllib3-1.26.4.dist-info/')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='client',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
