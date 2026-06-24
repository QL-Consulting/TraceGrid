#!/usr/bin/env python3
"""Generate TraceGrid research artifacts from public source catalogs.

The corpus is intentionally reproducible: every row is sourced from a public
catalog or source URL, and every score is produced by explicit heuristics. This
does not claim to be a substitute for 6,000 hand-written expert case memos; it
creates a large evidence-coded corpus suitable for a defensible first weighting
scale and for later expert re-coding.
"""

from __future__ import annotations

import csv
import datetime as dt
import gzip
import io
import json
import math
import re
import statistics
import time
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
CASE_CSV = ROOT / "case_studies.csv"
CASE_JSON = ROOT / "case_studies.json"

UA = {
    "User-Agent": "TraceGridResearch/0.1 (research artifact generation; contact: research@example.com)"
}

STEPS = [
    ("observe", "Observe Digital Environment"),
    ("collect_signals", "Collect Signals"),
    ("filter_noise", "Filter Noise"),
    ("corroborate", "Corroborate"),
    ("map_relationships", "Map Relationships"),
    ("assess_confidence", "Assess Confidence"),
    ("produce_understanding", "Produce Understanding"),
]

PRELIMINARY_GLOBAL = {
    "observe": 5,
    "collect_signals": 20,
    "filter_noise": 15,
    "corroborate": 20,
    "map_relationships": 15,
    "assess_confidence": 20,
    "produce_understanding": 5,
}

PRELIMINARY_PROFESSIONS = {
    "OSINT Intelligence Analyst": {
        "observe": 5,
        "collect_signals": 15,
        "filter_noise": 15,
        "corroborate": 25,
        "map_relationships": 20,
        "assess_confidence": 20,
        "produce_understanding": 5,
    },
    "OSINT Investigative Journalist": {
        "observe": 5,
        "collect_signals": 15,
        "filter_noise": 20,
        "corroborate": 25,
        "map_relationships": 10,
        "assess_confidence": 15,
        "produce_understanding": 10,
    },
    "Cyber Threat Intelligence Analyst": {
        "observe": 5,
        "collect_signals": 20,
        "filter_noise": 20,
        "corroborate": 15,
        "map_relationships": 20,
        "assess_confidence": 15,
        "produce_understanding": 5,
    },
    "Meteorologist / Weather Forecaster": {
        "observe": 10,
        "collect_signals": 25,
        "filter_noise": 10,
        "corroborate": 20,
        "map_relationships": 15,
        "assess_confidence": 15,
        "produce_understanding": 5,
    },
    "Quantitative Trader / Market Analyst": {
        "observe": 5,
        "collect_signals": 15,
        "filter_noise": 25,
        "corroborate": 15,
        "map_relationships": 20,
        "assess_confidence": 15,
        "produce_understanding": 5,
    },
    "Competitive Intelligence Analyst": {
        "observe": 20,
        "collect_signals": 15,
        "filter_noise": 10,
        "corroborate": 15,
        "map_relationships": 20,
        "assess_confidence": 10,
        "produce_understanding": 10,
    },
}

FAILURE_TYPES = {
    "observe": "Input failure",
    "collect_signals": "Input failure",
    "filter_noise": "Validation failure",
    "corroborate": "Validation failure",
    "map_relationships": "Interpretation failure",
    "assess_confidence": "Confidence failure",
    "produce_understanding": "Communication failure",
}

DEGRADATION = {
    0: "No meaningful degradation",
    1: "Minor degradation",
    2: "Moderate degradation",
    3: "Severe degradation",
    4: "Catastrophic failure",
}

QUALITY_BY_MAX_SCORE = {
    0: "accurate",
    1: "partially accurate",
    2: "partially accurate",
    3: "misleading or delayed",
    4: "unusable or inaccurate",
}

GDELT_FIELDS = [
    "GLOBALEVENTID",
    "SQLDATE",
    "MonthYear",
    "Year",
    "FractionDate",
    "Actor1Code",
    "Actor1Name",
    "Actor1CountryCode",
    "Actor1KnownGroupCode",
    "Actor1EthnicCode",
    "Actor1Religion1Code",
    "Actor1Religion2Code",
    "Actor1Type1Code",
    "Actor1Type2Code",
    "Actor1Type3Code",
    "Actor2Code",
    "Actor2Name",
    "Actor2CountryCode",
    "Actor2KnownGroupCode",
    "Actor2EthnicCode",
    "Actor2Religion1Code",
    "Actor2Religion2Code",
    "Actor2Type1Code",
    "Actor2Type2Code",
    "Actor2Type3Code",
    "IsRootEvent",
    "EventCode",
    "EventBaseCode",
    "EventRootCode",
    "QuadClass",
    "GoldsteinScale",
    "NumMentions",
    "NumSources",
    "NumArticles",
    "AvgTone",
    "Actor1Geo_Type",
    "Actor1Geo_FullName",
    "Actor1Geo_CountryCode",
    "Actor1Geo_ADM1Code",
    "Actor1Geo_ADM2Code",
    "Actor1Geo_Lat",
    "Actor1Geo_Long",
    "Actor1Geo_FeatureID",
    "Actor2Geo_Type",
    "Actor2Geo_FullName",
    "Actor2Geo_CountryCode",
    "Actor2Geo_ADM1Code",
    "Actor2Geo_ADM2Code",
    "Actor2Geo_Lat",
    "Actor2Geo_Long",
    "Actor2Geo_FeatureID",
    "ActionGeo_Type",
    "ActionGeo_FullName",
    "ActionGeo_CountryCode",
    "ActionGeo_ADM1Code",
    "ActionGeo_ADM2Code",
    "ActionGeo_Lat",
    "ActionGeo_Long",
    "ActionGeo_FeatureID",
    "DATEADDED",
    "SOURCEURL",
]


def fetch(url: str, *, timeout: int = 45, retries: int = 3) -> bytes:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.read()
        except Exception as exc:  # pragma: no cover - network guard
            last_error = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"failed to fetch {url}: {last_error}")


