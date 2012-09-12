from Tank.Core import AbstractPlugin
from Tank.Plugins.Aggregator import AggregatorPlugin
from Tank.Utils import CommonUtils
import logging
import subprocess
import tempfile


class ApacheBenchmarkPlugin(AbstractPlugin):

    SECTION = 'ab'
    
    def __init__(self, core):
        self.log = logging.getLogger(__name__)
        self.core = core
        self.end = None
        self.out_file = None
        self.process = None

    @staticmethod
    def get_key():
        return __file__;
    
    def configure(self):
        self.options = self.core.get_option(self.SECTION, "options", '')
        self.url = self.core.get_option(self.SECTION, "url", 'http://localhost/')
        self.requests = self.core.get_option(self.SECTION, "requests", '100')
        self.concurrency = self.core.get_option(self.SECTION, "concurrency", '1')
        self.out_file = tempfile.mkstemp('.log', 'ab_')[1]
        self.core.add_artifact_file(self.out_file)

    def prepare_test(self):
        aggregator = None
        try:
            aggregator = self.core.get_plugin_of_type(AggregatorPlugin)
        except Exception, ex:
            self.log.warning("No aggregator found: %s", ex)

        if aggregator:
            aggregator.set_source_files(self.out_file, None)
            
    def start_test(self):
        args = ['ab', '-r', '-g', self.out_file, '-n', self.requests, '-c', self.concurrency, self.url]
        self.log.debug("Starting ab with arguments: %s", args)
        self.process = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
           
    def is_test_finished(self):
        rc = self.process.poll()
        if rc != None:
            self.log.debug("%s exit code: %s", self.SECTION, rc)
            return rc
        else:
            return -1

        if self.process:
            CommonUtils.log_stdout_stderr(self.log, self.process.stdout, self.process.stderr, self.SECTION)

            
    def end_test(self, rc):
        if self.process and self.process.poll() == None:
            self.log.warn("Terminating ab process with PID %s", self.process.pid)
            self.process.terminate()
        else:
            self.log.debug("Seems ab finished OK")

        if self.process:
            CommonUtils.log_stdout_stderr(self.log, self.process.stdout, self.process.stderr, self.SECTION)
        return rc
            

 
