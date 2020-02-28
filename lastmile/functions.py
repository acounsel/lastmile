import csv
import datetime

from django.http import StreamingHttpResponse

class Echo:
    """An object that implements just the write method
    of the file-like interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing
        in a buffer."""
        return value

def get_export_response(Model, queryset):
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    field_list = get_field_list(Model)
    rows = get_rows(field_list, queryset)
    response = StreamingHttpResponse((
        writer.writerow(row) for row in rows),
            content_type="text/csv")
    today = datetime.date.today()
    content_disp = 'attatchment;filename="lastmile_%s.csv"' % today
    response['Content-Disposition'] = content_disp
    return response

def get_field_list(Model):
    field_list = []
    for field in Model._meta.get_fields():
        field_list.append(field.name)
    return field_list

def get_rows(field_list, queryset):
    rows = [field_list,]
    for instance in queryset:
        rows.append(get_row(field_list, instance))
    return rows

def get_row(field_list, instance):
    row = []
    for field in field_list:
        try:
            row.append(getattr(instance, field))
        except Exception as error:
            row.append('')
            print(error)
            pass
    return row