# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PoiReader
                                 A QGIS plugin
 This plugin reads and display TOMTOM POIs into canvas
                             -------------------
        begin                : 2016-05-25
        copyright            : (C) 2016 by Miles Lee TOMTOM ANZ PTY LTD.
        email                : miles.lee@tomtom.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load PoiReader class from file PoiReader.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .poi_reader import PoiReader
    return PoiReader(iface)
