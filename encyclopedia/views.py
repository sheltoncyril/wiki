from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
import random as rand
from . import util
import bleach  # pylint: disable=import-error
import re


def index(request):
    return render(request, "encyclopedia/index.html",
                  {"entries": util.list_entries()})


def entry(request, TITLE):
    ent = util.get_entry(TITLE)
    if ent is not None:
        parsed_md = util.mdparse(ent)
        return render(request, "encyclopedia/entry.html", {
            "heading": TITLE,
            "body": parsed_md
        })
    else:
        return render(
            request, "encyclopedia/error.html", {
                "titlebar": f"Wiki of {TITLE}",
                "error": f"Wiki for '{TITLE}' not found."
            })


def search(request):
    if request.method == 'GET' and request.GET['q']:
        q = request.GET['q']
        entries = util.search_entries(q)
        if len(entries) == 1:
            return HttpResponseRedirect(reverse("entry", args={entries[0]}))
        elif len(entries) == 0:
            return render(
                request, "encyclopedia/error.html", {
                    "titlebar":
                    f"Search results for '{q}'",
                    "error":
                    f"We tried but couldn't find any results '{q}' in our database."
                })
        else:
            return render(request, "encyclopedia/results.html", {
                "query": q,
                "entries": entries
            })
    else:
        return HttpResponseRedirect(reverse('index'))


def create(request):
    if request.method == "POST":
        title = bleach.clean(request.POST['title'])  # bleach to prevent xss
        content = bleach.clean(
            request.POST['content'])  # bleach to prevent xss
        print(str(len(title)) + ' ' + str(len(content)))
        if len(content) == 0:
            error = "Content cannot be empty."
            return render(request, 'encyclopedia/create.html', {
                "title": title,
                "content": content,
                "error": error
            })
        elif len(title) == 0:
            error = "Title cannot be empty."
            return render(request, 'encyclopedia/create.html', {
                "title": title,
                "content": content,
                "error": error
            })
        elif util.get_entry(title):
            error = "Wiki for " + title + " already exists."
            return render(request, 'encyclopedia/create.html', {
                "title": title,
                "content": content,
                "error": error
            })
        content = "# " + title + "\r\n" + content
        util.save_entry(title, content)
        return HttpResponseRedirect(reverse('entry', args={title}))
    else:
        return render(request, "encyclopedia/create.html", {
            "heading": "Create Wiki",
            "content": ""
        })


def edit(request, TITLE):
    if request.method == "POST":
        content = bleach.clean(
            request.POST['content'])  # bleach to prevent xss
        if len(content) == 0:
            error = "Content cannot be empty."
            return render(request, 'encyclopedia/edit.html', {
                "title": TITLE,
                "content": content,
                "error": error
            })
        content = "# " + TITLE + "\r\n" + content.strip()
        util.save_entry(TITLE, content)
        return HttpResponseRedirect(reverse('entry', args={TITLE}))
    else:
        return render(
            request, "encyclopedia/edit.html", {
                "title": TITLE,
                "content": re.sub(r"^# .*", '', util.get_entry(TITLE),
                                  1).strip()
            })


def random(request):
    return HttpResponseRedirect(
        reverse('entry', args={rand.choice(util.list_entries())}))
