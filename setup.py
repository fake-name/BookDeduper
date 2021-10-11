from distutils.core import setup, Extension

lzxm = Extension('lzx',
					sources = [
						'util/ext/lzx/compressor.c',
						'util/ext/lzx/lzc.c',
						'util/ext/lzx/lzxc.c',
						'util/ext/lzx/lzxd.c',
						'util/ext/lzx/lzxmodule.c',
					],
				include_dirs = ['util/ext/lzx'],
			)

msdesm = Extension('msdes',
					sources = [
						"util/ext/msdes/des.c",
						"util/ext/msdes/msdesmodule.c",
					],
				include_dirs = ['util/ext/msdes'],
			)

setup (name = 'calibre_extensions',
	   version = '0.0.1',
	   description = 'Test',
	   ext_modules = [lzxm, msdesm])



