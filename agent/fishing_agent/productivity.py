"""Pembuatan artefak produktivitas lokal tanpa layanan cloud."""

from __future__ import annotations

import csv
import json
import zipfile
from html import escape
from pathlib import Path
from typing import Iterable, Mapping, Sequence
from xml.etree import ElementTree


class ProductivityError(ValueError):
    """Input atau output productivity tidak valid."""


def _target(path: str | Path, overwrite: bool) -> Path:
    target = Path(path).expanduser().absolute()
    if target.exists() and not overwrite:
        raise ProductivityError(f"target sudah ada; approval overwrite diperlukan: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def create_markdown(
    path: str | Path,
    title: str,
    sections: Sequence[tuple[str, str]],
    *,
    overwrite: bool = False,
) -> Path:
    if not title.strip():
        raise ProductivityError("judul dokumen wajib diisi")
    target = _target(path, overwrite)
    body = [f"# {title.strip()}", ""]
    for heading, content in sections:
        if not heading.strip():
            raise ProductivityError("heading dokumen tidak boleh kosong")
        body.extend((f"## {heading.strip()}", "", content.rstrip(), ""))
    target.write_text("\n".join(body), encoding="utf-8")
    return target


def create_csv(
    path: str | Path,
    headers: Sequence[str],
    rows: Iterable[Sequence[object]],
    *,
    overwrite: bool = False,
) -> Path:
    if not headers or any(not str(header).strip() for header in headers):
        raise ProductivityError("headers CSV wajib diisi")
    target = _target(path, overwrite)
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        for row in rows:
            values = list(row)
            if len(values) != len(headers):
                raise ProductivityError("jumlah kolom row tidak sesuai header")
            writer.writerow(values)
    return target


def create_pptx(
    path: str | Path,
    slides: Sequence[Mapping[str, object]],
    *,
    overwrite: bool = False,
) -> Path:
    """Buat presentasi OOXML minimal yang dapat dibuka aplikasi presentasi."""
    if not slides:
        raise ProductivityError("presentasi membutuhkan minimal satu slide")
    target = _target(path, overwrite)
    parts = _pptx_parts(slides)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in parts.items():
            archive.writestr(name, content)
    validate_pptx(target)
    return target


def validate_pptx(path: str | Path) -> None:
    required = {
        "[Content_Types].xml",
        "_rels/.rels",
        "ppt/presentation.xml",
        "ppt/_rels/presentation.xml.rels",
        "ppt/slideLayouts/slideLayout1.xml",
        "ppt/slideMasters/slideMaster1.xml",
        "ppt/theme/theme1.xml",
    }
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        missing = required - names
        if missing:
            raise ProductivityError(f"PPTX tidak lengkap: {sorted(missing)}")
        if archive.testzip() is not None:
            raise ProductivityError("arsip PPTX rusak")
        try:
            for name in names:
                if name.endswith(".xml") or name.endswith(".rels"):
                    ElementTree.fromstring(archive.read(name))
        except ElementTree.ParseError as exc:
            raise ProductivityError(f"XML PPTX tidak valid: {exc}") from exc


