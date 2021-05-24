import io

import xlsxwriter
from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import HttpResponse
from django.utils.decorators import method_decorator


class CustomLoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CustomLoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class PermissionMixin(object):
    @method_decorator(
        user_passes_test(
            lambda u: u.groups.filter(name='rubedite_team') or u.is_superuser,
            login_url='/',
            redirect_field_name=None
        )
    )
    def dispatch(self, request, *args, **kwargs):
        return super(PermissionMixin, self).dispatch(request, *args, **kwargs)


class XLSResponseMixin(object):
    '''
    XLS response mixin. Receives list of data. Returns HTTP response object.
    '''
    def _generate_xls(self, data):
        '''
        generate xls file from list
        :param data: list of lists
        :return: file object
        '''
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        for row_num, columns in enumerate(data):
            for col_num, cell_data in enumerate(columns):
                worksheet.write(row_num, col_num, cell_data)
        workbook.close()
        output.seek(0)
        return output

    def xls_response(self, data, filename):
        response = HttpResponse(
            self._generate_xls(data),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response
