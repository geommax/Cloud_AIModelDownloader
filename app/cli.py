#!/usr/bin/env python3
"""
HF Model Downloader CLI
Hugging Face မှ AI Model များကို download ဆွဲပြီး local machine မှာသိမ်းဆည်းပေးသော CLI app
"""

import os
import sys
import argparse
from huggingface_hub import (
    HfApi,
    snapshot_download,
    hf_hub_download,
    login,
    list_models,
)
from huggingface_hub.utils import HfHubHTTPError


DOWNLOAD_DIR = os.environ.get("HF_DOWNLOAD_DIR", "/models")


def authenticate(token: str | None = None) -> HfApi:
    """Hugging Face token ဖြင့် authenticate လုပ်ပါ"""
    tok = token or os.environ.get("HF_TOKEN")
    if not tok:
        print("❌  HF_TOKEN environment variable သတ်မှတ်ထားရန် လိုအပ်ပါသည်။")
        print("   docker-compose.yml ထဲတွင် HF_TOKEN ကို .env file မှတဆင့် သတ်မှတ်ပါ။")
        sys.exit(1)
    login(token=tok, add_to_git_credential=False)
    return HfApi(token=tok)


def cmd_download(args):
    """Model တစ်ခုလုံးကို download ဆွဲပါ"""
    api = authenticate(args.token)
    repo_id = args.repo

    print(f"📦  Downloading: {repo_id}")
    print(f"📂  Save to:     {DOWNLOAD_DIR}/{repo_id}")

    try:
        path = snapshot_download(
            repo_id=repo_id,
            repo_type=args.type,
            revision=args.revision,
            local_dir=os.path.join(DOWNLOAD_DIR, repo_id.replace("/", "_")),
            token=api.token,
            allow_patterns=args.include,
            ignore_patterns=args.exclude,
        )
        print(f"✅  Download complete: {path}")
    except HfHubHTTPError as e:
        print(f"❌  Download failed: {e}")
        sys.exit(1)


def cmd_download_file(args):
    """Model repo ထဲက file တစ်ခုတည်းကို download ဆွဲပါ"""
    api = authenticate(args.token)

    print(f"📦  Downloading file: {args.filename} from {args.repo}")

    try:
        path = hf_hub_download(
            repo_id=args.repo,
            filename=args.filename,
            repo_type=args.type,
            revision=args.revision,
            local_dir=os.path.join(DOWNLOAD_DIR, args.repo.replace("/", "_")),
            token=api.token,
        )
        print(f"✅  File downloaded: {path}")
    except HfHubHTTPError as e:
        print(f"❌  Download failed: {e}")
        sys.exit(1)


def cmd_search(args):
    """Hugging Face Hub မှာ model ရှာပါ"""
    api = authenticate(args.token)

    print(f"🔍  Searching: {args.query}")
    print("-" * 60)

    models = list(api.list_models(
        search=args.query,
        limit=args.limit,
        sort="downloads",
        direction=-1,
    ))

    if not models:
        print("   ရလဒ်မရှိပါ။")
        return

    for i, model in enumerate(models, 1):
        downloads = getattr(model, "downloads", "N/A")
        likes = getattr(model, "likes", "N/A")
        print(f"  {i:>3}. {model.id}")
        print(f"       ⬇ {downloads:,} downloads  |  ❤ {likes} likes")

    print("-" * 60)
    print(f"  စုစုပေါင်း {len(models)} ခု တွေ့ရှိပါသည်။")


def cmd_info(args):
    """Model repo ၏ အချက်အလက်များကို ကြည့်ပါ"""
    api = authenticate(args.token)

    print(f"ℹ️   Model info: {args.repo}")
    print("-" * 60)

    try:
        info = api.model_info(args.repo)
        print(f"  Repo ID    : {info.id}")
        print(f"  Author     : {info.author}")
        print(f"  Downloads  : {info.downloads:,}")
        print(f"  Likes      : {info.likes}")
        print(f"  Tags       : {', '.join(info.tags or [])}")
        print(f"  Pipeline   : {info.pipeline_tag}")
        print(f"  License    : {getattr(info, 'card_data', {})}")
        print(f"  Last Update: {info.last_modified}")

        # List files
        siblings = info.siblings or []
        print(f"\n  📁 Files ({len(siblings)}):")
        total_size = 0
        for f in siblings:
            size = f.size or 0
            total_size += size
            size_str = _format_size(size)
            print(f"      {size_str:>10}  {f.rfilename}")
        print(f"      {'─' * 40}")
        print(f"      {_format_size(total_size):>10}  Total")

    except HfHubHTTPError as e:
        print(f"❌  Error: {e}")
        sys.exit(1)


