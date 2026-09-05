#!/usr/bin/env python3
"""Fixed digital-contrast assay; no glyph recognition or image enhancement output."""
import hashlib
import json
import math
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


COLUMNS = ['patch_id','page','row_id','source_ordinal','column','valid','reason','ink_json','nuisance_json','core_samples','patch_width','patch_height']


def check(ok,message):
    if not ok: raise ValueError(message)


def canon(obj):
    return json.dumps(obj,ensure_ascii=False,separators=(',',':'),sort_keys=True)


def load_sources(sources, cache, fetch=False):
    images = {}
    for source in sources:
        path = cache/source['filename']
        if not path.exists():
            check(fetch,'Missing image; use --fetch for the four registered official sources')
            check(source['page'] in ['f76r','f77r','f81r','f83r'],'Unadmitted source')
            check(source['url'].startswith('https://collections.library.yale.edu/iiif/2/'),'Source host')
            cache.mkdir(parents=True,exist_ok=True)
            data = urllib.request.urlopen(source['url'],timeout=90).read()
            check(hashlib.sha256(data).hexdigest()==source['sha256'],'Downloaded image hash mismatch')
            path.write_bytes(data)
        data = path.read_bytes()
        check(hashlib.sha256(data).hexdigest()==source['sha256'],'Image hash mismatch')
        image = Image.open(path)
        check(image.size==(source['width'],source['height']),'Native image dimensions')
        images[source['page']] = image.convert('RGB')
    return images


def patch_assay(rgb, background, xnorm, ynorm, spec):
    rgb = np.asarray(rgb,dtype=float); paper = np.asarray(background,dtype=float)
    gray = rgb.mean(axis=2); bg = paper.mean(axis=2)
    mask = (bg-gray)/np.maximum(bg,1) > spec['foreground_relative_darkness']
    h,w = mask.shape
    counts=[]; points=[]; widths=[]; qualified=0
    low,high = spec['horizontal_run_width']
    for y in range(2,h-2):
        padded = np.r_[False,mask[y],False].astype(np.int8)
        changes = np.diff(padded)
        starts=np.flatnonzero(changes==1); ends=np.flatnonzero(changes==-1)
        for start,end in zip(starts,ends):
            width=int(end-start)
            if not low<=width<=high: continue
            qualified+=1
            x=int((start+end-1)//2)
            if int(mask[y-2:y+3,x].sum()) >= spec['vertical_persistence_minimum']:
                points.append((y,x)); widths.append(width)
    core=len(points); paper_fraction=1-float(mask.mean())
    if core < spec['minimum_core_pixels']:
        return [],[],core,'INSUFFICIENT_VERTICAL_CORE'
    if paper_fraction < spec['minimum_paper_fraction']:
        return [],[],core,'INSUFFICIENT_PAPER'
    yy,xx=np.array(points).T
    contrast=np.log((paper[yy,xx]+1)/(rgb[yy,xx]+1))
    ink=np.median(contrast,axis=0)
    pvals=paper[~mask]/255
    quarter=max(1,w//4); band=max(1,h//4)
    dx=(paper[:,-quarter:].mean(axis=(0,1))-paper[:,:quarter].mean(axis=(0,1)))/255
    dy=(paper[-band:].mean(axis=(0,1))-paper[:band].mean(axis=(0,1)))/255
    nuisance=[float(mask.mean()),math.log1p(core),float(np.mean(widths)),float(np.std(widths)),core/max(qualified,1),*pvals.mean(axis=0),*pvals.std(axis=0),*dx,*dy,xnorm,ynorm]
    check(len(nuisance)==len(spec['nuisance_features']),'Nuisance schema')
    return np.round(ink,12).tolist(),np.round(nuisance,12).tolist(),core,'PASS'


def extract(images, rows, spec):
    output=[]
    for row in rows:
        image=images[row['page']]; iw,ih=image.size
        x0,y0,x1,y1=[int(row[k]) for k in ['x0','y0','x1','y1']]
        check(0<=x0<x1<=iw and 0<=y0<y1<=ih,'Row bounds')
        strip=image.crop((x0,y0,x1,y1))
        paper=strip.filter(ImageFilter.MaxFilter(spec['background']['max_filter_size'])).filter(ImageFilter.GaussianBlur(spec['background']['gaussian_radius']))
        pixels=np.array(strip); bg=np.array(paper); width=x1-x0
        for col in range(spec['windows_per_row']):
            a=col*width//spec['windows_per_row']; b=(col+1)*width//spec['windows_per_row']
            ink,nu,core,reason=patch_assay(pixels[:,a:b],bg[:,a:b],(x0+(a+b)/2)/iw,(y0+y1)/2/ih,spec)
            output.append(dict(patch_id=row['row_id']+f':W{col:02d}',page=row['page'],row_id=row['row_id'],source_ordinal=row['source_ordinal'],column=col,valid=int(reason=='PASS'),reason=reason,ink_json=canon(ink),nuisance_json=canon(nu),core_samples=core,patch_width=b-a,patch_height=y1-y0))
    return output
