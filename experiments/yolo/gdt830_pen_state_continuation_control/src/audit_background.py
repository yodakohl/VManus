#!/usr/bin/env python3
"""Post-result diagnostic only: unchanged assay on visually blank admitted paper."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from measure import patch_assay

EXP=Path(__file__).resolve().parent.parent


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-dir',type=Path,required=True)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    spec=json.loads((EXP/'src/SPEC.json').read_text())
    source=next(r for r in json.loads((EXP/'src/SOURCES.json').read_text()) if r['page']=='f76r')
    file=args.cache_dir/source['filename']
    assert hashlib.sha256(file.read_bytes()).hexdigest()==source['sha256']
    image=Image.open(file).convert('RGB');w,h=image.size
    # Chosen after the capacity result from the already viewed blank lower page.
    box=(round(.25*w),round(.88*h),round(.70*w),round(.90*h))
    strip=image.crop(box)
    background=strip.filter(ImageFilter.MaxFilter(spec['background']['max_filter_size'])).filter(ImageFilter.GaussianBlur(spec['background']['gaussian_radius']))
    raw=np.asarray(strip,dtype=float);paper=np.asarray(background,dtype=float)
    gray=raw.mean(2);bg=paper.mean(2)
    mask=(bg-gray)/np.maximum(bg,1)>spec['foreground_relative_darkness']
    ink,nu,core,reason=patch_assay(raw,paper,.475,.89,spec)
    result=dict(status='POST_RESULT_BACKGROUND_DIAGNOSTIC_ONLY',page='f76r',source_sha256=source['sha256'],rectangle_native=list(box),selection='visually blank lower paper; chosen after the control capacity stop, not a preregistered target test',raw_gray_quantiles=np.quantile(gray,[0,.1,.5,.9,1]).tolist(),estimated_paper_gray_quantiles=np.quantile(bg,[0,.1,.5,.9,1]).tolist(),foreground_fraction=float(mask.mean()),vertical_core_samples=core,assay_reason=reason,thresholds_changed=False,chronology_inferred=False)
    text=json.dumps(result,sort_keys=True,indent=2)+'\n';out=EXP/'artifacts/BACKGROUND_AUDIT.json'
    if args.check:assert out.read_text()==text
    else:out.write_text(text)
    print(text)


if __name__=='__main__':main()
