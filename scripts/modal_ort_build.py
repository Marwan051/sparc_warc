"""Build an AVX2-only ONNX Runtime wheel on Modal.

The wheel is built from ONNX Runtime v1.30.0 with the AVX-VNNI, AVX-512 and AMX
dispatch blocks disabled in MLAS. That forces every x86-64 host to use the same
AVX2/FMA3 kernels as the local baseline, which is the property the embedding
corpus needs.

The resulting wheel is written to the ``warc-ort-build`` Modal Volume.
"""

import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

import modal

APP_NAME = "warc-ort-build"
VOLUME_NAME = "warc-ort-build"
ORT_VERSION = "v1.30.0"

build_image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install(
        "build-essential",
        "git",
        "ninja-build",
        "pkg-config",
        "libprotobuf-dev",
        "protobuf-compiler",
        "libgomp1",
        "patchelf",
        "curl",
        "ca-certificates",
        "unzip",
        "wget",
        "libssl-dev",
        "zlib1g-dev",
        "libffi-dev",
        "libbz2-dev",
        "libreadline-dev",
        "libsqlite3-dev",
        "liblzma-dev",
    )
    .uv_pip_install(
        "cmake>=3.28,<4",
        "ninja",
        "numpy==2.5.3",
        "packaging",
        "protobuf>=4.25.8",
        "flatbuffers",
        "sympy",
        "setuptools",
        "wheel",
        "pybind11",
        "requests",
        "tqdm",
        "onnx",
    )
)

app = modal.App(APP_NAME)
volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)


def _run(command: list[str], cwd: Path | None = None, timeout: int | None = None) -> None:
    print("+ " + " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, check=True, timeout=timeout)


def _patch_platform(platform: Path) -> None:
    source = platform.read_text(encoding="utf-8")
    replacements = [
        # AVX-VNNI (256-bit) would override the plain AVX2 U8S8 kernel.
        ("if ((Cpuid7_1[0] & 0x10) != 0) {", "if (false) {"),
        # Entire AVX-512F/core/VNNI block.
        (
            "if (((Cpuid7[1] & 0x10000) != 0) && ((xcr0 & 0xE0) == 0xE0)) {",
            "if (false) {",
        ),
        # AVX-VNNI-INT8, which can replace the U8U8 dispatcher.
        ("if ((Cpuid7_1[3] & 0x10) != 0) {", "if (false) {"),
    ]
    for old, new in replacements:
        count = source.count(old)
        if count != 1:
            raise RuntimeError(f"expected exactly one occurrence, found {count}: {old[:100]}")
        source = source.replace(old, new, 1)

    amx_pattern = re.compile(
        r"if \(\(Cpuid7\[3\] & 0b1 << 24\) != 0 &&\s*"
        r"\(Cpuid7\[3\] & 0b1 << 25\) != 0 &&\s*"
        r"\(xcr0 & XFEATURE_MASK_XTILE\) == XFEATURE_MASK_XTILE\) \{"
    )
    if len(amx_pattern.findall(source)) != 1:
        raise RuntimeError("could not find the AMX dispatch condition")
    source = amx_pattern.sub("if (false) {", source, count=1)

    platform.write_text(source, encoding="utf-8")
    print(f"patched {platform}", flush=True)
    for line_number, line in enumerate(source.splitlines(), 1):
        if "if (false) {" in line:
            print(f"  patched line {line_number}: {line.strip()}", flush=True)


@app.function(
    image=build_image,
    cpu=16,
    memory=65536,
    timeout=14400,
    volumes={"/output": volume},
)
def build() -> dict:
    started = time.time()
    source_dir = Path("/ort")
    if source_dir.exists():
        shutil.rmtree(source_dir)

    _run(
        [
            "git",
            "clone",
            "--recursive",
            "--depth",
            "1",
            "--branch",
            ORT_VERSION,
            "https://github.com/microsoft/onnxruntime.git",
            str(source_dir),
        ]
    )
    _patch_platform(source_dir / "onnxruntime" / "core" / "mlas" / "lib" / "platform.cpp")

    cmake_version = subprocess.run(
        ["cmake", "--version"], capture_output=True, text=True, check=True
    ).stdout.splitlines()[0]
    print(f"using {cmake_version}", flush=True)
    print(f"nproc={os.cpu_count()}", flush=True)

    env = os.environ.copy()
    env["CMAKE_BUILD_PARALLEL_LEVEL"] = "16"
    env["PYTHONUNBUFFERED"] = "1"
    _run(
        [
            "./build.sh",
            "--config",
            "Release",
            "--build_wheel",
            "--enable_pybind",
            "--skip_submodule_sync",
            "--parallel",
            "16",
            "--cmake_generator",
            "Ninja",
            "--no_telemetry",
            "--compile_no_warning_as_error",
            "--allow_running_as_root",
            "--skip_tests",
            "--cmake_extra_defines",
            "onnxruntime_BUILD_UNIT_TESTS=OFF",
        ],
        cwd=source_dir,
        timeout=13800,
    )

    wheels = sorted(source_dir.glob("build/**/dist/onnxruntime-*.whl"))
    if not wheels:
        wheels = sorted(source_dir.glob("build/**/*.whl"))
    if not wheels:
        raise RuntimeError("build finished but no wheel was found")

    output_dir = Path("/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    for wheel in wheels:
        destination = output_dir / wheel.name
        shutil.copy2(wheel, destination)
        copied.append({"path": str(destination), "size": destination.stat().st_size})
        print(f"copied {destination} ({destination.stat().st_size} bytes)", flush=True)

    report = {
        "ort_version": ORT_VERSION,
        "cmake": cmake_version,
        "wheels": copied,
        "elapsed_seconds": round(time.time() - started, 1),
    }
    (output_dir / "build_report.json").write_text(json.dumps(report, indent=2))
    volume.commit()
    return report


@app.local_entrypoint()
def main() -> None:
    print(build.remote())
