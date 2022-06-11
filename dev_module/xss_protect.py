from html_sanitizer import Sanitizer


class xss_protect():
    @staticmethod
    def stop_code_filter(target):
        sanitizer = Sanitizer()
        # target = target.replace('<', '&lt;').replace('>', '&gt;').replace('\r\n', '<br>')
        target = sanitizer.sanitize(target)

        return target