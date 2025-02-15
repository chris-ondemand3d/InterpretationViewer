import requests
import json
import numpy as np

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, pyqtProperty


TAG_InstanceNumber = '00200013'
TAG_PatientName = '00100010'
TAG_PatientID = '00100020'
TAG_PatientSex = '00100040'
TAG_PatientAge = '00101010'
TAG_StudyInstanceUID = '0020000D'
TAG_StudyID = '00200010'
TAG_StudyDate = '00080020'
TAG_StudyTime = '00080030'
TAG_StudyDescription = '00081030'
TAG_SeriesInstanceUID = '0020000E'
TAG_SeriesNumber = '00200011'
TAG_SeriesDate = '00080021'
TAG_SeriesTime = '00080031'
TAG_SeriesDescription = '0008103E'
TAG_SOPInstanceUID = '00080018'
TAG_AccessionNumber = '00080050'
TAG_PixelSpacing = '00280030'
TAG_ImagePosition = '00200032'
TAG_ImageOrientation = '00200037'
TAG_SliceThickness ='00180050'
TAG_SliceLocation = '00201041'
TAG_Rows = '00280010'
TAG_Columns = '00280011'
TAG_RescaleIntercept = '00281052'
TAG_RescaleSlope = '00281053'
TAG_Modality = '00080060'
TAG_BodyPartExamined = '00180015'
TAG_NumberofStudyRelatedInstances = '00201208'
TAG_NumberofSeriesRelatedInstances = '00201209'
TAG_BitsAllocated = '00280100'
TAG_WindowCenter = '00281050'
TAG_WindowWidth = '00281051'

# home
HOST_URL = "http://localhost:44301"


