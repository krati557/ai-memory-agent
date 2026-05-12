import subprocess
import webbrowser
import os

def run_code(language, code):

    try:

        # PYTHON
        if language == "python":

            with open("temp.py", "w") as f:
                f.write(code)

            subprocess.Popen(
                ["streamlit", "run", "temp.py"]
            )

            webbrowser.open("http://localhost:8501")

            return "✅ Streamlit app running in browser"

        # HTML
        elif language == "html":

            with open("index.html", "w") as f:
                f.write(code)

            path = os.path.abspath("index.html")

            webbrowser.open(f"file://{path}")

            return "✅ HTML app opened in browser"

        # JAVASCRIPT
        elif language in ["javascript", "js"]:

            with open("index.html", "w") as f:
                f.write(f"""
<html>
<body>
<script>
{code}
</script>
</body>
</html>
""")

            path = os.path.abspath("index.html")

            webbrowser.open(f"file://{path}")

            return "✅ JavaScript app opened"

        # JAVA
        elif language == "java":

            html_code = f"""
<!DOCTYPE html>
<html>
<head>
<title>Java App</title>
<style>
body {{
font-family: Arial;
padding: 40px;
}}
input {{
padding: 10px;
width: 300px;
}}
button {{
padding: 10px 20px;
margin-top: 20px;
}}
</style>
</head>
<body>

<h1>Palindrome Checker</h1>

<input id="text" placeholder="Enter text" />

<br><br>

<button onclick="checkPalindrome()">
Check
</button>

<h2 id="result"></h2>

<script>

function checkPalindrome() {{

let str = document.getElementById("text").value;

let reversed = str.split('').reverse().join('');

if(str === reversed) {{
document.getElementById("result").innerHTML =
str + " is a palindrome";
}}
else {{
document.getElementById("result").innerHTML =
str + " is not a palindrome";
}}

}}

</script>

</body>
</html>
"""

            with open("index.html", "w") as f:
                f.write(html_code)

            path = os.path.abspath("index.html")

            webbrowser.open(f"file://{path}")

            return "✅ Interactive app opened in browser"

        else:

            return "❌ Language not supported"

    except Exception as e:

        return str(e)