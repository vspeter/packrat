from datetime import datetime
import json

from django.http import Http404
from django.utils.timezone import utc
from django.views.decorators.csrf import csrf_exempt

from packrat.Repos.models import Repo, Package, PackageFile, Mirror

@csrf_exempt
def sync(request):
    try:
        function = request.GET['function']
        data = request.POST['data']
        name = request.POST['name']
        psk = request.POST['psk']
    except KeyError:
        raise Http404

    try:
        data = json.loads(data)
    except ValueError:
        raise Http404

    try:
        mirror = Mirror.objects.get(name=name)
    except Mirror.DoesNotExit:
        raise Http404

    if psk != mirror.psk:
        raise Http404

    result = {}

    if function == 'sync.start':
        mirror.last_sync_start = datetime.utcnow().replace(tzinfo=utc)
        result = 'Ok'

    elif function == 'sync.complete':
        mirror.last_sync_complete = datetime.utcnow().replace(tzinfo=utc)
        result = 'Ok'

    elif function == 'mirror.info':
        result = {
            'description': mirror.description,
            'name': mirror.name,
            'last_sync_start': mirror.last_sync_start,
            'last_sync_complete': mirror.last_sync_complete
        }
        if result['last_sync_start']:
            result['last_sync_start'] = result[
                'last_sync_start'].strftime('%Y-%m-%d %H:%M:%S')
        if result['last_sync_complete']:
            result['last_sync_complete'] = result[
                'last_sync_complete'].strftime('%Y-%m-%d %H:%M:%S')

    elif function == 'repo.list':
        result = [i.pk for i in mirror.repo_list.all()]

    elif function == 'repo.get':
        try:
            id = data['id']
        except KeyError:
            raise Http404

        repo = Repo.objects.get(pk=id)
        result = {
            'description': repo.description,
            'manager_type': repo.manager_type,
            'release_type': repo.release_type,
            'distro': repo.distro,
            'version': repo.version,
            'created': repo.created.strftime('%Y-%m-%d %H:%M:%S'),
            'updated': repo.updated.strftime('%Y-%m-%d %H:%M:%S'),
            'package_list': [i.pk for i in repo.package_queryset.all()]
        }

    elif function == 'package.get':
        try:
            id = data['id']
            release = data['release']
            manager_type = data['manager_type']
        except KeyError:
            raise Http404

        package = Package.objects.get(pk=id)

        # TODO: this is redundant with package_list in models, find a way to
        # consolidate them
        if manager_type == 'deb':
            qs = package.packagefile_set.filter(packagefile__type='deb')

        elif manager_type in ('yum', 'zypper'):
            qs = package.packagefile_set.filter(packagefile__type='rpm')

        else:
            qs = package.packagefile_set.none()

        if release == 'ci':
            qs = qs.filter(
                ci_at__isnull=False,
                dev_at__isnull=True,
                prod_at__isnull=True).distinct()

        elif release == 'dev':
            qs = qs.filter(
                dev_at__isnull=False,
                prod_at__isnull=True).distinct()

        elif release == 'prod':
            qs = qs.filter(prod_at__isnull=False).distinct()

        result = {
            'name': package.name,
            'created': package.created.strftime('%Y-%m-%d %H:%M:%S'),
            'updated': package.updated.strftime('%Y-%m-%d %H:%M:%S'),
            'file_list': [i.pk for i in qs]
        }

    elif function == 'package-file.get':
        try:
            id = data['id']
        except KeyError:
            raise Http404

        file = PackageFile.objects.get(pk=id)
        result = {
            'version': file.version,
            'release': file.release,
            'type': file.type,
            'arch': file.arch,
            'file': file.file.name[2:],  # remove the ./
            'file_url': file.file.url,
            'created': file.created.strftime('%Y-%m-%d %H:%M:%S'),
            'updated': file.updated.strftime('%Y-%m-%d %H:%M:%S')
        }

    return HttpResponse(json.dumps(result), content_type='application/json')