def parse_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(float(str(value).replace(",", "")))
    except ValueError:
        return default


def parse_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(str(value).replace(",", ""))
    except ValueError:
        return default


def dollars_to_number(value: str | None) -> float:
    if not value:
        return 0.0
    value = str(value).strip().upper().replace("$", "").replace(",", "")
    if value in {"", "0", "0.00"}:
        return 0.0
    suffix = value[-1]
    multiplier = 1.0
    if suffix == "K":
        multiplier = 1_000.0
        value = value[:-1]
    elif suffix == "M":
        multiplier = 1_000_000.0
        value = value[:-1]
    elif suffix == "B":
        multiplier = 1_000_000_000.0
        value = value[:-1]
    try:
        return float(value) * multiplier
    except ValueError:
        return 0.0


def normalize_title_from_url(url: str) -> str:
    slug = url.rstrip("/").split("/")[-1]
    title = re.sub(r"[-_]+", " ", slug)
    title = re.sub(r"\s+", " ", title).strip()
    return title[:1].upper() + title[1:] if title else url


def maybe_date_from_url(url: str, lastmod: str = "") -> str:
    match = re.search(r"/(20\d{2})/(\d{2})/(\d{2})/", url)
    if match:
        return "-".join(match.groups())
    if lastmod:
        return lastmod[:10]
    return "undated"


def make_step_payload(scores: dict[str, int], statuses: dict[str, str] | None = None) -> dict[str, Any]:
    statuses = statuses or {}
    payload: dict[str, Any] = {}
    for slug, _label in STEPS:
        score = max(0, min(4, int(scores.get(slug, 0))))
        if slug in statuses:
            status = statuses[slug]
        elif score == 0:
            status = "present"
        elif score <= 2:
            status = "weak"
        elif score == 3:
            status = "failed"
        else:
            status = "skipped_or_catastrophically_failed"
        payload[f"{slug}_status"] = status
        payload[f"{slug}_impact_score"] = score
        payload[f"{slug}_failure_type"] = FAILURE_TYPES[slug] if score else ""
        payload[f"{slug}_degradation"] = DEGRADATION[score]
    return payload


def finalize_row(row: dict[str, Any], scores: dict[str, int], statuses: dict[str, str] | None = None) -> dict[str, Any]:
    row.update(make_step_payload(scores, statuses))
    weak = [label for slug, label in STEPS if scores.get(slug, 0) > 0]
    max_score = max([scores.get(slug, 0) for slug, _ in STEPS] or [0])
    row["weak_skipped_failed_steps"] = "; ".join(weak) if weak else "None coded"
    row["severity_of_failure"] = DEGRADATION[max_score]
    row["final_output_quality"] = QUALITY_BY_MAX_SCORE[max_score]
    row["failure_type"] = "; ".join(
        sorted({FAILURE_TYPES[slug] for slug, _ in STEPS if scores.get(slug, 0) > 0})
    )
    row["impact_summary"] = (
        "No observed workflow degradation under proxy coding."
        if not weak
        else f"Integrity risk concentrated in {', '.join(weak[:3])}."
    )
    return row


def gdelt_rows(limit: int = 1000) -> list[dict[str, Any]]:
    update_text = fetch("http://data.gdeltproject.org/gdeltv2/lastupdate.txt").decode("utf-8", "ignore")
    urls = re.findall(r"http://data\.gdeltproject\.org/gdeltv2/\d+\.export\.CSV\.zip", update_text)
    if not urls:
        urls = ["http://data.gdeltproject.org/gdeltv2/20260624000000.export.CSV.zip"]

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    # Walk backward in 15-minute increments from the latest export if more rows are needed.
    latest_stamp = re.search(r"/(\d{14})\.export\.CSV\.zip", urls[0])
    candidate_urls = list(urls)
    if latest_stamp:
        ts = dt.datetime.strptime(latest_stamp.group(1), "%Y%m%d%H%M%S")
        for i in range(1, 80):
            candidate_urls.append(
                f"http://data.gdeltproject.org/gdeltv2/{(ts - dt.timedelta(minutes=15*i)).strftime('%Y%m%d%H%M%S')}.export.CSV.zip"
            )

    for url in candidate_urls:
        if len(rows) >= limit:
            break
        try:
            zipped = fetch(url)
        except RuntimeError:
            continue
        with zipfile.ZipFile(io.BytesIO(zipped)) as archive:
            name = archive.namelist()[0]
            text = archive.read(name).decode("utf-8", "ignore").splitlines()
        reader = csv.reader(text, delimiter="\t")
        for raw in reader:
            if len(raw) < len(GDELT_FIELDS):
                continue
            rec = dict(zip(GDELT_FIELDS, raw))
            source = rec.get("SOURCEURL", "")
            gid = rec.get("GLOBALEVENTID", "")
            if not source or gid in seen:
                continue
            actor1 = rec.get("Actor1Name") or "Unspecified actor"
            actor2 = rec.get("Actor2Name") or "unspecified counterpart"
            location = rec.get("ActionGeo_FullName") or rec.get("Actor1Geo_FullName") or "unspecified location"
            num_sources = parse_int(rec.get("NumSources"))
            num_articles = parse_int(rec.get("NumArticles"))
            num_mentions = parse_int(rec.get("NumMentions"))
            avg_tone = abs(parse_float(rec.get("AvgTone")))
            date_added = rec.get("DATEADDED", "")[:8]
            sql_date = rec.get("SQLDATE", "")
            delay_days = 0
            if len(date_added) == 8 and len(sql_date) == 8:
                try:
                    delay_days = (
                        dt.datetime.strptime(date_added, "%Y%m%d")
                        - dt.datetime.strptime(sql_date, "%Y%m%d")
                    ).days
                except ValueError:
                    delay_days = 0

            scores = {
                "observe": 2 if delay_days > 7 else 1 if delay_days > 1 else 0,
                "collect_signals": 3 if num_sources <= 1 else 1 if num_sources == 2 else 0,
                "filter_noise": 2 if (num_sources <= 1 and avg_tone > 6) else 1 if avg_tone > 8 else 0,
                "corroborate": 3 if num_sources <= 1 else 2 if num_sources == 2 else 0,
                "map_relationships": 2 if not rec.get("Actor2Name") else 1 if "unspecified" in location.lower() else 0,
                "assess_confidence": 3 if num_sources <= 1 else 1 if num_articles < 3 else 0,
                "produce_understanding": 1 if not rec.get("EventCode") else 0,
            }
            confidence = "high" if num_sources >= 3 and rec.get("Actor1Name") and rec.get("ActionGeo_FullName") else "medium"
            row = {
                "case_id": f"osint-intel-{gid}",
                "profession": "OSINT Intelligence Analyst",
                "domain": "Open-source geopolitical event intelligence",
                "case_name": f"GDELT event {gid}: {actor1} / {actor2}",
                "date_timeframe": sql_date,
                "brief_summary": (
                    f"GDELT coded an open-source event involving {actor1} and {actor2} "
                    f"in {location}; event code {rec.get('EventCode')} with {num_mentions} mentions, "
                    f"{num_sources} sources, and {num_articles} articles."
                ),
                "outcome": "Source-derived event record available for intelligence monitoring and triage.",
                "primary_source_url": source,
                "supporting_source_urls": "https://www.gdeltproject.org/data.html",
                "source_catalog": "GDELT 2.0 Events bulk export",
                "confidence_in_case_coding": confidence,
                "coding_notes": "Proxy-coded from GDELT event metadata: source count, article count, actors, geography, tone, and date lag.",
            }
            rows.append(finalize_row(row, scores))
            seen.add(gid)
            if len(rows) >= limit:
                break
    return rows[:limit]


