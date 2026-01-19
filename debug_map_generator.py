
import os
import json
import webbrowser
from dotenv import load_dotenv

# Force load .env
load_dotenv()

def generate_debug_html():
    # 1. Get Keys
    js_api_key = os.getenv("AMAP_MAPS_JS_API_KEY") or os.getenv("AMAP_MAPS_API_KEY")
    security_code = os.getenv("AMAP_SECURITY_CODE", "")
    
    print(f"DEBUG: Using API Key: {js_api_key}")
    print(f"DEBUG: Using Security Code: {security_code}")

    if not js_api_key:
        print("ERROR: No API Key found! Check your .env file.")
        return

    # 2. Generate HTML with Error Handling
    html_content = f"""
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no, width=device-width">
    <title>Amap Fast Debug</title>
    <style>
        html, body, #container {{
            width: 100%;
            height: 100%;
            margin: 0;
            padding: 0;
            font-family: sans-serif;
        }}
        #info {{
            position: absolute;
            top: 20px;
            left: 20px;
            z-index: 100;
            background: white;
            padding: 10px;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}
    </style>
    <!-- 1. Security Config MUST be before Map Script -->
    <script type="text/javascript">
        window._AMapSecurityConfig = {{
            securityJsCode: "{security_code}"
        }};
    </script>
    <!-- 2. Load Map Script -->
    <script type="text/javascript" src="https://webapi.amap.com/maps?v=2.0&key={js_api_key}"></script>
</head>
<body>
    <div id="info">
        <h3>Fast Debugger</h3>
        <p>Key: {js_api_key}</p>
        <p>Security Code: {security_code if security_code else '<span style="color:red">MISSING</span>'}</p>
    </div>
    <div id="container"></div>
    
    <script type="text/javascript">
        // Global Error Handler
        window.onerror = function(msg, url, line, col, error) {{
            document.body.innerHTML += '<div style="position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); background:white; padding:20px; border:2px solid red; z-index:999;">' + 
            '<h2 style="color:red">JS Error Detected</h2>' + 
            '<p>' + msg + '</p>' + 
            '</div>';
        }};

        window.onload = function() {{
            if (typeof AMap === 'undefined') {{
                document.body.innerHTML += '<div style="position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); background:white; padding:20px; border:2px solid red; z-index:999;">' + 
                '<h2 style="color:red">AMap Object Not Found</h2>' + 
                '<p>The High-De Map API script failed to load.</p>' +
                '<ul><li>Check if Key is "Web JS API" type</li><li>Check network connection</li></ul>' +
                '</div>';
                return;
            }}

            try {{
                var map = new AMap.Map("container", {{
                    resizeEnable: true,
                    center: [116.397428, 39.90923],
                    zoom: 11
                }});
                
                var marker = new AMap.Marker({{
                    position: [116.397428, 39.90923],
                    title: "Beijing"
                }});
                map.add(marker);
                
                console.log("Map Init Success");
            }} catch(e) {{
                document.body.innerHTML += '<div style="position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); background:white; padding:20px; border:2px solid red; z-index:999;">' + 
                '<h2 style="color:red">Map Instantiation Error</h2>' + 
                '<p>' + e.message + '</p>' + 
                '</div>';
            }}
        }};
    </script>
</body>
</html>
    """
    
    filename = "fast_debug_map.html"
    with open(filename, "w") as f:
        f.write(html_content)
    
    print(f"Success! Generated {filename}")
    path = os.path.abspath(filename)
    print(f"File path: {path}")
    
    # Try to open automatically
    try:
        webbrowser.open('file://' + path)
    except:
        pass

if __name__ == "__main__":
    generate_debug_html()
