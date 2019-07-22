from conferences.models import Zosia


def get_zosia(request):
    zosia = Zosia.objects.find_active()
    if zosia:
        return {'zosia': zosia}