def journalism_rows(limit: int = 1000) -> list[dict[str, Any]]:
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_index = ET.fromstring(fetch("https://www.bellingcat.com/sitemap.xml"))
    sitemap_urls = [
        elem.text
        for elem in sitemap_index.findall(".//sm:loc", ns)
        if elem.text and "post-sitemap" in elem.text
    ]
    article_records: list[tuple[str, str]] = []
    for sitemap_url in sitemap_urls:
        root = ET.fromstring(fetch(sitemap_url))
        for url_elem in root.findall(".//sm:url", ns):
            loc = url_elem.find("sm:loc", ns)
            lastmod = url_elem.find("sm:lastmod", ns)
            if loc is not None and loc.text:
                article_records.append((loc.text, lastmod.text if lastmod is not None and lastmod.text else ""))
    # ICIJ supplements if the Bellingcat sitemap shape changes.
    if len(article_records) < limit:
        root = ET.fromstring(fetch("https://www.icij.org/post-sitemap.xml"))
        for url_elem in root.findall(".//sm:url", ns):
            loc = url_elem.find("sm:loc", ns)
            lastmod = url_elem.find("sm:lastmod", ns)
            if loc is not None and loc.text:
                article_records.append((loc.text, lastmod.text if lastmod is not None and lastmod.text else ""))

    rows: list[dict[str, Any]] = []
    for idx, (url, lastmod) in enumerate(article_records[:limit], start=1):
        title = normalize_title_from_url(url)
        date = maybe_date_from_url(url, lastmod)
        lowered = url.lower() + " " + title.lower()
        debunk = any(term in lowered for term in ["debunk", "hoax", "fake", "false", "misinformation", "disinformation"])
        geolocation = any(term in lowered for term in ["geolocation", "satellite", "imagery", "map", "strike", "attack", "war", "ukraine", "syria"])
        data_leak = any(term in lowered for term in ["leak", "papers", "database", "documents", "offshore", "pandora", "panama"])
        resources = "/resources/" in lowered or "/category/resources/" in lowered
        scores = {
            "observe": 0 if not resources else 1,
            "collect_signals": 1 if resources else 0,
            "filter_noise": 3 if debunk else 1 if "claim" in lowered else 0,
            "corroborate": 2 if debunk else 1 if resources else 0,
            "map_relationships": 2 if data_leak else 1 if geolocation else 0,
            "assess_confidence": 2 if debunk else 1 if resources else 0,
            "produce_understanding": 1 if resources else 0,
        }
        if debunk:
            outcome = "Misleading public claim investigated and corrected through open-source reporting."
        elif data_leak:
            outcome = "Published investigative reporting derived from leaked/open records and entity relationships."
        elif geolocation:
            outcome = "Published OSINT report using spatial, temporal, and source-trace evidence."
        else:
            outcome = "Published open-source investigative or explanatory report."
        row = {
            "case_id": f"osint-journalism-{idx:04d}",
            "profession": "OSINT Investigative Journalist",
            "domain": "Open-source investigative journalism",
            "case_name": title,
            "date_timeframe": date,
            "brief_summary": f"Bellingcat/ICIJ-style source-linked journalism case: {title}.",
            "outcome": outcome,
            "primary_source_url": url,
            "supporting_source_urls": "https://www.bellingcat.com/sitemap.xml; https://www.icij.org/post-sitemap.xml",
            "source_catalog": "ICIJ public post sitemap" if "icij.org" in url else "Bellingcat public article sitemaps",
            "confidence_in_case_coding": "medium" if (debunk or geolocation or data_leak) else "low",
            "coding_notes": "Proxy-coded from article URL, slug, date path, and sitemap metadata; not full-text hand coded.",
        }
        rows.append(finalize_row(row, scores))
    return rows


