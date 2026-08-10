#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, time
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--data-root', type=Path, required=True)
    ap.add_argument('--data-final', type=Path, required=True)
    ap.add_argument('--quick', type=int, default=0, help='Check first N rows per split; 0=full')
    args=ap.parse_args()
    print('data_root=', args.data_root)
    print('data_final=', args.data_final)
    if not args.data_root.exists(): raise SystemExit(f'missing data-root: {args.data_root}')
    if not args.data_final.exists(): raise SystemExit(f'missing data-final: {args.data_final}')
    total=0; miss=0
    t0=time.perf_counter()
    for split in ['train','val','test']:
        p=args.data_final/f'{split}.tsv'
        n=0; m=0; dur=0.0
        with p.open(encoding='utf-8') as f:
            for row in csv.DictReader(f, delimiter='\t'):
                n += 1
                dur += float(row.get('duration_sec') or 0)
                if not (args.data_root/row['audio_path']).exists(): m += 1
                if args.quick and n >= args.quick: break
        total += n; miss += m
        print(f'{split}: checked_rows={n} hours={dur/3600:.4f} missing={m}')
    print(f'total_checked={total} missing={miss} elapsed_sec={time.perf_counter()-t0:.2f}')
    if miss: raise SystemExit(2)
if __name__ == '__main__': main()
