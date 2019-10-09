from conferences.models import Zosia


def get_zosia(request):
    zosia = Zosia.objects.find_active()
    if zosia is not None:
        return {'zosia': zosia}
