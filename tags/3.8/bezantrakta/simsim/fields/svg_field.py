import sys
from io import BytesIO
from PIL import Image
import xml.etree.cElementTree as et

from django.core.exceptions import ValidationError
from django.forms import FileField
from django.utils import six


class SVGField(FileField):

    def to_python(self, data):
        """
        Кастомное поле для загрузки и проверки SVG-изображений.
        """
        test_file = super(FileField, self).to_python(data)
        if test_file is None:
            return None

        # Получение файлового объектав для Pillow
        if hasattr(data, 'temporary_file_path'):
            ifile = data.temporary_file_path()
        else:
            ifile = (
                BytesIO(data.read()) if
                hasattr(data, 'read') else
                BytesIO(data['content'])
            )

        try:
            # load() could spot a truncated JPEG, but it loads the entire
            # image in memory, which is a DoS vector. See #3848 and #18520.
            image = Image.open(ifile)
            # verify() must be called immediately after the constructor.
            image.verify()

            # Annotating so subclasses can reuse it for their own validation
            test_file.image = image
            test_file.content_type = Image.MIME[image.format]
        except Exception:
            # add a workaround to handle SVG images
            if not self.is_svg(ifile):
                six.reraise(ValidationError, ValidationError(
                    self.error_messages['invalid_image'],
                    code='invalid_image',
                ), sys.exc_info()[2])
        if hasattr(test_file, 'seek') and callable(test_file.seek):
            test_file.seek(0)
        return test_file

    def is_svg(self, f):
        """
        Проверка, является ли загружаемый файл SVG-изображением.
        """
        f.seek(0)
        tag = None
        try:
            for event, el in et.iterparse(f, ('start',)):
                tag = el.tag
                break
        except et.ParseError:
            pass
        return tag == '{http://www.w3.org/2000/svg}svg'
