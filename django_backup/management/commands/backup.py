import os
import zipfile
from datetime import datetime

from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.utils.timezone import activate

from django_backup.dropbox import DropboxCommands as DropboxHelper
from django_backup.main import BackupHelper


class Command(BaseCommand):
    help = 'Save/load django_backup from/to cloud storage'

    def __init__(self):
        super(Command, self).__init__()
        self.dropbox_token = getattr(settings, 'DROPBOX_ACCESS_TOKEN', None)

    def add_arguments(self, parser):
        parser.add_argument('-m', action='store_true', dest='include-media', help='Include media folder '
                                                                                  'to django_backup')
        parser.add_argument('-s', action='store_true', dest='save', help='Save django_backup')
        parser.add_argument('-l', action='store_true', dest='load', help='Load django_backup')
        parser.add_argument('-r', action='store_true', dest='replace', help='Delete old backups and replace '
                                                                            'them with a new')

    def handle(self, *args, **options):
        action = 'save' if options['save'] else 'load' if options['load'] else None
        include_media = options.get('include-media', None)
        replace = options.get('replace', None)
        self._validate(include_media, action)

        try:
            dropbox = DropboxHelper(access_token=settings.DROPBOX_ACCESS_TOKEN)
            backup_helper = BackupHelper(media_root=settings.MEDIA_ROOT if include_media else None)

            if action == 'save':
                self._save(backup_helper, dropbox, replace)
            else:
                self._load(backup_helper, dropbox)
        except Exception as e:
            print(e)
            self.stdout.write(self.style.ERROR(e))

    def _validate(self, include_media, action=None):
        if not self.dropbox_token:
            raise CommandError('DROPBOX_ACCESS_TOKEN is not set in settings')

        if not hasattr(settings, 'DATABASES'):
            raise CommandError('Please provide database settings')

        if action is None:
            raise CommandError('Please provide right action: --save or --load')

        if include_media and not hasattr(settings, 'MEDIA_ROOT'):
            raise CommandError('MEDIA_ROOT is not provided')

        elif not os.path.exists(getattr(settings, 'MEDIA_ROOT')):
            raise CommandError(
                '%s directory configured as MEDIA_ROOT does not exist' % (getattr(settings, 'MEDIA_ROOT')))

    @staticmethod
    def _save(backup_helper, dropbox, replace):
        activate(settings.TIME_ZONE)
        result_archive_name = 'django_backup-%s' % datetime.now().strftime('%Y-%m-%d_%H:%M')
        filename, compressed_file_path = backup_helper.backup_and_compress(result_archive_name)

        if replace:
            dropbox.delete_all_files()

        dropbox.upload(filename, compressed_file_path)

        if os.path.exists(compressed_file_path):
            os.remove(compressed_file_path)

    @staticmethod
    def _load(backup_helper, dropbox):
        working_dir = os.getcwd()
        path_to_file, hash = dropbox.download_last_backup(working_dir)
        extract_dir_path = '%s/%s' % (working_dir, hash)

        with zipfile.ZipFile(path_to_file, 'r') as zip_file:
            zip_file.extractall(extract_dir_path)

        os.remove(path_to_file)
        backup_helper.load_backup(extract_dir_path)
