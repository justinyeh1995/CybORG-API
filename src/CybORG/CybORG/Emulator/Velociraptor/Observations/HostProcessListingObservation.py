from CybORG.Shared import Observation


class HostProcessListingObservation(Observation):

    def __init__(self, hostname_process_list_dict=None, success:bool=None):

        super().__init__(success=success)

        if hostname_process_list_dict is None:
            hostname_process_list_dict = {}

        self.hostname_process_list_dict = hostname_process_list_dict