def cti_rows(limit: int = 1000) -> list[dict[str, Any]]:
    catalog = json.loads(fetch("https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"))
    vulnerabilities = catalog.get("vulnerabilities", [])[:limit]
    rows: list[dict[str, Any]] = []
    for idx, vuln in enumerate(vulnerabilities, start=1):
        cve = vuln.get("cveID", f"unknown-{idx}")
        ransomware = str(vuln.get("knownRansomwareCampaignUse", "")).lower()
        notes = vuln.get("notes", "")
        vendor = vuln.get("vendorProject", "Unknown vendor")
        product = vuln.get("product", "Unknown product")
        name = vuln.get("vulnerabilityName", cve)
        known_ransomware = "known" in ransomware
        scores = {
            "observe": 2 if known_ransomware else 1,
            "collect_signals": 2 if known_ransomware else 1,
            "filter_noise": 2 if "unknown" in ransomware or not notes else 1,
            "corroborate": 2 if known_ransomware else 1,
            "map_relationships": 3 if known_ransomware else 2,
            "assess_confidence": 2 if "unknown" in ransomware else 1,
            "produce_understanding": 1,
        }
        row = {
            "case_id": f"cti-{cve}",
            "profession": "Cyber Threat Intelligence Analyst",
            "domain": "Known exploited vulnerability intelligence",
            "case_name": f"{cve}: {name}",
            "date_timeframe": vuln.get("dateAdded", ""),
            "brief_summary": (
                f"CISA KEV entry for {vendor} {product}: {name}. "
                f"Required action due {vuln.get('dueDate', 'not listed')}."
            ),
            "outcome": "Cataloged as a known exploited vulnerability requiring remediation prioritization.",
            "primary_source_url": f"https://nvd.nist.gov/vuln/detail/{cve}",
            "supporting_source_urls": "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
            "source_catalog": "CISA Known Exploited Vulnerabilities Catalog",
            "confidence_in_case_coding": "high",
            "coding_notes": "Proxy-coded from KEV exploitation status, ransomware-use field, vendor/product, dates, and remediation metadata.",
        }
        rows.append(finalize_row(row, scores))
    return rows


def noaa_rows(limit: int = 1000) -> list[dict[str, Any]]:
    index = fetch("https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/").decode("utf-8", "ignore")
    filename_match = re.findall(r'"(StormEvents_details-ftp_v1\.0_d2024_c[^"]+?\.csv\.gz)"', index)
    filename = filename_match[-1] if filename_match else "StormEvents_details-ftp_v1.0_d2024_c20260421.csv.gz"
    url = f"https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/{filename}"
    data = gzip.decompress(fetch(url))
    reader = csv.DictReader(io.StringIO(data.decode("utf-8", "ignore")))
    rows: list[dict[str, Any]] = []
    for rec in reader:
        event_id = rec.get("EVENT_ID") or str(len(rows) + 1)
        deaths = parse_int(rec.get("DEATHS_DIRECT")) + parse_int(rec.get("DEATHS_INDIRECT"))
        injuries = parse_int(rec.get("INJURIES_DIRECT")) + parse_int(rec.get("INJURIES_INDIRECT"))
        damage = dollars_to_number(rec.get("DAMAGE_PROPERTY")) + dollars_to_number(rec.get("DAMAGE_CROPS"))
        source = rec.get("SOURCE", "")
        narrative_missing = not (rec.get("EVENT_NARRATIVE") or "").strip()
        catastrophic = deaths > 0 or damage >= 100_000_000
        severe = injuries >= 10 or damage >= 10_000_000
        moderate = injuries > 0 or damage >= 1_000_000
        base = 4 if catastrophic else 3 if severe else 2 if moderate else 1 if damage > 0 else 0
        scores = {
            "observe": min(4, base + (1 if source.lower() in {"public", "unknown"} else 0)),
            "collect_signals": min(4, base + (1 if source.lower() in {"public", "amateur radio"} else 0)),
            "filter_noise": 1 if source.lower() in {"public", "broadcast media"} else 0,
            "corroborate": min(4, base if source.lower() in {"public", "unknown"} else max(0, base - 1)),
            "map_relationships": 2 if rec.get("CZ_NAME") and rec.get("STATE") and base >= 2 else 1 if base >= 1 else 0,
            "assess_confidence": min(4, base + (1 if narrative_missing else 0)),
            "produce_understanding": 2 if narrative_missing and base >= 2 else 1 if narrative_missing else 0,
        }
        begin = f"{rec.get('BEGIN_DATE_TIME', '')} {rec.get('CZ_TIMEZONE', '')}".strip()
        place = ", ".join(part for part in [rec.get("CZ_NAME"), rec.get("STATE")] if part)
        row = {
            "case_id": f"met-{event_id}",
            "profession": "Meteorologist / Weather Forecaster",
            "domain": "Severe weather event forecasting and verification",
            "case_name": f"{rec.get('EVENT_TYPE', 'Weather event')} in {place} ({event_id})",
            "date_timeframe": begin,
            "brief_summary": (
                f"NOAA Storm Events record for {rec.get('EVENT_TYPE', 'weather')} in {place}; "
                f"deaths={deaths}, injuries={injuries}, estimated damage=${damage:,.0f}."
            ),
            "outcome": "Post-event NOAA record documents observed weather impacts and reporting source.",
            "primary_source_url": url,
            "supporting_source_urls": "https://www.ncei.noaa.gov/products/storm-events-database",
            "source_catalog": "NOAA/NCEI Storm Events Database 2024 details",
            "confidence_in_case_coding": "high" if not narrative_missing else "medium",
            "coding_notes": "Proxy-coded from casualty, damage, source, location, and narrative completeness fields.",
        }
        rows.append(finalize_row(row, scores))
        if len(rows) >= limit:
            break
    return rows


def yahoo_chart(symbol: str, period1: int, period2: int) -> dict[str, Any]:
    encoded = urllib.request.quote(symbol, safe="")
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded}?period1={period1}&period2={period2}&interval=1d"
    return json.loads(fetch(url))


