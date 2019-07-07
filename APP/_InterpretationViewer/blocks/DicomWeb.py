import requests
import json
import numpy as np

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot


TAG_StudyInstanceUID = '0020000D'
TAG_SeriesInstanceUID = '0020000E'
TAG_SOPInstanceUID = '00080018'
TAG_PixelSpacing = '00280030'
TAG_ImagePosition = '00200032'
TAG_SliceThickness ='00180050'
TAG_SliceLocation = '00201041'
TAG_Rows = '00280010'
TAG_Columns = '00280011'
TAG_RescaleIntercept = '00281052'
TAG_RescaleSlope = '00281053'
TAG_MODALITY = '00080060'


# HOST_URL = "http://dicomcloud.iptime.org:44301"
# HOST_URL = "http://192.168.0.17:44301"
HOST_URL = "http://192.168.200.140:44301"
# HOST_URL = "http://localhost:44301"
QIDORS_PREFIX = 'qidors'
WADORS_PREFIX = 'wadors'
STOWRS_PREFIX = 'stowrs'
HEADERS1 = {"Accept": "application/json"}
HEADERS2 = {"Accept": "multipart/related; type=\"application/octet-stream\""}
# HEADERS2 = {"Accept": "multipart/related; type=\"image/jpeg\""}


# Data1
# STUDY_UID = "1.2.410.200034.0.50551229.0.96050.22743.20111229.41"
# SERIES_UID = "1.2.410.200034.0.50551229.1.96055.227436784.16435555000241"
# Data2
STUDY_UID = "1.3.6.1.4.1.25403.114374082075733.11648.20190114105523.1"
SERIES_UID = "1.3.6.1.4.1.25403.114374082075733.11648.20190114105928.2"


DEFAULT_RESCALE_INTERCEPT = 1024


class cyDicomWeb(object):

    def __init__(self, host_url=HOST_URL, qidors_prefix=QIDORS_PREFIX, wadors_prefix=WADORS_PREFIX, *args, **kwds):
        super().__init__(*args, **kwds)
        self.host_url = host_url
        self.qidors_prefix = qidors_prefix
        self.wadors_prefix = wadors_prefix

    def initialize(self, study_uid=STUDY_UID, series_uid=SERIES_UID):
        self.study_uid = study_uid
        self.series_uid = series_uid
        self.metadata = self.requests_metadata()
        self.instance_uids = [i[TAG_SOPInstanceUID]['Value'][0] for i in self.metadata]
        self.width = self.metadata[0][TAG_Columns]['Value'][0]
        self.height = self.metadata[0][TAG_Rows]['Value'][0]
        self.length = len(self.metadata)
        self.rescale_slope = self.metadata[0][TAG_RescaleSlope]['Value'][0]
        self.rescale_intercept = self.metadata[0][TAG_RescaleIntercept]['Value'][0]
        self.spacing = self.metadata[0][TAG_PixelSpacing]['Value']
        # self.thickness = self.metadata[0][TAG_SliceThickness]['Value'][0]
        self.thickness = abs(self.metadata[0][TAG_ImagePosition]['Value'][2] - self.metadata[1][TAG_ImagePosition]['Value'][2])
        self.origin = self.metadata[0][TAG_ImagePosition]['Value']
        print("width, height :: ", self.width, self.height)
        print("slope, intercept:: ", self.rescale_slope, self.rescale_intercept)
        print("origin :: ", self.origin)
        print("spacing :: ", self.spacing)
        print("thickness :: ", self.thickness)

    def get_origin(self):
        return self.origin

    def get_dimensions(self):
        return self.width, self.height, self.length

    def get_spacing(self):
        return self.spacing

    def get_thickness(self):
        return self.thickness

    def get_rescale_params(self):
        return self.rescale_slope, self.rescale_intercept

    def requests_metadata(self):
        url = "%s/%s/studies/%s/series/%s/metadata" % (self.host_url, self.wadors_prefix, self.study_uid, self.series_uid)
        x = requests.get(url, headers=HEADERS1)
        c = x.status_code
        x = eval(x.text)
        metadata = sorted(x, key=lambda _key: _key[TAG_ImagePosition]['Value'][2])
        # metadata.reverse()
        return metadata

    def requests_buf16(self, instance_uid_info):
        instance_uid = instance_uid_info[0]
        idx = instance_uid_info[1]

        # retrieve instances with WADO RS
        url = "%s/%s/studies/%s/series/%s/instances/%s/frames/1" % (self.host_url, self.wadors_prefix,
                                                                    self.study_uid, self.series_uid, instance_uid)
        x = requests.get(url, headers=HEADERS2)
        c = x.status_code
        v = x.content
        idx_begin = v.find(b"\r\n\r\n")
        idx_begin = idx_begin + 4
        # print("idx_begin :: ", idx_begin)
        idx_end = v.rfind(b"\r\n--DICOM DATA BOUNDARY--")
        # print("idx_end :: ", idx_end)
        buf16 = v[idx_begin:idx_end]
        frame = np.frombuffer(buf16, dtype=np.int16)
        # frame.setflags(write=1)
        new_frame = np.ndarray(frame.shape)
        new_frame[:] = frame[:] * self.rescale_slope + self.rescale_intercept + DEFAULT_RESCALE_INTERCEPT
        return new_frame, idx

    def get_instance_uids(self):
        return self.instance_uids if hasattr(self, 'instance_uids') else None


def requests_buf16(params):
    url, headers, idx, rescale_params = params
    x = requests.get(url, headers=headers)
    c = x.status_code
    v = x.content
    idx_begin = v.find(b"\r\n\r\n")
    idx_begin = idx_begin + 4
    # print("idx_begin :: ", idx_begin)
    idx_end = v.rfind(b"\r\n--DICOM DATA BOUNDARY--")
    # print("idx_end :: ", idx_end)
    buf16 = v[idx_begin:idx_end]
    frame = np.frombuffer(buf16, dtype=np.int16)
    new_frame = np.ndarray(frame.shape)
    new_frame[:] = frame[:] * rescale_params[0] + rescale_params[1] + DEFAULT_RESCALE_INTERCEPT
    return new_frame, idx
