import QtQuick 2.0
import QtQuick.Layouts 1.3
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtGraphicalEffects 1.0
import cyhub 1.0

import "../style"


Item {
  id: menu_models

  function getCommonModel(){
    return items_common;
  }

  function getMeasureModel(){
    return items_measure;
  }

  // Common
  ListModel {
    id: items_common

    ListElement {
        name: "select"
        img_src: ""
        toggle: true
        selected: true
    }
    ListElement {
        name: "pan"
        img_src: ""
        toggle: true
        selected: false
    }
    ListElement {
        name: "zoom"
        img_src: ""
        toggle: true
        selected: false
    }
    ListElement {
        name: "fit"
        img_src: ""
        toggle: false
        selected: false
    }
    ListElement {
        name: "windowing"
        img_src: ""
        toggle: true
        selected: false
    }
    ListElement {
        name: "auto_windowing"
        img_src: ""
        toggle: false
        selected: false
    }
    ListElement {
        name: "reset_wwl"
        img_src: ""
        toggle: false
        selected: false
    }
    ListElement {
        name: "reset_all"
        img_src: ""
        toggle: false
        selected: false
    }
    ListElement {
        name: "key_image"
        img_src: ""
        toggle: false
        selected: false
    }
    ListElement {
        name: "cross_link"
        img_src: ""
        toggle: false
        selected: false
    }
    ListElement {
        name: "scout_img"
        img_src: ""
        toggle: false
        selected: false
    }
    ListElement {
        name: "report"
        img_src: ""
        toggle: false
        selected: false
    }
  }

  // Selection

  // Measure
  ListModel {
    id: items_measure

    ListElement {
        name: "ruler"
        img_src: ""
        toggle: true
        selected: false
    }
    ListElement {
        name: "angle3"
        img_src: ""
        toggle: true
        selected: false
    }
    ListElement {
        name: "tapeline"
        img_src: ""
        toggle: true
        selected: false
    }
    ListElement {
        name: "angle4"
        img_src: ""
        toggle: true
        selected: false
    }
    ListElement {
        name: "area"
        img_src: ""
        toggle: true
        selected: false
    }
    ListElement {
        name: "arrow"
        img_src: ""
        toggle: true
        selected: false
    }
  }

}