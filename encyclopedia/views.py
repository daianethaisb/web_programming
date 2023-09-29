from django.shortcuts import render
import random
import markdown2
from django.contrib import messages

from . import util

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def page(request, title):
    entryPage = util.get_entry(title)

    if entryPage is None:
         return render(request, "encyclopedia/errorPage.html", {
             "entryTitle": title
         })
    else:
        return render(request, "encyclopedia/page.html", {
            "entry": markdown2.markdown(util.get_entry(title)),
            "title": title
        })

def search(request):
    entries = util.list_entries()
    searchKey = request.GET.get("q")
    sub_list = []

    for entry in entries:
        if searchKey.lower() == entry.lower():
            return render(request, "encyclopedia/page.html", {
                "entry": markdown2.markdown(util.get_entry(searchKey)),
                "title": searchKey
            })
        elif searchKey.lower() in entry.lower():
            sub_list.append(entry)        

    if len(sub_list) > 0:
        return render(request, "encyclopedia/index.html",{
                "title":searchKey,
                "entries":sub_list
            })        
    else:
        messages.error(request, "No results found")
        return render(request, "encyclopedia/index.html")
            
def createPage(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        searchEntry = util.get_entry(title)

        if searchEntry != None:
            messages.error(request, "This entry already exists")
            return render(request, "encyclopedia/createPage.html", {
                "title": title,
                "entries": util.list_entries()
            })
             
        else:
            util.save_entry(title, content)
            return render(request, "encyclopedia/page.html", {
                "entry": markdown2.markdown(util.get_entry(title)),
                "title": title
        })
    else:
        title = ""
        content = ""
        return render(request, "encyclopedia/createPage.html", {
            "entries": util.list_entries()
        })
    
def editPage(request, title):
    content = util.get_entry(title)

    if request.method == 'POST':
        content = request.POST.get('edit')
        util.save_entry(title, content)
        
        return render(request, "encyclopedia/page.html", {
            "entry": markdown2.markdown(util.get_entry(title)),
            "title": title
        })
    else :
        return render(request, "encyclopedia/editPage.html", {
            "entry": title,
            "content": content
        })
 
def randomPage(request):
    return render(request, "encyclopedia/randomPage.html", {
        "entries":  random.choice(util.list_entries())
    })
     