import os

from django.core.files.storage import FileSystemStorage
from msadmin.qa.qauth_model import Problem, Hint
from msadmin.qa.qauth_model import ProblemAnswer,ProblemMediaFile
from msadminsite.settings import MEDIA_ROOT,QUICKAUTH_PROB_DIRNAME

# Will write (or overwrite if exists) a file
def do_write_file (fullPath, file, filename=None):
    os.makedirs(os.path.dirname(fullPath), exist_ok=True)
    with open(fullPath, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

# Writes a file under the MEDIA_ROOT within the given dirName
def write_file (dirName, file, filename=None):
    path = os.path.join(MEDIA_ROOT,dirName, filename if filename else file.name)
    do_write_file(path, file, filename)

# write a file to the problem_XXX dir if its a problem
# and to problem_XXX/hint_YYY if its a hint
def handle_uploaded_file(probId, f, hintId=None):
    if not hintId:
        pmf = ProblemMediaFile.objects.filter(problem_id=probId,filename=f.name)
    else: pmf = ProblemMediaFile.objects.filter(problem_id=probId, hint_id=hintId, filename=f.name)
    # We don't want to create a new row in the ProblemMedia table if the file has already been saved
    if not pmf:
        pmf = ProblemMediaFile(filename=f.name,problem_id=probId,hint_id=hintId)
        pmf.save()
    else:
        pmf = pmf[0]
    # if attempting to upload a file that is already there, it proceeds and overwrites it.
    path = MEDIA_ROOT
    dirName = Problem.getProblemDirName(probId)
    if not hintId:
        fullPath = os.path.join(path,QUICKAUTH_PROB_DIRNAME,dirName,f.name)
    else:
        hintDirName = Hint.getHintDirName(hintId)
        fullPath = os.path.join(path,QUICKAUTH_PROB_DIRNAME,dirName,hintDirName,f.name)
    do_write_file(fullPath,f)

    return pmf

def deleteMediaDir (probId, hintId):
    fs = FileSystemStorage()
    location = fs.location
    base_url = fs.base_url
    file_permissions_mode = fs.file_permissions_mode
    directory_permissions_mode = fs.directory_permissions_mode
    probLoc = os.path.join(location, QUICKAUTH_PROB_DIRNAME, Problem.getProblemDirName(probId))
    hintLoc = os.path.join(location, QUICKAUTH_PROB_DIRNAME, Problem.getProblemDirName(probId),Hint.getHintDirName(hintId))
    # Create a new FileSystemStorage object based on the default one.  It uses the new directory for the problem.
    fs = FileSystemStorage(location=probLoc ,file_permissions_mode=file_permissions_mode,directory_permissions_mode=directory_permissions_mode)
    fs2 = FileSystemStorage(location=hintLoc ,file_permissions_mode=file_permissions_mode,directory_permissions_mode=directory_permissions_mode)
    stuff = fs.listdir(Hint.getHintDirName(hintId)) # returns a 2-tuple of lists ([dirs], [files])
    files = stuff[1]
    #deletes all the files in the hint dir
    for f in files:
        fs2.delete(f)
    os.rmdir(hintLoc)


# delete the media file from the problem_XXX dir
# if its a hint media, delete from the problem_XXX/hint_YYY dir
def deleteMediaFile (probId, fileName, hintId=None):
    # Get the default FileSystemStorage class based on MEDIA_ROOT settings in settings.py
    fs = FileSystemStorage()
    location = fs.location
    base_url = fs.base_url
    file_permissions_mode = fs.file_permissions_mode
    directory_permissions_mode = fs.directory_permissions_mode
    if not hintId:
        newloc = os.path.join(location, QUICKAUTH_PROB_DIRNAME, Problem.getProblemDirName(probId))
    else:
        newloc = os.path.join(location, QUICKAUTH_PROB_DIRNAME, Problem.getProblemDirName(probId), Hint.getHintDirName(hintId))
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