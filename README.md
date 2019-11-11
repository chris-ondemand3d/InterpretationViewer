# **Contents** <br/>

**[Requirements](#requirements)** <br/>
**[Folder Structure](#folder-structure)** <br/>
**[App Structure](#app-structure)** <br/>
**[App Module Structure - DBM](#app-module-structure-dbm)** <br/>
**[App Module Structure - SliceView](#app-module-structure-sliceview)** <br/>
**[App Module Structure - MPR](#app-module-structure-mpr)** <br/>
**[How to run](#how-to-run)** <br/>
<br/>
<br/>

---

<br/>
<br/>



# Requiremtns

python 3.6.0 <br/>
PyQt 5.13 <br/>
cyCafe (Numpy, Boost, VTK, ...) <br/>
QApp (**note.** including in this project) <br/>
requests (HTTP Request) <br/>
psutil (Memory Check) <br/>
<br/>
<br/>
<br/>
<br/>



# Folder Structure

> **InterpretationViewer** <br/>
>> **APP** : App Modules <br/>
>>> **_InterpretationViewer** : Interpretation Viewer App Module <br/>
>>>> **blocks** : Blocks <br/>
>>>> **layout** : Layout <br/>
>>>
>>>> **App.py** : QQuickView for DBM, Slice, MPR <br/>
>>>> **CallbackMessage.py** : CallbackMsg Handler <br/>
>>>> **main.py** : App Entry Point <br/>
>>>> **main.qml** : Initial Main QML <br/>
>>
>> **COMMON** : Common Modules <br/>
>> **cyhub** : Framework for converging VTK and QT <br/>
<br/>
<br/>
<br/>
<br/>



# App Structure
![image](/uploads/34213f8f61369f068c7f9da573dfee5a/image.png) <br/>
<br/>
<br/>
<br/>
<br/>



# App Module Structure - DBM
![image](/uploads/55d9ee1d2b71719155fea366653e0e90/image.png) <br/>
<br/>
<br/>
<br/>
<br/>



# App Module Structure - SliceView
![image](/uploads/8d55a9519c21a77a5898f4d56514a37e/image.png) <br/>
<br/>
<br/>
<br/>
<br/>



# App Module Structure - MPR
![image](/uploads/334f94484e4d3443ad1b1472cbb0d57c/image.png) <br/>
<br/>
<br/>
<br/>
<br/>



# How to run

1. DICOMWeb Server should be running. (**DEMO Server :** https://github.com/DICOMcloud/DICOMcloud) <br/> 

2. It's available to upload through **StowRS**. (**Example :** https://dicomcloud.github.io/docs/dicomcloud/stow/) <br/>

3. HOST URL could be set in **DicomWeb.py 43-line** <br/>
```python
...
HOST_URL = "http://localhost:44301"
...
```
<br/>

4. Execute the **main.py** with python. <br/>

- **DBM / Viewer1 / Viewer2**
![image](/uploads/98b223de0525ccc69f94780ef4391b88/image.png) <br/>
<br/>
<br/>
<br/>


