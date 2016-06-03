# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PoiReader
                                 A QGIS plugin
 This plugin reads and display TOMTOM POIs into canvas
                              -------------------
        begin                : 2016-05-25
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Miles Lee TOMTOM ANZ PTY LTD.
        email                : miles.lee@tomtom.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QObject, SIGNAL
from PyQt4.QtGui import * #QAction, QIcon
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from poi_reader_dialog import PoiReaderDialog
from PyQt4.QtGui import QDialogButtonBox
import os.path
from qgis.core import *
import json
import urllib
from qgis.gui import *
import sys
import ogr, osr

class PoiReader:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        
        self.iface = iface
        #a reference to map cavans
        self.canvas = self.iface.mapCanvas()
        # this QGIS tool emits as QgsPoint after each click on the map canvas
        self.clickTool = QgsMapToolEmitPoint(self.canvas)
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'PoiReader_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = PoiReaderDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Poi Reader')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'PoiReader')
        self.toolbar.setObjectName(u'PoiReader')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('PoiReader', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/PoiReader/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Show TOMTOM POIs'),
            callback=self.run,
            parent=self.iface.mainWindow())
        result_canvasClicked = QObject.connect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDown)
        result_sliderChanged = QObject.connect(self.dlg.horizontalSlider, SIGNAL("valueChanged(int)"), self.handleSliderMove)
        result_pushButtonClicked = self.dlg.pushButton.clicked.connect(self.handleExtract)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Poi Reader'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        # Get the controls' values
        # make our clickTool the tool that we'll use for now
        self.canvas.setMapTool(self.clickTool)
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            #QMessageBox.information( self.iface.mainWindow(),"Info", str(self.dlg.horizontalSlider.value()) )
            

            
    def ComposeQueryString(self, Object, Radius, Lat, Lon):
        ObjectUrlEncoded = urllib.urlencode({'': Object}).replace("=","")
        APISTRING = "https://api.tomtom.com/search/2/poiSearch/" + Object + ".json?key=kspvru2jqtguafeuztf9fx6s&lat=" + Lat + "&lon=" + Lon + "&radius=" + Radius + "&limit=" + str(self.dlg.horizontalSlider.value())
        return APISTRING

    def Json2GeoJson(self, data):
        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry" : {
                        "type": "Point",
                        "coordinates": [d['position']["lon"], d['position']["lat"]],
                        },
                    "properties": {
                        "Name": d['poi']['name'],
                        "Address": d['address']['freeformAddress'] + ' ' + d['address']['country'],
                        "Categories": d['poi']['categories'],
                        "Distance": d['dist'],
                        "Lat": d['position']['lat'],
                        "Lon": d['position']['lon'],
                        },
                    } for d in data['results']]
            }
        
        return geojson

    


    def CoordinateConversion(self, Lat, Lon):
        Canvas = self.iface.mapCanvas()
        CurrentCRS = int(Canvas.mapRenderer().destinationCrs().authid().split(":")[1])
        OutputCRS = 4326
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(Lat, Lon)

        # create coordinate transformation
        inSpatialRef = osr.SpatialReference()
        inSpatialRef.ImportFromEPSG(CurrentCRS)

        outSpatialRef = osr.SpatialReference()
        outSpatialRef.ImportFromEPSG(OutputCRS)

        coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

        # transform point
        point.Transform(coordTransform)

        self.dlg.lineEdit_3.setText(str(point.GetY()))
        self.dlg.lineEdit_4.setText(str(point.GetX()))


    def handleMouseDown(self, point, button):
        self.CoordinateConversion(point.x(), point.y())
        #QMessageBox.information( self.iface.mainWindow(),"Info", "X,Y = %s,%s" % (str(point.x()),str(point.y())) )

    def handleSliderMove(self, number_of_pois):
        self.dlg.label_6.setText(str(number_of_pois))

    def handleExtract(self):
        Object = self.dlg.lineEdit.text()
        Radius = self.dlg.lineEdit_2.text()
        Lat = self.dlg.lineEdit_3.text()
        Lon = self.dlg.lineEdit_4.text()
            
        APISTRING = self.ComposeQueryString(Object, Radius, Lat, Lon)
            
        response = urllib.urlopen(APISTRING)
        jsondata = json.loads(response.read())
        geojson = self.Json2GeoJson(jsondata)

        tempjsonfilename = Object + Lat + Lon + ".json"
        tempjsonfile = open(tempjsonfilename, 'w')
        json.dump(geojson, tempjsonfile)
        tempjsonfile.close()
  
        datasource = tempjsonfilename
        layername = Object
        provider = "ogr"
        vlayer = QgsVectorLayer(datasource, layername, provider)
        QgsMapLayerRegistry.instance().addMapLayer(vlayer)
            
