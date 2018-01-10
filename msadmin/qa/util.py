import os

from django.core.files.storage import FileSystemStorage

from msadmin.qa.qauth_model import ProblemAnswer,ProblemMediaFile
from msadminsite.settings import MEDIA_ROOT


def handle_uploaded_file(probId, f):
    pmf = ProblemMediaFile.objects.filter(problem_id=probId,filename=f.name)
    # We don't want to create a new row in the ProblemMedia table if the file has already been saved
    if not pmf:
        pmf = ProblemMediaFile(filename=f.name,problem_id=probId)
        pmf.save()
    else:
        pmf = pmf[0]
    # if attempting to upload a file that is already there, it proceeds and overwrites it.
    path = MEDIA_ROOT
    dirName = getProblemDirName(probId)
    fullPath = os.path.join(path,"html5Probs",dirName,f.name)
    os.makedirs(os.path.dirname(fullPath), exist_ok=True)
    with open(fullPath, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return pmf


def deleteMediaFile (probId, fileName):
    # Get the default FileSystemStorage class based on MEDIA_ROOT settings in settings.py
    fs = FileSystemStorage()
    location = fs.location
    base_url = fs.base_url
    file_permissions_mode = fs.file_permissions_mode
    directory_permissions_mode = fs.directory_permissions_mode
    newloc = os.path.join(location, "html5Probs", getProblemDirName(probId))
    # Create a new FileSystemStorage object based on the default one.  It uses the new directory for the problem.
    fs2 = FileSystemStorage(location=newloc ,file_permissions_mode=file_permissions_mode,directory_permissions_mode=directory_permissions_mode)
    if fs2.exists(fileName):
        fs2.delete(fileName)


def deleteProblemAnswers (problem):
    answers = problem.getAnswers()
    for a in answers:
        a.delete()


def saveProblemMultiChoices (problem, correctAnswer, choices):
    i=0
    for c,l in zip(choices,['a','b','c','d','e']):
        pa = ProblemAnswer(choiceLetter=l,val=c,order=i,problem=problem)
        pa.save()
        i += 1


def saveProblemShortAnswers (problem, correctAnswer, answers):
    i=0
    for a in answers:
        pa = ProblemAnswer(val=a,order=i,problem=problem)
        pa.save()
        i += 1


def getProblemDirName (probId):
    return "problem_" + str(probId)