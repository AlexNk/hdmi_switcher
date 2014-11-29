# -*- coding: utf-8 -*-
#!/usr/bin/python

import subprocess
import re

from PyQt4.QtCore import *
from PyQt4 import QtGui
from PyKDE4.kdecore import *

import ctrl_pacmd

class dialog(QtGui.QDialog):
    def __init__(self, config, on_refresh_cfg):
        super(dialog, self).__init__()
        self.cards_def = ctrl_pacmd.ctrl().list_cards()
        self.cfg = config
        self.on_refresh_cfg = on_refresh_cfg
        self.initUI()
        
    def initUI(self):
        # create controls
        self.lbl_card = QtGui.QLabel(i18n("Sound card:"), self)
        self.cb_card = QtGui.QComboBox(self)
        self.connect(self.cb_card, SIGNAL("activated(int)"), self.on_card_select)

        self.lbl_def_prof = QtGui.QLabel(i18n("Default profile:"), self)
        self.cb_def_prof = QtGui.QComboBox(self)
        self.cb_def_prof.addItem("", None)
        self.connect(self.cb_def_prof, SIGNAL("activated(int)"), self.on_def_prof_select)

        self.lbl_hdmi_prof = QtGui.QLabel(i18n("HDMI profile:"), self)
        self.cb_hdmi_prof = QtGui.QComboBox(self)
        self.cb_hdmi_prof.addItem("", None)
        self.connect(self.cb_hdmi_prof, SIGNAL("activated(int)"), self.on_hdmi_prof_select)

        self.btn_close = QtGui.QPushButton(i18n("Close"), self)
        self.btn_close.clicked.connect(self.close)

        # prefill
        self.read_config()

        # position controls
        self.setFixedSize(450, 250)

        self.lbl_card.move(10, 10)
        self.cb_card.setFixedWidth(self.size().width() - 10 - 10)
        self.cb_card.move(10, self.lbl_card.pos().y() + 22)

        self.lbl_def_prof.move(20, self.cb_card.pos().y() + 22 * 2)
        self.cb_def_prof.setFixedWidth(self.size().width() - 20 - 10)
        self.cb_def_prof.move(20, self.lbl_def_prof.pos().y() + 22)

        self.lbl_hdmi_prof.move(20, self.cb_def_prof.pos().y() + 22 * 1.5)
        self.cb_hdmi_prof.setFixedWidth(self.size().width() - 20 - 10)
        self.cb_hdmi_prof.move(20, self.lbl_hdmi_prof.pos().y() + 22)

        self.btn_close.setFixedWidth(self.size().width() / 3)
        self.btn_close.move(10 + (self.size().width() - self.btn_close.size().width() - 10 - 10) / 2, self.size().height() - 22 - 10)

        self.setWindowTitle(i18n("Configuration"))

    def read_config(self):
        # fill cards
        select_card = -1
        card_idx = self.get_cfg_value("card_idx", "")
        for idx in self.cards_def.keys():
            self.cb_card.addItem("%s: %s" % (idx, self.cards_def[idx]["name"]), idx)
            if (idx == card_idx):
                select_card = self.cb_card.count() - 1
        # select saved card
        if (select_card != -1):
            self.cb_card.setCurrentIndex(select_card)
        elif (len(self.cards_def) > 0):
            self.cb_card.setCurrentIndex(0)
        self.on_card_select(self.cb_card.currentIndex())
        # select saved profile
        if (select_card != -1):
            def_profile = self.get_cfg_value("def_profile", "")
            hdmi_profile = self.get_cfg_value("hdmi_profile", "")
            n = 0
            for profile in self.cards_def[card_idx]["profiles"]:
                if (profile["id"] == def_profile):
                    self.cb_def_prof.setCurrentIndex(n)
                if (profile["id"] == hdmi_profile):
                    self.cb_hdmi_prof.setCurrentIndex(n)
                n += 1

    def get_cfg_value(self, name, def_value):
        val = self.cfg.readEntry(name, def_value)
        return str(val.toString()) if (type(val) == QVariant) else val

    def on_card_select(self, index):
        self.cb_def_prof.clear()
        self.cb_hdmi_prof.clear()
        card_idx = str(self.cb_card.itemData(index).toString())
        for profile in self.cards_def[card_idx]["profiles"]:
            self.cb_def_prof.addItem(profile["name"].decode("utf-8"), profile["id"])
            self.cb_hdmi_prof.addItem(profile["name"].decode("utf-8"), profile["id"])
        self.cfg.writeEntry("card_idx", card_idx)
        self.on_refresh_cfg()

    def on_def_prof_select(self, index):
        card_idx = str(self.cb_card.itemData(self.cb_card.currentIndex()).toString())
        id = str(self.cb_def_prof.itemData(index).toString())
        self.cfg.writeEntry("def_profile", id)
        self.on_refresh_cfg()


    def on_hdmi_prof_select(self, index):
        card_idx = str(self.cb_card.itemData(self.cb_card.currentIndex()).toString())
        id = str(self.cb_hdmi_prof.itemData(index).toString())
        self.cfg.writeEntry("hdmi_profile", id)
        self.on_refresh_cfg()
        
