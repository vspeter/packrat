from datetime import datetime
import json

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.utils.timezone import utc
from django.views.decorators.csrf import csrf_exempt

from packrat.Repos.forms import PackageFileForm
from packrat.Repos.models import Repo, Package, PackageFile, Mirror


def index(request):
    repo_list = Repo.objects.all()
    mirror_list = Mirror.objects.all()
    package_list = Package.objects.all()

    return render(
        request, 'Repos/index.html',
        {
            'package_list': package_list,
            'repo_list': repo_list,
            'mirror_list': mirror_list
        }
    )


def repo(request, repo_id):
    repo = get_object_or_404(Repo, pk=repo_id)
    package_list = repo.package_list.all()

    return render(
        request, 'Repos/repo.html',
        {
            'repo': repo,
            'package_list': package_list
        }
    )


def mirror(request, mirror_id):
    mirror = get_object_or_404(Mirror, pk=mirror_id)
    repo_list = mirror.repo_list.all()

    return render(
        request, 'Repos/mirror.html',
        {
            'mirror': mirror,
            'repo_list': repo_list
        }
    )


def package(request, package_id):
    package = get_object_or_404(Package, pk=package_id)
    file_list = package.packagefile_set.all()

    return render(
        request, 'Repos/package.html',
        {
            'package': package,
            'file_list': file_list
        }
    )


def packagefile(request, packagefile_id):
    file = get_object_or_404(PackageFile, pk=packagefile_id)

    return render(
        request, 'Repos/packagefile.html',
        {
            'file': file
        }
    )


def packagefile_add(request):
    if request.method == u'POST':
        form = PackageFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save()

            return HttpResponseRedirect(
                reverse('repos:package', args=(file.package.pk,)))

    else:
        form = PackageFileForm()

    return render(
        request, 'Repos/packagefile_add.html',
        {
            'form': form
        }
    )


def packagefile_promote(request, packagefile_id):
    file = get_object_or_404(PackageFile, pk=packagefile_id)
    if file.release == 'new':
        file.ci_at = datetime.utcnow().replace(tzinfo=utc)
    elif file.release == 'ci':
        file.dev_at = datetime.utcnow().replace(tzinfo=utc)
    elif file.release == 'dev':
        file.stage_at = datetime.utcnow().replace(tzinfo=utc)
    elif file.release == 'stage':
        file.prod_at = datetime.utcnow().replace(tzinfo=utc)
    file.save()

    return HttpResponseRedirect(reverse('repos:packagefile', args=(file.pk,)))


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
            'package_list': [i.pk for i in repo.package_list.all()]
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