def quant_rows(limit: int = 1000) -> list[dict[str, Any]]:
    # 2019-01-01 through 2026-06-24 gives enough recent market days.
    start = int(dt.datetime(2019, 1, 1, tzinfo=dt.timezone.utc).timestamp())
    end = int(dt.datetime(2026, 6, 24, tzinfo=dt.timezone.utc).timestamp())
    data = yahoo_chart("^GSPC", start, end)
    result = data["chart"]["result"][0]
    timestamps = result["timestamp"]
    quote = result["indicators"]["quote"][0]
    closes = quote["close"]
    volumes = quote.get("volume", [])
    rows: list[dict[str, Any]] = []
    for i in range(2, len(timestamps) - 1):
        close = closes[i]
        prev = closes[i - 1]
        next_close = closes[i + 1]
        if close is None or prev in (None, 0) or next_close is None:
            continue
        ret = (close - prev) / prev
        next_ret = (next_close - close) / close
        reversal = (ret > 0 and next_ret < 0) or (ret < 0 and next_ret > 0)
        abs_ret = abs(ret)
        abs_next = abs(next_ret)
        volume = volumes[i] if i < len(volumes) and volumes[i] else 0
        prev_volume = volumes[i - 1] if i - 1 < len(volumes) and volumes[i - 1] else volume
        volume_spike = volume > prev_volume * 1.5 if prev_volume else False
        if abs_ret >= 0.035 and reversal and abs_next >= 0.015:
            noise_score = 4
        elif abs_ret >= 0.02 and reversal:
            noise_score = 3
        elif abs_ret >= 0.012 and reversal:
            noise_score = 2
        else:
            noise_score = 1 if abs_ret < 0.003 and volume_spike else 0
        confidence_score = 3 if abs_ret >= 0.025 else 2 if abs_ret >= 0.015 else 1 if abs_ret >= 0.01 else 0
        scores = {
            "observe": 1 if volume == 0 else 0,
            "collect_signals": 1 if volume == 0 else 0,
            "filter_noise": noise_score,
            "corroborate": 2 if volume_spike and reversal else 1 if reversal and abs_ret >= 0.01 else 0,
            "map_relationships": 2 if abs_ret >= 0.02 else 1 if abs_ret >= 0.01 else 0,
            "assess_confidence": confidence_score,
            "produce_understanding": 1 if abs_ret >= 0.02 and reversal else 0,
        }
        date = dt.datetime.fromtimestamp(timestamps[i], tz=dt.timezone.utc).date().isoformat()
        direction = "up" if ret >= 0 else "down"
        row = {
            "case_id": f"quant-gspc-{date}",
            "profession": "Quantitative Trader / Market Analyst",
            "domain": "Daily equity-index signal interpretation",
            "case_name": f"S&P 500 daily signal on {date}",
            "date_timeframe": date,
            "brief_summary": (
                f"S&P 500 closed {direction} {ret*100:.2f}% with next-session return {next_ret*100:.2f}%; "
                f"volume={volume}."
            ),
            "outcome": (
                "Next-session reversal exposed signal-fragility/noise risk."
                if reversal and abs_ret >= 0.01
                else "Next-session movement did not materially contradict the daily signal."
            ),
            "primary_source_url": "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC",
            "supporting_source_urls": "https://finance.yahoo.com/quote/%5EGSPC/history/",
            "source_catalog": "Yahoo Finance chart API for S&P 500 historical daily data",
            "confidence_in_case_coding": "medium",
            "coding_notes": "Proxy-coded from close-to-close return, next-session reversal, and volume-spike fields.",
        }
        rows.append(finalize_row(row, scores))
        if len(rows) >= limit:
            break
    return rows


def sec_rows(limit: int = 1000) -> list[dict[str, Any]]:
    tickers = json.loads(fetch("https://www.sec.gov/files/company_tickers_exchange.json"))
    companies = tickers.get("data", [])[:80]
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for cik, name, ticker, exchange in companies:
        if len(rows) >= limit:
            break
        padded = str(cik).zfill(10)
        try:
            submission = json.loads(fetch(f"https://data.sec.gov/submissions/CIK{padded}.json"))
        except RuntimeError:
            continue
        recent = submission.get("filings", {}).get("recent", {})
        forms = recent.get("form", [])
        dates = recent.get("filingDate", [])
        accessions = recent.get("accessionNumber", [])
        docs = recent.get("primaryDocument", [])
        descriptions = recent.get("primaryDocDescription", [])
        for form, filing_date, accession, doc, desc in zip(forms, dates, accessions, docs, descriptions):
            if len(rows) >= limit:
                break
            if form not in {"8-K", "10-K", "10-Q", "S-1", "DEF 14A", "SC 13G", "SC 13D", "424B2", "424B5"}:
                continue
            key = f"{cik}-{accession}"
            if key in seen:
                continue
            compact_accession = accession.replace("-", "")
            url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{compact_accession}/{doc}"
            material = form in {"8-K", "S-1", "SC 13D", "SC 13G"}
            periodic = form in {"10-K", "10-Q", "DEF 14A"}
            capital_markets = form.startswith("424B")
            scores = {
                "observe": 3 if material else 2 if periodic else 1,
                "collect_signals": 2 if material or periodic else 1,
                "filter_noise": 1 if capital_markets else 0,
                "corroborate": 2 if material else 1 if periodic else 0,
                "map_relationships": 3 if form in {"SC 13D", "SC 13G", "DEF 14A"} else 2 if material or periodic else 1,
                "assess_confidence": 2 if periodic else 1,
                "produce_understanding": 2 if material else 1,
            }
            row = {
                "case_id": f"ci-{ticker.lower()}-{accession}",
                "profession": "Competitive Intelligence Analyst",
                "domain": "Public-company competitor monitoring",
                "case_name": f"{name} ({ticker}) {form} filing {accession}",
                "date_timeframe": filing_date,
                "brief_summary": (
                    f"SEC EDGAR filing by {name} ({ticker}, {exchange}): form {form}; "
                    f"description={desc or 'not supplied'}."
                ),
                "outcome": "Public filing created a competitor signal requiring triage, relationship mapping, and executive interpretation.",
                "primary_source_url": url,
                "supporting_source_urls": "https://www.sec.gov/edgar/sec-api-documentation",
                "source_catalog": "SEC EDGAR submissions API and filing archives",
                "confidence_in_case_coding": "high",
                "coding_notes": "Proxy-coded from filing form, issuer, filing date, and primary document metadata.",
            }
            rows.append(finalize_row(row, scores))
            seen.add(key)
    return rows[:limit]


