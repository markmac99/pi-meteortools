# tests for auroracam

import configparser
import platform
import os
import shutil
from archAndFree import getFilesToUpload, getDeletableFiles, compressAndDelete
from archAndFree import compressAndUpload
from auroraCam import getAWSConn


dummydirs = ['20240913_060041', '20240916_060545', '20240917_175030', 
              '20240914_060223', '20240909_180941', '20240912_055859', 
              '20240907_181430', '20240910_055535', 
              '20240911_180453', '20240909_055352', '20240913_180005', '20240916_175254', 
              '20240914_175741', '20240912_180229', '20240911_055717', '20240908_181206', 
              '20240907_055026', '20240917_060726', '20240908_055210', '20240910_180717']


def loadDummyConfig():
    cfgobj = configparser.ConfigParser()
    cfgobj.read('config.ini')
    return cfgobj


def createDummyData(cfg):
    for f in dummydirs:
        os.makedirs(os.path.join(cfg['auroracam']['datadir'], f), exist_ok=True)
        open(os.path.join(cfg['auroracam']['datadir'], f, 'test1.txt'), 'w').write('hello')
    return 


def removeDummyData(cfg):
    for f in dummydirs:
        shutil.rmtree(os.path.join(cfg['auroracam']['datadir'], f))
    return 


def test_getAWSConn_noidserver():
    uid = platform.uname()[1]
    cfg = loadDummyConfig()
    s3 = getAWSConn(cfg, uid, uid)
    assert s3 is not None


def test_getAWSConn_localkey():
    uid = platform.uname()[1]
    cfg = loadDummyConfig()
    cfg['uploads']['idkey']='/mnt/e/dev/aws/awskeys/actest.csv'
    s3 = getAWSConn(cfg, uid, uid)
    assert s3 is not None


def test_getAWSConn_withidserver():
    uid = 'auroracam'
    cfg = loadDummyConfig()
    cfg['uploads']['idserver'] = 'wordpresssite'
    cfg['uploads']['idkey']='~/.ssh/auroracam'
    s3 = getAWSConn(cfg, uid, uid)
    assert s3 is not None


def test_getFilesToUpload_s3():
    cfg = loadDummyConfig()
    cfg['auroracam']['datadir']='/tmp/testac'
    cfg['uploads']['idkey']='/mnt/e/dev/aws/awskeys/actest.csv'
    cfg['auroracam']['camid']='UK9999'
    cfg['uploads']['s3uploadloc']='s3://ukmon-shared'
    ftu = getFilesToUpload(cfg, uid='auroracam')
    try:
        os.remove(os.path.join('/tmp/testac', 'FILES_TO_UPLOAD.inf'))
    except Exception:
        pass
    assert ftu != []
    assert ftu[0] == '20240916_175254'


def test_getFilesToUpload_ftp():
    cfg = loadDummyConfig()
    cfg['auroracam']['datadir']='/tmp/testac'
    cfg['auroracam']['camid']='UK9999'
    cfg['archive']['archserver']='thelinux'
    cfg['archive']['archuser']='mark'
    cfg['archive']['archfldr']='/data3/astrodata/actest'
    cfg['archive']['archkey']='~/.ssh/markskey.pem'
    ftu = getFilesToUpload(cfg, uid='auroracam')
    try:
        os.remove(os.path.join('/tmp/testac', 'FILES_TO_UPLOAD.inf'))
    except Exception:
        pass
    assert ftu != []
    assert ftu[0] == '20240916_175254'


def test_getFilesToUpload_localonly():
    cfg = loadDummyConfig()
    open('/tmp/FILES_TO_UPLOAD.inf', 'w').write('20240916_175254\n')
    cfg['auroracam']['datadir']='/tmp/testac'
    cfg['auroracam']['camid']='UK9999'
    ftu = getFilesToUpload(cfg, uid='auroracam')
    try:
        os.remove(os.path.join('/tmp/testac', 'FILES_TO_UPLOAD.inf'))
    except Exception:
        pass
    assert ftu != []
    assert ftu[0] == '20240916_175254'


def test_getDeletableFiles():
    cfg = loadDummyConfig()
    cfg['auroracam']['datadir']='/tmp/testac'
    createDummyData(cfg)
    flist = getDeletableFiles(cfg, ['20240911_055717'])
    removeDummyData(cfg)
    assert flist[0] == '20240907_055026'
    assert '20240911_055717' in flist


def test_compressAndDelete():
    cfg = loadDummyConfig()
    cfg['auroracam']['datadir']='/tmp/testac'
    createDummyData(cfg)
    zipfile = compressAndDelete(cfg, '20240907_055026')
    assert zipfile == '/tmp/testac/20240907_055026.zip'
    assert not os.path.isdir('/tmp/testac/20240907_055026')
    removeDummyData(cfg)


def test_compressAndupload():
    cfg = loadDummyConfig()
    cfg['auroracam']['datadir']='/tmp/testac'
    cfg['archive']['archserver']='thelinux'
    cfg['archive']['archuser']='mark'
    cfg['archive']['archfldr']='/data3/astrodata/actest'
    cfg['archive']['archkey']='~/.ssh/markskey.pem'
    createDummyData(cfg)
    zipfile = compressAndUpload(cfg, '20240907_055026')
    assert zipfile == '/tmp/testac/20240907_055026.zip'
    assert os.path.isdir('/tmp/testac/20240907_055026')
    removeDummyData(cfg)


def test_compressAndupload_noarch():
    cfg = loadDummyConfig()
    cfg['auroracam']['datadir']='/tmp/testac'
    createDummyData(cfg)
    zipfile = compressAndUpload(cfg, '20240907_055026')
    assert zipfile == '/tmp/testac/20240907_055026.zip'
    assert os.path.isdir('/tmp/testac/20240907_055026')
    assert os.path.isfile(zipfile)
    removeDummyData(cfg)