def _pptx_parts(slides: Sequence[Mapping[str, object]]) -> dict[str, str]:
    slide_ids = []
    slide_rels = []
    slide_parts: dict[str, str] = {}
    for index, slide in enumerate(slides, start=1):
        title = str(slide.get("title", f"Slide {index}"))
        body = str(slide.get("body", ""))
        slide_ids.append(f'<p:sldId id="{255 + index}" r:id="rId{index + 2}"/>')
        slide_rels.append(
            f'<Relationship Id="rId{index + 2}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{index}.xml"/>'
        )
        slide_parts[f"ppt/slides/slide{index}.xml"] = _slide_xml(title, body)
        slide_parts[f"ppt/slides/_rels/slide{index}.xml.rels"] = (
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
            "</Relationships>"
        )
    parts = {
        "[Content_Types].xml": _content_types(len(slides)),
        "_rels/.rels": _root_rels(),
        "ppt/presentation.xml": (
            '<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
            'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
            '<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>'
            f'<p:sldIdLst>{"".join(slide_ids)}</p:sldIdLst>'
            '<p:sldSz cx="12192000" cy="6858000" type="screen16x9"/>'
            '<p:notesSz cx="6858000" cy="9144000"/></p:presentation>'
        ),
        "ppt/_rels/presentation.xml.rels": (
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>'
            + "".join(slide_rels)
            + "</Relationships>"
        ),
        "ppt/slideLayouts/slideLayout1.xml": _layout_xml(),
        "ppt/slideLayouts/_rels/slideLayout1.xml.rels": _layout_rels(),
        "ppt/slideMasters/slideMaster1.xml": _master_xml(),
        "ppt/slideMasters/_rels/slideMaster1.xml.rels": _master_rels(),
        "ppt/theme/theme1.xml": _theme_xml(),
    }
    parts.update(slide_parts)
    return parts


def _slide_xml(title: str, body: str) -> str:
    return (
        '<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
        '<p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/>'
        '<p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>'
        f'<p:sp><p:nvSpPr><p:cNvPr id="2" name="Title"/><p:cNvSpPr txBox="1"/>'
        '<p:nvPr/></p:nvSpPr><p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/>'
        f'<a:p><a:r><a:rPr lang="id-ID" sz="2800"/><a:t>{escape(title)}</a:t></a:r></a:p></p:txBody></p:sp>'
        f'<p:sp><p:nvSpPr><p:cNvPr id="3" name="Body"/><p:cNvSpPr txBox="1"/>'
        '<p:nvPr/></p:nvSpPr><p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/>'
        f'<a:p><a:r><a:rPr lang="id-ID" sz="1800"/><a:t>{escape(body)}</a:t></a:r></a:p></p:txBody></p:sp>'
        '</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'
    )


def _content_types(count: int) -> str:
    slides = "".join(
        f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, count + 1)
    )
    return (
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>'
        '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>'
        '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>'
        '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>'
        + slides
        + "</Types>"
    )


def _root_rels() -> str:
    return '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/></Relationships>'


def _layout_xml() -> str:
    return '<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank"><p:cSld name="Blank"><p:spTree/></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>'


def _layout_rels() -> str:
    return '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/></Relationships>'


def _master_xml() -> str:
    return '<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld name="Master"><p:spTree/></p:cSld><p:clrMap accent1="accent1" accent2="accent2" bg1="lt1" bg2="lt2" folHlink="hlink" hlink="hlink" tx1="dk1" tx2="dk2"/><p:sldLayoutIdLst><p:sldLayoutId id="1" r:id="rId1"/></p:sldLayoutIdLst></p:sldMaster>'


def _master_rels() -> str:
    return '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/></Relationships>'


def _theme_xml() -> str:
    return '<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Fishing OS"><a:themeElements><a:clrScheme name="Fishing"><a:dk1><a:sysClr val="windowText" lastClr="000000"/></a:dk1><a:lt1><a:sysClr val="window" lastClr="FFFFFF"/></a:lt1><a:accent1><a:srgbClr val="167D9A"/></a:accent1><a:accent2><a:srgbClr val="F4A261"/></a:accent2><a:hlink><a:srgbClr val="0000FF"/></a:hlink><a:folHlink><a:srgbClr val="800080"/></a:folHlink></a:clrScheme><a:fontScheme name="Fishing"><a:majorFont><a:latin typeface="Arial"/></a:majorFont><a:minorFont><a:latin typeface="Arial"/></a:minorFont></a:fontScheme><a:fmtScheme name="Fishing"><a:fillStyleLst/><a:lnStyleLst/><a:effectStyleLst/><a:bgFillStyleLst/></a:fmtScheme></a:themeElements></a:theme>'


__all__ = ["ProductivityError", "create_csv", "create_markdown", "create_pptx", "validate_pptx"]
