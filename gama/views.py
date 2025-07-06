from django.shortcuts import render

# Create your views here.

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render

from pathlib import Path
import subprocess
import time
import uuid

from gumper import config as gcf
from gumper.gumper_client_web import main as gumper_main


DBG = False

def index(request):
    #return HttpResponse("Hello, world. You're at the gama index.")
    return render(request, "gama/index.html")

def analysis(request):
    text = request.POST.get("text", "")
    context = {"text": text}
    request.session["curid"] = str(uuid.uuid4())[0:6]
    curid = request.session["curid"]
    out_dir = settings.IO_DIR / curid
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    with open(out_dir / "input.txt", encoding="utf8", mode="w") as f:
        f.write(text)
    # Run preprocessing
    try:
        subprocess.run(
            ["python3", "../preprocessing/g2s_client_running_text.py",
             str(out_dir / "input.txt"), "-p", "-d", "-n", "-s", "-b", "001"],
            check=True,
            cwd=settings.PREPRO_DIR,
        )
    except subprocess.CalledProcessError as e:
        context["error"] = f"Analysis failed: {e}"
        return render(request, "gama/analysis.html", context)
    # Run scansion
    orig_poem_path = out_dir / "input.txt"
    prepro_poem_path = out_dir / "out_001" / "input_pp_out_norm_spa_001.txt"
    print(f"  - Start scansion: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}")
    scansion = gumper_main(gcf, orig_poem_path, prepro_poem_path)
    DBG and print("Scansion", scansion)
    context = {"result": "".join(scansion)}
    return render(request, "gama/analysis.html", context)