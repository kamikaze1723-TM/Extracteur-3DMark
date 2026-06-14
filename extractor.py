import os
import zipfile
import tempfile
import xml.etree.ElementTree as ET
from statistics import mean
import re

def strip_ns(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag

def parse_xml_file(path):
    root = ET.parse(path).getroot()
    data = []
    for elem in root.iter():
        tag = strip_ns(elem.tag)
        text = (elem.text or "").strip()
        if text:
            data.append((tag, text))
        for k, v in elem.attrib.items():
            val = str(v).strip()
            if val:
                data.append((f"{tag}_{strip_ns(k)}", val))
                data.append((strip_ns(k), val))
    return data

def safe_float(v):
    try:
        return float(str(v).replace(",", "."))
    except Exception:
        return None

def safe_int(v):
    try:
        return int(float(v))
    except Exception:
        return None

def find_first(pairs, patterns, exclude=None):
    exclude = exclude or []
    for p in patterns:
        p = p.lower()
        for k, v in pairs:
            if k.lower() == p:
                return v
    for p in patterns:
        p = p.lower()
        for k, v in pairs:
            lk = k.lower()
            if lk.startswith(f"{p}_") or lk.endswith(f"_{p}") or f"_{p}_" in lk:
                if not any(x in lk or x in str(v).lower() for x in exclude): return v
    for p in patterns:
        p = p.lower()
        if len(p) >= 4:
            for k, v in pairs:
                lk = k.lower()
                if p in lk:
                    if not any(x in lk or x in str(v).lower() for x in exclude): return v
    return None

def collect_archive_info(archive_path):
    result = {"archive": archive_path, "files": [], "pairs": [], "summary": {}, "scores": [], "fps_values": []}

    with zipfile.ZipFile(archive_path, "r") as zf:
        names = zf.namelist()
        result["files"] = names
        with tempfile.TemporaryDirectory() as td:
            zf.extractall(td)
            for name in names:
                full = os.path.join(td, name)
                if os.path.isfile(full) and name.lower().endswith(".xml"):
                    try: result["pairs"].extend(parse_xml_file(full))
                    except Exception: pass
            
            # Extract Monitoring Data
            monitoring_path = os.path.join(td, "Monitoring.csv")
            if os.path.exists(monitoring_path):
                try:
                    with open(monitoring_path, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                    if lines:
                        headers = lines[0].strip().split(";")
                        idx_time, idx_cpu_t, idx_gpu_t, idx_gpu_l, idx_cpu_c, idx_gpu_c = -1, -1, -1, -1, -1, -1
                        for i, h in enumerate(headers):
                            hl = h.lower()
                            if "runtime" in hl: idx_time = i
                            elif "processorcoretemperature" in hl: idx_cpu_t = i
                            elif "gputemperature" in hl: idx_gpu_t = i
                            elif "gpuload" in hl: idx_gpu_l = i
                            elif "processorcoreclock" in hl and idx_cpu_c == -1: idx_cpu_c = i
                            elif "gpucoreclock" in hl: idx_gpu_c = i
                        
                        m_time, m_cpu_t, m_gpu_t, m_gpu_l, m_cpu_c, m_gpu_c = [], [], [], [], [], []
                        for line in lines[1:]:
                            parts = line.strip("\n").split(";")
                            if idx_time != -1 and len(parts) > idx_time and parts[idx_time]:
                                m_time.append(safe_float(parts[idx_time]))
                                m_cpu_t.append(safe_float(parts[idx_cpu_t]) if idx_cpu_t != -1 and len(parts) > idx_cpu_t and parts[idx_cpu_t] else None)
                                m_gpu_t.append(safe_float(parts[idx_gpu_t]) if idx_gpu_t != -1 and len(parts) > idx_gpu_t and parts[idx_gpu_t] else None)
                                m_gpu_l.append(safe_float(parts[idx_gpu_l]) if idx_gpu_l != -1 and len(parts) > idx_gpu_l and parts[idx_gpu_l] else None)
                                m_cpu_c.append(safe_float(parts[idx_cpu_c]) if idx_cpu_c != -1 and len(parts) > idx_cpu_c and parts[idx_cpu_c] else None)
                                m_gpu_c.append(safe_float(parts[idx_gpu_c]) if idx_gpu_c != -1 and len(parts) > idx_gpu_c and parts[idx_gpu_c] else None)
                        
                        result["monitoring"] = {
                            "time": m_time,
                            "cpu_temp": m_cpu_t,
                            "gpu_temp": m_gpu_t,
                            "gpu_load": m_gpu_l,
                            "cpu_clock": m_cpu_c,
                            "gpu_clock": m_gpu_c
                        }
                except Exception:
                    pass

    pairs = result["pairs"]
    benchmark_id = find_first(pairs, ["benchmark_run_id", "benchmarkrunid", "run_id"])
    benchmark_name = find_first(pairs, ["workload_name", "benchmarkname", "testname", "resultname"]) or "3DMark Benchmark"
    
    api = find_first(pairs, ["graphics_api", "graphicsapi", "api", "backend", "directx", "vulkan", "opengl"])
    start_time = find_first(pairs, ["benchmark_start_time", "starttime"])
    finish_time = find_first(pairs, ["benchmark_finish_time", "endtime"])
    loops = find_first(pairs, ["loop_count", "loopsdone", "testloopsdone", "loopcount"])
    
    resolution = None
    pw = find_first(pairs, ["physicalwidth", "physical_width"])
    ph = find_first(pairs, ["physicalheight", "physical_height"])
    if pw and ph:
        resolution = f"{pw}x{ph}"
    else:
        resolution = find_first(pairs, ["display_resolution", "screenresolution", "displayresolution", "render_resolution", "resolution"])
        if not resolution:
            for k, v in pairs:
                if k.lower() in ["commandline", "command_line"]:
                    m1 = re.search(r'--screenWidth=(\d+)', str(v))
                    m2 = re.search(r'--screenHeight=(\d+)', str(v))
                    if m1 and m2:
                        resolution = f"{m1.group(1)}x{m2.group(1)}"
                        break

    gpu = find_first(pairs, ["adapter_name", "graphicscard", "graphicsadapter", "videocard", "gpu_name", "gpu"]) or "Unknown GPU"
    cpu = find_first(pairs, ["cpu", "processor", "cpu_name", "processor_name"]) or "Unknown CPU"
    os_name = find_first(pairs, ["os", "operatingsystem", "os_name", "os_version", "osversion", "platform"], exclude=["bios"])
    ram = find_first(pairs, ["memory", "ram", "systemmemory", "memorytotal", "physical_memory"], exclude=["dedicated", "shared", "minimum", "maximum", "current", "clock"])
    vram = find_first(pairs, ["mem_size", "dedicatedvideomemory", "dedicatedmemory", "video_memory", "videomemory", "vram", "adapter_memory"])
    driver = find_first(pairs, ["driverversion", "driver_version", "graphicsdriver", "driver"])

    if ram and str(ram).isdigit(): ram = f"{int(ram) // 1048576} MB" if int(ram) > 1000000 else f"{ram} MB"
    if vram and str(vram).isdigit(): vram = f"{int(vram) // 1048576} MB" if int(vram) > 1000000 else f"{vram} MB"

    stability = find_first(pairs, ["stabilitydx", "dx12stability", "stability"])
    best_score = find_first(pairs, ["bestscoredx", "dx12bestscore"])
    worst_score = find_first(pairs, ["worstscoredx", "dx12worstscore"])
    passed = find_first(pairs, ["passdx", "dx12passed"])

    if not best_score: best_score = find_first(pairs, ["overallscoredxforpass"])

    primary_results = []
    for k, v in pairs:
        if k.lower() == "primary_result":
            fv = safe_float(v)
            if fv is not None: primary_results.append(fv)

    pass_scores = []
    for k, v in pairs:
        lk = k.lower()
        if "overallscoredxforpass" in lk or "graphicsscoredxforpass" in lk or "3dmarkscoreforpass" in lk:
            iv = safe_int(v)
            if iv is not None: pass_scores.append(iv)

    dedup_scores = []
    seen = set()
    for s in pass_scores:
        if s not in seen:
            dedup_scores.append(s)
            seen.add(s)

    avg_fps = round(mean(primary_results), 3) if primary_results else None
    avg_score = round(mean(dedup_scores), 1) if dedup_scores else None

    stability_num = safe_float(stability)
    if stability_num is not None: stability = round(stability_num, 2)

    passed_text = None
    if str(passed) in ("1", "1.0", "true", "True"): passed_text = "PASS"
    elif passed is not None: passed_text = "FAIL"

    result["summary"] = {
        "Benchmark name": benchmark_name,
        "Benchmark ID": benchmark_id,
        "GPU": gpu,
        "CPU": cpu,
        "RAM": ram,
        "VRAM": vram,
        "OS": os_name,
        "Driver": driver,
        "API": api,
        "Resolution": resolution,
        "Start time": start_time,
        "Finish time": finish_time,
        "Loop count": safe_int(loops) if loops is not None else loops,
        "Best score": safe_int(best_score) if best_score is not None else best_score,
        "Worst score": safe_int(worst_score) if worst_score is not None else worst_score,
        "Average score": avg_score,
        "Stability %": stability,
        "Average FPS": avg_fps,
        "Passed": passed_text,
        "Computer": find_first(pairs, ["computer_name", "computername"]),
        "User": find_first(pairs, ["username", "user_name"]),
    }
    
    # Advanced Hardware
    mb_vendor = find_first(pairs, ["Mainboard_Vendor", "mainboardvendor", "motherboardvendor"])
    mb_model = find_first(pairs, ["Mainboard_Model", "mainboardmodel", "motherboardmodel"])
    if mb_vendor or mb_model:
        result["summary"]["Motherboard"] = f"{mb_vendor or ''} {mb_model or ''}".strip()
    
    bios_vendor = find_first(pairs, ["BIOS_Vendor", "biosvendor"])
    bios_date = find_first(pairs, ["BIOS_Date", "biosdate"])
    if bios_vendor or bios_date:
        result["summary"]["BIOS"] = f"{bios_vendor or ''} {bios_date or ''}".strip()
        
    ram_speed = find_first(pairs, ["Marketing_Frequency", "memoryfrequency", "ramspeed"])
    if ram_speed:
        result["summary"]["RAM Speed"] = f"{ram_speed} MHz"
    
    result["scores"] = dedup_scores[:]
    result["fps_values"] = primary_results[:]
    return result
