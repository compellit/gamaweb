from django.shortcuts import render

# Create your views here.

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.utils import translation

from pathlib import Path
import subprocess
import time
import uuid

from gumper import config as gcf
from gumper.gumper_client_web import main as gumper_main


DBG = False

def index(request):
    #return HttpResponse("Hello, world. You're at the gama index.")
    request.session.pop('analysis_data', None)
    request.session.pop('curid', None)
    return render(request, "gama/index.html")

def analysis(request):
    lang = request.POST.get('language')
    if lang:
        request.session[translation.LANGUAGE_SESSION_KEY] = lang

    if request.method == "POST" and request.POST.get("text"):
        text = request.POST.get("text", "")
        if not text:
            return redirect("gama:error", errtype="empty")
        if len(text) > 4500:
            return redirect("gama:error", errtype="too_long")
        corpus_name = request.POST.get("corpus_name") or "Unnamed corpus"
        doc_name = request.POST.get("doc_name") or "Untitled"
        doc_subtitle = request.POST.get("doc_subtitle") or "—"
        author = request.POST.get("author") or "Unknown"

        # Sauvegarder en session
        request.session['analysis_data'] = {
            "text": text,
            "corpus_name": corpus_name,
            "doc_name": doc_name,
            "doc_subtitle": doc_subtitle,
            "author": author,
        }
    else:
        analysis_data = request.session.get('analysis_data')
        if analysis_data:
            text = analysis_data.get("text", "")
            corpus_name = analysis_data.get("corpus_name", _("Unnamed corpus"))
            doc_name = analysis_data.get("doc_name", _("Untitled"))
            doc_subtitle = analysis_data.get("doc_subtitle", "—")
            author = analysis_data.get("author", _("Unknown"))
        else:
            # Pas de données, on redirige erreur
            return redirect("gama:error", errtype="empty")

    context = {
        "text": text,
        "corpus_name": corpus_name,
        "doc_name": doc_name,
        "doc_subtitle": doc_subtitle,
        "author": author,
    }
    request.session["curid"] = str(uuid.uuid4())[0:6]
    curid = request.session["curid"]
    out_dir = settings.IO_DIR / curid
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    with open(out_dir / "input.txt", encoding="utf8", mode="w") as f:
        f.write(text)
    # Run preprocessing
    try:
        subprocess.run(
            ["python", "../preprocessing/g2s_client_running_text.py",
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
    print(f"  - Start scansion: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
    scansion = gumper_main(gcf, orig_poem_path, prepro_poem_path)
    DBG and print("Scansion", scansion)
    print(scansion)
    context["result"] = "".join(scansion)
    return render(request, "gama/analysis.html", context)


def error(request, errtype):
    if errtype == "empty":
        err_message = _("The input text cannot be empty.")
    elif errtype == "too_long":
        err_message = _("The input text is too long to be processed.")
    else:
        return render(request, "gama/error.html", {
            "message": _("An unexpected error occurred.")
        })
    context = {
        "error_message": err_message,
    }
    return render(request, "gama/index.html", context)
