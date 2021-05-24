__author__ = 'tracker_maker'
import os


class PHPSniffer:
    def __init__(self):
        pass

    @staticmethod
    def sniff(filename):
        sniffer_output = os.popen('phpcs --standard=Zend ' + filename)
        report = []
        i = 0
        for line in sniffer_output:
            i += 1
            if i < 5:
                continue
            if not PHPSniffer.ignore(line):
                report.append(PHPSniffer.parse_line(line))
        return report

    @staticmethod
    def parse_line(line):
        line = line.split('|')
        return {
            'line': line[0],
            'type': line[1],
            'comment': line[2]
        }

    @staticmethod
    def ignore(line):
        if line.find('Short PHP opening tag') > 0:
            return True
        if line.find('tabs are not allowed') > 0:
            return True
        if line.count('|') < 2:
            return True
        return False

