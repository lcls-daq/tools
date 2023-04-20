import re
import sys
import pycdb
import pydaq
import argparse


def auto_int(val):
    return int(val, 0)


def parse_source(src):
    daq = pydaq.Control(0)
    hutch, src = re.split(':', src)
    det, detid, dev, devid = re.split('[/|]', src)
    
    det = daq.detectors().index(det)
    detid = int(detid)
    dev = daq.devices().index(dev)
    devid = int(devid)

    return hutch, src, det<<24 | detid<<16 | dev<<8 | devid<<0


def diff_list(prefix, list1, list2):
    if len(list1) == len(list2):
        for i, (v1, v2) in enumerate(zip(list1, list2)):
            name = f"{prefix}.{i}" if prefix else f"{i}"
            if isinstance(v1, dict) and isinstance(v2, dict):
                diff_dict(name, v1, v2)
            elif isinstance(v1, list) and isinstance(v2, list):
                diff_list(name, v1, v2)
            else:
                print(f"mismatch for {name}: {v1} vs {v2}")
    else:
        print("mismatched list lens",
              f" {prefix}:" if prefix else ":",
              f"{len(list1)} vs {len(list2)}")


def diff_dict(prefix, dict1, dict2):
    keys1 = set(dict1)
    keys2 = set(dict2)
    if keys1 == keys2:
        for key in dict1.keys():
            if dict1[key] != dict2[key]:
                name = f"{prefix}.{key}" if prefix else f"{key}"
                if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                    diff_dict(name, dict1[key], dict2[key])
                elif isinstance(dict1[key], list) and isinstance(dict2[key], list):
                    diff_list(name, dict1[key], dict2[key])
                else:
                    print(f"mismatch for {name}: {dict1[key]} vs {dict2[key]}")
    else:
        print("mismatched dict keys", f" {prefix}:" if prefix else ":")
        print(f"keys in first dict but not second: {keys1-keys2}")
        print(f"keys in second dict but not first: {keys2-keys1}")


def main(hutch1, name1, src1, hutch2, name2, src2, alias, dbkey):
    if hutch1 == hutch2:
        db1 = db2 = pycdb.Db(f"/cds/group/pcds/dist/pds/{hutch1}/misc/.configdbrc")
    else:
        db1 = pycdb.Db(f"/cds/group/pcds/dist/pds/{hutch1}/misc/.configdbrc")
        db2 = pycdb.Db(f"/cds/group/pcds/dist/pds/{hutch2}/misc/.configdbrc")
    if dbkey is not None:
        if len(dbkey) > 1:
            dbkey1 = dbkey[0]
            dbkey2 = dbkey[0]
        else:
            dbkey1 = dbkey[0]
            dbkey2 = dbkey[0]
        xtc1 = db1.get(key=dbkey1, src=src1)[0]
        xtc2 = db2.get(key=dbkey1, src=src2)[0]
    else:
        xtc1 = db1.get(alias=alias, src=src1)[0]
        xtc2 = db2.get(alias=alias, src=src2)[0]

    cfg1 = xtc1.get()
    cfg2 = xtc2.get()

    print(f"Diffing the configs or {name1} and {name2}:")
    diff_dict(None, cfg1, cfg2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Diffs config xtc blobs from the configuration database'
    )

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        '-a',
        '--alias',
        default='BEAM',
        metavar='ALIAS',
        help='the db alias to use for accessing the configs'
    )

    group.add_argument(
        '-k',
        '--key',
        metavar='KEY',
        type=auto_int,
        nargs='+',
        help='the db key to use for accessing the configs'
    )

    parser.add_argument(
        'src1',
        metavar='HUTCH:SRC',
        type=parse_source,
        help='the source id of the first detector'
    )

    parser.add_argument(
        'src2',
        metavar='HUTCH:SRC',
        type=parse_source,
        help='the source id of the second detector'
    )

    args = parser.parse_args()

    try:
        sys.exit(main(*args.src1, *args.src2, args.alias, args.key))
    except KeyboardInterrupt:
        pass
