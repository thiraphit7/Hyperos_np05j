#!/usr/bin/env python
from __future__ import print_function
import getopt, posixpath, signal, struct, sys
import os, copy
import binascii

sparse_file_list = {
    "super":"super.img",
    "metadata":"metadata.img",
    "vm-bootsys":"vm-bootsys.img",
    "rescue":"rescue.img",
    "userdata":"userdata.img",
}

unsparse_file_list = {
    "xbl":"xbl_s.melf",
    "xbl_config":"xbl_config.elf",
    "shrm":"shrm.elf",
    "uefi":"uefi.elf",
    "uefisecapp":"uefi_sec.elf",
    "xbl_ramdump":"XblRamdump.elf",
    "aop":"aop.mbn",
    "aop_config":"aop_devcfg.mbn",
    "abl":"abl.elf",
    "tz":"tz.mbn",
    "featenabler":"featenabler.mbn",
    "devcfg":"devcfg.mbn",
    "hyp":"hypvmperformance.mbn",
    "keymaster":"keymint.mbn",
    "modem":"NON-HLOS.bin",
    "bluetooth":"BTFM.bin",
    "dsp":"dspso.bin",
    "qupfw":"qupv3fw.elf",
    "uefisecapp":"uefi_sec.mbn",
    "imagefv":"imagefv.elf",
    "multiimgoem":"multi_image.mbn",
    "cpucp":"cpucp.elf",
    "cpucp_dtb":"cpucp_dtbs.elf",
    "spuservice":"spu_service.mbn",
    "logfs":"logfs_ufs_8mb.bin",
    "storsec":"storsec.mbn",
    "vendor_boot":"vendor_boot.img",
    "dtbo":"dtbo.img",
    "vbmeta":"vbmeta.img",
    "vbmeta_system":"vbmeta_system.img",
    "recovery":"recovery.img",
    "boot":"boot.img",
    "multiimgqti":"multi_image_qti.mbn",
    "toolsfv":"tools.fv",
    "init_boot":"init_boot.img",
    "misc":"misc.img",
    "countrycode":"countrycode.img",
    "soccp_debug":"sdi.mbn",
    "soccp_dcd":"dcd.mbn",
    "xbl_sc_test_mode":"xbl_sc_test_mode.bin",
    "pdp":"pdp.elf",
    "pdp_cdb":"pdp_cdb.elf",
    "pvmfw":"pvmfw.img",
    "idmanager":"idmanager.mbn",
}


MAX_DOWNLOAD_SIZE = 768*1024*1024;
MAX_SPARSE_PARTS = 20;

SPARSE_IMAGE_HEAD_SZ = 28;
SPARSE_CHUNK_HEAD_SZ = 12;
SPARSE_OVER_HEAD_SZ = SPARSE_IMAGE_HEAD_SZ + 2*SPARSE_CHUNK_HEAD_SZ + 4

file_list=dict(unsparse_file_list,**sparse_file_list)

class SparseChunk:
    def __init__(self):
        self.type  = 0
        self.size = 0
        self.total_sz = 0
        self.data_sz = 0
        self.bksz = 0
        self.data = []

def split_sparse_chunk(backed_sz,bck,sck):

    split_max_len = MAX_DOWNLOAD_SIZE - SPARSE_OVER_HEAD_SZ
    backed_real_sz = backed_sz[0] - SPARSE_CHUNK_HEAD_SZ - 4

    if backed_real_sz + bck.data_sz<= split_max_len:
      backed_sz[0] += bck.total_sz
      return 0,0
    elif backed_real_sz >= (split_max_len*7)/8 :
      if bck.total_sz <= split_max_len :
        backed_sz[0] = bck.total_sz + SPARSE_IMAGE_HEAD_SZ + SPARSE_CHUNK_HEAD_SZ
        return 0,1
      else:
        over_flag = 1
        backed_real_sz = 0
    else:
      over_flag = 0

    split_sz = bck.bksz * ((split_max_len - backed_real_sz) / bck.bksz)

    sck.type = bck.type
    sck.size = bck.size
    sck.bksz = bck.bksz

    sck.data_sz = bck.data_sz - split_sz
    sck.total_sz = sck.data_sz + SPARSE_CHUNK_HEAD_SZ
    sck.data = bck.data[split_sz:]
    sck.size = sck.total_sz / sck.bksz

    bck.data_sz = split_sz
    bck.total_sz = bck.data_sz + SPARSE_CHUNK_HEAD_SZ
    bck.data = bck.data[:bck.data_sz]
    bck.size = bck.total_sz / bck.bksz
    backed_sz[0] = SPARSE_CHUNK_HEAD_SZ + 4

    if over_flag == 1:
      backed_sz[0] = bck.total_sz
      return 1,1
    else:
      backed_sz[0] = SPARSE_CHUNK_HEAD_SZ + SPARSE_IMAGE_HEAD_SZ
      return 1,2

