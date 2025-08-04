from django.shortcuts import render

# Create your views here.

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.utils import translation
from django.shortcuts import redirect

from pathlib import Path
import subprocess
import zipfile
import time
import uuid
import re
import csv
import tempfile
import json
import os

from gumper import config as gcf
from gumper.gumper_client_web import main as gumper_main


DBG = False
DEFAULTS_TO_TRANSLATE = {
    "corpus_name": ["Unnamed corpus"],
    "doc_name": ["Untitled"],
    "doc_subtitle": ["—"],
    "author": ["Unknown"],
    "date": ["—"],
}

def handle_language(request):
    lang = None
    if request.method == "POST":
        lang = request.POST.get("language")

    if lang:
        translation.activate(lang)
        request.LANGUAGE_CODE = lang
    else:
        lang = translation.get_language()
        translation.activate(lang)

    return lang


def load_example_poems():
    example_path = os.path.join(settings.BASE_DIR, "gama", "ext_data", "ex_poem.json")
    try:
        with open(example_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def index(request):
    #return HttpResponse("Hello, world. You're at the gama index.")
    handle_language(request)
    request.session.pop('analysis_data', None)
    request.session.pop('curid', None)
    example_poems = load_example_poems()
    return render(request, "gama/index.html", {"example_poems": example_poems})

def translate_if_default(value, key):
    if value in DEFAULTS_TO_TRANSLATE.get(key, []):
        return _(value)
    return value

def analysis(request):
    handle_language(request)

    if request.method == "POST":
        text = request.POST.get("text", "")
        if not text:
            return redirect("gama:error", errtype="empty")
        if len(text) > 4500:
            return redirect("gama:error", errtype="too_long")
        if any(len(line.strip()) > 200 for line in text.splitlines() if line.strip()):
            return redirect("gama:error", errtype="not_verse")

        corpus_name_key = request.POST.get("corpus_name") or "—"
        doc_name_key = request.POST.get("doc_name") or "—"
        doc_subtitle_key = request.POST.get("doc_subtitle") or "—"
        author_key = request.POST.get("author") or "Unknown"
        date_key = request.POST.get("date") or "—"

        request.session['analysis_data'] = {
            "text": text,
            "corpus_name": corpus_name_key,
            "doc_name": doc_name_key,
            "doc_subtitle": doc_subtitle_key,
            "author": author_key,
            "date": date_key,
        }

        request.session["curid"] = str(uuid.uuid4())[0:6]
        curid = request.session["curid"]
        out_dir = settings.IO_DIR / curid
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        with open(out_dir / "input.txt", encoding="utf8", mode="w") as f:
            f.write(text)

        try:
            subprocess.run(
                ["python", "../preprocessing/g2s_client_running_text.py",
                 str(out_dir / "input.txt"), "-p", "-d", "-n", "-s", "-b", "001"],
                check=True,
                cwd=settings.PREPRO_DIR,
            )
        except subprocess.CalledProcessError as e:
            context = {
                "error": f"Analysis failed: {e}",
                "text": text,
            }
            return render(request, "gama/analysis.html", context)

        orig_poem_path = out_dir / "input.txt"
        prepro_poem_path = out_dir / "out_001" / "input_pp_out_norm_spa_001.txt"
        scansion, results_data = gumper_main(gcf, orig_poem_path, prepro_poem_path)

        request.session['analysis_result'] = "".join(scansion)
        request.session['results_data'] = results_data

        #Redirection nouvelle view pour PRG
        return redirect("gama:analysis_result")

    return redirect("gama:index")

def analysis_result(request):
    handle_language(request)
    analysis_data = request.session.get("analysis_data")
    analysis_result = request.session.get("analysis_result")

    if not analysis_data or not analysis_result:
        return redirect("gama:error", errtype="empty")

    corpus_name = translate_if_default(analysis_data.get("corpus_name", "Unnamed corpus"), "corpus_name")
    doc_name = translate_if_default(analysis_data.get("doc_name", "Untitled"), "doc_name")
    doc_subtitle = translate_if_default(analysis_data.get("doc_subtitle", "—"), "doc_subtitle")
    author = translate_if_default(analysis_data.get("author", "Unknown"), "author")
    date = translate_if_default(analysis_data.get("date", "—"), "date")

    context = {
        "text": analysis_data.get("text", ""),
        "corpus_name": corpus_name,
        "doc_name": doc_name,
        "doc_subtitle": doc_subtitle,
        "author": author,
        "date": date,
        "result": analysis_result,
    }

    return render(request, "gama/analysis.html", context)

def error(request, errtype):
    handle_language(request)
    if errtype == "empty":
        err_message = _("The input text cannot be empty.")
    elif errtype == "too_long":
        err_message = _("The input text is too long. Maximum length allowed: 4500 characters.")
    elif errtype == "not_verse":
        err_message = _("The input text does not seem to be in verse (lines too long?).")
    else:
        return render(request, "gama/error.html", {
            "message": _("An unexpected error occurred.")
        })

    example_poems = load_example_poems()
    context = {
        "error_message": err_message,
        "example_poems": example_poems,
    }
    return render(request, "gama/index.html", context)

def export_results(request):
    handle_language(request)

    analysis_data = request.session.get("analysis_data")
    results_data = request.session.get("results_data")
    text = analysis_data.get("text", "") if analysis_data else ""
    curid = request.session.get("curid", "000000")

    if not results_data:
        return HttpResponse("No analysis results to export.", status=400)

    corpus_name_key = analysis_data.get("corpus_name", "Unnamed corpus")
    doc_name_key = analysis_data.get("doc_name", "Untitled")
    doc_subtitle_key = analysis_data.get("doc_subtitle", "—")
    author_key = analysis_data.get("author", "Unknown")
    date_key = analysis_data.get("date", "—")

    corpus_name = translate_if_default(corpus_name_key, "corpus_name")
    doc_name = translate_if_default(doc_name_key, "doc_name")
    doc_subtitle = translate_if_default(doc_subtitle_key, "doc_subtitle")
    author = translate_if_default(author_key, "author")
    date = translate_if_default(date_key, "date")

    with tempfile.TemporaryDirectory() as tmpdir:
        # input.txt
        with open(f"{tmpdir}/input.txt", "w", encoding="utf-8") as f:
            f.write(text)

        # metadata.tsv
        with open(f"{tmpdir}/metadata.tsv", "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerow([_("corpus_name"), _("title"), _("subtitle"), _("author"), _("date")])
            writer.writerow([corpus_name, doc_name, doc_subtitle, author,date])

        # results.tsv
        with open(f"{tmpdir}/results.tsv", "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "#", _("original_text"), _("preprocessing"),
                _("metrical_syllables"), _("stressed_syllables"), _("no_extra_rhythmic")
            ], delimiter="\t")
            writer.writeheader()
            for row in results_data:
                writer.writerow({
                    "#": row["line"],
                    _("original_text"): row["original_text"],
                    _("preprocessing"): row["preprocessing"],
                    _("metrical_syllables"): row["metrical_syllables"],
                    _("stressed_syllables"): row["stressed_syllables"],
                    _("no_extra_rhythmic"): row["no_extra_rhythmic"]
                })
        # zip
        zip_filename = f"results_scansion_{curid}.zip"
        zip_path = f"{tmpdir}/{zip_filename}"
        with zipfile.ZipFile(zip_path, "w") as zipf:
            zipf.write(f"{tmpdir}/input.txt", "input.txt")
            zipf.write(f"{tmpdir}/metadata.tsv", "metadata.tsv")
            zipf.write(f"{tmpdir}/results.tsv", "results.tsv")

        with open(zip_path, "rb") as f:
            response = HttpResponse(f.read(), content_type="application/zip")
            response["Content-Disposition"] = f"attachment; filename={zip_filename}"
            return response

def about(request):
    """'About' page for each language."""
    handle_language(request)
    lang = request.LANGUAGE_CODE
    translation.activate(lang)
    return render(request, f"gama/about/about_{lang}.html")
