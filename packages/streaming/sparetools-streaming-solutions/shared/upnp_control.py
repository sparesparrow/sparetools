#!/usr/bin/env python3
"""
UPnP Control Script for TV Screen Casting
"""

import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

def send_soap_request(url, service_type, action, args=None):
    """Send a SOAP request to a UPnP service"""
    if args is None:
        args = {}

    # Build SOAP envelope
    soap_body = f"""<?xml version="1.0"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
<s:Body>
<u:{action} xmlns:u="{service_type}">"""

    for arg_name, arg_value in args.items():
        soap_body += f"<{arg_name}>{arg_value}</{arg_name}>"

    soap_body += f"""
</u:{action}>
</s:Body>
</s:Envelope>"""

    headers = {
        'SOAPAction': f'"{service_type}#{action}"',
        'Content-Type': 'text/xml; charset=utf-8'
    }

    response = requests.post(url, data=soap_body, headers=headers, timeout=10)
    return response

def browse_content_directory(server_url, object_id="0"):
    """Browse UPnP ContentDirectory"""
    control_url = f"{server_url}/ctl/ContentDir"
    service_type = "urn:schemas-upnp-org:service:ContentDirectory:1"

    args = {
        'ObjectID': object_id,
        'BrowseFlag': 'BrowseDirectChildren',
        'Filter': '*',
        'StartingIndex': '0',
        'RequestedCount': '10',
        'SortCriteria': ''
    }

    response = send_soap_request(control_url, service_type, 'Browse', args)

    if response.status_code == 200:
        # Parse the response to extract items
        root = ET.fromstring(response.text)
        result_elem = root.find('.//{urn:schemas-upnp-org:service:ContentDirectory:1}Result')

        if result_elem is not None:
            result_xml = result_elem.text
            result_root = ET.fromstring(result_xml)

            items = []
            for item in result_root:
                if item.tag.endswith('item'):
                    title = item.find('.//{http://purl.org/dc/elements/1.1/}title')
                    res = item.find('.//{urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/}res')

                    if title is not None and res is not None:
                        items.append({
                            'id': item.get('id'),
                            'title': title.text,
                            'url': res.text
                        })

            return items

    return []

def set_av_transport_uri(tv_ip, media_url, title="Screen Cast"):
    """Tell the TV to play media from the given URL"""
    control_url = f"http://{tv_ip}:38400/upnp/control/mingusavtr"
    service_type = "urn:schemas-upnp-org:service:AVTransport:1"

    # Create DIDL-Lite XML for the media item
    didl_xml = f"""<?xml version="1.0" encoding="utf-8"?>
<DIDL-Lite xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/"
           xmlns:dc="http://purl.org/dc/elements/1.1/"
           xmlns:upnp="urn:schemas-upnp-org:metadata-1-0/upnp/">
  <item id="1" parentID="0" restricted="1">
    <dc:title>{title}</dc:title>
    <upnp:class>object.item.videoItem</upnp:class>
    <res protocolInfo="http-get:*:video/mp4:*">{media_url}</res>
  </item>
</DIDL-Lite>"""

    args = {
        'InstanceID': '0',
        'CurrentURI': media_url,
        'CurrentURIMetaData': didl_xml
    }

    response = send_soap_request(control_url, service_type, 'SetAVTransportURI', args)
    return response.status_code == 200

def play_media(tv_ip):
    """Start playback on the TV"""
    control_url = f"http://{tv_ip}:38400/upnp/control/mingusavtr"
    service_type = "urn:schemas-upnp-org:service:AVTransport:1"

    args = {
        'InstanceID': '0',
        'Speed': '1'
    }

    response = send_soap_request(control_url, service_type, 'Play', args)
    return response.status_code == 200

def main():
    # Configuration
    minidlna_server = "http://192.168.200.160:8200"
    tv_ip = "192.168.200.44"

    print("🔍 Browsing MiniDLNA content...")

    # Browse the video directory (assuming videos are in object ID that contains them)
    # Let's try browsing the root first
    items = browse_content_directory(minidlna_server, "0")

    print(f"📁 Found {len(items)} items")

    for item in items:
        print(f"  - {item['title']}: {item['url']}")

    # Look for our screen test file
    screen_file = None
    for item in items:
        if 'screen_test' in item['title']:
            screen_file = item
            break

    if screen_file:
        print(f"🎬 Found screen capture: {screen_file['title']}")
        print(f"   URL: {screen_file['url']}")

        # Tell TV to play this file
        print("📺 Telling TV to play screen capture...")

        if set_av_transport_uri(tv_ip, screen_file['url'], screen_file['title']):
            print("✅ Set transport URI successfully")

            # Start playback
            if play_media(tv_ip):
                print("▶️  Started playback on TV!")
            else:
                print("❌ Failed to start playback")
        else:
            print("❌ Failed to set transport URI")
    else:
        print("❌ Screen capture file not found in MiniDLNA")

if __name__ == "__main__":
    main()