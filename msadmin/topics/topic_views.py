from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
import os
from msadminsite.settings import MEDIA_ROOT,TOPIC_INTROS_DIRNAME
from msadmin.qa.util import do_write_file_text

from django.core.files.storage import FileSystemStorage
from msadmin.qa.qauth_model import Topic, ProblemTopicMap
from .json import getIntroHTML

# Shows the main page of the site
@login_required
def main (request):
    topics = Topic.objects.all()
    return render(request, 'msadmin/topics/topics_main.html', {'topics': topics})


@login_required
def create_topic (request):
    return render(request, 'msadmin/topics/topics_edit.html',{})




@login_required
def save_topic (request):
    if request.method == "POST":
        post = request.POST
        id = post['id']
        intro = post['intro']
        desc = post['descr']
        summary = post['summary']
        if id:
            t = get_object_or_404(Topic,id=id)
            t.intro = intro
            t.description = desc
            t.summary = summary
            t.save()
        else:
            t = Topic(intro=intro,description=desc,summary=summary)
            t.save()

            # the intro is HTML that should be written to the file
            #
    return redirect('topics_edit', topicId=t.id)



@login_required
def edit_topic (request, topicId):
    t = get_object_or_404(Topic,id=topicId)
    probs = t.getProblems()
    html = getIntroHTML(t)
    return render(request, 'msadmin/topics/topics_edit.html', {'topic': t, 'problems': probs, 'introHTML': html})