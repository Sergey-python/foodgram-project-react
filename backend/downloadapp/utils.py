import mimetypes

from django.conf import settings
from django.http.response import HttpResponse


class DownloadFile:
    """
    Класс, предастовляющий интерфесы для работы с файлами для скачивания.
    """

    def __init__(self, file_name: str, content: dict):
        self.file_name = file_name
        self.content = content

    def get_file_path(self) -> str:
        return settings.DOWNLOADFILES_DIR + "/" + self.file_name

    def make_txt_file_to_dowload(self) -> str:
        file_path = self.get_file_path()
        with open(file_path, "w") as file:
            for line in self.content:
                value_list = map(str, line.values())
                file.write(" - ".join(value_list) + "\n")
        return file_path

    def download_file(self) -> HttpResponse:
        file_path = self.make_txt_file_to_dowload()
        file = open(file_path, "r")
        mime_type, _ = mimetypes.guess_type(file_path)
        response = HttpResponse(file, content_type=mime_type)
        response[
            "Content-Disposition"
        ] = f"attachment; filename={self.file_name}"
        return response
