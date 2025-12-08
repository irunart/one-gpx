# Lookup Elevation From DTM File

- **Original Link**: https://hash.hupili.net/lookup-elevation-from-dtm-file
- **Last Fetch Time**: 2025-12-08
- **Author**: hupili
- **Tags**: gpx, elevation, dtm, hk100, data processing

## Summary

This article addresses the issue of inaccurate elevation data in a GPX file for the HK100 race. The author found negative elevation values in the official GPX file and corrected them using Hong Kong's Digital Terrain Model (DTM) data. The article explains how to use the DTM data to look up the correct elevation for each point in the GPX file, providing a more accurate representation of the terrain.

## Sanitized Content

The article discusses an issue found in a GPX file downloaded from the official HK100 website, which was prepared by Coros. The GPX file contained points with negative elevation, as deep as -100m, which is inaccurate. For example, the original file showed a maximum elevation of 859 and a minimum of -102, which contradicts the known elevation of Tai Mo Shan.

To fix this, the author used the Hong Kong government's Digital Terrain Model (DTM) data file, which has a 5m resolution. After applying the DTM data, the fixed GPX file showed a maximum elevation of 928 and all elevations above sea level.

The DTM is a digital terrain model of the Hong Kong Special Administrative Region, providing topography in a 5-meter raster grid with an accuracy of ±5m. It includes non-ground information like elevated roads and bridges. The downloaded DTM file, `Whole_HK_DTM_5m.asc`, is a 300MB plain text file in Esri Grid format.

The metadata of the DTM file includes:
*   `ncols`: 12751
*   `nrows`: 9601
*   `xllcorner`: 799997.5
*   `yllcorner`: 799997.5
*   `cellsize`: 5
*   `NODATA_value`: -9999

The `(xllcorner, yllcorner)` coordinates are in the HK1980 grid system (EPSG:2326), which can be converted to GPS coordinates using the `pyproj` library. This allows for locating the corresponding cell in the DTM matrix given GPS coordinates. The fix for the HK100 course GPX involves iterating through `trkpt` elements in the GPX file and looking up the real elevation from the DTM.

The article also provides Python code to visualize the DTM file, which generates an image showing the silhouette of Hong Kong.
