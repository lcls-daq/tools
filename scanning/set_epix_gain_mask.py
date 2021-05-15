import pydaq
import pycdb
import argparse
import numpy as np


def get_db_from_daq(daqinfo):
    try:
        host, platform = daqinfo.split(":")
    except ValueError:
        host = daqinfo
        platform = 0
    daq = pydaq.Control(host, platform)
    daq.connect()
    dbalias = daq.dbalias()
    dbpath = daq.dbpath()
    daq.disconnect()
    return dbpath, dbalias


def get_src_info(src):
    """
    Encodes a detinfo src string into its integer equivalent 
    """
    daq = pydaq.Control('test')
    detname, detid, devname, devid = src.split("/")
    det = daq.detectors().index(detname) & 0xff
    detid = int(detid) & 0xff
    dev = daq.devices().index(devname) & 0xff
    devid = int(devid) & 0xff
    return (det << 24) | (detid << 16) | (dev << 8) | devid


def set_gain_mask(gain_arr, trbit, dbpath, dbalias, src):
    """
    gain_arr: 3-d numpy array of the gain values
    dbpath: db path connection info file path
    dbalias: e.g. BEAM, NOBEAM, etc.
    src: XcsEndstation/0/Epix10ka2M/0
    """
    srcid = get_src_info(src)

    db = pycdb.Db(dbpath)
    xtc = db.get(alias=dbalias, src=srcid)[0]
    cfg = xtc.get()
    if 'elemCfg' in cfg:
        for i, elem in enumerate(cfg['elemCfg']):
            mask = elem['asicMask']
            elem['asicPixelConfigArray'] = gain_arr[i].tolist()
            for asicNum in range(4):
                if mask & (1 << asicNum) :
                    elem['asics'][asicNum]['trbit'] = trbit
    else:
        mask = cfg['AsicMask']
        cfg['asicPixelConfigArray'] = gain_arr.tolist()
        for asicNum in range(4):
            if mask & (1 << asicNum):
                cfg['asics'][asicNum]['trbit'] = trbit
    xtc.set(cfg)
    db.set(xtc, dbalias)
    db.commit()


def main():
    parser = argparse.ArgumentParser(description='Epix pixel gain mask setter')
    parser.add_argument("-A",
                        "--dbalias",
                        default="BEAM",
                        help="data base key in use")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-H',
                       '--hutch',
                       help='hutch configuration database to use')
    group.add_argument('-d',
                       '--daq',
                       help='use a running DAQ to discover the db to use')
    parser.add_argument('-t',
                        '--trbit',
                        action="store_true",
                        help='set the trbit controls High->Low vs Med->Low')
    parser.add_argument("src",
                        help="the detector source string e.g. XcsEndstation/0/Epix10ka2M/0")
    parser.add_argument('mask',
                        type=argparse.FileType('r'),
                        help='the mask file to load')

    args = parser.parse_args()

    dbpath = None
    if args.hutch:
        dbalias = args.dbalias
        dbpath = f"/cds/group/pcds/dist/pds/{args.hutch.lower()}/misc/.configdbrc"
    else:
        dbpath, dbalias = get_db_from_daq(args.daq)

    mask = np.loadtxt(args.mask)
    # turn the mask into a 3d array if needed
    if mask.shape[0] > 352:
        mask = mask.reshape(mask.shape[0]//352, 352, mask.shape[1])

    gains = np.where(mask > 0, 0x8, 0xc)

    if args.trbit:
        print("Setting pixels to High/Low gain based on mask file")
    else:
        print("Setting pixels to Medium/Low gain based on mask file")

    set_gain_mask(gains, int(args.trbit), dbpath, dbalias, args.src)


if __name__ == '__main__':
    main()
