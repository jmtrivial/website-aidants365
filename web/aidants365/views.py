from django.contrib.auth.decorators import login_required
from django.views.static import serve


@login_required
def protected_serve(request, document_url=None, document_root=None, show_indexes=False):
    path = request.path[len(document_url):]
    return serve(request, path, document_root, show_indexes)