def cmd_list_downloaded(_args):
    """Download ဆွဲပြီးသား model များကို ပြပါ"""
    print(f"📂  Downloaded models in {DOWNLOAD_DIR}:")
    print("-" * 60)

    if not os.path.exists(DOWNLOAD_DIR):
        print("   Download directory မရှိသေးပါ။")
        return

    entries = sorted(os.listdir(DOWNLOAD_DIR))
    if not entries:
        print("   Download ဆွဲထားသော model မရှိသေးပါ။")
        return

    for entry in entries:
        full_path = os.path.join(DOWNLOAD_DIR, entry)
        if os.path.isdir(full_path):
            size = _dir_size(full_path)
            print(f"  📁 {entry}  ({_format_size(size)})")

    print("-" * 60)


def _format_size(size_bytes: int) -> str:
    """Bytes ကို human-readable format သို့ ပြောင်းပါ"""
    if size_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    while size >= 1024 and i < len(units) - 1:
        size /= 1024
        i += 1
    return f"{size:.1f} {units[i]}"


def _dir_size(path: str) -> int:
    """Directory ၏ total size ကို bytes ဖြင့် return ပြန်ပါ"""
    total = 0
    for dirpath, _dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total += os.path.getsize(fp)
    return total


def main():
    parser = argparse.ArgumentParser(
        prog="hfdl",
        description="🤗 Hugging Face Model Downloader CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  hfdl download meta-llama/Llama-2-7b-hf
  hfdl download google/gemma-2b --exclude "*.bin"
  hfdl download-file meta-llama/Llama-2-7b-hf config.json
  hfdl search "text generation" --limit 20
  hfdl info microsoft/phi-2
  hfdl list
""",
    )

    # Global args
    parser.add_argument(
        "--token", "-t",
        help="HF Token (default: $HF_TOKEN env var)",
        default=None,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- download ---
    p_dl = subparsers.add_parser("download", aliases=["dl"], help="Model repo download ဆွဲပါ")
    p_dl.add_argument("repo", help="Repo ID (e.g. meta-llama/Llama-2-7b-hf)")
    p_dl.add_argument("--type", choices=["model", "dataset", "space"], default="model", help="Repo type")
    p_dl.add_argument("--revision", default=None, help="Branch / tag / commit")
    p_dl.add_argument("--include", nargs="*", default=None, help="Include patterns (e.g. *.safetensors)")
    p_dl.add_argument("--exclude", nargs="*", default=None, help="Exclude patterns (e.g. *.bin)")
    p_dl.set_defaults(func=cmd_download)

    # --- download-file ---
    p_dlf = subparsers.add_parser("download-file", aliases=["dlf"], help="File တစ်ခုတည်းကို download ဆွဲပါ")
    p_dlf.add_argument("repo", help="Repo ID")
    p_dlf.add_argument("filename", help="File name to download")
    p_dlf.add_argument("--type", choices=["model", "dataset", "space"], default="model")
    p_dlf.add_argument("--revision", default=None)
    p_dlf.set_defaults(func=cmd_download_file)

    # --- search ---
    p_search = subparsers.add_parser("search", aliases=["s"], help="Model ရှာပါ")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--limit", "-n", type=int, default=10, help="Max results")
    p_search.set_defaults(func=cmd_search)

    # --- info ---
    p_info = subparsers.add_parser("info", aliases=["i"], help="Model info ကြည့်ပါ")
    p_info.add_argument("repo", help="Repo ID")
    p_info.set_defaults(func=cmd_info)

    # --- list ---
    p_list = subparsers.add_parser("list", aliases=["ls"], help="Download ဆွဲပြီးသား model များကို ပြပါ")
    p_list.set_defaults(func=cmd_list_downloaded)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
