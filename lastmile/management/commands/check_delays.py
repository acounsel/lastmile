from django.core.management.base import BaseCommand

from lastmile.functions import check_action_dates
from lastmile.models import Action


class Command(BaseCommand):
    help = 'Checks for action items that have passed \
        their expected completion date'

    def handle(self, *args, **options):
        if datetime.datetime.today().weekday() == 0:
            actions = Action.objects.filter(
                status=Action.ACTIVE,
                expected_completion_date__isnull=False
            )
            total, delays = check_action_dates(actions)
            self.stdout.write(
                self.style.SUCCESS(
                    'Found {0} delays from {1} action items' \
                    .format(total, delays)
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS(
                'Waiting for Monday'))
