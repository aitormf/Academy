#
#  Copyright (C) 1997-2016 JDE Developers Team
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see http://www.gnu.org/licenses/.
#  Authors :
#       Irene Lope Rodriguez<irene.lope236@gmail.com>
#       Vanessa Fernandez Matinez<vanessa_1895@msn.com>


from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel
from PyQt5.QtGui import QPen, QPainter
from PyQt5.QtCore import QPoint, QPointF, pyqtSignal, Qt
from PyQt5 import QtGui, QtCore
import numpy as np
import math
from math import pi as pi
import cv2


class MapWidget(QWidget):

    stopSIG=pyqtSignal()
    
    def __init__(self,winParent):    
        super(MapWidget, self).__init__()
        self.winParent=winParent
        self.initUI()
        self.laser = []
        self.trail = []
        
    
    def initUI(self):
        self.map = cv2.imread("resources/images/mapgrannyannie.png", cv2.IMREAD_GRAYSCALE)
        self.map = cv2.resize(self.map, (500, 500))
        image = QtGui.QImage(self.map.data, self.map.shape[1], self.map.shape[0], self.map.shape[1], QtGui.QImage.Format_Indexed8);
        self.pixmap = QtGui.QPixmap.fromImage(image)
        self.height = self.pixmap.height()
        self.width = self.pixmap.width()
        self.mapWidget = QLabel(self)
        self.mapWidget.setPixmap(self.pixmap)
        self.mapWidget.resize(self.width, self.height)

        self.resize(300,300)
        self.setMinimumSize(500,500)


    def setLaserValues(self, laser):
        # Init laser array
        if len(self.laser) == 0:
            for i in range(laser.numLaser):
                self.laser.append((0,0))

        for i in range(laser.numLaser):
            dist = laser.distanceData[i]/1000.0
            angle = -math.pi/2 + math.radians(i)
            self.laser[i] = (dist, angle)


    def RTx(self, angle, tx, ty, tz):
        RT = np.matrix([[1, 0, 0, tx], [0, math.cos(angle), -math.sin(angle), ty], [0, math.sin(angle), math.cos(angle), tz], [0,0,0,1]])
        return RT
        
    
    def RTy(self, angle, tx, ty, tz):
        RT = np.matrix([[math.cos(angle), 0, math.sin(angle), tx], [0, 1, 0, ty], [-math.sin(angle), 0, math.cos(angle), tz], [0,0,0,1]])
        return RT
    
    
    def RTz(self, angle, tx, ty, tz):
        RT = np.matrix([[math.cos(angle), -math.sin(angle), 0, tx], [math.sin(angle), math.cos(angle),0, ty], [0, 0, 1, tz], [0,0,0,1]])
        return RT

    def RTRobot(self):
        RTy = self.RTy(pi, 0.6, -1, 0)
        return RTy


    def drawRobot(self, painter):
        scale = 50

        pose = self.winParent.getPose3D()
        x = pose.getX()
        y = pose.getY()
        yaw = pose.getYaw()

        final_poses = self.RTRobot() * np.matrix([[x], [y], [1], [1]]) * scale
        painter.translate(QPoint(final_poses[0], final_poses[1]))
        painter.rotate(-180*yaw/pi)

        triangle = QtGui.QPolygon()
        triangle.append(QtCore.QPoint(x+50/3, y-4))
        triangle.append(QtCore.QPoint(x+50/3, y+50/3-4))
        triangle.append(QtCore.QPoint(x-9, y+2.25))

        pen = QPen(Qt.red, 2)
        painter.setPen(pen)
        painter.drawPolygon(triangle)

    def prob2Color(self, prob):
        r = 0
        g = 0
        b = 0
        if (prob > 50):
            g = 255 * (prob - 50)/50
            b = 255 * (100 - prob)/50
        elif (prob <= 50):
            b = 255 * prob/50
            r = 255 * (50 - prob)/50

        return QtGui.QColor(r,g,b)



    def drawParticle(self, painter, centerX, centerY, yaw, prob):
        color = self.prob2Color(prob)
        pen = QPen(color, 2)

        #painter.translate(QPoint(centerX, centerX))
        #painter.rotate(-180*yaw/pi)

        painter.setPen(pen)
        brush = QtGui.QBrush(QtCore.Qt.SolidPattern)
        brush.setColor(color)
        painter.setBrush(brush)
        d=5

        painter.drawLine(0,0,17,0)
        painter.drawEllipse(QPoint(centerX, centerY), d, d)


    def drawParticles(self, painter):
        particles = self.winParent.getParticles()
        scale = 50

        for p in particles:
            pos = self.RTRobot() * np.matrix([[p.x], [p.y], [1], [1]]) * scale
            self.drawParticle(painter, pos[0], pos[1], p.yaw, p.prob)


    def paintEvent(self, e):

        copy = self.pixmap.copy()
        painter = QtGui.QPainter(copy)

        painter.translate(QPoint(self.width/2, self.height/2))
        #self.drawTrail(painter)
        #self.drawVacuum(painter)
        self.drawParticles(painter)

        self.mapWidget.setPixmap(copy)
        painter.end()
        
        
class LogoWidget(QWidget):
    stopSIG=pyqtSignal()
    
    def __init__(self,winParent):    
        super(LogoWidget, self).__init__()
        self.winParent=winParent
        self.initUI()
        
    
    def initUI(self):
        self.logo = cv2.imread("resources/logo_jderobot1.png", cv2.IMREAD_UNCHANGED)
        self.logo = cv2.resize(self.logo, (100, 100))
        image = QtGui.QImage(self.logo.data, self.logo.shape[1], self.logo.shape[0], QtGui.QImage.Format_ARGB32);
        self.pixmap = QtGui.QPixmap.fromImage(image)
        self.height = self.pixmap.height()
        self.width = self.pixmap.width()
        self.logoWidget = QLabel(self)
        self.logoWidget.setPixmap(self.pixmap)
        self.logoWidget.resize(self.width, self.height)

        self.resize(300,300)
        self.setMinimumSize(100,100)


