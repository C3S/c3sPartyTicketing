from pyramid.view import view_config


@view_config(
    renderer='templates/error_page.pt',
    route_name='error_page',
)
def error_page_view(request):

    return {'foo': 'bar'}
