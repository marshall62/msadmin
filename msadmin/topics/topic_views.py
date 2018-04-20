from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
import os
from msadminsite.settings import MEDIA_ROOT,TOPIC_INTROS_DIRNAME
from msadmin.qa.util import do_write_file_text

from django.core.files.storage import FileSystemStorage
from msadmin.qa.qauth_model import Topic, ProblemTopicMap

# Shows the main page of the site
@login_required
def main (request):
    topics = Topic.objects.all()
    return render(request, 'msadmin/topics/topics_main.html', {'topics': topics})


@login_required
def create_topic (request):
    return render(request, 'msadmin/topics/topics_edit.html',{})


def writeTopicIntroHTMLFile (intro, htmlText):
    path = os.path.join(MEDIA_ROOT,TOPIC_INTROS_DIRNAME, intro, intro+".html")
    do_write_file_text(path, htmlText)

@login_required
def save_topic (request):
    if request.method == "POST":
        post = request.POST
        id = post['id']
        intro = post['intro']
        desc = post['descr']
        summary = post['summary']
        htmlText = post['htmlText']
        writeTopicIntroHTMLFile(intro,htmlText)
            # the intro is HTML that should be written to the file
            #


    return redirect('topics_edit', topicId=4)

@login_required
def edit_topic (request, topicId):
    t = get_object_or_404(Topic,id=topicId)
    return render(request, 'msadmin/topics/topics_edit.html', {'topic': t})