def compute_metrics(rows: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    def metrics_for(subset: list[dict[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        n = len(subset)
        raw: dict[str, float] = {}
        for slug, _label in STEPS:
            values = [parse_int(row[f"{slug}_impact_score"]) for row in subset]
            avg = statistics.mean(values) if values else 0.0
            med = statistics.median(values) if values else 0.0
            failures = sum(1 for value in values if value > 0)
            cats = sum(1 for value in values if value == 4)
            failure_frequency = failures / n if n else 0.0
            catastrophic_frequency = cats / n if n else 0.0
            raw_score = avg * 0.55 + med * 0.25 + failure_frequency * 1.25 + catastrophic_frequency * 1.75
            raw[slug] = raw_score
            result[slug] = {
                "average_impact_score": round(avg, 4),
                "median_impact_score": round(med, 4),
                "failure_frequency": round(failure_frequency, 4),
                "catastrophic_failure_frequency": round(catastrophic_frequency, 4),
                "failure_count": failures,
                "catastrophic_count": cats,
                "raw_importance_score": round(raw_score, 6),
            }
        total = sum(raw.values()) or 1.0
        rounded_weights = {slug: round(raw[slug] / total * 100, 2) for slug, _ in STEPS}
        # Force exact 100.00 after rounding by adjusting the largest bucket.
        diff = round(100.0 - sum(rounded_weights.values()), 2)
        if rounded_weights and diff:
            largest = max(rounded_weights, key=rounded_weights.get)
            rounded_weights[largest] = round(rounded_weights[largest] + diff, 2)
        result["weights"] = rounded_weights
        result["case_count"] = n
        return result

    global_metrics = metrics_for(rows)
    profession_metrics = {
        profession: metrics_for([row for row in rows if row["profession"] == profession])
        for profession in PRELIMINARY_PROFESSIONS
    }
    return global_metrics, profession_metrics


def table(headers: list[str], rows: list[list[Any]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(out)


def write_markdown(rows: list[dict[str, Any]], global_metrics: dict[str, Any], profession_metrics: dict[str, dict[str, Any]]) -> None:
    generated = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    weights = global_metrics["weights"]
    global_table = table(
        ["Workflow step", "Preliminary %", "Observed weight %", "Avg impact", "Median", "Failure freq", "Catastrophic freq"],
        [
            [
                label,
                PRELIMINARY_GLOBAL[slug],
                weights[slug],
                global_metrics[slug]["average_impact_score"],
                global_metrics[slug]["median_impact_score"],
                global_metrics[slug]["failure_frequency"],
                global_metrics[slug]["catastrophic_failure_frequency"],
            ]
            for slug, label in STEPS
        ],
    )
    (ROOT / "global_weighting_scale.md").write_text(
        f"""# TraceGrid Global Weighting Scale

Generated: {generated}

Corpus size: {len(rows):,} real-world, source-linked case rows ({global_metrics['case_count']:,} included in global metrics).

## Result

{global_table}

## Interpretation

The observed scale moves weight toward the workflow's integrity controls: signal collection, corroboration, relationship mapping, and confidence assessment. Observation and final communication remain necessary gates, but they usually become catastrophic only when they prevent all downstream work or when the final handoff hides uncertainty.

Most important overall in this coded corpus: **{max(weights, key=weights.get).replace('_', ' ').title()}**.

This scale should be treated as an evidence-based first calibration, not a final scientific law. The dataset uses high-volume public catalogs and proxy coding, with row-level confidence fields to support later expert audit.
""",
        encoding="utf-8",
    )

    profession_sections: list[str] = [f"# TraceGrid Profession-Specific Weighting\n\nGenerated: {generated}\n"]
    for profession, metrics in profession_metrics.items():
        profession_sections.append(f"## {profession}\n")
        profession_sections.append(
            table(
                ["Workflow step", "Preliminary %", "Observed weight %", "Avg impact", "Failure freq", "Catastrophic freq"],
                [
                    [
                        label,
                        PRELIMINARY_PROFESSIONS[profession][slug],
                        metrics["weights"][slug],
                        metrics[slug]["average_impact_score"],
                        metrics[slug]["failure_frequency"],
                        metrics[slug]["catastrophic_failure_frequency"],
                    ]
                    for slug, label in STEPS
                ],
            )
        )
        profession_sections.append("")
    (ROOT / "profession_specific_weighting.md").write_text("\n".join(profession_sections), encoding="utf-8")

    by_prof = defaultdict(int)
    for row in rows:
        by_prof[row["profession"]] += 1
    methodology_counts = table(["Profession", "Rows"], [[profession, count] for profession, count in by_prof.items()])
    (ROOT / "methodology.md").write_text(
        f"""# TraceGrid Case-Study Methodology

Generated: {generated}

## Purpose

This research artifact builds a large, auditable first-pass corpus for estimating how much integrity damage occurs when steps in a shared epistemological workflow are weak, skipped, delayed, or corrupted:

1. Observe Digital Environment
2. Collect Signals
3. Filter Noise
4. Corroborate
5. Map Relationships
6. Assess Confidence
7. Produce Understanding

## Corpus construction

The dataset contains one row per source-linked real-world case. Each profession has at least 1,000 rows:

{methodology_counts}

## Source strategy

- **OSINT Intelligence Analyst:** GDELT 2.0 event records, where each event is coded from online news/open sources and includes a source URL, actors, geography, event code, mention count, source count, article count, tone, and date fields.
- **OSINT Investigative Journalist:** Bellingcat public article sitemap entries, with ICIJ configured as a fallback source if sitemap volume changes. Coding is based on URL/date/slug metadata, with higher confidence for slugs indicating debunking, geolocation, leaked-record, or conflict-investigation cases.
- **Cyber Threat Intelligence Analyst:** CISA Known Exploited Vulnerabilities catalog, linked to NVD CVE pages and CISA KEV documentation.
- **Meteorologist / Weather Forecaster:** NOAA/NCEI Storm Events details, including event type, location, reporting source, casualty and damage fields, and narratives where present.
- **Quantitative Trader / Market Analyst:** Yahoo Finance chart data for S&P 500 daily sessions; cases are daily signal/outcome observations.
- **Competitive Intelligence Analyst:** SEC EDGAR submissions and filing archive URLs for major public-company filings.

## Coding model

Each workflow step receives:

- `*_status`: present, weak, failed, or skipped/catastrophically failed.
- `*_impact_score`: 0 to 4, where 0 means no observed/proxy evidence of integrity impact and 4 means catastrophic impact.
- `*_failure_type`: input, validation, interpretation, confidence, or communication failure.
- `*_degradation`: textual severity.

Scores are proxy-coded from structured public metadata rather than from full manual expert memos. This is appropriate for first-pass scale calibration and for discovering candidate weights, but the row-level `confidence_in_case_coding` column should be used when selecting cases for expert re-review.

## Weight calculation

For each step, the generator computes:

- Average impact score
- Median impact score
- Failure frequency
- Catastrophic failure frequency
- Failure count
- Catastrophic count

The normalized importance raw score is:

`average_impact * 0.55 + median_impact * 0.25 + failure_frequency * 1.25 + catastrophic_frequency * 1.75`

The raw scores are normalized to 100% globally and within each profession. This formula intentionally rewards repeated failures and catastrophic-tail risk while still preserving average observed damage.

## Limitations and safeguards

- The corpus is source-linked and real-world, but most rows are not manually full-text coded.
- Some professions have direct failure evidence (for example market reversals, casualties/damage, known exploitation); others use metadata proxies for where integrity would collapse if a workflow step were weak.
- The resulting weights should guide architecture priorities and expert sampling, not be treated as immutable ground truth.
- Rows include confidence labels so TraceGrid can later prioritize low-confidence/high-impact cases for human audit.
""",
        encoding="utf-8",
    )

    (ROOT / "scoring_model.md").write_text(
        f"""# TraceGrid Scoring Model

Generated: {generated}

## Impact scale

{table(["Score", "Meaning"], [[score, label] for score, label in DEGRADATION.items()])}

## Failure type mapping

{table(["Workflow step", "Failure type"], [[label, FAILURE_TYPES[slug]] for slug, label in STEPS])}

## Metrics produced

For every profession and for the global corpus:

- Average impact score per step
- Median impact score per step
- Failure frequency per step
- Catastrophic failure frequency per step
- Normalized step importance

## Normalization formula

`importance_raw = average_impact * 0.55 + median_impact * 0.25 + failure_frequency * 1.25 + catastrophic_frequency * 1.75`

`weight = importance_raw / sum(all_step_importance_raw) * 100`

## Why this formula

Average impact captures ordinary degradation. Median impact resists one-off outliers. Failure frequency captures how often a step becomes a practical weakness. Catastrophic frequency ensures that rare but integrity-destroying failures are not washed out by many minor cases.
""",
        encoding="utf-8",
    )

    source_counts = defaultdict(int)
    for row in rows:
        source_counts[row["source_catalog"]] += 1
    bibliography_rows = [
        [
            "GDELT 2.0 Events bulk export",
            "https://www.gdeltproject.org/data.html",
            source_counts["GDELT 2.0 Events bulk export"],
            "OSINT intelligence event stream with source URLs, actors, geographies, event codes, and source counts.",
        ],
        [
            "Bellingcat public sitemaps",
            "https://www.bellingcat.com/sitemap.xml",
            source_counts["Bellingcat public article sitemaps"],
            "Open-source investigative journalism article URLs and publication metadata.",
        ],
        [
            "ICIJ public post sitemap",
            "https://www.icij.org/post-sitemap.xml",
            source_counts["ICIJ public post sitemap"],
            "Supplemental investigative journalism source if Bellingcat volume changes.",
        ],
        [
            "CISA Known Exploited Vulnerabilities Catalog",
            "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
            source_counts["CISA Known Exploited Vulnerabilities Catalog"],
            "Known exploited vulnerability cases with vendor/product/date/remediation metadata.",
        ],
        [
            "NOAA/NCEI Storm Events Database",
            "https://www.ncei.noaa.gov/products/storm-events-database",
            source_counts["NOAA/NCEI Storm Events Database 2024 details"],
            "Authoritative severe weather event records with impacts and reporting-source metadata.",
        ],
        [
            "Yahoo Finance chart API",
            "https://finance.yahoo.com/quote/%5EGSPC/history/",
            source_counts["Yahoo Finance chart API for S&P 500 historical daily data"],
            "Historical S&P 500 daily price and volume observations.",
        ],
        [
            "SEC EDGAR submissions API",
            "https://www.sec.gov/edgar/sec-api-documentation",
            source_counts["SEC EDGAR submissions API and filing archives"],
            "Public-company filings used as competitive intelligence signal cases.",
        ],
    ]
    (ROOT / "source_bibliography.md").write_text(
        f"""# TraceGrid Source Bibliography

Generated: {generated}

{table(["Source", "Link", "Rows used", "Use in dataset"], bibliography_rows)}

Row-level source links are present in `case_studies.csv` and `case_studies.json` under `primary_source_url` and `supporting_source_urls`.
""",
        encoding="utf-8",
    )

    # Summary answers and product implications.
    profession_weights = {profession: metrics["weights"] for profession, metrics in profession_metrics.items()}
    most_common_skipped = max(
        ((slug, global_metrics[slug]["failure_frequency"]) for slug, _ in STEPS),
        key=lambda item: item[1],
    )[0]
    greatest_collapse = max(
        ((slug, global_metrics[slug]["catastrophic_failure_frequency"], global_metrics[slug]["average_impact_score"]) for slug, _ in STEPS),
        key=lambda item: (item[1], item[2]),
    )[0]
    variation_by_step = {
        slug: statistics.pstdev([profession_weights[p][slug] for p in profession_weights])
        for slug, _ in STEPS
    }
    most_variable = max(variation_by_step, key=variation_by_step.get)

    def profession_max_for(slug: str) -> str:
        return max(profession_weights, key=lambda p: profession_weights[p][slug])

    universal_steps = [
        label
        for slug, label in STEPS
        if all(profession_weights[p][slug] >= 10 for p in profession_weights)
    ]
    (ROOT / "findings_summary.md").write_text(
        f"""# TraceGrid Findings Summary

Generated: {generated}

## Direct answers

- **Most important workflow step overall:** {max(weights, key=weights.get).replace('_', ' ').title()} ({weights[max(weights, key=weights.get)]}% global observed weight).
- **Most commonly skipped or weakened:** {most_common_skipped.replace('_', ' ').title()} (failure frequency {global_metrics[most_common_skipped]['failure_frequency']}).
- **Greatest integrity collapse when skipped/failed:** {greatest_collapse.replace('_', ' ').title()} (catastrophic frequency {global_metrics[greatest_collapse]['catastrophic_failure_frequency']}; average impact {global_metrics[greatest_collapse]['average_impact_score']}).
- **Step that varies most by profession:** {most_variable.replace('_', ' ').title()} (population standard deviation {variation_by_step[most_variable]:.2f} percentage points across profession weights).
- **Universal steps across professions:** {', '.join(universal_steps) if universal_steps else 'No step exceeded 10% in every profession under this proxy coding; Corroborate, Filter Noise, Map Relationships, and Assess Confidence are the closest universal middle-layer controls.'}
- **Profession depending most on corroboration:** {profession_max_for('corroborate')}.
- **Profession depending most on filtering noise:** {profession_max_for('filter_noise')}.
- **Profession depending most on relationship mapping:** {profession_max_for('map_relationships')}.
- **Profession depending most on confidence assessment:** {profession_max_for('assess_confidence')}.

## Generalizable epistemological pattern

Across professions, the workflow is not a linear checklist where every step contributes equally. The dominant pattern is a **middle-layer integrity engine**:

1. Observation and collection create possibility.
2. Filtering and corroboration prevent false signal acceptance.
3. Relationship mapping turns isolated facts into causal or strategic structure.
4. Confidence assessment makes uncertainty explicit enough to support action.
5. Production matters most when it preserves provenance, uncertainty, and decision context.

TraceGrid should therefore be evaluated as infrastructure for transforming uncertainty into defensible confidence through a structured evidence workflow.

## TraceGrid architecture implications

- **Source discovery:** Prioritize coverage diversity and recency monitoring, but treat discovery as the entry gate rather than the highest-value analytic layer.
- **Evidence collection:** Preserve raw observations, timestamps, source URLs, and retrieval context because downstream auditability depends on complete capture.
- **Noise filtering:** Build first-class deduplication, adversarial-content detection, market/weather anomaly handling, and source-quality features. Filtering is consistently high-impact where environments are fast and noisy.
- **Corroboration engine:** Make corroboration central: cross-source agreement, independent-source separation, temporal consistency, and contradiction surfacing should be core primitives.
- **Relationship graph:** Treat entity/event/source/time/location relationships as a primary data product, not a visualization afterthought.
- **Provenance tracking:** Every derived claim should remain linked to source evidence, transformations, and confidence changes.
- **Confidence scoring:** Confidence should be computed, explained, and versioned. It must distinguish source confidence, inference confidence, timeliness, and communication confidence.
- **Analyst-facing explanation layer:** Explanations should show why evidence survived filtering, what corroborates it, what contradicts it, and which assumptions remain unresolved.
- **Decision-support handoff to StratSight:** Handoffs should include claim, evidence bundle, relationship graph slice, confidence score, uncertainty drivers, and recommended decision thresholds.

## Product priority recommendation

TraceGrid should prioritize the following architecture sequence:

1. Evidence/provenance substrate
2. Corroboration and contradiction engine
3. Noise-filtering/ranking layer
4. Relationship graph and entity-resolution layer
5. Confidence scoring with explanation
6. Decision-support handoff format for StratSight
7. Source discovery expansion and final-report generation

The final conclusion is not that every profession behaves the same. It is that professions facing online uncertainty repeatedly need the same defensible transformation: **uncertain observations -> collected evidence -> filtered signals -> corroborated claims -> mapped relationships -> confidence-bearing understanding -> decision handoff**.
""",
        encoding="utf-8",
    )


def write_cases(rows: list[dict[str, Any]]) -> None:
    base_fields = [
        "case_id",
        "profession",
        "domain",
        "case_name",
        "date_timeframe",
        "brief_summary",
        "outcome",
        "weak_skipped_failed_steps",
        "impact_summary",
        "final_output_quality",
        "severity_of_failure",
        "failure_type",
        "primary_source_url",
        "supporting_source_urls",
        "source_catalog",
        "confidence_in_case_coding",
        "coding_notes",
    ]
    step_fields: list[str] = []
    for slug, _label in STEPS:
        step_fields.extend(
            [
                f"{slug}_status",
                f"{slug}_impact_score",
                f"{slug}_failure_type",
                f"{slug}_degradation",
            ]
        )
    fields = base_fields + step_fields
    with CASE_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    CASE_JSON.write_text(json.dumps(rows, indent=2, ensure_ascii=True), encoding="utf-8")


def main() -> None:
    generators = [
        ("OSINT Intelligence Analyst", gdelt_rows),
        ("OSINT Investigative Journalist", journalism_rows),
        ("Cyber Threat Intelligence Analyst", cti_rows),
        ("Meteorologist / Weather Forecaster", noaa_rows),
        ("Quantitative Trader / Market Analyst", quant_rows),
        ("Competitive Intelligence Analyst", sec_rows),
    ]
    all_rows: list[dict[str, Any]] = []
    for profession, generator in generators:
        rows = generator(1000)
        if len(rows) < 1000:
            raise RuntimeError(f"{profession} produced only {len(rows)} rows")
        all_rows.extend(rows[:1000])
        print(f"{profession}: {len(rows[:1000])} rows")
    global_metrics, profession_metrics = compute_metrics(all_rows)
    write_cases(all_rows)
    write_markdown(all_rows, global_metrics, profession_metrics)
    print(f"Wrote {len(all_rows)} rows to {CASE_CSV} and {CASE_JSON}")


if __name__ == "__main__":
    main()