def read_chunk_from_file(FH,blk_sz):
    chunk = SparseChunk()
    header_bin = FH.read(12)
    header = struct.unpack("<2H2I", header_bin)
    chunk.type = header[0]
    reserved1 = header[1]
    chunk.size = header[2]
    chunk.total_sz = header[3]
    chunk.bksz = blk_sz
    chunk.data_sz = chunk.total_sz - SPARSE_CHUNK_HEAD_SZ
    #print ("chunk.type=0x%x reserved1=0x%x chunk.size=%d chunk.total_sz=%d chunk.bksz=%d chunk.data_sz=%d " % (chunk.type, reserved1, chunk.size, chunk.total_sz, chunk.bksz,chunk.data_sz))
    if chunk.type == 0xCAC1:
      if chunk.data_sz != (chunk.size * blk_sz):
        raise Exception(" Raw chunk input size (%u) does not match output size (%u)!!!"
              % (chunk.data_sz, chunk.size * blk_sz))
      else:
        chunk.data = FH.read(chunk.data_sz)
    elif chunk.type == 0xCAC2:
      if chunk.data_sz != 4:
        raise Exception("Fill chunk should have 4 bytes of fill, but this has %u!!!"
              % (chunk.data_sz), end="")
      else:
        chunk.data = FH.read(4)
    elif chunk.type == 0xCAC3:
      if chunk.data_sz != 0:
        print("Don't care chunk input size is non-zero (%u)" % (chunk.data_sz))
    elif chunk.type == 0xCAC4:
      if chunk.data_sz != 4:
        raise Exception("CRC32 chunk should have 4 bytes of CRC, but this has %u!!!"
              % (chunk.data_sz), end="")
      else:
        chunk.data = FH.read(4)
        crc = struct.unpack("<I",chunk.data)
        print("Unverified CRC32 0x%08X" % (crc))
    else:
        raise Exception("Unknown chunk type 0x%04X!!!" % (chunk.type), end="")
    return chunk

def calulate_sparse_chunk_crc(chunk,crc):
    if chunk.type == 0xCAC1:
      crc = binascii.crc32(chunk.data,crc)
    elif chunk.type == 0xCAC2:
      fill_buf = chunk.data*(chunk.bksz/chunk.data_sz)
      for j in xrange(1,chunk.size+1):
        crc = binascii.crc32(fill_buf,crc)
    return crc

def gen_sparse_crc(path):
    sparse_parts = 0
    crc_result_list = [0 for i in range(MAX_SPARSE_PARTS)]
    backedsize = [SPARSE_IMAGE_HEAD_SZ]

    FH = open(path, 'rb')
    header_bin = FH.read(SPARSE_IMAGE_HEAD_SZ)
    header = struct.unpack("<I4H4I", header_bin)

    magic = header[0]
    major_version = header[1]
    minor_version = header[2]
    file_hdr_sz = header[3]
    chunk_hdr_sz = header[4]
    blk_sz = header[5]
    total_blks = header[6]
    total_chunks = header[7]
    image_checksum = header[8]
    image_sz = 0

    if magic != 0xED26FF3A:
      raise Exception("%s: Magic should be 0xED26FF3A but is 0x%08X"
            % (path, magic))
    if major_version != 1 or minor_version != 0:
      raise Exception("%s: I only know about version 1.0, but this is version %u.%u"
            % (path, major_version, minor_version))
    if file_hdr_sz != 28:
      raise Exception("%s: The file header size was expected to be 28, but is %u."
            % (path, file_hdr_sz))
    if chunk_hdr_sz != 12:
      raise Exception("%s: The chunk header size was expected to be 12, but is %u."
            % (path, chunk_hdr_sz))

    print("%s: Total of %u %u-byte output blocks in %u input chunks."
          % (path, total_blks, blk_sz, total_chunks))

    if image_checksum != 0:
      print("checksum=0x%08X" % (image_checksum))

    offset = 0

    for i in xrange(1,total_chunks+1):
      rchunk = read_chunk_from_file(FH,blk_sz)
      split_flag = 1
      sck = SparseChunk()
      while(split_flag == 1):
        split_flag,sparse_part = split_sparse_chunk(backedsize,rchunk,sck)
        if (sparse_part==1): sparse_parts += 1
        crc_result_list[sparse_parts] = calulate_sparse_chunk_crc(rchunk,crc_result_list[sparse_parts])
        if (sparse_part==2): sparse_parts += 1
        #print("%d : crc_result_list[%d] = 0x%x" % (i , sparse_parts , crc_result_list[sparse_parts] & (2**32-1)))
        rchunk = copy.deepcopy(sck)
    return sparse_parts + 1, crc_result_list

def gen_crc(file_path):
    f = open(file_path, "rb")
    crc = binascii.crc32(f.read())
    return crc

def get_sparse_count(cmd):
    line = os.popen(cmd, 'r').readline()
    if line[0]=='I' or line[0]=='i':
        return -1;
    return int(line)

#------------------------------------------------------------------------------
if __name__ == "__main__":
    thispath = os.path.dirname(__file__)
    path = os.path.join(thispath, 'images')
    crclist = os.path.join(path, 'crclist.txt')
    sparsecrclist = os.path.join(path, 'sparsecrclist.txt')
    crc = 0
    try:
        fs = open(sparsecrclist, 'w')
        f  = open(crclist, 'w')
        fs.write("SPARSECRC-LIST\n")
        f.write("CRC-LIST\n")
        for ptn in file_list:
          filepath = os.path.join(path, file_list[ptn])
          print(filepath)
          if not os.path.isfile(filepath):
            print(filepath + ' doesn\'t exist, skip it')
            continue
          if unsparse_file_list.has_key(ptn):
            crc = gen_crc(filepath)
            if crc:
              f.write(ptn + ' ' + hex(crc & (2**32-1)) + '\n')
          else:
            size = os.path.getsize(filepath)
            parts,crclist = gen_sparse_crc(filepath)
            if parts == 0:
              raise Exception("sparse file error!!!!!!!")
            else:
              fs.write(ptn + ' ' + str(parts))
              for i in xrange(1,parts+1):
                fs.write(' ' + hex(crclist[i-1] & (2**32-1)))
              fs.write('\n')
    except Exception, e:
        os.remove(crclist)
        os.remove(sparsecrclist)
        raise
