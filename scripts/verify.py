#!/usr/bin/env python3
"""
homiwiki 무결성 검증 스크립트
사용: python3 scripts/verify.py [--root path]

검증 항목:
1. 모든 docs/{id}/ 폴더에 doc.json 존재
2. _index.json의 모든 ID와 폴더 일치
3. doc.json이 참조하는 이미지가 실제 존재
4. 고아 이미지 (사용 안 되는 파일) 검출
5. 깨진 위키링크 (data-link) 검출
6. NFD 인코딩 파일/폴더 검출 (Mac/Windows 호환성)
"""

import json
import os
import re
import sys
import unicodedata
from pathlib import Path
from collections import defaultdict


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    docs_dir = root / 'docs'
    
    if not docs_dir.exists():
        print(f"❌ docs/ 폴더 없음: {docs_dir}")
        sys.exit(1)
    
    errors = []
    warnings = []
    info = []
    
    # === 1. _index.json 로드 ===
    index_path = docs_dir / '_index.json'
    if not index_path.exists():
        errors.append(f"_index.json 없음: {index_path}")
        index_data = {}
        index_doc_ids = set()
    else:
        with open(index_path, encoding='utf-8') as f:
            index_data = json.load(f)
        if index_data.get('version') == 2:
            index_doc_ids = set(index_data.get('docs', {}).keys())
        else:
            index_doc_ids = set(index_data.get('docs', []))
    
    info.append(f"_index.json: {len(index_doc_ids)}개 문서 등록")
    
    # === 2. NFD 인코딩 검사 ===
    nfd_paths = []
    for path in docs_dir.rglob('*'):
        rel = path.relative_to(root)
        name = path.name
        if unicodedata.normalize('NFC', name) != name:
            nfd_paths.append(str(rel))
    
    if nfd_paths:
        errors.append(f"NFD 형식 파일/폴더 {len(nfd_paths)}개 발견:")
        for p in nfd_paths[:10]:
            errors.append(f"  - {p}")
    
    # === 3. 폴더 vs _index.json 일치 검사 ===
    folder_doc_ids = set()
    for entry in docs_dir.iterdir():
        if entry.is_dir() and not entry.name.startswith('_'):
            folder_doc_ids.add(entry.name)
    
    info.append(f"실제 폴더: {len(folder_doc_ids)}개")
    
    # _index.json에 있는데 폴더 없음
    missing_folders = index_doc_ids - folder_doc_ids
    if missing_folders:
        errors.append(f"_index.json에 등록되었지만 폴더 없음: {missing_folders}")
    
    # 폴더 있는데 _index.json에 없음
    unregistered = folder_doc_ids - index_doc_ids
    if unregistered:
        warnings.append(f"폴더는 있지만 _index.json에 등록 안 됨: {unregistered}")
    
    # === 4. 각 문서 검증 ===
    all_referenced_images = defaultdict(list)  # doc_id -> [images...]
    all_existing_images = defaultdict(list)
    all_wikilinks = defaultdict(list)
    all_doc_data = {}
    
    for doc_id in folder_doc_ids:
        doc_dir = docs_dir / doc_id
        doc_json = doc_dir / 'doc.json'
        
        if not doc_json.exists():
            errors.append(f"[{doc_id}] doc.json 없음")
            continue
        
        try:
            with open(doc_json, encoding='utf-8') as f:
                doc = json.load(f)
            all_doc_data[doc_id] = doc
        except json.JSONDecodeError as e:
            errors.append(f"[{doc_id}] doc.json 파싱 실패: {e}")
            continue
        
        # 4-1. 폴더 안 실제 이미지 목록
        for img_file in doc_dir.iterdir():
            if img_file.suffix.lower() in ('.webp', '.png', '.jpg', '.jpeg', '.gif', '.svg'):
                all_existing_images[doc_id].append(img_file.name)
        
        # 4-2. doc.json이 참조하는 이미지
        referenced = set()
        info_box = doc.get('infobox')
        if isinstance(info_box, dict) and info_box.get('image'):
            referenced.add(info_box['image'])
        
        content = doc.get('content', '')
        if isinstance(content, list):
            content = '\n'.join(str(c) for c in content)
        
        if isinstance(content, str):
            # <img src="..."> 추출
            for m in re.finditer(r'<img[^>]+src="([^"]+)"', content):
                referenced.add(m.group(1))
            # 위키링크 추출
            for m in re.finditer(r'data-link="([^"]+)"', content):
                all_wikilinks[doc_id].append(m.group(1))
        
        all_referenced_images[doc_id] = list(referenced)
        
        # 4-3. 참조한 이미지가 실제 존재하는지
        for ref_img in referenced:
            # http(s):// 절대 URL 또는 _shared/ 는 따로 처리
            if ref_img.startswith(('http://', 'https://')):
                continue
            
            # _shared/xxx.webp 형태
            if ref_img.startswith('_shared/') or ref_img.startswith('../_shared/'):
                shared_path = docs_dir / '_shared' / Path(ref_img).name
                if not shared_path.exists():
                    errors.append(f"[{doc_id}] 공유 이미지 참조하지만 _shared/에 없음: {ref_img}")
                continue
            
            # 같은 폴더 안 (파일명만)
            local_path = doc_dir / ref_img
            if not local_path.exists():
                errors.append(f"[{doc_id}] 이미지 참조하지만 파일 없음: {ref_img}")
        
        # 4-4. 고아 이미지 검출
        for actual_img in all_existing_images[doc_id]:
            if actual_img not in referenced:
                warnings.append(f"[{doc_id}] 고아 이미지 (참조 안 됨): {actual_img}")
    
    # === 5. 위키링크 무결성 검사 ===
    # _index.json에 있는 ID 또는 redirects의 키여야 함
    valid_link_targets = set(index_doc_ids)
    if index_data.get('redirects'):
        valid_link_targets.update(index_data['redirects'].keys())
    
    broken_links = defaultdict(list)
    for doc_id, links in all_wikilinks.items():
        for link in links:
            if link not in valid_link_targets:
                broken_links[doc_id].append(link)
    
    if broken_links:
        warnings.append("미정의 위키링크 (아직 만들어지지 않은 문서일 수 있음):")
        for doc_id, links in broken_links.items():
            unique_links = sorted(set(links))
            warnings.append(f"  [{doc_id}] → {unique_links}")
    
    # === 결과 출력 ===
    print("=" * 60)
    print("homiwiki 무결성 검증 결과")
    print("=" * 60)
    
    if info:
        print("\n📊 정보:")
        for line in info:
            print(f"  • {line}")
    
    if errors:
        print(f"\n❌ 에러 ({len(errors)}건):")
        for line in errors:
            print(f"  {line}")
    
    if warnings:
        print(f"\n⚠️  경고 ({len(warnings)}건):")
        for line in warnings:
            print(f"  {line}")
    
    if not errors and not warnings:
        print("\n✅ 모든 검증 통과")
    
    print()
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
