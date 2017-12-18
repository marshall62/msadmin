from django.http import HttpResponse

# Shows the main page of the site
def main (request):
    return HttpResponse("This is the test authoring system")