QIDORS_PREFIX = 'qidors'
WADORS_PREFIX = 'wadors'
STOWRS_PREFIX = 'stowrs'
HEADERS1 = {"Accept": "application/json"}
HEADERS2 = {"Accept": "multipart/related; type=\"application/octet-stream\""}
HEADERS3 = {"Accept": "multipart/related; type=\"image/jpeg\""}


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

    def reset(self):
        if hasattr(self, '_stop'):
            del self._stop
        if hasattr(self, 'study_uid'):
            del self.study_uid
        if hasattr(self, 'series_uid'):
            del self.series_uid
        if hasattr(self, 'metadata'):
            del self.metadata
        if hasattr(self, 'scout_img_data'):
            del self.scout_img_data
        if hasattr(self, 'instance_uids'):
            self.instance_uids.clear()
            del self.instance_uids
        if hasattr(self, 'width'):
            del self.width
        if hasattr(self, 'height'):
            del self.height
        if hasattr(self, 'length'):
            del self.length
        if hasattr(self, 'rescale_slope'):
            del self.rescale_slope
        if hasattr(self, 'rescale_intercept'):
            del self.rescale_intercept
        if hasattr(self, 'spacing'):
            self.spacing.clear()
            del self.spacing
        if hasattr(self, 'thickness'):
            del self.thickness
        if hasattr(self, 'origin'):
            del self.origin
        if hasattr(self, 'patient_pos_ori'):
            self.patient_pos_ori.clear()
            del self.patient_pos_ori

    @pyqtProperty(bool)
    def stop(self):
        if hasattr(self, '_stop'):
            return self._stop
        return False

    @stop.setter
    def stop(self, stop):
        self._stop = stop

    def query_studies(self, conditions=None):
        return self.requests_studies(conditions)

    def query_series(self, study_uid):
        return self.requests_series(study_uid)

    def query_thumbnail_img(self, study_uid, series_uid, num):

        def _get_img_buf(_instance):
            if _instance is None:
                return None
            _thumbnail_uid = instance[0][TAG_SOPInstanceUID]['Value'][0]
            _thumbnail_bits = instance[0][TAG_BitsAllocated]['Value'][0]
            url = "%s/%s/studies/%s/series/%s/instances/%s/frames/1" \
                  % (self.host_url, self.wadors_prefix,
                     study_uid, series_uid, _thumbnail_uid)
            x = requests.get(url, headers=HEADERS3)
            if x.status_code != 200:
                return None
            v = x.content
            idx_begin = v.find(b"\r\n\r\n")
            idx_begin = idx_begin + 4
            idx_end = v.rfind(b"\r\n--DICOM DATA BOUNDARY--")
            return v[idx_begin:idx_end]

        instance = self.requests_instances(study_uid, series_uid, {'BitsAllocated':8})
        if len(instance) != 0:
            return _get_img_buf(instance)
        instance = self.requests_instances(study_uid, series_uid, {'InstanceNumber':num})
        if len(instance) != 0:
            return _get_img_buf(instance)

        # TODO else

        return None

    def query_metadata(self, study_uid=STUDY_UID, series_uid=SERIES_UID):
        self.reset()
        self.study_uid = study_uid
        self.series_uid = series_uid
        self.metadata = self.requests_metadata()
        if self.metadata is None:
            return False

        self.scout_img_data = None

        # TODO have to check modality and bits allocated
        for i in self.metadata:
            _modality = i[TAG_Modality]['Value'][0]
            if not(_modality is 'CT' or _modality is 'MR' or _modality is 'PX'):
                self.metadata.remove(i)
                continue
            if i[TAG_BitsAllocated]['Value'][0] != 16:
                self.scout_img_data = i
                self.metadata.remove(i)

        self.instance_uids = [i[TAG_SOPInstanceUID]['Value'][0] for i in self.metadata]
        self.bits = self.metadata[0][TAG_BitsAllocated]['Value'][0]
        self.width = np.max([i[TAG_Columns]['Value'][0] for i in self.metadata])
        self.height = np.max([i[TAG_Rows]['Value'][0] for i in self.metadata])
        self.length = len(self.metadata)
        self.rescale_slope = self.metadata[0][TAG_RescaleSlope]['Value'][0]
        self.rescale_intercept = self.metadata[0][TAG_RescaleIntercept]['Value'][0]
        self.spacing = self.metadata[0][TAG_PixelSpacing]['Value']
        # self.thickness = self.metadata[0][TAG_SliceThickness]['Value'][0]
        self.thickness = abs(self.metadata[0][TAG_ImagePosition]['Value'][2] - self.metadata[1][TAG_ImagePosition]['Value'][2]) if len(self.metadata) > 1 else 1
        self.origin = [0, 0, 0] # NOTE do not assign  the img position of dcm tag!!
        self.window_center = self.metadata[0][TAG_WindowCenter]['Value'][0]
        self.window_width = self.metadata[0][TAG_WindowWidth]['Value'][0]

        # orientation
        self.patient_pos_ori = []
        if len(self.metadata) > 1:
            for m in self.metadata:
                _pos = m[TAG_ImagePosition]['Value']
                _ori = m[TAG_ImageOrientation]['Value']
                self.patient_pos_ori.append([_pos, _ori])

        # debug check
        print("width, height :: ", self.width, self.height)
        print("slope, intercept:: ", self.rescale_slope, self.rescale_intercept)
        print("origin :: ", self.origin)
        print("spacing :: ", self.spacing)
        print("thickness :: ", self.thickness)
        print("window center :: ", self.window_center)
        print("window width :: ", self.window_width)

        return True

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

    def get_wwl(self):
        return self.window_width, self.window_center

    def requests_studies(self, conditions=None):
        search = ""
        if conditions:
            _cond = "?"
            for k, v in conditions.items():
                _cond += "%s=%s&"%(k, v)
            search = _cond[:-1]

        url = "%s/%s/studies%s" % (self.host_url, self.qidors_prefix, search)
        x = requests.get(url, headers=HEADERS1)
        if x.status_code != 200:
            return None
        x = eval(x.text)
        return x

    def requests_series(self, study_uid):
        url = "%s/%s/series?StudyInstanceUID=%s" % (self.host_url, self.qidors_prefix, study_uid)
        x = requests.get(url, headers=HEADERS1)
        if x.status_code != 200:
            return None
        x = eval(x.text)
        return x

    def requests_instances(self, study_uid, series_uid, conditions=None):
        search = ""
        if conditions:
            _cond = "&"
            for k, v in conditions.items():
                _cond += "%s=%s&" % (k, v)
            search = _cond[:-1]
        url = "%s/%s/instances?StudyInstanceUID=%s&SeriesInstanceUID=%s%s" % (self.host_url, self.qidors_prefix, study_uid, series_uid, search)
        x = requests.get(url, headers=HEADERS1)
        if x.status_code != 200:
            return None
        x = eval(x.text)
        return x

    def requests_metadata(self):
        url = "%s/%s/studies/%s/series/%s/metadata" % (self.host_url, self.wadors_prefix, self.study_uid, self.series_uid)
        x = requests.get(url, headers=HEADERS1)
        if x.status_code != 200:
            return None
        x = eval(x.text)
        metadata = sorted(x, key=lambda _key: _key[TAG_InstanceNumber]['Value'])
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
        del buf16, frame
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
    del buf16, frame, v, c, x
    return new_frame, idx


def requests_buf(params):
    url, headers, idx, bits, rescale_params = params
    x = requests.get(url, headers=headers)
    c = x.status_code
    v = x.content
    idx_begin = v.find(b"\r\n\r\n")
    idx_begin = idx_begin + 4
    # print("idx_begin :: ", idx_begin)
    idx_end = v.rfind(b"\r\n--DICOM DATA BOUNDARY--")
    # print("idx_end :: ", idx_end)
    buf = v[idx_begin:idx_end]

    if bits == 8:
        frame = np.frombuffer(buf, dtype=np.int8)
        new_frame = np.ndarray(frame.shape)
        new_frame[:] = frame[:]
    elif bits == 16:
        frame = np.frombuffer(buf, dtype=np.int16)
        new_frame = np.ndarray(frame.shape)
        new_frame[:] = frame[:] * rescale_params[0] + rescale_params[1] + DEFAULT_RESCALE_INTERCEPT
    else:
        new_frame = frame = None

    del buf, frame, v, c, x
    return new_frame, idx
