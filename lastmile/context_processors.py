from lastmile.models import Action, Actor, Commitment


def base_data_processor(request):
    context = {
        'Action': Action._meta,
        'Actor': Actor._meta,
        'Commitment': Commitment._meta,
    }
    return context