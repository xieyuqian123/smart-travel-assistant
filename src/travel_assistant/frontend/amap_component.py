
import json

def render_amap_html(api_key: str, markers: list, path_coordinates: list, height: int = 600, security_code: str = "") -> str:
    """Generates the HTML content for embeding an Amap (Gaode Map) instance.
    
    Args:
        api_key: The Amap Web JS API Key.
        markers: List of dicts, each with {'position': [lz, lat], 'title': 'Name', 'content': 'Label'}.
        path_coordinates: List of [lng, lat] pairs defining the route polyline.
        height: Height of the map container in pixels.
        security_code: The Amap Web JS Security Code (jscode), required for v2.0+.
        
    Returns:
        HTML string.
    """
    
    # Serialize data for JS injection
    markers_json = json.dumps(markers)
    path_json = json.dumps(path_coordinates)
    
    html = f"""
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no, width=device-width">
    <title>Amap Itinerary</title>
    <style>
        html, body, #container {{
            width: 100%;
            height: {height}px;
            margin: 0;
            padding: 0;
        }}
        .custom-marker {{
            background-color: white;
            padding: 5px 10px;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            font-size: 12px;
            font-weight: bold;
            color: #333;
            border: 1px solid #ccc;
            white-space: nowrap;
        }}
    </style>
    <!-- Load Amap JS API -->
    <script type="text/javascript">
        window._AMapSecurityConfig = {{
            securityJsCode: '{security_code}' 
        }};
    </script>
    <script type="text/javascript" src="https://webapi.amap.com/maps?v=2.0&key={api_key}"></script>
    <script type="text/javascript">
        // Global error handler for script loading
        window.onerror = function(message, source, lineno, colno, error) {{
            var container = document.getElementById("container");
            if (container) {{
                 container.innerHTML += '<div style="color:red; padding:10px;"><h3>Map Error</h3>' + message + '</div>';
            }}
        }};
    </script>
</head>
<body>
<div id="container"></div>
<script type="text/javascript">
    // Wait for API to load
    window.onload = function() {{
        if (typeof AMap === 'undefined') {{
            document.getElementById("container").innerHTML = '<div style="color:red; padding:20px; text-align:center;"><h3>Amap JS API Failed to Load</h3><p>Possible reasons:</p><ul><li>Invalid API Key</li><li>Network blockage</li><li>Wrong Key Type (Must be "Web JS API")</li></ul></div>';
            return;
        }}
        
        try {{
            var map = new AMap.Map("container", {{
                resizeEnable: true,
                center: [116.397428, 39.90923], // Default center (Beijing)
                zoom: 11
            }});
            
            // Listen for map load complete
            map.on('complete', function() {{
                console.log("Map loaded successfully");
            }});
            
            // Listen for errors (if AMap exposes an error event, usually instantiation throws or logs to console)

            var markersData = {markers_json};
            var pathData = {path_json};
            
            // Add markers
            markersData.forEach(function(item) {{
                // Simple default marker
                var marker = new AMap.Marker({{
                    position: item.position,
                    title: item.title,
                    label: {{
                        content: "<div class='custom-marker'>" + item.content + "</div>",
                        direction: 'top'
                    }}
                }});
                map.add(marker);
            }});
            
            // Draw polyline if path exists
            if (pathData && pathData.length > 1) {{
                var polyline = new AMap.Polyline({{
                    path: pathData,
                    isOutline: true,
                    outlineColor: '#ffeeff',
                    borderWeight: 3,
                    strokeColor: "#3366FF", 
                    strokeOpacity: 1,
                    strokeWeight: 6,
                    strokeStyle: "solid",
                    strokeDasharray: [10, 5],
                    lineJoin: 'round',
                    lineCap: 'round',
                    zIndex: 50,
                }});
                map.add(polyline);
            }}
            
            // Fit view to include all markers and path
            map.setFitView();
            
        }} catch(e) {{
             document.getElementById("container").innerHTML = '<div style="color:red; padding:20px;"><h3>Map Init Exception</h3>' + e.message + '</div>';
        }}
    }};
</script>
</body>
</html>
    """
    return html
