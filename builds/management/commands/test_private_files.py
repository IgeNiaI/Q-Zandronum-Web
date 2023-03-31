from http.client import HTTPException
from urllib import request as url_request
from urllib.error import HTTPError

from django.core.management.base import BaseCommand

from builds.models import Build, QCDEBuild


class Command(BaseCommand):
    help = 'verifies if files accessible through sendfile'

    def out(self, *args):
        return self.stdout.write(*args)

    def test_url(self, url, expected_success=True):

        success_flag = False
        response = None

        try:
            req = url_request.Request(url, headers=self.headers)
            response = url_request.urlopen(req)
        except HTTPException as exc:
            self.out(self.style.ERROR(f"HTTPException: {exc}"))
        except HTTPError as exc:
            if exc.code == 404:
                if expected_success:
                    self.out(self.style.ERROR(f"HttpError: {exc} {exc.code}"))
            else:
                self.out(self.style.ERROR(f"HttpError: {exc} {exc.code}"))
        else:
            if response.status in (200, 206):
                success_flag = True

        if success_flag is expected_success:
            style = self.style.SUCCESS
            msg = " OK "
        else:
            style = self.style.ERROR
            msg = "FAIL"

        self.out(style(f"[{msg}] Status: {response.status if response else None} url: {url}"))
        return success_flag is expected_success

    def add_arguments(self, parser):
        parser.add_argument('domain', type=str)
        parser.add_argument('-H', "--noheaders", action="store_true",
                            help="don't send range header so counters will work")

    def handle(self, *args, **options):
        builds = Build.objects.all()
        domain = options['domain'].strip("/")

        if options['noheaders']:
            self.headers = {}
        else:
            self.headers = {"RANGE": "bytes=1-99"}
        self.out(f"using headers: {self.headers}")

        for build in builds:
            self.out()
            url = domain + build.get_absolute_url()
            media_url = domain + build.file.url

            self.out(f'Will check {build}')
            self.test_url(url)
            self.test_url(media_url, False)

        for build in QCDEBuild.objects.all():
            self.out()
            url = domain + build.get_absolute_url()
            media_url = domain + build.file.url

            self.out(f'Will check {build}')
            self.test_url(url)
            self.test_url(media_url, False)
