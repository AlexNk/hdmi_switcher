# -*- coding: utf-8 -*-
#!/usr/bin/python
import weakref
import ctrl_pacmd
import config_dialog

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.plasma import Plasma
from PyKDE4 import plasmascript

 
timer_delay = 3 * 1000

class hdmi_plasmoid(plasmascript.Applet):
    def __init__(self,parent,args=None):
        plasmascript.Applet.__init__(self,parent)
        self.ctrl = ctrl_pacmd.ctrl()
        self.enabled = False
        self.rect = None
 
    def init(self):
        self.setHasConfigurationInterface(True)

        self.cfg = self.config()
        self.read_config()

        self.setBackgroundHints(Plasma.Applet.TranslucentBackground)
        self.layout = QGraphicsLinearLayout(self.applet)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setOrientation(Qt.Horizontal)
        self.icon = Plasma.IconWidget()
        self.layout.addItem(self.icon)
        self.resize(128, 128)
        self.connect(self.icon, SIGNAL("clicked()"), self.on_click)

        self.timer = QTimer()
        self.connect(self.timer, SIGNAL("timeout()"), self.on_timer) 
        self.timer.start(timer_delay)

    def paintInterface(self, painter, option, rect):
        if (self.rect == None) or (self.rect != rect):
            self.rect = QRect(rect.x(), rect.y(), rect.width(), rect.height())
            self.update_icon()

    def showConfigurationInterface(self):
        # KDE 4.4 and above
        self.dlg = config_dialog.dialog(self.cfg, self.read_config)
        self.dlg.show() 

    def update_icon(self):
        pixmap = QPixmap(self.rect.width(), self.rect.height())
        pixmap.fill(QColor(0, 0, 0, 0))
        
        paint = QPainter(pixmap)
        paint.setRenderHint(QPainter.SmoothPixmapTransform)
        paint.setRenderHint(QPainter.Antialiasing)

        font = QFont("Arial")
        font.setBold(True)
        font.setPointSize(pixmap.width())
        cur_w = QFontMetrics(font).width("HDMI")
        cur_pt_size = font.pointSize()
        new_w = pixmap.width()
        new_pt_size = new_w * (float(cur_pt_size) / float(cur_w))
        font.setPointSize(new_pt_size)
        paint.setFont(font)
           
        paint.setPen(QColor(150, 0, 0) if self.enabled else QColor(64, 64, 64))
        paint.drawText(pixmap.rect(), Qt.AlignVCenter | Qt.AlignHCenter, "HDMI")
        paint.end()

        self.icon.setIcon(QIcon(pixmap))
        self.icon.update()

    def on_click(self):
        self.enabled = not self.enabled
        self.ctrl.select_profile(self.card_idx, self.hdmi_profile if self.enabled else self.def_profile)
        self.update_icon()

    def on_timer(self):
        active = self.ctrl.get_active_profile(self.card_idx)
        if (active != None):
            print active, self.hdmi_profile
            enabled = (active == self.hdmi_profile)
            if (enabled != self.enabled):
                self.enabled = enabled
                self.update_icon()

    def read_config(self):
        self.card_idx = self.get_cfg_value("card_idx", "")
        self.def_profile = self.get_cfg_value("def_profile", "")
        self.hdmi_profile = self.get_cfg_value("hdmi_profile", "")

    def get_cfg_value(self, name, def_value):
        val = self.cfg.readEntry(name, def_value)
        return str(val.toString()) if (type(val) == QVariant) else val

def CreateApplet(parent):
    return hdmi_plasmoid(parent)
