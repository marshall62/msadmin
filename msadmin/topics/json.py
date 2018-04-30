import os
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from msadmin.qa.util import write_file, do_write_file_text, read_file
from msadminsite.settings import MEDIA_ROOT,MEDIA_URL, TOPIC_INTROS_DIRNAME
from msadmin.qa.qauth_model import Topic

# Can save either a file (topicIntroFile) or a piece of HTML text.   If both are given, it will use the file
# If HTML text is given, it will create a file in the topicIntros area of the server and will write the HTML into it
# If a file is given, it is written to the topicIntros area of the server (replacing any file that is there).
# Problems with the HTML editor:
#  Once saved it is now in a file and reloading the page cannot easily show the text that was saved
#  How can we tell the difference between an uploaded file and text saved to a file?
#  Should we allow editing with the editor of both?
#  It seems like we can always read from the file and stick HTML in the editor and then allow edit of it so that save will overwrite the existing file.
#  For now we only handle files.
def save_topic_intro (request, topicId):
    if request.method == "POST":
        t = get_object_or_404(Topic,id=topicId)
        post = request.POST
        if 'topicIntroFile' in request.FILES:
            path = os.path.join(MEDIA_ROOT,TOPIC_INTROS_DIRNAME, t.intro)
            write_file(path,request.FILES['topicIntroFile'], t.intro +".html")
        else:
            htmlText = post['topicIntroHTML']
            if htmlText.strip() != '':
                writeTopicIntroHTMLFile(t.intro,htmlText)
        path = os.path.join(MEDIA_ROOT,TOPIC_INTROS_DIRNAME, t.intro,t.intro +".html")
        html = read_file(path)
        d = {
            'message': "Successfully saved",
            'htmlText': html
        }
        return JsonResponse(d)

def getIntroHTML (topic):
    path = os.path.join(MEDIA_ROOT,TOPIC_INTROS_DIRNAME, topic.intro,topic.intro +".html")
    html = read_file(path)
    if not html:
        return ''
    return html



def writeTopicIntroHTMLFile (intro, htmlText):
    path = os.path.join(MEDIA_ROOT,TOPIC_INTROS_DIRNAME, intro, intro+".html")
    do_write_file_text(path, htmlText)

def save_topic_intro_image_file (request, topicId):
    if request.method == "POST":
        file = request.FILES['file']
        t = get_object_or_404(Topic,id=topicId)
        path = os.path.join(MEDIA_ROOT,TOPIC_INTROS_DIRNAME, t.intro)
        write_file(path,file)
        imgURL = os.path.join(MEDIA_URL,TOPIC_INTROS_DIRNAME,t.intro,file.name)
        return JsonResponse({'url': imgURL })