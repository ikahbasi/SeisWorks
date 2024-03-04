class Result:
    '''
    create: 1402-05-07
    '''
    def __init__(self, eventid, phasetype, reference_catalog,
                 dl_phases,
                 stream, otime):
        self.eventid = eventid
        self.otime = otime
        self.phasetype = phasetype
        self.reference_catalog = reference_catalog
        self.dl_phases = dl_phases
        self.stream = stream