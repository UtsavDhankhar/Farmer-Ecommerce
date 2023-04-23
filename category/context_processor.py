from .models import Category


def dropdown_links(request):

    categroy_link = Category.objects.all()
    return {'links' : categroy_link}