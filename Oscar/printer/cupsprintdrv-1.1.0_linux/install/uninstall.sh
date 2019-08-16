#!/bin/sh

echo "---------------------------------------"
echo "printer Micronics"
echo "printercupsdrv-1.0.0 uninstaller"
echo "---------------------------------------"


if [ "$(id -u)" != "0" ]
then
    echo "This script requires root user access."
    echo "Re-run as root user."
    exit 1
fi

echo "remove rastertoprinter filter"
@if [ -e /usr/lib/cups/filter/rastertoprinter ]; then echo "Removing rastertoprinter"; rm -f /usr/lib/cups/filter/rastertoprinter; fi
@if [ -d /usr/share/cups/model/printer ]; then echo "Removing dir .../cups/model/printer"; rm -rf /usr/share/cups/model/printer; fi
echo ""

echo "Uninstall Complete"
echo "---------------------------------------"

